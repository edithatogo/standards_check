"""Malformed files, mismatched identities and incomplete accessibility fail closed."""

import json
import shutil
import sys
import xml.etree.ElementTree as ET

from jsonschema import Draft202012Validator
import pytest

from scripts import validate_artifacts as artifacts
from scripts import verify_site_accessibility as accessibility

STEM = "new-databases-registers"


@pytest.fixture
def artifact_root(tmp_path, monkeypatch):
    for name, source in (
        ("recipes", artifacts.RECIPES),
        ("inputs", artifacts.INPUTS),
        ("generated", artifacts.GENERATED),
    ):
        destination = tmp_path / name
        destination.mkdir()
        for path in source.glob(f"{STEM}.*"):
            shutil.copyfile(path, destination / path.name)
    pack = tmp_path / "packs/org.prisma/prisma/2020/pack.json"
    pack.parent.mkdir(parents=True)
    pack.write_text("{}")
    monkeypatch.setattr(artifacts, "ROOT", tmp_path)
    monkeypatch.setattr(artifacts, "RECIPES", tmp_path / "recipes")
    monkeypatch.setattr(artifacts, "INPUTS", tmp_path / "inputs")
    monkeypatch.setattr(artifacts, "GENERATED", tmp_path / "generated")
    monkeypatch.setattr(artifacts, "VARIANTS", {STEM: artifacts.VARIANTS[STEM]})
    monkeypatch.setattr(sys, "argv", ["validate_artifacts.py"])
    return tmp_path


@pytest.mark.parametrize("raw", [b"{", b"\xff", b"null", b"[]"])
def test_json_admission_rejects_malformed_or_non_object_inputs(tmp_path, monkeypatch, capsys, raw):
    monkeypatch.setattr(artifacts, "ROOT", tmp_path)
    path = tmp_path / "invalid.json"
    path.write_bytes(raw)
    with pytest.raises(SystemExit) as error:
        artifacts.validate(path, Draft202012Validator({"type": "object"}))
    assert error.value.code == 1
    assert "ERROR:" in capsys.readouterr().err


@pytest.mark.parametrize("schema", [[], {"type": 42}])
def test_invalid_schema_cannot_turn_validation_into_a_pass(tmp_path, monkeypatch, schema):
    monkeypatch.setattr(artifacts, "ROOT", tmp_path)
    monkeypatch.setattr(artifacts, "SCHEMAS", tmp_path)
    (tmp_path / "invalid.json").write_text(json.dumps(schema))
    with pytest.raises(SystemExit) as error:
        artifacts.make_validator("invalid.json")
    assert error.value.code == 1


@pytest.mark.parametrize(
    "group, field, value, message",
    [
        ("recipes", "recipe_id", "example/other-recipe", "wrong recipe_id"),
        ("recipes", "source_standard", "example/other-standard", "wrong source_standard"),
        ("recipes", "input_contract", "dev.other.contract.v1", "wrong input contract"),
        ("inputs", "template", "updated_databases_registers", "wrong template"),
        ("generated", "recipe_id", "example/other-recipe", "wrong recipe"),
    ],
)
def test_valid_json_with_wrong_family_identity_is_rejected(
    artifact_root, capsys, group, field, value, message
):
    suffix = ".scene.json" if group == "generated" else ".json"
    path = artifact_root / group / f"{STEM}{suffix}"
    document = json.loads(path.read_text())
    document[field] = value
    if group == "inputs":
        document["previous_review"] = {"studies": 1, "reports": 1}
        document["total_included"]["studies"] += 1
        document["total_included"]["reports"] += 1
    path.write_text(json.dumps(document))
    with pytest.raises(SystemExit) as error:
        artifacts.main()
    assert error.value.code == 1
    assert message in capsys.readouterr().err


def test_missing_generated_artifacts_require_explicit_scaffolding_opt_in(
    artifact_root, monkeypatch
):
    (artifact_root / "generated" / f"{STEM}.svg").unlink()
    with pytest.raises(SystemExit) as error:
        artifacts.main()
    assert error.value.code == 1
    monkeypatch.setattr(sys, "argv", ["validate", "--allow-missing-generated"])
    artifacts.main()
    (artifact_root / "packs/org.prisma/prisma/2020/pack.json").unlink()
    with pytest.raises(SystemExit):
        artifacts.main()


@pytest.mark.parametrize(
    "defect, message",
    [
        ("reading_order", "reading order differs from its recipe"),
        ("nodes", "node count differs from its recipe"),
    ],
)
def test_scene_cannot_lose_an_item_or_change_its_order(artifact_root, capsys, defect, message):
    path = artifact_root / "generated" / f"{STEM}.scene.json"
    scene = json.loads(path.read_text())
    if defect == "reading_order":
        scene[defect].reverse()
    else:
        scene[defect].pop()
    path.write_text(json.dumps(scene))
    with pytest.raises(SystemExit):
        artifacts.main()
    assert message in capsys.readouterr().err


@pytest.mark.parametrize(
    "attribute, value, message",
    [
        ("role", "presentation", "role=img"),
        ("aria-labelledby", "other", "identify its title"),
        ("aria-describedby", "other", "complete accessible description"),
    ],
)
def test_svg_accessible_entrypoints_are_required(artifact_root, capsys, attribute, value, message):
    path = artifact_root / "generated" / f"{STEM}.svg"
    root = ET.fromstring(path.read_text())
    root.set(attribute, value)
    path.write_text(ET.tostring(root, encoding="unicode"))
    with pytest.raises(SystemExit):
        artifacts.main()
    assert message in capsys.readouterr().err


def test_site_cli_checks_every_page_and_returns_nonzero_for_any_failure(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(sys, "argv", ["accessibility"])
    assert accessibility.main() == 2
    monkeypatch.setattr(sys, "argv", ["accessibility", str(tmp_path)])
    assert accessibility.main() == 1
    valid = '<a href="#main-content">Skip</a><h1>Title</h1><main id="main-content"></main>'
    (tmp_path / "valid.html").write_text(valid)
    assert accessibility.main() == 0
    (tmp_path / "bad.html").write_text("<h1>Bad</h1>")
    assert accessibility.main() == 1
    assert "bad.html" in capsys.readouterr().err
