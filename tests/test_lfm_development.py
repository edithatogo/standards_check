"""Development experiment regressions: no inference or source downloads in routine CI."""
import json
from pathlib import Path

import pytest

from scripts import five_class_benchmark as five
from scripts import lfm_development as lfm

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("left,right,joint,expected", [
    ("yes", "yes", "yes", "equivalent"),
    ("yes", "no", "yes", "broader"),
    ("no", "yes", "yes", "narrower"),
    ("no", "no", "no", "contradictory"),
    ("no", "no", "yes", "indeterminate"),
    ("yes", "no", "no", "abstain"),
    ("unknown", "yes", "yes", "abstain"),
])
def test_compile(left, right, joint, expected):
    assert lfm.compile_direction(left, right, joint) == expected


def test_choice():
    assert lfm.choose({"choice": "yes", "probabilities": {"yes": .9, "no": .1}}, {"yes", "no"}, .8) == "yes"
    assert lfm.choose({"choice": "yes", "probabilities": {"yes": .5, "no": .5}}, {"yes", "no"}, .8) == "abstain"
    for bad in (
        {"choice": "yes", "probabilities": {"yes": .1, "no": .9}},
        {"choice": "yes", "probabilities": {"yes": float("nan"), "no": .9}},
        {"choice": "yes", "probabilities": {"yes": True, "no": 0}},
        {"choice": "yes", "probabilities": {"yes": .9, "no": .9}},
        {"choice": "yes", "probabilities": {"yes": .9, "other": .1}},
    ):
        with pytest.raises(ValueError):
            lfm.choose(bad, {"yes", "no"}, .8)


def answer(options, label, confidence=1.0):
    return {"choice": label, "probabilities": {
        key: confidence if key == label else (1 - confidence) / (len(options) - 1)
        for key in options
    }}


def decision_response():
    return {"answers": {
        "relation": answer(lfm.RELATIONS, "equivalent", .94),
        "a_to_b": answer(lfm.YES_NO, "yes"),
        "b_to_a": answer(lfm.YES_NO, "no"),
        "joint": answer(lfm.YES_NO, "yes"),
    }}


def test_decision_contract():
    direct, directional, probabilities = lfm.decision_vote(decision_response())
    assert direct == "abstain" and directional == "broader"
    assert probabilities["relation"]["equivalent"] == .94
    payload = lfm.decision_payload({"id": "opaque", "source": "A", "candidate": "B"})
    assert payload["state"] == {"A": "A", "B": "B"}
    assert "opaque" not in json.dumps(payload)


def fixture():
    return json.loads((ROOT / "contracts/examples/semantic-reconciliation-synthetic-v1.json").read_text())


def test_synthetic_only_and_direction():
    data = fixture()
    ledger = lfm.prepare_fixture(data)
    assert len(ledger["cases"]) == 36
    assert set(row["reference"] for row in ledger["cases"]) == set(five.LABELS)
    assert ledger["cases"][1]["reference"] == "broader"
    assert len(ledger["cases"][0]["id"]) == 64
    with pytest.raises(ValueError):
        lfm.prepare_fixture({**data, "label_origin": "natural"})
    data["cases"][0]["forward"] = "contradiction"
    with pytest.raises(ValueError, match="unsupported"):
        lfm.prepare_fixture(data)


def test_paired_does_not_discard_abstention():
    expected = {"a": "equivalent", "b": "broader"}
    a = {"a": "abstain", "b": "broader"}
    b = {"a": "equivalent", "b": "equivalent"}
    assert lfm.metrics(expected, a)["abstained"] == 1
    assert lfm.metrics(expected, b)["false_equivalence"] == 1
    assert lfm.paired(expected, a, b) == {
        "both_correct": 0, "incumbent_only": 1, "challenger_only": 1,
        "both_wrong": 0, "disagreements": 2, "shared_same_wrong": 0,
    }
    with pytest.raises(ValueError):
        lfm.metrics(expected, {"a": "equivalent"})


@pytest.mark.parametrize("model", ["d1", "lfm25-instruct", "lfm3", "lfm25-thinking", "lfm2-2.6b", "minicpm5", "k2-horizon"])
def test_existing_harness_and_receipts(model, monkeypatch, tmp_path):
    def score(ledger, records, assets, sha):
        return {
            "records": [{**row, "predicted": row["reference"]} for row in records],
            "asset_hashes": {"weights": sha}, "wall_seconds": 0.0,
        }
    monkeypatch.setattr(five, "score", score)
    calls = []
    def post(endpoint, payload):
        calls.append(endpoint)
        if endpoint == "systemone":
            return decision_response() if len(calls) > 1 else {}
        assert endpoint == "chat/completions"
        data = json.loads(payload["messages"][1]["content"])
        assert set(data) == {"A", "B"}
        assert all(set(line) == {"number", "text"} for lines in data.values() for line in lines)
        assert payload["seed"] == 724
        return {"choices": [{"message": {"content": json.dumps({
            "label": "equivalent", "a": [1], "b": [1],
        })}}]}
    report = lfm.run(fixture(), model, post, tmp_path, tmp_path)
    assert report["scientific_qualification"] is False
    assert report["canonical_packs_promoted"] == 0
    assert report["summary"]["minilm"]["correct"] == 36
    assert report["summary"]["direct"]["n"] == 36
    assert len(calls) == 36
    assert "The review report" not in json.dumps(report)
    if model == "d1":
        assert len(report["invalid_decisions"]) == 1
        assert report["summary"]["directional"]["abstained"] == 1
    else:
        assert report["summary"]["direct"]["false_equivalence"] == 24


@pytest.mark.parametrize("damage,reason", [("coverage", "coverage"), ("digest", "digest")])
def test_corrupt_vote_receipt_fails_closed(damage, reason, monkeypatch, tmp_path):
    monkeypatch.setattr(five, "score", lambda ledger, records, assets, sha: {
        "records": [{**row, "predicted": "abstain"} for row in records],
        "asset_hashes": {}, "wall_seconds": 0,
    })
    def votes(pairs, complete):
        if damage == "coverage":
            return []
        return [{"id": pair["id"], "source_sha256": "wrong", "candidate_sha256": "wrong"} for pair in pairs]
    monkeypatch.setattr(five, "adjudicate_pairs", votes)
    with pytest.raises(ValueError, match=reason):
        lfm.run(fixture(), "lfm3", None, tmp_path, tmp_path)


def test_shared_judge_rejects_unblinded_input():
    with pytest.raises(ValueError, match="unblinded"):
        five.adjudicate_pairs([{"id": "x", "source": "A", "candidate": "B", "reference": "equivalent"}], None)


@pytest.mark.parametrize("model,cap,thinking", [
    ("lfm3", 256, False),
    ("lfm25-instruct", 256, None),
    ("lfm25-thinking", 512, True),
    ("lfm2-2.6b", 256, None),
    ("minicpm5", 512, None),
    ("k2-horizon", 1024, None),
])
def test_declared_output_budget(model, cap, thinking):
    options = lfm.generation_options(model)
    assert options["max_tokens"] == cap and options["seed"] == 724
    assert options.get("chat_template_kwargs", {}).get("enable_thinking") is thinking


def test_truncated_response_is_held_even_if_content_looks_valid():
    from collections import Counter
    receipt = Counter()
    valid = {"choices": [{"finish_reason": "length", "message": {"content": '{"label":"equivalent"}'}}]}
    held = lfm.observed_completion(lambda *_: valid, {"max_tokens": 512}, receipt)
    assert held["choices"][0]["message"]["content"] == ""
    assert receipt == {"length": 1}
    valid["choices"][0]["finish_reason"] = "stop"
    assert lfm.observed_completion(lambda *_: valid, {}, receipt) == valid
    assert receipt == {"length": 1, "stop": 1}
    for model in ("d1", "unregistered"):
        with pytest.raises(ValueError):
            lfm.generation_options(model)


def test_k2_bounded_reasoning_is_declared():
    assert lfm.generation_options("k2-horizon")["chat_template_kwargs"] == {"reasoning_effort": "low"}
