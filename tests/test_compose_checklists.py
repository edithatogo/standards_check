"""Synthetic composition controls; similarity never discharges an obligation."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import compose_checklists as composition


def rights(status="cleared"):
    return {
        "status": status,
        "spdx": "CC0-1.0",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Synthetic fixture",
        "redistribution": "Synthetic fixture only",
    }


def pack(name, *texts):
    return {
        "schema_version": "dev.standardflow.standard-pack.v1",
        "pack_id": f"test/{name}/1",
        "version": "1",
        "kind": "reporting",
        "title": "Synthetic checklist",
        "authority": {
            "publisher": "Fixture",
            "source_url": "https://example.org/checklist",
            "retrieved_at": "2026-11-25",
            "source_sha256": "a" * 64,
        },
        "verification": {
            "status": "source_reconciled",
            "verified_at": "2026-11-25",
            "verified_by": ["Fixture"],
            "evidence": ["Synthetic evidence"],
        },
        "rights": rights(),
        "requirements": [
            {
                "id": f"item:{i}",
                "display_number": str(i),
                "section": "Synthetic",
                "verbatim_text": text,
                "normalized_requirement": text,
                "guidance": None,
                "source_anchor": f"table/row/{i}",
                "rights": {"inherit_from_pack": True},
                "evidence_expectations": ["document_span"],
            }
            for i, text in enumerate(texts, 1)
        ],
    }


def test_exact_repeat_selection_is_deduplicated_but_text_matches_are_not():
    a = pack("a", "Report all outcomes.", "Report trial registration.")
    b = pack("b", "Report all outcomes.", "Report one outcome.")
    result = composition.compose([a, b, deepcopy(a)], top_k=2)
    assert result == composition.compose([b, a], top_k=2)
    assert len(result["packs"]) == 2
    assert len(result["requirements"]) == 4
    assert result["semantic_merges"] == 0
    assert result["applicability"] == "not_assessed"
    assert all(edge["status"] == "candidate_similarity" for edge in result["candidates"])
    assert any(edge["score"] == 1.0 for edge in result["candidates"])
    assert "Report all outcomes" not in json.dumps(result)
    assert result["requirements"][0]["source_anchor"] == "table/row/1"
    assert all(len(p["pack_content_sha256"]) == 64 for p in result["packs"])
    assert all(edge["query"][0] != edge["candidate"][0] for edge in result["candidates"])
    assert len([edge for edge in result["candidates"] if edge["query"] == ["test/a/1", "1", "item:1"]]) == 2


def test_lexical_overlap_preserves_negation_and_unrelated_items():
    a = pack("a", "Report all outcomes.", "Apples")
    b = pack("b", "Do not report all outcomes.", "Bananas")
    result = composition.compose([a, b], top_k=1)
    assert len(result["requirements"]) == 4
    assert result["semantic_merges"] == 0
    assert len(result["candidates"]) == 2
    assert all(0 < edge["score"] < 1 for edge in result["candidates"])
    assert all(edge["query"][2] == "item:1" for edge in result["candidates"])


def test_unverified_uncleared_and_empty_requirements_remain_visible_but_unindexed():
    a = pack("a", "Report outcome.", "Do not export this item.", "... ")
    a["requirements"][1]["rights"] = rights("link_only")
    b = pack("b", "Do not index this pack.")
    b["rights"] = rights("review_required")
    b["requirements"][0]["rights"] = rights()
    c = pack("c", "Do not index this unverified pack.")
    c["verification"]["status"] = "imported_unverified"
    result = composition.compose([c, b, a])
    assert [row["status"] for row in result["requirements"]] == [
        "candidate_review", "held_rights", "held_no_terms", "held_rights", "held_source"
    ]
    assert result["candidates"] == []
    assert "Do not" not in json.dumps(result)


@pytest.mark.parametrize("top_k", [0, 21, True])
def test_top_k_bounds(top_k):
    with pytest.raises(ValueError, match="top_k"):
        composition.compose([pack("a", "Report outcome.")], top_k=top_k)


def test_ambiguous_identity_bounds_and_nonreporting_refused(monkeypatch):
    a = pack("a", "Report outcome.")
    different = deepcopy(a)
    different["version"] = "2"
    with pytest.raises(ValueError, match="conflicting pack identity"):
        composition.compose([a, different])
    different = deepcopy(a)
    different["requirements"].append(deepcopy(different["requirements"][0]))
    with pytest.raises(ValueError, match="duplicate requirement"):
        composition.compose([different])
    with pytest.raises(ValueError, match="select at least one"):
        composition.compose([])
    different = deepcopy(a)
    different["kind"] = "risk_of_bias"
    with pytest.raises(ValueError, match="reporting or protocol"):
        composition.compose([different])
    monkeypatch.setattr(composition, "MAX_REQUIREMENTS", 1)
    with pytest.raises(ValueError, match="requirement limit"):
        composition.compose([a, pack("b", "Report method.")])
    monkeypatch.setattr(composition, "MAX_TEXT_CHARS", 5)
    with pytest.raises(ValueError, match="text limit"):
        composition.compose([a])


def test_ties_are_ranked_stably_and_limited():
    a = pack("a", "Report outcomes.")
    b = pack("b", "Report outcomes.", "Report outcomes.")
    result = composition.compose([b, a], top_k=1)
    edges = [edge for edge in result["candidates"] if edge["query"][0] == "test/a/1"]
    assert len(edges) == 1 and edges[0]["candidate"][2] == "item:1"


def test_cli_exact_bytes_and_bounded_reads(tmp_path, monkeypatch, capsys):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(json.dumps(pack("a", "Report outcomes.")), encoding="utf-8")
    b.write_text(json.dumps(pack("b", "Report outcomes.")), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.compose_checklists", "--pack", str(a), "--pack", str(b)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["input_file_sha256s"] == sorted(hashlib.sha256(p.read_bytes()).hexdigest() for p in [a, b])
    assert report["semantic_merges"] == 0
    monkeypatch.setattr(composition, "MAX_PACK_BYTES", 5)
    monkeypatch.setattr(sys, "argv", ["compose", "--pack", str(a)])
    with pytest.raises(ValueError, match="pack byte limit"):
        composition.main()
    assert capsys.readouterr().out == ""


def test_invalid_pack_schema_and_duplicate_json_fields_fail(tmp_path, monkeypatch):
    from jsonschema.exceptions import ValidationError

    a = pack("a", "Report outcome.")
    a.pop("authority")
    with pytest.raises(ValidationError):
        composition.compose([a])
    path = tmp_path / "duplicate.json"
    path.write_text('{"version":"1","version":"2"}', encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["compose", "--pack", str(path)])
    with pytest.raises(ValueError, match="duplicate JSON field"):
        composition.main()
