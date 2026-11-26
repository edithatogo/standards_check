import json
from itertools import product
from pathlib import Path

import pytest

from scripts.evidence_factorial import acquisition_cells, contrasts, neural_cells, summarize


def test_factorial_contrasts_recover_known_interactions():
    cells = {}
    for a, b, c in product((0, 1), repeat=3):
        cells[f"{a}{b}{c}"] = {"case": [{"correct": a + 2 * b + 3 * a * b + 4 * a * b * c}]}
    effects = contrasts(cells, ["A", "B", "C"], "correct")
    assert effects["A:B:C"] == 4
    assert effects["A:B"] == 5
    assert effects["A"] == 3.5


def test_full_acquisition_design_has_balanced_orders_and_original_pairs():
    path = Path("contracts/examples/semantic-reconciliation-synthetic-v1.json")
    cases = json.loads(path.read_text())["cases"]
    cells = acquisition_cells(cases)
    assert set(cells) == {"".join(map(str, v)) for v in product((0, 1), repeat=3)}
    for key, rows in cells.items():
        assert len(rows) == 24
        assert {len(r) for r in rows.values()} == {1 if key.count("1") < 2 else 2 if key.count("1") == 2 else 6}
        for outcomes in rows.values():
            assert all(row["calls"] == key.count("1") for row in outcomes)
            assert all(row["reranks"] == int(key[2]) for row in outcomes)
    assert summarize(cells["110"])["complete"] == 23
    assert summarize(cells["101"])["complete"] == 19.5
    assert summarize(cells["111"])["calls"] == 72


def test_neural_factorial_retains_actual_predictions_and_unknown_proof():
    def state(complete):
        return {"complete": complete, "evidence_ids": ["x:parent"] if complete else ["x:head"], "predictions": {
            "lexical": "equivalent" if complete else "abstain",
            "strict_nli": "equivalent" if complete else "abstain",
            "lexical_verified": "abstain", "proof_required": "abstain"}}
    report = {"cases": [{"id": "x", "family": "F", "reference": "equivalent", "states": {"head": state(False), "rule_terminal": state(True)}}]}
    cells = neural_cells(report)
    assert summarize(cells["110"])["correct"] == 1
    assert summarize(cells["111"])["correct"] == 0
    assert contrasts(cells, ["A", "N", "P"], "correct")["A:P"] == -1
    with pytest.raises(ValueError, match="unique"):
        neural_cells({"cases": report["cases"] * 2})


def test_incomplete_or_unpaired_factorial_fails_closed():
    from scripts.evidence_factorial import order_summaries

    with pytest.raises(ValueError, match="incomplete"):
        contrasts({}, ["A"], "correct")
    with pytest.raises(ValueError, match="unpaired"):
        contrasts({"0": {"x": [{"correct": 0}]}, "1": {"y": [{"correct": 1}]}}, ["A"], "correct")
    with pytest.raises(ValueError, match="unpaired order"):
        order_summaries({"x": [{"order": ["a"]}], "y": [{"order": ["b"]}]})


def test_cli_pins_input_and_exports_complete_cells(tmp_path, monkeypatch):
    from scripts import evidence_factorial as module

    path = Path("contracts/examples/semantic-reconciliation-synthetic-v1.json")
    output = tmp_path / "out.json"
    monkeypatch.setattr("sys.argv", ["factorial", "--fixture", str(path), "--output", str(output)])
    module.main()
    report = json.loads(output.read_text())
    assert report["acquisition"]["n"] == 24
    assert len(report["acquisition"]["orders"]["111"]) == 6
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    with pytest.raises(ValueError, match="unqualified input"):
        module.read_pinned(bad, module.FIXTURE_SHA)


def test_cli_semantic_receipt_identity_check(tmp_path, monkeypatch):
    from scripts import evidence_factorial as module

    fixture = Path("contracts/examples/semantic-reconciliation-synthetic-v1.json")
    cases = json.loads(fixture.read_text())["cases"]
    initial = acquisition_cells(cases)["000"]
    rows = []
    for key, outcomes in initial.items():
        row = outcomes[0]
        state = {"complete": False, "evidence_ids": [key + ":head"], "predictions": {
            label: "abstain" for label in ("lexical", "strict_nli", "lexical_verified", "proof_required")}}
        rows.append({"id": key, "family": row["family"], "reference": row["reference"],
                     "states": {"head": state, "rule_terminal": state}})
    report = {"fixture_sha256": module.FIXTURE_SHA, "cases": rows}
    original = module.read_pinned
    monkeypatch.setattr(module, "read_pinned", lambda path, expected: report if expected == module.NEURAL_SHA else original(path, expected))
    output = tmp_path / "out.json"
    monkeypatch.setattr("sys.argv", ["factorial", "--fixture", str(fixture), "--neural-report", "mock.json", "--output", str(output)])
    module.main()
    assert json.loads(output.read_text())["semantic"]["n"] == 24
    report["fixture_sha256"] = "wrong"
    with pytest.raises(ValueError, match="fixture mismatch"):
        module.main()
    report["fixture_sha256"] = module.FIXTURE_SHA
    rows[0]["family"] = "other"
    with pytest.raises(ValueError, match="reference identity mismatch"):
        module.main()
