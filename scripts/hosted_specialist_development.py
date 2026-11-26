"""Bounded model-relative service diagnostics on previously public development data only."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path

from . import costing_retrieval as cost
from . import lfm_development as lfm

FIXTURE_PATH = "contracts/examples/semantic-reconciliation-synthetic-v1.json"
FIXTURE_HASH = "55d1dd465c413a4d64890974de42a9719c63b7a711f8172eb70b35160b28c3d0"
BASELINE_HASH = "09ba04a03e5942f71b3d18e6c6c2f0f3050298ad120d0b6d56ea209b29660bad"
DECISION_MODELS = {
    "d1.2-ultra": ("https://api.liquid.ai/decisions/v1/systemone", "LIQUID_API_KEY"),
    "d1.2": ("https://api.liquid.ai/decisions/v1/systemone", "LIQUID_API_KEY"),
    "jev-1.13.0": ("https://api.typesafe.ai/v1/systemone", "TYPESAFE_API_KEY"),
}
RERANK_MODELS = {
    **{
        model: ("https://api.voyageai.com/v1/rerank", "VOYAGE_API_KEY")
        for model in ("rerank-2.5", "rerank-2.5-lite", "rerank-3", "rerank-3-lite")
    },
    **{
        model: ("https://api.cohere.com/v2/rerank", "CO_API_KEY")
        for model in ("rerank-v5.0-pro", "rerank-v5.0-fast")
    },
    **{
        model: ("https://api.jina.ai/v1/rerank", "JINA_API_KEY")
        for model in ("jina-reranker-v3.5", "jina-reranker-v2-base-multilingual")
    },
}
LOCAL_QWEN = "qwen3-reranker-0.6b-q8"


def frozen_costing(root, baseline):
    _, _, queries, targets, references, paths = cost.load_inputs(root)
    if {path.name: cost.file_hash(path) for path in paths} != cost.FROZEN_INPUT_SHA256:
        raise ValueError("frozen costing source mismatch")
    if cost.file_hash(baseline) != BASELINE_HASH:
        raise ValueError("unqualified baseline receipt")
    prior = json.loads(baseline.read_text(encoding="utf-8"))
    rows = prior["results"]["bge"]["rows"]
    rankings = {(row["instrument_id"], row["item_id"]): row["ranking"] for row in rows}
    if len(rows) != len(rankings) or set(rankings) != set(queries):
        raise ValueError("frozen query mismatch")
    if any(len(order) != len(targets) or set(order) != set(targets) for order in rankings.values()):
        raise ValueError("frozen target mismatch")
    if cost.pool_sha256(rankings, 10) != cost.FROZEN_POOL_SHA256:
        raise ValueError("frozen BGE candidate pool mismatch")
    return queries, targets, references, rankings


def rerank_payload(model, query, documents):
    payload = {"model": model, "query": query, "documents": documents}
    if model in ("rerank-2.5", "rerank-2.5-lite", "rerank-3", "rerank-3-lite"):
        payload.update(top_k=len(documents), truncation=False)
    else:
        payload["top_n"] = len(documents)
    if model.startswith("jina-"):
        payload["return_documents"] = False
    if model.startswith("rerank-v5."):
        payload["max_tokens_per_doc"] = 512
    return payload


def evaluate_rerank(queries, targets, references, rankings, model, post):
    """No labels, stable IDs or baseline scores are sent to the inference endpoint."""
    ranked, rows = {}, []
    started = time.perf_counter()
    for key, order in sorted(rankings.items()):
        candidates = order[:10]
        payload = rerank_payload(model, queries[key], [targets[c] for c in candidates])
        response = post(payload)
        returned = response.get("model")
        if returned is not None and returned != model:
            raise ValueError("provider model identity mismatch")
        scores = cost.parse_reranker_results(candidates, response["results"])
        ranked[key] = cost.rank(scores)
        rows.append(
            {
                "instrument_id": key[0],
                "item_id": key[1],
                "returned_model": returned,
                "scores": scores,
                "usage": usage(response),
            }
        )
    result = cost.evaluate(references, set(targets), ranked)
    result["paired_vs_bge"] = cost.paired_retrieval(references, rankings, ranked)
    return {
        "protocol": "frozen-costing-rerank-development-v1",
        "requested_model": model,
        "reference_status": "research_seed_review_required",
        "scientific_qualification": False,
        "semantic_merges": 0,
        "top10_pool_sha256": cost.pool_sha256(rankings, 10),
        "seconds": time.perf_counter() - started,
        "requests": len(rows),
        "result": result,
        "provider_rows": rows,
    }


def usage(response):
    data = response.get("usage", {})
    if not isinstance(data, dict):
        return {}
    return {
        key: data[key]
        for key in ("input_tokens", "output_tokens", "total_tokens", "prompt_tokens")
        if type(data.get(key)) is int and data[key] >= 0
    }


def evaluate_decision(root, model, post):
    from .blind_adjudication import blinded_cases

    fixture = root / FIXTURE_PATH
    if cost.file_hash(fixture) != FIXTURE_HASH:
        raise ValueError("unqualified synthetic fixture")
    ledger = lfm.prepare_fixture(json.loads(fixture.read_text(encoding="utf-8")))
    pairs = blinded_cases(ledger["cases"])
    references = {row["id"]: row["reference"] for row in ledger["cases"]}
    direct, directional, rows = {}, {}, []
    started = time.perf_counter()
    for pair in pairs:
        response = post({"model": model, **lfm.decision_payload(pair)})
        if response.get("model") != model:
            raise ValueError("provider model identity mismatch")
        invalid = False
        try:
            direct[pair["id"]], directional[pair["id"]], probabilities = lfm.decision_vote(response)
        except (ValueError, TypeError, KeyError):
            direct[pair["id"]] = directional[pair["id"]] = "abstain"
            probabilities = None
            invalid = True
        rows.append(
            {
                "id": pair["id"],
                "invalid": invalid,
                "probabilities": probabilities,
                "usage": usage(response),
            }
        )
    return {
        "protocol": "hosted-typed-decision-development-v1",
        "requested_model": model,
        "fixture_sha256": FIXTURE_HASH,
        "relation_orientation": "legacy-B-relative-to-A",
        "scientific_qualification": False,
        "canonical_packs_promoted": 0,
        "requests": len(rows),
        "seconds": time.perf_counter() - started,
        "summary": {
            "direct": lfm.metrics(references, direct),
            "directional": lfm.metrics(references, directional),
        },
        "records": rows,
    }


def make_post(session, endpoint, key, budget):
    """Fixed endpoint, no redirects or retries; never retain credentials or response text."""
    count = 0

    def post(payload):
        nonlocal count
        count += 1
        if count > budget or len(json.dumps(payload).encode("utf-8")) > 32_768:
            raise ValueError("request budget exceeded")
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        with session.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=(5, 120),
            allow_redirects=False,
            stream=True,
        ) as response:
            if response.status_code != 200:
                raise ValueError(f"provider HTTP {response.status_code}")
            raw = response.raw.read(1_000_001, decode_content=True)
        if len(raw) > 1_000_000:
            raise ValueError("provider response exceeds limit")
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ValueError("provider response is not an object")
        return result

    return post


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", required=True, choices=[*DECISION_MODELS, *RERANK_MODELS, LOCAL_QWEN]
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-hosted-public-development", action="store_true")
    parser.add_argument("--max-requests", type=int, required=True)
    args = parser.parse_args()
    if args.model == LOCAL_QWEN:
        endpoint, key = "http://127.0.0.1:18883/v1/rerank", None
    else:
        if not args.allow_hosted_public_development or os.environ.get("GITHUB_ACTIONS") == "true":
            raise SystemExit("hosted execution requires explicit local authorization; not PR CI")
        endpoint, env = (DECISION_MODELS | RERANK_MODELS)[args.model]
        key = os.environ.get(env)
        if not key:
            raise SystemExit(f"missing local credential {env}")
    decision = args.model in DECISION_MODELS
    expected_requests = 36 if decision else 106
    if args.max_requests != expected_requests:
        raise SystemExit(f"declare exactly {expected_requests} maximum requests")
    if not decision and args.baseline is None:
        raise SystemExit("exact verified baseline receipt required")
    import requests

    started_at = datetime.now(UTC).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with requests.Session() as session:
            session.trust_env = False
            post = make_post(session, endpoint, key, args.max_requests)
            if decision:
                result = evaluate_decision(args.root, args.model, post)
            else:
                frozen = frozen_costing(args.root, args.baseline)
                result = evaluate_rerank(*frozen, args.model, post)
    except (OSError, ValueError, KeyError, TypeError, requests.RequestException) as exc:
        result = {
            "requested_model": args.model,
            "status": "failed",
            "error_type": type(exc).__name__,
            "scientific_qualification": False,
        }
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("experiment failed closed; sanitized failure receipt retained") from None
    result["status"] = "completed"
    result["access"] = "local-loopback" if args.model == LOCAL_QWEN else "hosted-service"
    result["started_at"] = started_at
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
