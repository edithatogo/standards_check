"""Actual source-pack conditional clauses; scenario facts are synthetic."""

import copy
import json
from pathlib import Path

import pytest

from scripts.source_applicability import evaluate_seed

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "contracts/applicability/prisma-2020-conditional.v0.1.0.json"


def load():
    seed = json.loads(SEED.read_text())
    return seed, (ROOT / seed["source"]["path"]).read_bytes()


def facts(*literals):
    return (
        "\n".join(json.dumps({"literal": literal, "evidence_id": f"synthetic:{i}"})
                  for i, literal in enumerate(literals)) + "\n"
    ).encode()


def test_explicit_clauses_preserve_all_parent_requirements():
    seed, raw = load()
    result = evaluate_seed(
        seed, raw, facts("meta_analysis_performed", "!screening_automation_used")
    )
    rows = result["subclauses"]
    assert len(result["parent_items_retained"]) == 42
    assert len(rows) == 7
    assert rows["prisma-2020:13d:meta-analysis-methods"]["status"] == "required"
    assert rows["prisma-2020:20b:meta-analysis-results"]["status"] == "required"
    assert rows["prisma-2020:8:screening-automation"]["status"] == "not_applicable"
    assert rows["prisma-2020:9:collection-automation"]["status"] == "unknown"
    assert result["admission"].startswith("held_")


def test_all_clauses_true_false_unknown_and_conflicted():
    seed, raw = load()
    for clause in seed["clauses"]:
        key, atom = clause["id"], clause["condition_atom"]
        for evidence, expected in (
            (facts(atom), "required"),
            (facts("!" + atom), "not_applicable"),
            (b"\n", "unknown"),
            (facts(atom, "!" + atom), "held_conflict"),
        ):
            assert evaluate_seed(seed, raw, evidence)["subclauses"][key]["status"] == expected


def test_tampered_source_locator_and_unknown_fact_are_rejected():
    seed, raw = load()
    with pytest.raises(ValueError):
        evaluate_seed(seed, raw + b" ", b"\n")
    bad = copy.deepcopy(seed)
    bad["clauses"][0]["line"] = 1
    with pytest.raises(ValueError):
        evaluate_seed(bad, raw, b"\n")
    with pytest.raises(ValueError):
        evaluate_seed(seed, raw, facts("invented"))
