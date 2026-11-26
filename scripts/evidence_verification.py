"""Advisory evidence-action and equivalence verification development experiment."""

from __future__ import annotations

import hashlib
import json
import re
import time
from itertools import product

from .blind_adjudication import classify_nli
from .costing_retrieval import parse_reranker_results, rank
from .evidence_action_replay import build_replay, decision, observe, split_document
from .evidence_deficit_replay import formal_controls, visible_candidate
from .lfm_development import metrics, paired
from .task_framing import compile_witness, strict_agreement

PREFIX = "A report complies if and only if "
WORLDS = tuple(product((False, True), repeat=2))
MODELS = ("minilm", "deberta")


def truth_set(text):
    """Exact closed two-atom grammar; reject natural text and additional clauses."""
    if not text.startswith(PREFIX) or not text.endswith("."):
        return None
    expr = text[len(PREFIX) : -1]
    implies = re.fullmatch(r"(alpha|beta) implies (alpha|beta)", expr)
    binary = re.fullmatch(
        r"(alpha|beta) is (true|false) (and|or) (alpha|beta) is (true|false)", expr
    )
    if not (implies or binary):
        return None
    result = []
    for i, world in enumerate(WORLDS):
        values = dict(zip(("alpha", "beta"), world, strict=True))
        if implies:
            a, b = implies.groups()
            satisfied = not values[a] or values[b]
        else:
            a, va, op, b, vb = binary.groups()
            first, second = values[a] == (va == "true"), values[b] == (vb == "true")
            satisfied = first and second if op == "and" else first or second
        if satisfied:
            result.append(i)
    return set(result)


def formal_verdict(source, candidate, complete):
    if not complete:
        return {"status": "incomplete", "relation": "abstain", "counterexamples": []}
    a, b = truth_set(source), truth_set(candidate)
    if not a or not b:
        return {"status": "unsupported", "relation": "abstain", "counterexamples": []}
    different = a ^ b
    relation = compile_witness(*("yes" if s else "no" for s in (a - b, b - a, a & b)))
    return {
        "status": "counterexample" if different else "verified",
        "relation": relation,
        "a_worlds": sorted(a),
        "b_worlds": sorted(b),
        "counterexamples": [
            {"world": list(WORLDS[i]), "a": i in a, "b": i in b} for i in sorted(different)
        ],
    }


def gate(label, complete, proof):
    """Fail closed for equivalence; other labels remain unverified advisory candidates."""
    if not complete or (label == "equivalent" and proof["status"] != "verified"):
        return "abstain"
    return label


def assess(row, scorers):
    """Only source and currently visible anchored target text reach the scorer."""
    source = row["source"]
    candidate = visible_candidate(row)
    complete = candidate is not None
    if not complete:
        candidate = row["evidence"][row["id"] + ":head"]
    raw = {}
    for model in MODELS:
        started = time.perf_counter()
        forward = scorers[model](source, candidate)
        reverse = scorers[model](candidate, source)
        raw[model] = {
            "forward": list(forward),
            "reverse": list(reverse),
            "prediction": classify_nli(forward, reverse),
            "seconds": time.perf_counter() - started,
            "calls": 2,
        }
    proof = formal_verdict(source, candidate, complete)
    lexical = decision(observe(row))
    agreement = strict_agreement([raw[m]["prediction"] for m in MODELS]) if complete else "abstain"
    predictions = {m: raw[m]["prediction"] for m in MODELS}
    predictions.update(
        lexical=lexical,
        strict_nli=agreement,
        proof_required=gate(agreement, complete, proof),
        lexical_verified=gate(lexical, complete, proof),
        formal=proof["relation"],
    )
    return {
        "complete": complete,
        "visible_candidate": candidate,
        "source": source,
        "evidence_ids": sorted(row["evidence"]),
        "raw": raw,
        "proof": proof,
        "predictions": predictions,
    }


def rerank_state(row, corpus, scorer):
    pool = row["pool"]
    started = time.perf_counter()
    scores = parse_reranker_results(
        pool,
        [
            {"index": i, "relevance_score": scorer(row["source"], corpus[key])}
            for i, key in enumerate(pool)
        ],
    )
    ranking = rank(scores)
    new = {key: corpus[key] for key in ranking[:2] if key not in row["evidence"]}
    after = {**row, "evidence": {**row["evidence"], **new}}
    return after, {
        "ranking": ranking,
        "scores": scores,
        "new_evidence": new,
        "calls": len(pool),
        "seconds": time.perf_counter() - started,
    }


def summarize(rows):
    reference = {row["id"]: row["reference"] for row in rows}
    predictions = rows[0]["predictions"]
    base = {row["id"]: row["predictions"]["lexical"] for row in rows}
    result = {}
    for name in predictions:
        pred = {row["id"]: row["predictions"][name] for row in rows}
        result[name] = {
            **metrics(reference, pred),
            "paired_vs_lexical": paired(reference, base, pred),
            "missed_equivalents": sum(
                reference[k] == "equivalent" and pred[k] != reference[k] for k in reference
            ),
        }
    return result


def run(cases, scorers, scorer):
    started = time.perf_counter()
    replay = build_replay(cases)
    lookup = {(r["id"], tuple(r["history"])): r for r in replay}
    layouts = {r["id"]: split_document(r) for r in cases}
    rows = []
    for row in replay:
        if row["split"] != "test" or row["history"]:
            continue
        key = row["id"]
        expanded = lookup[(key, ("expand",))]
        lexical = lookup[(key, ("expand", "deep_rerank"))]
        rule = lookup[(key, ("expand", "parent" if row["parent_link"] else "deep_rerank"))]
        corpus = {
            f"{r['id']}:{part}": layouts[r["id"]][i]
            for r in cases
            if r["family"] == row["family"]
            for i, part in enumerate(("head", "tail"))
        }
        neural, receipt = rerank_state(expanded, corpus, scorer)
        states = {
            name: assess(state, scorers)
            for name, state in (
                ("head", row),
                ("expanded", expanded),
                ("lexical_deep", lexical),
                ("neural_deep", neural),
                ("rule_terminal", rule),
            )
        }
        rows.append(
            {
                "id": key,
                "split": row["split"],
                "family": row["family"],
                "reference": row["reference"],
                "pool": row["pool"],
                "states": states,
                "neural_rerank": receipt,
                "lexical_rerank": expanded["transitions"]["deep_rerank"],
            }
        )
    summary = {}
    for name in rows[0]["states"]:
        group = [{"id": r["id"], "reference": r["reference"], **r["states"][name]} for r in rows]
        summary[name] = {**summarize(group), "complete_pairs": sum(r["complete"] for r in group)}
    formal = []
    for control in formal_controls():
        key = control["id"]
        row = {
            "id": key,
            "source": control["source"],
            "evidence": {key + ":parent": control["candidate"]},
            "parent_link": True,
        }
        formal.append({"id": key, "reference": control["reference"], **assess(row, scorers)})
    before = {r["id"]: r["states"]["lexical_deep"]["complete"] for r in rows}
    after = {r["id"]: r["states"]["neural_deep"]["complete"] for r in rows}
    return {
        "claim_boundary": "Synthetic development only; proof covers exact finite grammar, not source authority",
        "cases": rows,
        "summary": summary,
        "rerank_completeness": {
            "gained_ids": sorted(k for k in before if after[k] and not before[k]),
            "lost_ids": sorted(k for k in before if before[k] and not after[k]),
        },
        "formal": {"cases": formal, "summary": summarize(formal)},
        "review_resolved": 0,
        "seconds": time.perf_counter() - started,
    }


def pinned_fixture(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("fixture hash mismatch")
    return json.loads(raw)["cases"]
