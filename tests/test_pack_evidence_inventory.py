import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts.pack_evidence_inventory import inventory, closure, certificate, baseline


def fixture():
    return {"pack_id": "demo", "version": "1", "rights": {"status": "cleared"}, "verification": {"status": "source_reconciled"}, "requirements": [
        {"id": "d:1", "display_number": "1", "section": "Methods", "source_anchor": "source:1", "verbatim_text": "Report the analysis methods and software used.", "normalized_requirement": "Report analysis methods and software.", "rights": {"inherit_from_pack": True}, "evidence_expectations": ["document_span"]},
        {"id": "d:2", "display_number": "2", "section": "Results", "source_anchor": "source:2", "verbatim_text": "Report the summary estimates and refer to item #1.", "normalized_requirement": "Report summary estimates.", "rights": {"inherit_from_pack": True}, "evidence_expectations": ["document_span"]},
    ]}


def raw(pack):
    return (json.dumps(pack, indent=2) + "\n").encode()


def test_source_bound_inventory_closure_and_missing_evidence():
    data = raw(fixture())
    inv = inventory(data, hashlib.sha256(data).hexdigest())
    assert len(inv["units"]) == 2
    assert inv["edges"][0]["from"] == "d:2"
    assert closure(inv, ["d:2"], 1) == ["d:2"]
    assert closure(inv, ["d:2"], 2) == ["d:2", "d:1"]
    result = certificate(inv, ["d:2"], ["d:2", "d:1"])
    assert result["missing"] == ["d:1"]
    assert result["structural_coverage_complete"] is False
    assert certificate(inv, ["d:2", "d:1"], ["d:2", "d:1"])["structural_coverage_complete"] is True
    assert result["semantic_completeness"] == "not_established"


def test_reject_unqualified_pack_and_invented_edges():
    p = fixture()
    data = raw(p)
    with pytest.raises(ValueError, match="digest"):
        inventory(data, "bad")
    for key, value in [("rights", {"status": "unknown"}), ("verification", {"status": "candidate"})]:
        bad = raw({**p, key: value})
        with pytest.raises(ValueError, match="eligible"):
            inventory(bad, hashlib.sha256(bad).hexdigest())
    p["requirements"][1]["verbatim_text"] = "See item #9."
    data = raw(p)
    inv = inventory(data, hashlib.sha256(data).hexdigest())
    assert inv["unresolved_references"][0]["target_number"] == "9"
    assert not certificate(inv, ["d:2"], ["d:2"])["structural_coverage_complete"]
    with pytest.raises(ValueError, match="identity"):
        closure(inv, ["invented"], 2)
    with pytest.raises(ValueError, match="identity"):
        certificate(inv, ["invented"], ["d:2"])


def test_baseline_preserves_query_denominator_and_declared_identity():
    data = raw(fixture())
    result = baseline(data, hashlib.sha256(data).hexdigest())
    assert result["queries"] == 2
    assert result["candidate_pairs"] == 4
    for entry in result["methods"].values():
        assert len(entry["rows"]) == 2
        assert {r["expected"] for r in entry["rows"]} == {"d:1", "d:2"}
    assert result["claim_boundary"] == "masked_source_identity_recovery_not_semantic_relevance"
