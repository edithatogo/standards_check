"""Exercise the explicit, bounded legacy-to-Rust PRISMA count contract.

Run from the repository root with ``python -m scripts.qualify_legacy_prisma``.
This is a differential fixture runner, not a converter or a cutover decision.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

from .check_standardflow_import import git
from .orthogonal_experiments import generated_pair
from .source_xml import parse_xml
from .validate_artifacts import make_validator, validate, validate_svg
from .verify_legacy_standardflow import verify_history

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "legacy/standardflow"
CORPUS = ROOT / "contracts/examples/legacy-prisma-parity.json"
CONDITIONS = {
    "database_records_only",
    "duplicates_are_only_prescreen_removal",
    "all_sought_reports_retrieved",
    "legacy_full_text_articles_are_reports",
    "one_report_per_included_study",
    "exclusion_reason_partition_supplied",
}
COUNT_FIELDS = {
    "identified",
    "duplicates",
    "screened",
    "records_excluded",
    "assessed",
    "reports_excluded",
    "new_studies",
    "previous_studies",
    "total_studies",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_pair(case: dict, legacy: dict) -> None:
    """Check supplied witnesses and both inputs without filling missing facts."""
    flow = case["rust_input"]
    require(
        flow["template"] in {"new_databases_registers", "updated_databases_registers"},
        "only database-only new/updated pairs are in this contract",
    )
    updated = flow["template"] == "updated_databases_registers"
    conditions = CONDITIONS | ({"previous_and_new_studies_disjoint"} if updated else set())
    require(
        case["conditions"] == dict.fromkeys(conditions, True)
        and all(value is True for value in case["conditions"].values()),
        "all explicit conditions must be supplied as true; they cannot be inferred",
    )
    counts = case["expected_counts"]
    require(
        set(counts) == COUNT_FIELDS
        and all(type(value) is int and 0 <= value <= 2**53 - 1 for value in counts.values()),
        "expected counts must be explicit nonnegative safe integers",
    )
    require(
        counts["identified"] == counts["duplicates"] + counts["screened"]
        and counts["screened"] == counts["records_excluded"] + counts["assessed"]
        and counts["assessed"] == counts["reports_excluded"] + counts["new_studies"]
        and counts["total_studies"] == counts["previous_studies"] + counts["new_studies"],
        "authored expectations violate count conservation",
    )
    prefix = "new_" if updated else ""
    expected_legacy = {
        "diagram_type": "PRISMA_2020_UPDATED" if updated else "PRISMA",
        prefix + "records_identified": counts["identified"],
        prefix + "records_after_duplicates_removed": counts["screened"],
        prefix + "records_screened": counts["screened"],
        prefix + "records_excluded": counts["records_excluded"],
        prefix + "full_text_articles_assessed": counts["assessed"],
        prefix + "full_text_articles_excluded": counts["reports_excluded"],
        prefix + "studies_included": counts["new_studies"],
    }
    if updated:
        expected_legacy.update(
            previous_studies=counts["previous_studies"],
            total_studies_included=counts["total_studies"],
        )
    else:
        require(counts["previous_studies"] == 0, "a new review cannot supply previous studies")
    require(legacy == expected_legacy, "legacy counts differ from the authored expectations")
    database = flow["databases_registers"]
    expected_database = {
        "databases": counts["identified"],
        "registers": 0,
        "duplicate_records_removed": counts["duplicates"],
        "records_marked_ineligible_by_automation": 0,
        "records_removed_other_reasons": 0,
        "records_screened": counts["screened"],
        "records_excluded": counts["records_excluded"],
        "reports_sought": counts["assessed"],
        "reports_not_retrieved": 0,
        "reports_assessed": counts["assessed"],
        "reports_included": counts["new_studies"],
    }
    require(
        {key: value for key, value in database.items() if key != "reports_excluded"}
        == expected_database,
        "explicit database counts differ or are missing",
    )
    reasons = database["reports_excluded"]
    require(
        sum(reason["reports"] for reason in reasons) == counts["reports_excluded"],
        "the supplied exclusion-reason partition must match the legacy total",
    )
    require(flow["other_methods"] is None, "other-method streams are outside this contract")
    for field, count in (("new_included", "new_studies"), ("total_included", "total_studies")):
        require(
            flow[field] == {"studies": counts[count], "reports": counts[count]},
            "this contract requires one report per included study",
        )
    previous = {"studies": counts["previous_studies"], "reports": counts["previous_studies"]}
    require(
        flow["previous_review"] == (previous if updated else None),
        "previous review must explicitly preserve one report per included study",
    )


def expected_node_counts(case: dict) -> tuple[dict, dict]:
    """Independent observations expected in each renderer's distinct node model."""
    counts = case["expected_counts"]
    values = [
        counts[key]
        for key in (
            "identified",
            "screened",
            "screened",
            "records_excluded",
            "assessed",
            "reports_excluded",
            "new_studies",
        )
    ]
    updated = case["rust_input"]["template"] == "updated_databases_registers"
    if updated:
        values = [counts["previous_studies"], *values, counts["total_studies"]]
    legacy = {chr(ord("A") + index): [value] for index, value in enumerate(values)}
    rust = {
        "db-identified": [counts["identified"], 0, counts["identified"]],
        "db-removed": [counts["duplicates"], 0, 0, counts["duplicates"]],
        "db-screened": [counts["screened"]],
        "db-records-excluded": [counts["records_excluded"]],
        "db-reports-sought": [counts["assessed"]],
        "db-reports-not-retrieved": [0],
        "db-reports-assessed": [counts["assessed"]],
        "db-reports-excluded": [
            counts["reports_excluded"],
            *[
                reason["reports"]
                for reason in case["rust_input"]["databases_registers"]["reports_excluded"]
            ],
        ],
    }
    if updated:
        rust["previous-included"] = [counts["previous_studies"]] * 2
    rust["new-included"] = [counts["new_studies"]] * 2
    if updated:
        rust["total-included"] = [counts["total_studies"]] * 2
    return legacy, rust


def displayed_counts(text: str) -> list[int]:
    return [int(value) for value in re.findall(r"\(n\s*=\s*(\d+)\)", text)]


def legacy_svg_counts(path: Path) -> dict[str, list[int]]:
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    nodes = parse_xml(path.read_bytes(), 16_000_000).findall(".//svg:g[@class='node']", namespace)
    result = {}
    for node in nodes:
        identifier = node.findtext("svg:title", namespaces=namespace)
        if identifier is None or identifier in result:
            raise ValueError("legacy SVG has invalid node IDs")
        text = "\n".join("".join(line.itertext()) for line in node.findall("svg:text", namespace))
        result[identifier] = displayed_counts(text)
    return result


def run(
    command: list[str], *, cwd: Path = ROOT, success: bool = True
) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        command, cwd=cwd, env=environment, capture_output=True, text=True, timeout=120
    )
    if success and result.returncode:
        raise ValueError(
            f"Command failed ({result.returncode}): {command}\n{result.stdout}{result.stderr}"
        )
    return result


def render_legacy(input_path: Path, output: Path) -> None:
    run(
        [sys.executable, "-m", "src.cli", "generate", str(input_path), "--output", str(output)],
        cwd=LEGACY,
    )


def rust_command(cli: Path, input_path: Path, output: Path, format_: str) -> list[str]:
    return [
        str(cli),
        "--json",
        "diagram",
        "prisma",
        str(input_path),
        "--format",
        format_,
        "--output",
        str(output),
    ]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exercise_pair(case: dict, cli: Path, work: Path, legacy: dict | None = None) -> dict:
    work.mkdir()
    input_path = work / "input.json"
    input_path.write_text(json.dumps(case["rust_input"]), encoding="utf-8")
    legacy_output = work / "legacy.svg"
    legacy_path = LEGACY / case["legacy_fixture"] if legacy is None else work / "legacy.json"
    if legacy is not None:
        legacy_path.write_text(json.dumps(legacy), encoding="utf-8")
    render_legacy(legacy_path, legacy_output)
    expected_legacy, expected_rust = expected_node_counts(case)
    observed_legacy = legacy_svg_counts(legacy_output)
    # Legacy duplicates its inclusion count into a meta-analysis claim without evidence.
    # That node is deliberately excluded from this count-preservation contract.
    ignored = "J" if case["rust_input"]["template"].startswith("updated_") else "H"
    require(observed_legacy.pop(ignored, None) is not None, "legacy synthesis node is missing")
    require(observed_legacy == expected_legacy, f"{case['id']}: legacy displayed counts differ")
    outputs = {"legacy.svg": legacy_output}
    for format_, suffix in (("scene-json", "scene.json"), ("svg", "svg"), ("text", "txt")):
        output = work / f"rust.{suffix}"
        run(rust_command(cli, input_path, output, format_))
        outputs[output.name] = output
    scene = validate(outputs["rust.scene.json"], make_validator("scene-graph.v1.schema.json"))
    require(len(scene["nodes"]) == len(expected_rust), "Rust scene node count differs")
    for field in ("label", "aria_label"):
        observed = {node["id"]: displayed_counts(node[field]) for node in scene["nodes"]}
        require(observed == expected_rust, f"{case['id']}: Rust {field} counts differ")
    require(scene["reading_order"] == list(expected_rust), "Rust reading order differs")
    validate_svg(outputs["rust.svg"], scene)
    text = outputs["rust.txt"].read_text(encoding="utf-8")
    require(text == scene["text_equivalent"], "Rust text output differs from its scene")
    labels = {node["id"]: node["label"] for node in scene["nodes"]}
    require(all(label in text for label in labels.values()), "text equivalent omits a stage")
    for edge in scene["edges"]:
        relationship = f"{labels[edge['from']]} → {labels[edge['to']]} ({edge['kind']})"
        require(relationship in text, "text equivalent omits a flow relationship")
    return {
        "id": case["id"],
        "counts": case["expected_counts"],
        "legacy_nodes_compared": list(expected_legacy),
        "rust_nodes_compared": list(expected_rust),
        "outputs_sha256": {name: digest(path) for name, path in outputs.items()},
    }


def exercise_difference(case: dict, legacy: dict, cli: Path, work: Path) -> dict:
    """Assert intentional stricter Rust rejection; never count it as equivalence."""
    work.mkdir()
    legacy = deepcopy(legacy)
    flow = deepcopy(case["rust_input"])
    if flow["template"] == "new_databases_registers":
        legacy["records_screened"] += 1
        flow["databases_registers"]["records_screened"] += 1
        name, diagnostic, node = "screening-conservation", "SF-PRISMA-010", "C"
        changed_count = legacy["records_screened"]
    else:
        legacy["total_studies_included"] += 1
        for field in ("studies", "reports"):
            flow["total_included"][field] += 1
        name, diagnostic, node = "updated-total-conservation", "SF-PRISMA-040", "I"
        changed_count = legacy["total_studies_included"]
    legacy_input, rust_input = work / "legacy.json", work / "rust.json"
    legacy_input.write_text(json.dumps(legacy), encoding="utf-8")
    rust_input.write_text(json.dumps(flow), encoding="utf-8")
    legacy_output, rust_output = work / "legacy.svg", work / "rust.svg"
    render_legacy(legacy_input, legacy_output)
    require(
        legacy_svg_counts(legacy_output).get(node) == [changed_count],
        "legacy did not render the inconsistent count",
    )
    result = run(rust_command(cli, rust_input, rust_output, "svg"), success=False)
    require(
        result.returncode == 1 and not rust_output.exists(),
        "inconsistent Rust input must fail without producing an artifact",
    )
    error = json.loads(result.stderr)["error"]
    codes = sorted({item["code"] for item in error["diagnostics"]["diagnostics"]})
    require(
        error["kind"] == "validation" and diagnostic in codes,
        "Rust rejected the counterexample for the wrong reason",
    )
    return {
        "id": name,
        "legacy_exit_code": 0,
        "rust_exit_code": 1,
        "rust_output_created": False,
        "rust_diagnostic_codes": codes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rust-cli", required=True, type=Path, help="Built standardflow executable"
    )
    parser.add_argument("--output", type=Path, help="Write the JSON evidence receipt")
    arguments = parser.parse_args()
    cli = arguments.rust_cli.resolve(strict=True)
    provenance = verify_history()
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    require(
        corpus["schema_version"] == "dev.standardflow.legacy-prisma-qualification.v1",
        "unexpected differential corpus version",
    )
    require(
        [case["id"] for case in corpus["cases"]] == ["new-database-only", "updated-database-only"],
        "both declared cases are required",
    )
    pairs, differences = [], []
    generated, generated_differences = [], []
    # Keep temporary paths inside ROOT so the shared artifact validator can name them.
    with tempfile.TemporaryDirectory(prefix=".legacy-prisma-qualification-", dir=ROOT) as temporary:
        work = Path(temporary)
        for case in corpus["cases"]:
            fixture = (LEGACY / case["legacy_fixture"]).resolve(strict=True)
            require(fixture.is_relative_to(LEGACY), "fixture must belong to the preserved subtree")
            legacy = json.loads(fixture.read_text(encoding="utf-8"))
            validate_pair(case, legacy)
            pairs.append(exercise_pair(case, cli, work / case["id"]))
            differences.append(
                exercise_difference(case, legacy, cli, work / (case["id"] + "-invalid"))
            )
        for parts in ((1, 2, 3, 4), (17, 5, 9, 61), (101, 37, 23, 89)):
            for previous in (None, 13):
                case, legacy = generated_pair(parts, previous)
                validate_pair(case, legacy)
                generated.append(exercise_pair(case, cli, work / case["id"], legacy))
                generated_differences.append(
                    exercise_difference(case, legacy, cli, work / (case["id"] + "-invalid"))
                )
    require(verify_history() == provenance, "source provenance changed during qualification")
    receipt = {
        "result": "pass",
        "claim": "bounded legacy-to-Rust PRISMA count preservation",
        "repository_revision": git(ROOT, "rev-parse", "HEAD"),
        "working_tree_status": git(ROOT, "status", "--short"),
        "source_provenance": provenance,
        "corpus_sha256": digest(CORPUS),
        "rust_executable_sha256": digest(cli),
        "python": sys.version.split()[0],
        "graphviz": run(["dot", "-V"]).stderr.strip(),
        "dependencies": {
            name: importlib.metadata.version(name) for name in ("click", "graphviz", "jsonschema")
        },
        "pairs": pairs,
        "intentional_validation_differences": differences,
        "generated_pairs": generated,
        "generated_intentional_validation_differences": generated_differences,
        "claim_limits": [
            "two authored and six generated database-only pairs under explicitly supplied conditions",
            "not full legacy-to-Rust semantic, layout, format, CLI or web compatibility",
            "legacy quantitative-synthesis claims are excluded from comparison",
            "structural text/ARIA fidelity is not assistive-technology or accessibility certification",
            "not independent methodological approval, source-rights clearance or a cutover decision",
        ],
    }
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(f"Legacy PRISMA qualification failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
