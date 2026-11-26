from pathlib import Path

from scripts.costing_scope_audit import audit


def test_actual_costing_candidates_preserve_every_item_and_domain():
    result = audit(Path(__file__).resolve().parents[1])
    assert result["instrument_records"] == 26
    assert result["mapped_items"] == 106
    assert result["target_domains"] == 31
    assert result["candidate_pairs"] == 3286
    assert sum(row["editorial_association"] for row in result["rows"]) == 125
    assert len(result["scope_disagreements"]) == 11
    assert len({(r["instrument"], r["item"], r["domain"]) for r in result["rows"]}) == 3286
    assert all(row["relation"] == "covers_topic_candidate" for row in result["rows"])
    assert result["semantic_merges"] == result["equivalence_candidates"] == 0
    assert result["solver_status"].startswith("held_")
