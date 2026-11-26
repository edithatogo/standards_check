"""Development-only retrieval against the existing editorial costing mapping seed."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

from .lexical_text import cosine, term_counts, tfidf_vectors

KS = (1, 3, 5, 10)
MODELS = {
    "bge": {
        "id": "BAAI/bge-small-en-v1.5",
        "revision": "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a",
        "file": "onnx/model.onnx",
        "sha256": "828e1496d7fabb79cfa4dcd84fa38625c0d3d21da474a00f08db0f559940cf35",
        "licence": "MIT",
    },
    "reranker": {
        "id": "cross-encoder/ms-marco-MiniLM-L6-v2",
        "revision": "739bce82df32cacea8ff0edf73ab49ae315e5a5f",
        "file": "onnx/model_quint8_avx2.onnx",
        "sha256": "c80a8b34256ea453093d612e3ac48d3d965a0c0a48c7906709af8b8e28461bf9",
        "licence": "Apache-2.0",
    },
}
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def rank(scores, *, positive=False):
    if any(not math.isfinite(score) for score in scores.values()):
        raise ValueError("nonfinite retrieval score")
    return [
        key
        for key in sorted(scores, key=lambda key: (-scores[key], key))
        if not positive or scores[key] > 0
    ]


def evaluate(references, targets, rankings):
    """Missing candidates count as misses; ties are settled before evaluation."""
    if not references or set(rankings) != set(references):
        raise ValueError("query coverage mismatch")
    rows = []
    for key, expected in sorted(references.items()):
        order = rankings[key]
        if not expected or not expected <= targets:
            raise ValueError("invalid reference association")
        if len(order) != len(set(order)) or not set(order) <= targets:
            raise ValueError("invalid candidate ranking")
        hits = [int(candidate in expected) for candidate in order]
        gain = sum(hit / math.log2(i + 2) for i, hit in enumerate(hits[:5]))
        ideal = sum(1 / math.log2(i + 2) for i in range(min(5, len(expected))))
        rows.append(
            {
                "instrument_id": key[0],
                "item_id": key[1],
                "reference": sorted(expected),
                "ranking": order,
                "hits": {str(k): sum(hits[:k]) for k in KS},
                "reciprocal_rank": next((1 / (i + 1) for i, hit in enumerate(hits) if hit), 0.0),
                "ndcg5": gain / ideal,
            }
        )

    def summarize(group):
        n = len(group)
        total = sum(len(row["reference"]) for row in group)
        micro_recall = {str(k): sum(row["hits"][str(k)] for row in group) / total for k in KS}
        precision = {str(k): sum(row["hits"][str(k)] for row in group) / (n * k) for k in KS}
        return {
            "queries": n,
            "positive_associations": total,
            "no_candidates": sum(not row["ranking"] for row in group),
            "macro_query_recall": {
                str(k): sum(row["hits"][str(k)] / len(row["reference"]) for row in group) / n
                for k in KS
            },
            "micro_recall": micro_recall,
            "precision_at_k": precision,
            "mrr": sum(row["reciprocal_rank"] for row in group) / n,
            "ndcg5": sum(row["ndcg5"] for row in group) / n,
        }

    instruments = sorted({key[0] for key in references})
    return {
        **summarize(rows),
        "by_instrument": {
            inst: summarize([row for row in rows if row["instrument_id"] == inst])
            for inst in instruments
        },
        "rows": rows,
    }


def lexical_rankings(queries, targets, method):
    docs = {("query", key): term_counts(value, method) for key, value in queries.items()}
    docs.update({("target", key): term_counts(value, method) for key, value in targets.items()})
    vectors = tfidf_vectors(docs)
    rankings = {}
    for key in queries:
        scores = {
            candidate: cosine(vectors.get(("query", key), {}), vectors.get(("target", candidate), {}))
            for candidate in targets
        }
        rankings[key] = rank(scores, positive=True)
    return rankings


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class LocalRanker:
    """Pinned ONNX graphs, bounded tokenization and CPU-only execution."""

    def __init__(self, directory, name):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        self.name = name
        model = directory / "model.onnx"
        if model.stat().st_size > 200_000_000 or file_hash(model) != MODELS[name]["sha256"]:
            raise ValueError("unqualified retrieval model bytes")
        self.tokenizer = Tokenizer.from_file(str(directory / "tokenizer.json"))
        self.tokenizer.no_truncation()
        self.tokenizer.no_padding()
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(
            str(model), sess_options=options, providers=["CPUExecutionProvider"]
        )
        self.inputs = {value.name for value in self.session.get_inputs()}
        allowed = {"input_ids", "attention_mask", "token_type_ids"}
        if not {"input_ids", "attention_mask"} <= self.inputs <= allowed:
            raise ValueError("unsupported retrieval inputs")
        self.output = "last_hidden_state" if name == "bge" else "logits"
        if self.output not in {value.name for value in self.session.get_outputs()}:
            raise ValueError("unexpected retrieval output name")
        self.asset_hashes = {
            path.name: file_hash(path)
            for path in (model, directory / "tokenizer.json", directory / "config.json")
        }
        self.version = ort.__version__

    def __call__(self, first, second=None):
        import numpy as np

        encoded = self.tokenizer.encode(first, second)
        if len(encoded.ids) > 512:
            raise ValueError("retrieval input exceeds context; no truncation")
        values = {
            "input_ids": encoded.ids,
            "attention_mask": encoded.attention_mask,
            "token_type_ids": encoded.type_ids,
        }
        feed = {key: np.asarray([values[key]], dtype=np.int64) for key in self.inputs}
        output = np.asarray(self.session.run([self.output], feed)[0], dtype=np.float64)
        if not np.isfinite(output).all():
            raise ValueError("nonfinite retrieval output")
        if self.name == "bge":
            if output.shape != (1, len(encoded.ids), 384):
                raise ValueError("unexpected BGE hidden state shape")
            vector = output[0, 0]
            norm = np.linalg.norm(vector)
            if not np.isfinite(norm) or norm == 0:
                raise ValueError("invalid embedding norm")
            return vector / norm
        if output.shape != (1, 1):
            raise ValueError("unexpected reranker score shape")
        return float(output[0, 0])


def compare(queries, targets, references, embed=None, rerank=None):
    if set(queries) != set(references) or not targets:
        raise ValueError("input/reference coverage mismatch")
    report = {}
    for method in ("word", "char"):
        start = time.perf_counter()
        rankings = lexical_rankings(queries, targets, method)
        report[method] = {
            **evaluate(references, set(targets), rankings),
            "seconds": time.perf_counter() - start,
        }
    if embed is not None:
        start = time.perf_counter()
        vectors = {key: embed(value) for key, value in targets.items()}
        rankings = {}
        for key, query in queries.items():
            vector = embed(QUERY_PREFIX + query)
            scores = {candidate: float(vector @ target) for candidate, target in vectors.items()}
            rankings[key] = rank(scores)
        report["bge"] = {
            **evaluate(references, set(targets), rankings),
            "seconds": time.perf_counter() - start,
        }
        if rerank is not None:
            start = time.perf_counter()
            refined = {}
            for key, order in rankings.items():
                scores = {
                    candidate: rerank(queries[key], targets[candidate]) for candidate in order[:10]
                }
                refined[key] = rank(scores)
            report["bge_then_reranker10"] = {
                **evaluate(references, set(targets), refined),
                "seconds": time.perf_counter() - start,
            }
    elif rerank is not None:
        raise ValueError("reranking requires a candidate retrieval method")
    return report


def run(root, assets=None):
    from .validate_costing_reconciliation import validate

    catalogue = root / "reconciliations" / "costing"
    paths = [catalogue / "costing-standards-registry.json", catalogue / "costing-item-mappings.json"]
    registry, mappings = (json.loads(path.read_text(encoding="utf-8")) for path in paths)
    if validate(registry, mappings):
        raise ValueError("invalid costing metadata")
    queries, references = {}, {}
    for row in mappings["mappings"]:
        key = (row["instrument_id"], row["item_id"])
        queries[key] = row["topic"]
        references[key] = set(row["domain_ids"])
    targets = {row["id"]: row["definition"] for row in registry["domains"]}
    models = {name: LocalRanker(assets / name, name) for name in MODELS} if assets else {}
    return {
        "protocol": "costing-editorial-retrieval-development-v1",
        "reference_status": mappings["mapping_status"],
        "claim_boundary": "Editorial covers_topic agreement only; no independent semantic labels.",
        "scientific_qualification": False,
        "semantic_merges": 0,
        "instrument_records": len(registry["instruments"]),
        "mapped_instruments": len({key[0] for key in queries}),
        "queries": len(queries),
        "target_domains": len(targets),
        "candidate_pool_pairs": len(queries) * len(targets),
        "input_sha256": {path.name: file_hash(path) for path in paths},
        "models": {
            name: {**MODELS[name], "assets": model.asset_hashes, "runtime_version": model.version}
            for name, model in models.items()
        },
        "results": compare(queries, targets, references, models.get("bge"), models.get("reranker")),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--assets", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root, args.assets)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    summary = {
        key: {k: v for k, v in row.items() if k not in {"rows", "by_instrument"}}
        for key, row in result["results"].items()
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
