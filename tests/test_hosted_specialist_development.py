"""Specialist service boundaries: no live calls or credentials in routine tests."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import hosted_specialist_development as hosted
from scripts import lfm_development as lfm

ROOT = Path(__file__).resolve().parents[1]


def test_rerank_uses_only_text_and_exact_candidate_indices():
    queries = {("i", "1"): "cost"}
    targets = {"a": "valuation", "b": "reporting"}
    references = {("i", "1"): {"a"}}
    rankings = {("i", "1"): ["b", "a"]}

    def post(payload):
        assert payload == {
            "model": "rerank-2.5", "query": "cost", "documents": ["reporting", "valuation"],
            "top_k": 2, "truncation": False,
        }
        return {"model": "rerank-2.5", "results": [
            {"index": 0, "relevance_score": .1}, {"index": 1, "relevance_score": .9}
        ], "usage": {"total_tokens": 15, "secret": "not retained"}}

    result = hosted.evaluate_rerank(queries, targets, references, rankings, "rerank-2.5", post)
    assert result["result"]["macro_query_recall"]["1"] == 1.0
    assert result["result"]["paired_vs_bge"]["1"]["gained_associations"] == 1
    assert result["provider_rows"][0]["usage"] == {"total_tokens": 15}
    assert result["scientific_qualification"] is False
    with pytest.raises(ValueError, match="identity"):
        hosted.evaluate_rerank(queries, targets, references, rankings, "rerank-2.5",
                               lambda _: {"model": "wrong"})


def test_jina_and_cohere_and_native_payloads():
    assert hosted.rerank_payload("jina-reranker-v3.5", "q", ["a"])["return_documents"] is False
    assert hosted.rerank_payload("rerank-v5.0-pro", "q", ["a"])["max_tokens_per_doc"] == 512
    assert hosted.rerank_payload(hosted.LOCAL_QWEN, "q", ["a"])["top_n"] == 1
    assert hosted.usage({"usage": None}) == {}


def test_decision_only_original_fixture_no_reference_leak():
    calls = []
    def post(payload):
        assert set(payload) == {"model", "state", "questions"}
        assert set(payload["state"]) == {"A", "B"}
        calls.append(payload)
        return {"model": "jev-1.13.0", "answers": {}}
    result = hosted.evaluate_decision(ROOT, "jev-1.13.0", post)
    assert len(calls) == 36
    assert result["summary"]["direct"]["abstained"] == 36
    assert all(row["invalid"] for row in result["records"])
    with pytest.raises(ValueError, match="identity"):
        hosted.evaluate_decision(ROOT, "jev-1.13.0", lambda _: {"model": "jev-latest"})


def test_decision_success_reuses_existing_probability_contract():
    def answer(options, chosen):
        return {"choice": chosen, "probabilities": {k: float(k == chosen) for k in options}}
    def post(payload):
        return {"model": "d1.2-ultra", "answers": {
            "relation": answer(lfm.RELATIONS, "equivalent"),
            "a_to_b": answer(lfm.YES_NO, "yes"),
            "b_to_a": answer(lfm.YES_NO, "yes"),
            "joint": answer(lfm.YES_NO, "yes"),
        }}
    result = hosted.evaluate_decision(ROOT, "d1.2-ultra", post)
    assert result["summary"]["direct"]["correct"] == 12
    assert result["summary"]["directional"]["false_equivalence"] == 24


def test_credential_gate_before_network(monkeypatch, tmp_path):
    args = ["hosted", "--model", "jev-1.13.0", "--output", str(tmp_path / "out.json"),
            "--max-requests", "36"]
    monkeypatch.setattr(sys, "argv", args)
    with pytest.raises(SystemExit, match="authorization"):
        hosted.main()
    monkeypatch.setattr(sys, "argv", args + ["--allow-hosted-public-development"])
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(SystemExit, match="not PR CI"):
        hosted.main()
    monkeypatch.delenv("GITHUB_ACTIONS")
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="credential"):
        hosted.main()


def test_http_client_bounded_and_nonredirecting():
    class Response:
        status_code = 200
        raw = SimpleNamespace(read=lambda *args, **kwargs: b'{"results":[]}')
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
    def request(endpoint, **kw):
        assert endpoint == "https://example.invalid"
        assert kw["allow_redirects"] is False
        assert kw["stream"] is True
        assert kw["headers"] == {"Authorization": "Bearer fixture"}
        return Response()
    session = SimpleNamespace(post=request)
    post = hosted.make_post(session, "https://example.invalid", "fixture", 1)
    assert post({}) == {"results": []}
    with pytest.raises(ValueError, match="budget"):
        post({})
    Response.status_code = 302
    with pytest.raises(ValueError, match="HTTP 302"):
        hosted.make_post(session, "https://example.invalid", "fixture", 1)({})
    Response.status_code = 200
    Response.raw = SimpleNamespace(read=lambda *a, **kw: b"x" * 1_000_001)
    with pytest.raises(ValueError, match="exceeds"):
        hosted.make_post(session, "https://example.invalid", "fixture", 1)({})


def test_frozen_baseline_rejects_unqualified_receipt(tmp_path):
    bad = tmp_path / "fake.json"
    bad.write_text(json.dumps({}))
    with pytest.raises(ValueError, match="baseline"):
        hosted.frozen_costing(ROOT, bad)
    with pytest.raises(ValueError, match="fixture"):
        fixture = tmp_path / hosted.FIXTURE_PATH
        fixture.parent.mkdir(parents=True)
        fixture.write_text("{}")
        hosted.evaluate_decision(tmp_path, "d1.2", lambda _: pytest.fail("network not permitted"))


def test_larger_qwen_is_local_only(monkeypatch, tmp_path):
    model = hosted.LOCAL_QWEN_4B
    assert model in hosted.LOCAL_QWEN_MODELS and model not in hosted.RERANK_MODELS
    assert hosted.rerank_payload(model, "query", ["candidate"]) == {
        "model": model, "query": "query", "documents": ["candidate"], "top_n": 1,
    }
    monkeypatch.setattr(sys, "argv", ["hosted", "--model", model, "--max-requests", "106",
                                     "--output", str(tmp_path / "out.json")])
    with pytest.raises(SystemExit, match="baseline"):
        hosted.main()
