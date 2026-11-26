"""Candidate conditional scope is distinct from reporting content."""
import hashlib
import json

import pytest

from scripts.conditional_scope_audit import audit_projection, audit_source


def clause(key, parent, condition):
    return {
        "id": key,
        "parent_item": parent,
        "condition_atom": condition,
        "source_anchor": f"item:{parent}",
        "line": 1,
        "review_status": "source_text_corroborated_not_independent_adjudication",
        "text_sha256": "a" * 64,
    }


def test_same_trigger_different_reporting_atoms_has_two_witnesses():
    rows = [clause("methods", "13d", "meta_analysis"), clause("results", "20b", "meta_analysis")]
    report = audit_projection(rows)
    assert report["condition_only_collisions"] == 1
    assert report["candidate_equivalences_distinct_ids"] == 0
    pair = report["pairs"][0]
    assert pair["relation"] == "indeterminate"
    assert pair["witnesses"]["a_only"] == {
        "condition:meta_analysis": True,
        "obligation:methods": True,
        "obligation:results": False,
    }
    assert pair["witnesses"]["b_only"]["obligation:results"] is True
    assert pair["witnesses"]["b_only"]["obligation:methods"] is False
    assert report["admission"] == "held_independent_scope_and_fact_review"


def test_distinct_subclauses_with_same_parent_remain_distinct():
    rows = [clause("summary", "20b", "meta_analysis"), clause("direction", "20b", "groups_compared")]
    pair = audit_projection(rows)["pairs"][0]
    assert pair["same_parent"] is True
    assert pair["same_trigger"] is False
    assert pair["relation"] == "indeterminate"


def test_projection_rejects_duplicate_and_invalid_candidate_state():
    row = clause("methods", "13d", "meta_analysis")
    with pytest.raises(ValueError, match="duplicate"):
        audit_projection([row, row])
    with pytest.raises(ValueError, match="candidate"):
        audit_projection([{**row, "review_status": "approved"}])
    with pytest.raises(ValueError, match="bounded"):
        audit_projection([])
    with pytest.raises(ValueError, match="invalid"):
        audit_projection([{**row, "condition_atom": ""}])


def test_source_binding_reuses_existing_adapter_and_preserves_parent_inventory():
    pack = {
        "pack_id": "example",
        "version": "1",
        "authority": {"source_sha256": "b" * 64},
        "requirements": [
            {"id": "13d", "source_anchor": "item:13d", "verbatim_text": "Report methods if used."},
            {"id": "20b", "source_anchor": "item:20b", "verbatim_text": "Report results if used."},
        ],
    }
    raw = (json.dumps(pack, indent=2) + "\n").encode()
    lines = raw.decode().splitlines()
    clauses = [clause("methods", "13d", "meta_analysis"), clause("results", "20b", "meta_analysis")]
    for record, item in zip(clauses, pack["requirements"], strict=True):
        record.pop("text_sha256")
        record["line"] = next(i for i, line in enumerate(lines, 1) if item["verbatim_text"] in line)
    seed = {
        "schema_version": "dev.standardflow.source-conditional-clauses.v1",
        "status": "source_corroborated_review_required",
        "source": {"sha256": hashlib.sha256(raw).hexdigest(), "pack_id": "example", "version": "1", "official_pdf_sha256": "b" * 64},
        "clauses": clauses,
    }
    result = audit_source(seed, raw)
    assert result["binding"] == "source_adapter_verified"
    assert result["parent_items_retained"] == ["13d", "20b"]
    assert result["condition_only_collisions"] == 1
    with pytest.raises(ValueError, match="source pack digest mismatch"):
        audit_source(seed, raw + b" ")
    seed["clauses"][0]["line"] = 1
    with pytest.raises((ValueError, json.JSONDecodeError)):
        audit_source(seed, raw)


def test_pinned_prisma_seed_against_actual_pack():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    seed = json.loads(
        (root / "contracts/applicability/prisma-2020-conditional.v0.1.0.json").read_text()
    )
    report = audit_source(seed, (root / seed["source"]["path"]).read_bytes())
    assert len(report["parent_items_retained"]) == 42
    assert len(report["pairs"]) == 21
    assert len(report["identity_controls"]) == 7
    assert all(row["relation"] == "equivalent" for row in report["identity_controls"])
    collisions = [row for row in report["pairs"] if row["same_trigger"]]
    assert len(collisions) == 1
    assert collisions[0]["relation"] == "indeterminate"
    assert report["admission"] == "held_independent_scope_and_fact_review"


def test_all_prisma_candidate_fact_states_preserve_parent_inventory():
    from itertools import product
    from pathlib import Path

    from scripts.source_applicability import evaluate_seed

    root = Path(__file__).resolve().parents[1]
    seed = json.loads(
        (root / "contracts/applicability/prisma-2020-conditional.v0.1.0.json").read_text()
    )
    pack = (root / seed["source"]["path"]).read_bytes()
    atoms = sorted({row["condition_atom"] for row in seed["clauses"]})
    statuses = ("unknown", "required", "not_applicable", "held_conflict")
    assert len(atoms) == 6
    scenarios = 0
    checks = 0
    for state in product(statuses, repeat=len(atoms)):
        facts = []
        expected = dict(zip(atoms, state, strict=True))
        for atom, status in expected.items():
            if status in ("required", "held_conflict"):
                facts.append(atom)
            if status in ("not_applicable", "held_conflict"):
                facts.append("!" + atom)
        raw = (
            "\n".join(
                json.dumps({"literal": literal, "evidence_id": f"synthetic:{i}"})
                for i, literal in enumerate(facts)
            )
            + "\n"
        ).encode()
        report = evaluate_seed(seed, pack, raw)
        assert len(report["parent_items_retained"]) == 42
        assert report["admission"] == "held_independent_scope_and_fact_review"
        for row in seed["clauses"]:
            assert report["subclauses"][row["id"]]["status"] == expected[row["condition_atom"]]
            checks += 1
        scenarios += 1
    assert (scenarios, checks) == (4096, 28672)
