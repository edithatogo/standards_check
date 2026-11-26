"""Offline behavioral tests; fake runtimes are not scientific inference receipts."""
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from scripts import blind_adjudication as blind
from scripts import five_class_benchmark as five
from scripts import semantic_benchmark as semantic

ROOT = Path(__file__).resolve().parents[1]
ENTAIL = (0.01, 0.98, 0.01)
NEUTRAL = (0.01, 0.01, 0.98)


def write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def invoke(monkeypatch, module, *args):
    monkeypatch.setattr(sys, "argv", [module.__name__, *map(str, args)])
    module.main()


class FakeNLI:
    asset_hashes = {"model": "test-only"}
    version = "test-only"

    def __init__(self, assets, **kwargs):
        pass

    def score(self, premise, hypothesis):
        if premise == "too long":
            raise ValueError("context")
        return ENTAIL if premise == hypothesis else NEUTRAL


class FakeLlama:
    """Simulate the optional inference boundary; validate real output processing."""

    def __init__(self, **kwargs):
        pass

    def create_chat_completion(self, messages, **kwargs):
        pair = json.loads(messages[1]["content"])
        a, b = pair["A"], pair["B"]
        if a == "bad" or (isinstance(a, list) and a[0]["text"] == "bad"):
            text = "invalid JSON"
        elif isinstance(a, str):
            text = json.dumps({"label": "equivalent", "a_quote": a, "b_quote": b})
        elif "a_condition" in kwargs["response_format"]["schema"]["properties"]:
            text = json.dumps({"a_condition": "P", "b_condition": "P_AND_Q", "a": [2], "b": [2]})
        else:
            text = json.dumps({"label": "equivalent", "a": [1], "b": [1]})
        return {"choices": [{"message": {"content": text}}]}


@pytest.fixture
def fake_runtime(monkeypatch, tmp_path):
    path = tmp_path / "test-weights.gguf"
    path.write_bytes(b"synthetic runtime stub")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setitem(sys.modules, "llama_cpp", SimpleNamespace(Llama=FakeLlama, __version__="test"))
    for model in list(blind.MODELS.values()) + list(five.JUDGES.values()):
        monkeypatch.setitem(model, "sha256", digest)
    return path


def test_pinned_sources_and_formal_controls_are_separate(tmp_path):
    legacy = blind.source_pairs(ROOT, tmp_path)
    assert legacy["cases"]
    assert legacy["held_sources"]  # optional publisher XML is not acquired by regression CI
    assert len({p["id"] for p in legacy["cases"]}) == len(legacy["cases"])
    result = five.prepare(ROOT)
    cases = result["cases"]
    assert len({p["id"] for p in cases}) == len(cases)
    dev = {p["family"] for p in cases if p["split"] == "dev"}
    test = {p["family"] for p in cases if p["split"] == "test"}
    assert dev and test and dev.isdisjoint(test)
    for p in cases:
        assert p["source_anchors"]
        if p["origin"] == "formal_source_derived":
            assert p["reference"] in five.LABELS
        else:
            assert p["reference"] is None
    for path, parser in [
        (tmp_path / "source/archetypes/spirit-2025.docx", five.spirit_rows),
        (tmp_path / "source/archive/processed/CONSORT_2025_checklist.docx", five.consort_rows),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"wrong pin")
        with pytest.raises(ValueError, match="pin|blob"):
            parser(tmp_path)
    with pytest.raises(ValueError):
        five.relation(0, 1)
    with pytest.raises(ValueError):
        five.render(0, "P", "Q")
    assert five.evidence_spans("A\n\nB\r\n") == [(0, 1), (3, 4)]


def test_blind_vote_and_receipt_fail_closed(tmp_path, monkeypatch, fake_runtime):
    pairs = [
        {"id": "1", "source": "private source", "candidate": "private source"},
        {"id": "2", "source": "bad", "candidate": "other"},
    ]
    inp = write_json(tmp_path / "blinded.json", pairs)
    left = blind.judge(inp, fake_runtime, "qwen")
    right = blind.judge(inp, fake_runtime, "smollm")
    assert [v["label"] for v in left["votes"]] == ["equivalent", "abstain"]
    assert "private source" not in json.dumps(left)
    assert blind.span("x x", "x") is None
    assert blind.span("x", " ") is None
    with pytest.raises(ValueError, match="mismatch"):
        blind.consensus(left["votes"][0], left["votes"][1])
    with pytest.raises(ValueError, match="pinned"):
        blind.judge(inp, write_json(tmp_path / "bad.gguf", {}), "qwen")
    write_json(inp, [{**pairs[0], "reference": "equivalent"}])
    with pytest.raises(ValueError, match="unblinded"):
        blind.judge(inp, fake_runtime, "qwen")
    monkeypatch.setattr(semantic, "LocalNLI", FakeNLI)
    ledger = {
        "cases": [{**p, "split": "test", "family": "f"} for p in pairs],
        "held_sources": [],
        "families": ["f"],
    }
    pin = left["input_sha256"]
    report = blind.evaluate(ledger, pin, left, right, tmp_path)
    assert report["canonical_packs_promoted"] == 0
    assert "private source" not in json.dumps(report)
    assert report["records"][0]["predicted"] == "equivalent"
    for bad in (
        {**right, "input_sha256": "changed"},
        {**right, "model": left["model"]},
        {**right, "votes": right["votes"][:1]},
        {**right, "votes": [*right["votes"], right["votes"][0]]},
    ):
        with pytest.raises(ValueError):
            blind.evaluate(ledger, pin, left, bad, tmp_path)
    tampered = {**ledger, "cases": [{**ledger["cases"][0], "source": "changed"}, ledger["cases"][1]]}
    with pytest.raises(ValueError, match="digest"):
        blind.evaluate(tampered, pin, left, right, tmp_path)


def test_five_class_judging_and_pair_digest_validation(tmp_path, monkeypatch, fake_runtime):
    controlled = {"id": "a", "source": five.render(five.P, "Report sample.", "Report date."),
                  "candidate": five.render(five.P & five.Q, "Report sample.", "Report date.")}
    natural = {"id": "b", "source": "private text", "candidate": "private text"}
    invalid = {"id": "c", "source": "bad", "candidate": "too long"}
    pairs = [controlled, natural, invalid]
    left = five.judge(pairs, fake_runtime, "qwen4", {"revision": "test"})
    right = five.judge(pairs, fake_runtime, "phi4", {"revision": "test"})
    assert [v["label"] for v in left["votes"]] == ["narrower", "equivalent", "abstain"]
    assert "private text" not in json.dumps(left)
    with pytest.raises(ValueError, match="unqualified"):
        five.judge(pairs, write_json(tmp_path / "bad.gguf", {}), "phi4", {"revision": "test"})
    with pytest.raises(ValueError, match="unblinded"):
        five.judge([{**natural, "family": "test"}], fake_runtime, "phi4", {"revision": "test"})
    ledger = {"cases": [
        {**controlled, "split": "test", "family": "f", "reference": "narrower"},
        {**natural, "split": "test", "family": "f", "reference": None},
        {**invalid, "split": "test", "family": "g", "reference": "indeterminate"},
    ]}
    rows = five.merge_votes(ledger, pairs, left, right)
    assert [r["label"] for r in rows] == ["narrower", "equivalent", "abstain"]
    assert "private text" not in json.dumps(rows)
    for bad in (
        {**right, "input_sha256": "changed"},
        {**right, "model": left["model"]},
        {**right, "votes": right["votes"][:2]},
        {**right, "votes": [*right["votes"], right["votes"][0]]},
        {**right, "votes": [{**right["votes"][0], "source_sha256": "changed"}, *right["votes"][1:]]},
    ):
        with pytest.raises(ValueError):
            five.merge_votes(ledger, pairs, left, bad)
    monkeypatch.setattr(semantic, "LocalNLI", FakeNLI)
    report = five.score(ledger, rows, tmp_path, "test")
    assert report["natural_consensus_count"] == report["natural_consensus_agreement"] == 1
    assert report["records"][2]["predicted"] == "abstain"
    assert report["records"][2]["forward"] is None


def test_cli_receipt_workflows_keep_natural_pairs_unlabelled(tmp_path, monkeypatch, fake_runtime):
    monkeypatch.setattr(semantic, "LocalNLI", FakeNLI)
    blind_dir = tmp_path / "blind"
    invoke(monkeypatch, blind, "prepare", "--directory", blind_dir, "--root", ROOT, "--source-dir", tmp_path)
    for name in blind.MODELS:
        invoke(monkeypatch, blind, "judge", "--directory", blind_dir, "--model", name, "--weights", fake_runtime)
    invoke(monkeypatch, blind, "evaluate", "--directory", blind_dir, "--nli-assets", tmp_path)
    assert read_json(blind_dir / "benchmark-receipt.json")["canonical_packs_promoted"] == 0
    directory = tmp_path / "five"
    invoke(monkeypatch, five, "prepare", "--directory", directory, "--root", ROOT)
    metadata = write_json(tmp_path / "metadata.json", {"revision": "test"})
    for name in five.JUDGES:
        invoke(monkeypatch, five, "judge", "--directory", directory, "--name", name,
               "--weights", fake_runtime, "--model-metadata", metadata)
    invoke(monkeypatch, five, "baseline", "--directory", directory, "--assets", tmp_path)
    receipt = read_json(directory / "five-class-receipt.json")
    assert receipt["canonical_packs_promoted"] == 0
    assert receipt["qualification"]["qualified"] is False
    assert receipt["escalation"]["eligible"] is True
    invoke(monkeypatch, five, "additional", "--directory", directory, "--assets", tmp_path)
    receipt = read_json(directory / "five-class-receipt.json")
    assert receipt["paired_errors"] == {"fixed": 0, "introduced": 0}
    receipt["escalation"]["eligible"] = False
    write_json(directory / "five-class-receipt.json", receipt)
    with pytest.raises(ValueError, match="no material"):
        invoke(monkeypatch, five, "additional", "--directory", directory, "--assets", tmp_path)


def test_local_nli_validates_model_assets_shape_and_context(monkeypatch, tmp_path):
    model_file = tmp_path / "model_quint8_avx2.onnx"
    model_file.write_bytes(b"synthetic model")
    pin = hashlib.sha256(model_file.read_bytes()).hexdigest()
    config = tmp_path / "config.json"
    write_json(config, {"id2label": dict(enumerate(semantic.LABELS))})
    write_json(tmp_path / "tokenizer.json", {})
    state = SimpleNamespace(inputs=["input_ids", "attention_mask"], length=4, logits=[[0., 5., 0.]])

    class Tokenizer:
        @classmethod
        def from_file(cls, name):
            return cls()

        def no_truncation(self):
            pass

        def no_padding(self):
            pass

        def encode(self, a, b):
            return SimpleNamespace(ids=[1] * state.length, attention_mask=[1] * state.length,
                                   type_ids=[0] * state.length)

    class Session:
        def __init__(self, path, sess_options, providers):
            assert providers == ["CPUExecutionProvider"]

        def get_inputs(self):
            return [SimpleNamespace(name=n) for n in state.inputs]

        def run(self, outputs, inputs):
            assert all(v.dtype == np.int64 for v in inputs.values())
            return [state.logits]

    monkeypatch.setitem(sys.modules, "tokenizers", SimpleNamespace(Tokenizer=Tokenizer))
    monkeypatch.setitem(sys.modules, "onnxruntime", SimpleNamespace(
        SessionOptions=SimpleNamespace, InferenceSession=Session, __version__="test"))
    with pytest.raises(ValueError, match="model bytes"):
        semantic.LocalNLI(tmp_path)
    write_json(config, {"id2label": {"0": "neutral", "1": "entailment", "2": "contradiction"}})
    with pytest.raises(ValueError, match="label order"):
        semantic.LocalNLI(tmp_path, expected_model_sha256=pin)
    write_json(config, {"id2label": dict(enumerate(semantic.LABELS))})
    state.inputs = ["input_ids"]
    with pytest.raises(ValueError, match="model inputs"):
        semantic.LocalNLI(tmp_path, expected_model_sha256=pin)
    state.inputs = ["input_ids", "attention_mask", "token_type_ids"]
    nli = semantic.LocalNLI(tmp_path, expected_model_sha256=pin)
    assert nli.asset_hashes["model_quint8_avx2.onnx"] == pin
    assert nli.score("A", "B")[1] > .95
    state.length = 513
    with pytest.raises(ValueError, match="context"):
        nli.score("A", "B")
    state.length = 3
    state.logits = [[0, 1]]
    with pytest.raises(ValueError, match="output"):
        nli.score("A", "B")
    state.logits = [[0, float("nan"), 1]]
    with pytest.raises(ValueError, match="output"):
        nli.score("A", "B")


def test_semantic_metrics_and_cli_are_candidate_only(tmp_path, monkeypatch):
    class Doc(list):
        def has_annotation(self, name):
            return True

    class NLP:
        meta = {"version": "3.8.0"}

        def __call__(self, text):
            return Doc([SimpleNamespace(lemma_=w, pos_="NOUN", dep_="ROOT",
                         head=SimpleNamespace(lemma_=w), is_space=False, is_punct=False)
                        for w in text.split()])

    nlp = NLP()
    assert semantic.dependency_similarity(nlp, "", "") == 0
    assert semantic.dependency_similarity(nlp, "A", "A") == 1
    with pytest.raises(ValueError, match="annotations"):
        semantic.dependency_similarity(lambda text: SimpleNamespace(has_annotation=lambda x: False), "A", "B")
    cases = [
        {"id": "1", "family": "dev", "split": "dev", "source": "Report sample.",
         "candidate": "Report sample.", "forward": "entailment", "reverse": "entailment"},
        {"id": "2", "family": "test", "split": "test", "source": "Report sample.",
         "candidate": "Do not report sample.", "forward": "neutral", "reverse": "neutral"},
    ]
    for bad in ([], [cases[0], cases[0]]):
        with pytest.raises(ValueError, match="empty or duplicate"):
            semantic.validate_cases(bad)
    with pytest.raises(ValueError, match="threshold"):
        semantic.bidirectional(ENTAIL, ENTAIL, .42)
    with pytest.raises(ValueError, match="coverage"):
        semantic.measures([True], [])
    with pytest.raises(ValueError, match="development"):
        semantic.select_threshold([])
    assert blind.classify_nli((.34, .33, .33), ENTAIL) == "abstain"
    report = semantic.evaluate(cases, nlp, FakeNLI(tmp_path))
    assert report["summary"]["bidirectional_nli"]["test"]["tn"] == 1
    assert report["canonical_packs_promoted"] == 0
    assert "Report sample" not in json.dumps(report)
    monkeypatch.setitem(sys.modules, "spacy", SimpleNamespace(load=lambda name: nlp, __version__="test"))
    monkeypatch.setitem(sys.modules, "resource", SimpleNamespace(
        getrusage=lambda *a: SimpleNamespace(ru_maxrss=0), RUSAGE_SELF=0))
    monkeypatch.setattr(semantic, "LocalNLI", FakeNLI)
    fixture = write_json(tmp_path / "cases.json", {"schema_version": 1, "label_origin": "synthetic_analyst_authored", "cases": cases})
    output = tmp_path / "output" / "receipt.json"
    args = ("--cases", fixture, "--assets", tmp_path, "--output", output, "--revision", "test")
    invoke(monkeypatch, semantic, *args)
    assert read_json(output)["canonical_packs_promoted"] == 0
    nlp.meta = {"version": "wrong"}
    with pytest.raises(ValueError, match="spaCy"):
        invoke(monkeypatch, semantic, *args)
    write_json(fixture, {"schema_version": 0})
    with pytest.raises(ValueError, match="fixture"):
        invoke(monkeypatch, semantic, *args)
