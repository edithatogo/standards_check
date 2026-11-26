"""Run only after the existing locked native CLI build; synthetic, offline evidence."""

import json
from copy import deepcopy
from pathlib import Path

from scripts.qualify_legacy_prisma import digest, displayed_counts, run, rust_command
from scripts.qualify_searchright_exchange import flow_view
from scripts.validate_artifacts import make_validator, validate, validate_svg

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/searchright-exchange/complete-flow.json"
CLI = ROOT / "target/debug/standardflow"
OUTPUT = ROOT / "target/coverage/searchright-native"

# Independently specified from the original synthetic counts, not the mapped output.
EXPECTED = {
    "db-identified": [8, 2, 10],
    "db-removed": [1, 1, 0, 2],
    "db-screened": [8],
    "db-records-excluded": [3],
    "db-reports-sought": [5],
    "db-reports-not-retrieved": [1],
    "db-reports-assessed": [4],
    "db-reports-excluded": [2, 1, 1],
    "new-included": [1, 2],
}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_native_synthetic_flow_conservation():
    # No build/download here. Assurance prepares the locked executable first.
    cli = CLI.resolve(strict=True)
    OUTPUT.mkdir(parents=True, exist_ok=False)
    source = json.loads(FIXTURE.read_bytes())
    mapping = flow_view(
        source, expected_review="fixture:independent-control", template="new_databases_registers"
    )
    assert mapping["status"] == "candidate_only"
    source_path = OUTPUT / "source.json"
    source_path.write_bytes(FIXTURE.read_bytes())
    mapping_path = OUTPUT / "mapping.json"
    write_json(mapping_path, mapping)
    input_path = OUTPUT / "mapped-flow.json"
    write_json(input_path, mapping["view"])
    outputs = {
        "scene-json": OUTPUT / "scene.json",
        "svg": OUTPUT / "scene.svg",
        "text": OUTPUT / "scene.txt",
    }
    for format_, path in outputs.items():
        run(rust_command(cli, input_path, path, format_))
    scene = validate(outputs["scene-json"], make_validator("scene-graph.v1.schema.json"))
    assert len(scene["nodes"]) == len(EXPECTED)
    assert scene["reading_order"] == list(EXPECTED)
    assert len(scene["edges"]) == 8
    assert {(edge["from"], edge["to"]) for edge in scene["edges"]} == {
        ("db-identified", "db-removed"),
        ("db-identified", "db-screened"),
        ("db-screened", "db-records-excluded"),
        ("db-screened", "db-reports-sought"),
        ("db-reports-sought", "db-reports-not-retrieved"),
        ("db-reports-sought", "db-reports-assessed"),
        ("db-reports-assessed", "db-reports-excluded"),
        ("db-reports-assessed", "new-included"),
    }
    observations = {}
    for field in ("label", "aria_label"):
        observed = {node["id"]: displayed_counts(node[field]) for node in scene["nodes"]}
        assert observed == EXPECTED
        excluded = next(node[field] for node in scene["nodes"] if node["id"] == "db-reports-excluded")
        assert "Synthetic A (n = 1)" in excluded
        assert "Synthetic B (n = 1)" in excluded
        assert excluded.index("Synthetic A") < excluded.index("Synthetic B")
        observations[field] = observed
    validate_svg(outputs["svg"], scene)
    text = outputs["text"].read_text(encoding="utf-8")
    assert text == scene["text_equivalent"]
    labels = {node["id"]: node["label"] for node in scene["nodes"]}
    assert all(label in text for label in labels.values())
    for edge in scene["edges"]:
        assert f"{labels[edge['from']]} → {labels[edge['to']]} ({edge['kind']})" in text

    # Mutate one native input count; bypass the Python precheck intentionally.
    bad = deepcopy(mapping["view"])
    bad["databases_registers"]["records_screened"] += 1
    bad_input, bad_output = OUTPUT / "negative-input.json", OUTPUT / "rejected.svg"
    write_json(bad_input, bad)
    negative = run(rust_command(cli, bad_input, bad_output, "svg"), success=False)
    (OUTPUT / "negative-stderr.json").write_text(negative.stderr, encoding="utf-8")
    assert negative.returncode == 1 and not bad_output.exists()
    error = json.loads(negative.stderr)["error"]
    codes = sorted({item["code"] for item in error["diagnostics"]["diagnostics"]})
    assert error["kind"] == "validation" and "SF-PRISMA-010" in codes
    pins = [
        FIXTURE,
        ROOT / "scripts/qualify_searchright_exchange.py",
        ROOT / "schemas/prisma-flow.v1.schema.json",
        ROOT / "schemas/scene-graph.v1.schema.json",
        ROOT / "recipes/prisma-2020/new-databases-registers.json",
        ROOT / "tests/fixtures/searchright-exchange/flow.schema.json",
        ROOT / "Cargo.lock",
        ROOT / "rust-toolchain.toml",
        Path(__file__).resolve(),
    ]
    write_json(
        OUTPUT / "receipt.json",
        {
            "scope": "synthetic_offline_native_conservation_only",
            "pins": {str(path.relative_to(ROOT)): digest(path) for path in pins},
            "native_cli_sha256": digest(cli),
            "artifacts": {path.name: digest(path) for path in sorted(OUTPUT.iterdir())},
            "expected_node_counts": EXPECTED,
            "observed_node_counts": observations,
            "reading_order": scene["reading_order"],
            "edges_checked": len(scene["edges"]),
            "negative": {
                "returncode": negative.returncode,
                "diagnostic_codes": codes,
                "output_created": False,
            },
            "consumer_runtime_qualified": False,
            "canonical_packs_promoted": 0,
        },
    )
