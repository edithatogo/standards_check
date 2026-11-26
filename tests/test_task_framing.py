"""Orthogonal task development boundaries; no external inference in unit tests."""

import itertools
from pathlib import Path

import pytest

from scripts import lfm_development as lfm
from scripts import task_framing as framing

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("a,b,both,expected", [
    ("no", "no", "yes", "equivalent"),
    ("yes", "no", "yes", "narrower"),
    ("no", "yes", "yes", "broader"),
    ("yes", "yes", "no", "contradictory"),
    ("yes", "yes", "yes", "indeterminate"),
])
def test_witness_truth_table(a, b, both, expected):
    assert framing.compile_witness(a, b, both) == expected
    assert framing.compile_witness(b, a, both) == framing.swap_relation(expected)


def test_unknown_or_empty_scope_holds():
    valid = {("no","no","yes"),("yes","no","yes"),("no","yes","yes"),
             ("yes","yes","yes"),("yes","yes","no")}
    for parts in itertools.product(("yes","no","unknown","abstain"), repeat=3):
        if parts not in valid:
            assert framing.compile_witness(*parts) == "abstain"
    with pytest.raises(ValueError):
        framing.swap_relation("invented")


def test_reciprocal_rank_fusion():
    assert framing.reciprocal_rank_fusion(["a","b","c"], ["b","c"]) == ["b","c","a"]
    assert framing.reciprocal_rank_fusion(["b","a"], ["a","b"]) == ["a","b"]
    with pytest.raises(ValueError):
        framing.reciprocal_rank_fusion(["a","a"], ["b"])


def test_frame_query():
    assert framing.frame_query("topic", "raw") == "topic"
    assert framing.frame_query("topic", "domain-index") == (
        "Identify the economic domain whose definition substantively covers this reporting topic. Topic: topic"
    )
    with pytest.raises(ValueError):
        framing.frame_query("topic", "unknown")


def test_views_conserve_text_and_reverse_only_options():
    pair = {"id": "opaque", "source": "A text", "candidate": "B text"}
    views = framing.decision_views(pair)
    assert views["original"] == lfm.decision_payload(pair)
    assert views["swapped"]["state"] == {"A": "B text", "B": "A text"}
    assert views["witness"]["state"] == views["original"]["state"]
    for key, question in views["original"]["questions"].items():
        reversed_question = views["option-reversed"]["questions"][key]
        assert question == reversed_question
        assert list(question["criteria"]) == list(reversed(reversed_question["criteria"]))
    assert framing.payload_hash(views["original"]) != framing.payload_hash(views["option-reversed"])
    with pytest.raises(ValueError, match="unblinded"):
        framing.decision_views({**pair, "reference": "equivalent"})


def response(payload, labels):
    return {"answers": {
        key: {"choice": label, "probabilities": {k: float(k == label) for k in payload["questions"][key]["criteria"]}}
        for key, label in labels.items()
    }}


def test_witness_decoder_and_swap():
    views = framing.decision_views({"id": "id", "source": "A", "candidate": "B"})
    witness = views["witness"]
    reply = response(witness, {"a_only": "yes", "b_only": "no", "both": "yes"})
    assert framing.decode_view("witness", witness, reply)[:2] == ("narrower", None)
    reply = response(views["swapped"], {"relation": "broader", "a_to_b": "yes", "b_to_a": "no", "joint": "yes"})
    assert framing.decode_view("swapped", views["swapped"], reply)[:2] == ("narrower", "narrower")
    with pytest.raises(ValueError, match="coverage"):
        framing.decode_view("witness", witness, {"answers": {}})
    with pytest.raises(ValueError, match="unknown decision"):
        framing.decode_view("unknown", views["swapped"], reply)
    assert framing.strict_agreement(["equivalent", "equivalent"]) == "equivalent"
    assert framing.strict_agreement(["equivalent", "abstain"]) == "abstain"
    assert framing.strict_agreement(["narrower", "broader"]) == "abstain"


def test_full_blinded_decision_receipt():
    import json
    fixture = json.loads((ROOT / "contracts/examples/semantic-reconciliation-synthetic-v1.json").read_text())
    calls = []
    def post(payload):
        assert set(payload) == {"state", "questions"}
        assert set(payload["state"]) == {"A", "B"}
        calls.append(payload)
        if "a_only" in payload["questions"]:
            return response(payload, {"a_only": "no", "b_only": "no", "both": "yes"})
        return response(payload, {"relation": "equivalent", "a_to_b": "yes", "b_to_a": "yes", "joint": "yes"})
    result = framing.run_decision_frames(fixture, post)
    assert len(calls) == result["requests"] == 144
    assert result["summary"]["agreement"]["false_equivalence"] == 24
    assert result["scientific_qualification"] is False
    failed = framing.run_decision_frames(fixture, lambda _: {"answers": {}})
    assert failed["summary"]["agreement"]["abstained"] == 36
    assert all(row["views"]["witness"]["invalid"] for row in failed["records"])


def test_embedding_validation_and_two_views():
    def vector(n):
        return [float(i == n) for i in range(1024)]
    def reply(text):
        return {"model": framing.EMBED_MODEL, "data": [{"index": 0, "embedding": vector(1 if "relevant" in text else 0)}]}
    with pytest.raises(ValueError, match="model"):
        framing.embedding_vector({"model": "wrong"})
    with pytest.raises(ValueError, match="coverage"):
        framing.embedding_vector({"model": framing.EMBED_MODEL, "data": []})
    for bad in ([1], [0]*1024, [float("nan")]*1024, [True]*1024):
        with pytest.raises(ValueError):
            framing.embedding_vector({"model": framing.EMBED_MODEL, "data": [{"index": 0, "embedding": bad}]})
    calls = []
    def post(payload):
        calls.append(payload["input"])
        return reply(payload["input"])
    queries, targets = {("i","1"): "relevant"}, {"a": "relevant", "b": "other"}
    references, bge = {("i","1"): {"a"}}, {("i","1"): ["b", "a"]}
    result = framing.embedding_views(queries, targets, references, bge, post)
    assert result["requests"] == len(calls) == 4
    assert calls[-1].startswith("Instruct: ")
    assert result["results"]["raw"]["macro_query_recall"]["1"] == 1
    assert result["results"]["raw"]["paired_vs_bge"]["1"]["gained_associations"] == 1
    with pytest.raises(ValueError, match="coverage"):
        framing.embedding_views(queries, targets, {}, bge, post)


def test_fusion_rejects_unqualified_receipt(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="baseline"):
        framing.retrieval_fusion(ROOT, path)


def test_reranker_domain_frame_preserves_candidate_pool():
    from scripts.hosted_specialist_development import evaluate_rerank, LOCAL_QWEN
    def post(payload):
        assert payload["query"] == framing.frame_query("cost", "domain-index")
        assert payload["documents"] == ["b", "a"]
        return {"model": LOCAL_QWEN, "results": [{"index": 1, "relevance_score": .9}, {"index": 0, "relevance_score": .1}]}
    result = evaluate_rerank({("i","1"): "cost"}, {"a":"a","b":"b"}, {("i","1"): {"a"}},
                             {("i","1"): ["b","a"]}, LOCAL_QWEN, post, query_frame="domain-index")
    assert result["query_frame"] == "domain-index"
    assert result["result"]["macro_query_recall"]["1"] == 1
    assert len(result["provider_rows"][0]["payload_sha256"]) == 64
