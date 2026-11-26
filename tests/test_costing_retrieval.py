"""Offline retrieval and exact denominator regression tests."""

from math import isclose
from pathlib import Path
from types import SimpleNamespace
import sys

import numpy as np
import pytest

from scripts import costing_retrieval as cost
from scripts.costing_retrieval import evaluate, rank
from scripts.lexical_text import cosine, term_counts, tfidf_vectors


def test_rank_ties_and_nonfinite():
    assert rank({"b": 1.0, "a": 1.0, "c": 0.0}, positive=True) == ["a", "b"]
    assert rank({"b": -0.1, "a": 0.0}) == ["a", "b"]
    with pytest.raises(ValueError):
        rank({"a": float("nan")})


def test_retrieval_metrics_keep_unreturned_reference():
    references = {("i", "1"): {"a", "c"}, ("i", "2"): {"b"}}
    result = evaluate(references, {"a", "b", "c"}, {("i", "1"): ["b", "a"], ("i", "2"): []})
    assert result["queries"] == 2
    assert result["positive_associations"] == 3
    assert result["no_candidates"] == 1
    assert isclose(result["macro_query_recall"]["5"], .25)
    assert isclose(result["micro_recall"]["5"], 1 / 3)
    assert isclose(result["mrr"], .25)
    assert result["by_instrument"]["i"]["queries"] == 2


@pytest.mark.parametrize("bad", [{("i", "1"): ["a", "a"]}, {("i", "1"): ["z"]}, {}])
def test_bad_ranking_rejected(bad):
    with pytest.raises(ValueError):
        evaluate({("i", "1"): {"a"}}, {"a"}, bad)


def test_invalid_reference_rejected():
    with pytest.raises(ValueError, match="reference"):
        evaluate({("i", "1"): {"z"}}, {"a"}, {("i", "1"): []})


def test_shared_lexical_scores():
    assert term_counts("  Study identification. ", "word") == {
        "study": 1, "identification": 1, "study identification": 1
    }
    assert term_counts("!@#", "char") == {}
    with pytest.raises(ValueError):
        term_counts("sample", "unknown")
    vectors = tfidf_vectors({
        "a": term_counts("sample cost", "word"), "b": term_counts("sample cost", "word"),
        "c": term_counts("date", "word"), "empty": {},
    })
    assert "empty" not in vectors
    assert cosine(vectors["a"], vectors["b"]) == 1.0
    assert cosine(vectors["a"], vectors["c"]) == 0.0


def test_neural_candidate_budget_and_no_label_leakage():
    queries = {("instrument", "1"): "cost topic"}
    targets = {f"d{i:02}": f"domain {i:02}" for i in range(12)}
    references = {("instrument", "1"): {"d11"}}
    calls = []
    def embed(text):
        assert text in [*targets.values(), cost.QUERY_PREFIX + "cost topic"]
        return np.array([1.0, 0.0])
    def rerank(query, passage):
        assert query == "cost topic"
        calls.append(passage)
        return 1.0
    report = cost.compare(queries, targets, references, embed, rerank)
    assert len(calls) == 10
    assert report["bge"]["rows"][0]["ranking"][-1] == "d11"
    assert report["bge_then_reranker10"]["micro_recall"]["10"] == 0
    assert "domain 11" not in calls
    with pytest.raises(ValueError, match="requires"):
        cost.compare(queries, targets, references, rerank=rerank)
    with pytest.raises(ValueError, match="coverage"):
        cost.compare(queries, targets, {})


def test_real_catalogue_baseline_and_cli(tmp_path, monkeypatch, capsys):
    root = Path(__file__).resolve().parents[1]
    result = cost.run(root)
    assert result["queries"] == 106 and result["target_domains"] == 31
    assert result["candidate_pool_pairs"] == 3286 and result["mapped_instruments"] == 5
    assert result["instrument_records"] == 26
    assert result["reference_status"] == "research_seed_review_required"
    assert result["scientific_qualification"] is False and result["semantic_merges"] == 0
    assert result["results"]["word"]["positive_associations"] == 125
    assert len(result["results"]["char"]["rows"]) == 106
    output = tmp_path / "receipts" / "costing.json"
    monkeypatch.setattr(sys, "argv", ["costing_retrieval", "--root", str(root), "--output", str(output)])
    cost.main()
    assert output.is_file()
    assert "micro_recall" in capsys.readouterr().out
    with pytest.raises(ValueError, match="invalid costing"):
        from scripts import validate_costing_reconciliation as validation
        monkeypatch.setattr(validation, "validate", lambda *args: ["bad"])
        cost.run(root)


def test_runtime_shape_and_asset_boundary(tmp_path, monkeypatch):
    for name in ("model.onnx", "tokenizer.json", "config.json"):
        (tmp_path / name).write_bytes(b"fixture")
    pin = cost.file_hash(tmp_path / "model.onnx")
    state = SimpleNamespace(
        inputs=["input_ids", "attention_mask", "token_type_ids"],
        outputs=["last_hidden_state", "logits"], ids=[1, 2], value=np.ones((1, 2, 384))
    )
    class Tokenizer:
        @classmethod
        def from_file(cls, _):
            return cls()
        def no_padding(self):
            pass
        def no_truncation(self):
            pass
        def encode(self, first, second):
            return SimpleNamespace(ids=state.ids, attention_mask=[1] * len(state.ids),
                                   type_ids=[0] * len(state.ids))
    class Session:
        def __init__(self, model, sess_options, providers):
            assert providers == ["CPUExecutionProvider"]
        def get_inputs(self):
            return [SimpleNamespace(name=n) for n in state.inputs]
        def get_outputs(self):
            return [SimpleNamespace(name=n) for n in state.outputs]
        def run(self, output, feed):
            return [state.value]
    monkeypatch.setitem(sys.modules, "tokenizers", SimpleNamespace(Tokenizer=Tokenizer))
    monkeypatch.setitem(sys.modules, "onnxruntime", SimpleNamespace(
        SessionOptions=SimpleNamespace, InferenceSession=Session, __version__="test"))
    with pytest.raises(ValueError, match="model bytes"):
        cost.LocalRanker(tmp_path, "bge")
    for model in cost.MODELS.values():
        monkeypatch.setitem(model, "sha256", pin)
    state.inputs = ["input_ids"]
    with pytest.raises(ValueError, match="inputs"):
        cost.LocalRanker(tmp_path, "bge")
    state.inputs = ["input_ids", "attention_mask"]
    state.outputs = []
    with pytest.raises(ValueError, match="output name"):
        cost.LocalRanker(tmp_path, "bge")
    state.outputs = ["last_hidden_state", "logits"]
    embed = cost.LocalRanker(tmp_path, "bge")
    assert np.isclose(np.linalg.norm(embed("sample")), 1)
    assert embed.asset_hashes["model.onnx"] == pin
    state.ids = list(range(513))
    with pytest.raises(ValueError, match="context"):
        embed("long")
    state.ids = [1, 2]
    state.value = np.full((1, 2, 384), np.nan)
    with pytest.raises(ValueError, match="nonfinite"):
        embed("sample")
    state.value = np.ones((1, 1, 384))
    with pytest.raises(ValueError, match="hidden state"):
        embed("sample")
    state.value = np.zeros((1, 2, 384))
    with pytest.raises(ValueError, match="norm"):
        embed("sample")
    rerank = cost.LocalRanker(tmp_path, "reranker")
    with pytest.raises(ValueError, match="score shape"):
        rerank("query", "target")
    state.value = np.array([[0.5]])
    assert rerank("query", "target") == .5


def test_pool_order_binding():
    ranks = {("i", "1"): ["a", "b"], ("i", "2"): ["b", "a"]}
    assert cost.pool_sha256(ranks, 2) == cost.pool_sha256(dict(reversed(list(ranks.items()))), 2)
    assert cost.pool_sha256(ranks, 2) != cost.pool_sha256({**ranks, ("i", "1"): ["b", "a"]}, 2)


def test_provider_indices_bound_to_candidates():
    candidates = ["b", "a"]
    rows = [{"index": 0, "relevance_score": .2}, {"index": 1, "relevance_score": .9}]
    assert cost.parse_reranker_results(candidates, rows) == {"b": .2, "a": .9}


@pytest.mark.parametrize("rows", [
    [{"index": 0, "relevance_score": .9}],
    [{"index": 0, "relevance_score": .9}, {"index": 0, "relevance_score": .1}],
    [{"index": True, "relevance_score": .1}, {"index": 0, "relevance_score": .2}],
    [{"index": 0, "relevance_score": float("nan")}, {"index": 1, "relevance_score": .2}],
    [{"index": 0, "relevance_score": .1}, {"index": 3, "relevance_score": .2}],
    [{"index": 0, "relevance_score": True}, {"index": 1, "relevance_score": .2}],
    [None, {"index": 1, "relevance_score": .2}],
    None,
])
def test_invalid_provider_rows_fail_closed(rows):
    with pytest.raises(ValueError):
        cost.parse_reranker_results(["a", "b"], rows)


def test_duplicate_provider_candidates_held():
    with pytest.raises(ValueError):
        cost.parse_reranker_results(["a", "a"], [])


def test_paired_gain_and_harm_at_equal_budget():
    refs = {("i", "1"): {"a"}, ("i", "2"): {"c"}}
    before = {("i", "1"): ["b", "a"], ("i", "2"): ["c", "d"]}
    after = {("i", "1"): ["a", "b"], ("i", "2"): ["d", "c"]}
    result = cost.paired_retrieval(refs, before, after)
    assert result["1"] == {
        "gained_associations": 1, "lost_associations": 1, "improved_queries": 1,
        "harmed_queries": 1, "unchanged_queries": 0,
    }
    assert result["10"]["gained_associations"] == result["10"]["lost_associations"] == 0
    with pytest.raises(ValueError, match="coverage"):
        cost.paired_retrieval(refs, before, {})
    with pytest.raises(ValueError, match="pool"):
        cost.paired_retrieval(refs, before, {**after, ("i", "2"): ["c", "e"]})


def test_frozen_candidate_pool_rejected_before_reranking():
    queries = {("instrument", "1"): "cost topic"}
    targets = {"a": "cost", "b": "date"}
    refs = {("instrument", "1"): {"a"}}
    def forbidden(*args):
        pytest.fail("reranker called before frozen pool validation")
    with pytest.raises(ValueError, match="frozen BGE"):
        cost.compare(queries, targets, refs, lambda _: np.array([1.0, 0.0]),
                     forbidden, expected_pool="invalid")
    root = Path(__file__).resolve().parents[1]
    with pytest.raises(ValueError, match="unknown reranker"):
        cost.run(root, reranker="bge")
