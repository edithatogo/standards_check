"""Contract preview is a constrained static mirror, not a data export."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError

from scripts import render_contract_preview as preview

ROOT = Path(__file__).resolve().parents[1]


def test_table_escapes_all_content():
    html = preview.table(["<Title>"], [["<script>alert(1)</script>&"]])
    assert "<script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;&amp;" in html
    assert '<th scope="col">&lt;Title&gt;</th>' in html


def test_reference_registry_rejects_duplicate_ids():
    assert preview.registry([{"id": "a"}, {"id": "b"}]) == {"a", "b"}
    with pytest.raises(ValueError, match="duplicate"):
        preview.registry([{"id": "a"}, {"id": "a"}])


def test_planned_only_boundary():
    planned = {"status": "planned", "design": {"inputs": []}, "freeze": None, "runs": [], "claims": [{"status": "planned"}]}
    preview.require_planned(planned)
    for path, value in [("status", "executed"), ("freeze", {}), ("runs", [{}]), ("claims", [{"status": "observed"}]), ("design", {"inputs": [{}]})]:
        modified = deepcopy(planned)
        modified[path] = value
        with pytest.raises(ValueError, match="planned"):
            preview.require_planned(modified)


def test_committed_contracts_and_exact_preview(tmp_path):
    output = tmp_path / "preview"
    revision = "a" * 40
    manifest = preview.build(ROOT, output, revision)
    assert manifest["revision"] == revision
    assert manifest["dataset_status"] == "held"
    assert manifest["publication_status"] == "planned"
    assert set(manifest["files"]) == set(preview.SOURCES.values()) | {"index.html", "README.md"}
    for source, filename in preview.SOURCES.items():
        assert (output / filename).read_bytes() == (ROOT / source).read_bytes()
    for filename, digest in manifest["files"].items():
        assert hashlib.sha256((output / filename).read_bytes()).hexdigest() == digest
    assert json.loads((output / "manifest.json").read_text()) == manifest
    page = (output / "index.html").read_text()
    assert "E4" in page and "E8" in page and "F11" in page
    assert "coverage_cells" in page and "citation_pairs" in page and "Planned" in page
    with pytest.raises(ValueError, match="new directory"):
        preview.build(ROOT, output, revision)
    with pytest.raises(ValueError, match="revision"):
        preview.build(ROOT, tmp_path / "bad-revision", "main")
    assert not (tmp_path / "bad-revision").exists()


def test_committed_graph_rejects_unbound_and_unsafe_plan():
    graph = json.loads((ROOT / preview.GRAPH).read_text())
    schema = json.loads((ROOT / preview.SCHEMA).read_text())
    publication = json.loads((ROOT / preview.FOLLOWUP).read_text())
    preview.validate_graph(ROOT, graph, schema, publication)
    for defect in ("duplicate", "experiment", "foreign_key", "figure", "workflow", "task", "issue", "input_producer", "dataset"):
        bad = deepcopy(graph)
        if defect == "duplicate":
            bad["tables"].append(deepcopy(bad["tables"][0]))
        elif defect == "experiment":
            bad["tables"][0]["experiment_ids"] = ["EX"]
        elif defect == "foreign_key":
            bad["tables"][1]["references"][0]["column"] = "missing"
        elif defect == "figure":
            bad["figures"][0]["table_ids"] = ["missing"]
        elif defect == "workflow":
            bad["gates"][0]["workflow"] = ".github/workflows/nonexistent.yml"
        elif defect == "task":
            bad["gates"][0]["task"] = "T01.999"
        elif defect == "issue":
            bad["gates"][0]["issue"] = 999
        elif defect == "input_producer":
            bad["existing_inputs"][0]["producer"] = "scripts/nonexistent.py"
        else:
            bad["release"]["dataset_status"] = "approved"
        with pytest.raises((ValueError, ValidationError)):
            preview.validate_graph(ROOT, bad, schema, publication)
