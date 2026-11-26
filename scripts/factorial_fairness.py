"""Matched-budget retrieval factorial and full-corpus design ledger (advisory)."""

from __future__ import annotations

import argparse
import hashlib
import json
from importlib.metadata import version
from itertools import combinations, product
from pathlib import Path

import numpy as np

from .costing_retrieval import rank
from .evidence_action_replay import (
    FIXTURE_SHA,
    decision,
    observe,
    reference,
    split_document,
    tokens,
)
from .lexical_text import cosine, term_counts, tfidf_vectors

FACTORS = ("deficit_query", "hybrid_pool", "character_rank")
NEURAL_SHA = "7a79c7734a6d202332fa1a65178a1fb4a9b14e83762041418574dd3a7eea2f7d"
LEDGER_SHA = "4bcf3434f1b907df9a0b52afcaef90b8a184aae05e8ab9b9a30a2f692a0439c2"


def bits(n):
    return ["".join(map(str, v)) for v in product((0, 1), repeat=n)]


def full_design():
    return bits(6)


def design_rank():
    matrix = np.asarray([[1 if bit == "1" else -1 for bit in row] for row in full_design()])
    terms = [axes for size in range(7) for axes in combinations(range(6), size)]
    contrasts = np.column_stack([matrix[:, axes].prod(axis=1) for axes in terms])
    if not np.array_equal(contrasts.T @ contrasts, 64 * np.eye(64)):
        raise ValueError("full factorial matrix is not orthogonal")
    return int(np.linalg.matrix_rank(contrasts))


def coverage_ledger(rows):
    ids = {r["id"] for r in rows}
    if not rows or len(ids) != len(rows):
        raise ValueError("empty or duplicate catalogue identity")
    # Source receipts do not qualify the six-component pipeline or its reference.
    # Never convert absent eligibility evidence into completed or negative results.
    return {
        "factors": ["layout", "structure", "tagging", "retrieval", "reranking", "decision"],
        "total_slots": 64 * len(rows),
        "configuration_matrix_rank": design_rank(),
        "executed_slots": 0,
        "rows": [
            {
                "id": r["id"],
                "source_blob_sha": r["source_blob_sha"],
                "source_status": r.get("source_observation", "not_evidenced"),
                "rights_status": r.get("rights_observation", "not_evidenced"),
                "cells": [
                    {"configuration": key, "status": "held_source_or_component_qualification"}
                    for key in full_design()
                ],
            }
            for r in sorted(rows, key=lambda row: row["id"])
        ],
    }


def score(query, corpus, method):
    docs = {("q", "q"): term_counts(query, method)}
    docs.update({("t", k): term_counts(v, method) for k, v in corpus.items()})
    vectors = tfidf_vectors(docs)
    return {k: cosine(vectors.get(("q", "q"), {}), vectors.get(("t", k), {})) for k in corpus}


def controlled(cases):
    """Cross query, generation and ranking at six candidates and two *new* fragments."""
    layouts = {r["id"]: split_document(r) for r in cases}
    if len(layouts) != len(cases):
        raise ValueError("duplicate case")
    cells, features = {key: {} for key in bits(3)}, {}
    for row in cases:
        key = row["id"]
        head, _, parent = layouts[key]
        evidence = {key + ":head": head}
        corpus = {
            f"{r['id']}:{part}": layouts[r["id"]][i]
            for r in cases
            if r["family"] == row["family"]
            for i, part in enumerate(("head", "tail"))
            if f"{r['id']}:{part}" not in evidence
        }
        if len(corpus) < 6:
            raise ValueError("insufficient eligible candidates for matched pool")
        state = {"id": key, "source": row["source"], "evidence": evidence, "parent_link": parent}
        obs = observe(state)
        features[key] = [len(row["source"].split()), len(head.split()), *obs[2:]]
        for q in (0, 1):
            query = row["source"]
            if q:
                query += " " + " ".join(sorted(tokens(query) - tokens(head)) * 2)
            # All arms compute both channels over the same unseen universe. This
            # isolates selection utility, not the incremental cost of hybrid search.
            word, char = (score(query, corpus, method) for method in ("word", "char"))
            rankings = [rank(s) for s in (word, char)]
            reciprocal = {k: sum(1 / (60 + order.index(k) + 1) for order in rankings) for k in corpus}
            for g in (0, 1):
                pool = (rank(reciprocal) if g else rankings[0])[:6]
                for m in (0, 1):
                    scores = char if m else word
                    selected = rank({k: scores[k] for k in pool})[:2]
                    after = observe({**state, "evidence": {**evidence, **{k: corpus[k] for k in selected}}})
                    pred, gold = decision(after), reference(row)
                    target = key + ":tail"
                    cells[f"{q}{g}{m}"][key] = {
                        "id": key, "family": row["family"], "split": row["split"],
                        "pool": pool, "selected": selected, "target_in_pool": int(target in pool),
                        "complete": int(after[0]), "correct": int(pred == gold),
                        "false_equivalence": int(pred == "equivalent" and gold != "equivalent"),
                        "abstained": int(pred == "abstain"), "reference": gold, "prediction": pred,
                        "scored_candidates_per_channel": len(corpus),
                        "selected_words": sum(len(corpus[k].split()) for k in selected),
                    }
    return cells, features


def paired_bayes(cells, names, field, *, draws=10000, seed=17):
    """Bayesian bootstrap over family means; uncertainty only over observed families."""
    keys = bits(len(names))
    if set(cells) != set(keys):
        raise ValueError("incomplete paired design")
    ids = set(cells[keys[0]])
    if not ids or any(set(c) != ids for c in cells.values()):
        raise ValueError("unpaired case identities")
    groups = {k: cells[keys[0]][k]["family"] for k in ids}
    if any(row["family"] != groups[k] for cell in cells.values() for k, row in cell.items()):
        raise ValueError("unpaired family identities")
    families = sorted(set(groups.values()))
    weights = np.random.default_rng(seed).dirichlet(np.ones(len(families)), size=draws)
    out = {}
    for size in range(1, len(names) + 1):
        for axes in combinations(range(len(names)), size):
            effects = {
                k: sum(
                    (-1) ** sum(b[i] == "0" for i in axes) * cells[b][k][field] for b in keys
                ) / 2 ** (len(names) - size)
                for k in ids
            }
            group = np.asarray([np.mean([effects[k] for k in sorted(ids) if groups[k] == f]) for f in families])
            samples = weights @ group
            out[":".join(names[i] for i in axes)] = {
                "mean": float(group.mean()), "interval_90": np.quantile(samples, [0.05, 0.95]).tolist(),
                "family_effects": dict(zip(families, group.tolist(), strict=True)),
                "probability_positive": float(np.mean(samples > 0)),
            }
    return out


def hierarchical_predict(x, y, families, cases, x_test):
    """Fixed-prior logistic random intercepts; Laplace plus Gauss-Hermite prediction."""
    # Standardisation and all random effects use training families only.
    centre, scale = x.mean(axis=0), x.std(axis=0)
    scale = np.where(scale > 0, scale, 1)
    fixed = np.column_stack((np.ones(len(x)), (x - centre) / scale))
    random = np.column_stack([
        np.asarray([key == v for key in group], dtype=float)
        for group in (families, cases) for v in sorted(set(group))
    ])
    design = np.column_stack((fixed, random))
    prior_sd = np.asarray([2.] + [1.] * x.shape[1] + [.8] * len(set(families)) + [1.] * len(set(cases)))
    precision = np.diag(1 / prior_sd ** 2)
    weight = np.zeros(design.shape[1])
    for _ in range(60):
        probability = 1 / (1 + np.exp(-np.clip(design @ weight, -40, 40)))
        hessian = design.T @ ((probability * (1 - probability))[:, None] * design) + precision
        step = np.linalg.solve(hessian, design.T @ (y - probability) - precision @ weight)
        weight += step
        if np.max(np.abs(step)) < 1e-8:
            break
    else:
        raise ValueError("hierarchical posterior mode did not converge")
    covariance = np.linalg.inv(hessian)[:fixed.shape[1], :fixed.shape[1]]
    held = np.column_stack((np.ones(len(x_test)), (x_test - centre) / scale))
    mu = held @ weight[:fixed.shape[1]]
    # Integrate over uncertainty and unseen case/family intercepts, never fit them on test.
    variance = np.einsum("ij,jk,ik->i", held, covariance, held) + .8 ** 2 + 1.
    nodes, weights = np.polynomial.hermite.hermgauss(24)
    logits = mu[:, None] + np.sqrt(2 * variance)[:, None] * nodes
    return (1 / (1 + np.exp(-np.clip(logits, -40, 40)))) @ weights / np.sqrt(np.pi)


def observed_neural_ranking(cases, report):
    """Rank identical unseen candidates using actual cached neural scores and lexical scores."""
    source = {r["id"]: r for r in cases}
    layout = {k: split_document(r) for k, r in source.items()}
    rows = []
    for row in report["cases"]:
        key = row["id"]
        pool = row["pool"]
        scores = row["neural_rerank"]["scores"]
        if len(set(pool)) != len(pool) or set(pool) != set(scores) or row["family"] != source[key]["family"]:
            raise ValueError("invalid neural pool binding")
        corpus = {f"{k}:{part}": layout[k][i] for k, r in source.items()
                  if r["family"] == row["family"] for i, part in enumerate(("head", "tail"))}
        if not set(pool) <= set(corpus):
            raise ValueError("pool outside family corpus")
        current = row["states"]["expanded"]
        seen = set(current["evidence_ids"])
        unseen = [k for k in pool if k not in seen]
        lexical = score(source[key]["source"], {k: corpus[k] for k in pool}, "char")
        result = {"id": key, "family": row["family"], "pool": pool, "unseen": unseen,
                  "complete_before": current["complete"], "target_in_pool": key+":tail" in pool}
        for name, values in (("lexical", lexical), ("neural", scores)):
            selected = rank({k: values[k] for k in unseen})[:2]
            result[name] = {"selected": selected, "complete": current["complete"] or key+":tail" in selected,
                            "new_words": sum(len(corpus[k].split()) for k in selected)}
        rows.append(result)
    return {"rows": rows, "complete": {name: sum(row[name]["complete"] for row in rows) for name in ("lexical", "neural")},
            "fresh_neural_calls": 0, "boundary": "Retained scores, equal novel-fragment caps; no imputed NLI outcomes"}


def matched_coverage(report):
    """Compare proof routing to a confidence-only advisory selection at the same coverage."""
    rows = report["cases"]
    mode = "rule_terminal"
    state = [(r, r["states"][mode]) for r in rows]
    accepted = [(r, s) for r, s in state if s["predictions"]["strict_nli"] != "abstain"]
    proof = [(r, s) for r, s in state if s["predictions"]["proof_required"] != "abstain"]
    # Confidence is only a fixed ranking heuristic, not a calibrated probability of correctness.
    def confidence(item):
        r, s = item
        return (-min(max(v[d]) for v in s["raw"].values() for d in ("forward", "reverse")), r["id"])
    matched = sorted(accepted, key=confidence)[:len(proof)]
    out = {mode: {name: {"accepted": len(items), "correct": sum(s["predictions"][label] == r["reference"] for r, s in items),
                        "false_equivalence": sum(s["predictions"][label] == "equivalent" and r["reference"] != "equivalent" for r, s in items),
                        "ids": sorted(r["id"] for r, _ in items)}
                 for name, items, label in (("unrestricted_advisory", accepted, "strict_nli"), ("matched_confidence_advisory", matched, "strict_nli"), ("proof_required", proof, "proof_required"))}}
    return out


def predict_grouped(cells, features, *, models=("beta", "ridge_logistic", "bayesian_hierarchical", "xgboost")):
    """Predict completeness before acquisition, using leave-one-family-out folds."""
    entries = [(key, b, row) for b, cell in sorted(cells.items()) for key, row in sorted(cell.items())]
    x = np.asarray([features[k] + [int(i) for i in b] for k, b, _ in entries])
    y = np.asarray([r["complete"] for _, _, r in entries])
    group = np.asarray([r["family"] for _, _, r in entries])
    output = {name: np.zeros(len(entries)) for name in models}
    folds = []
    for family in sorted(set(group)):
        train, test = group != family, group == family
        if not train.any() or not test.any():
            raise ValueError("at least two families required")
        indices = np.flatnonzero(test)
        for name in models:
            if name == "beta":
                for i in indices:
                    labels = [y[j] for j in np.flatnonzero(train) if entries[j][1] == entries[i][1]]
                    output[name][i] = (sum(labels) + 1) / (len(labels) + 2)
                continue
            if name == "bayesian_hierarchical":
                output[name][test] = hierarchical_predict(
                    x[train], y[train], group[train], [entries[j][0] for j in np.flatnonzero(train)], x[test]
                )
                continue
            if name == "ridge_logistic":
                from sklearn.linear_model import LogisticRegression
                from sklearn.pipeline import make_pipeline
                from sklearn.preprocessing import StandardScaler

                estimator = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000))
            elif name == "xgboost":
                from xgboost import XGBClassifier

                estimator = XGBClassifier(n_estimators=64, max_depth=2, learning_rate=0.05,
                                          reg_lambda=5.0, n_jobs=1, random_state=17, tree_method="hist")
            else:
                raise ValueError("unknown predictive model")
            if len(np.unique(y[train])) == 1:
                output[name][test] = (y[train].sum() + 1) / (train.sum() + 2)
            else:
                estimator.fit(x[train], y[train])
                output[name][test] = estimator.predict_proba(x[test])[:, 1]
        folds.append({"family": family, "train_families": sorted(set(group[train])), "n": int(test.sum())})
    metrics = {}
    for name, p in output.items():
        p = np.clip(p, 1e-6, 1 - 1e-6)
        loss = -(y * np.log(p) + (1 - y) * np.log1p(-p))
        metrics[name] = {"n": len(y), "brier": float(np.mean((y-p)**2)), "log_loss": float(loss.mean()),
                         "family_brier": {f: float(np.mean((y[group == f]-p[group == f])**2)) for f in sorted(set(group))}}
    return {"folds": folds, "metrics": metrics, "predictions": [
        {"id": k, "cell": b, "family": r["family"], "observed": int(y[i]),
         "probabilities": {name: float(p[i]) for name, p in output.items()}}
        for i, (k, b, r) in enumerate(entries)
    ]}


def read_pinned(path, digest):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError("unqualified input bytes")
    return json.loads(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=Path("contracts/examples/semantic-reconciliation-synthetic-v1.json"))
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--neural-report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--predictive", action="store_true")
    args = parser.parse_args()
    cases = read_pinned(args.fixture, FIXTURE_SHA)["cases"]
    cells, features = controlled(cases)
    held = {b: {k: r for k, r in cell.items() if r["split"] == "test"} for b, cell in cells.items()}
    fields = ("target_in_pool", "complete", "correct", "false_equivalence", "abstained")
    result = {"boundary": "Exposed synthetic development; no new neural inference or scientific admission",
              "fixture_sha256": FIXTURE_SHA, "factors": FACTORS, "case_outcomes": cells,
              "heldout_summary": {b: {f: sum(r[f] for r in cell.values()) for f in fields} for b, cell in held.items()},
              "heldout_resource_counts": {b: {"pool_slots": sum(len(r["pool"]) for r in cell.values()),
                    "new_fragments": sum(len(r["selected"]) for r in cell.values()),
                    "scored_candidates_per_channel": sum(r["scored_candidates_per_channel"] for r in cell.values()),
                    "selected_words": sum(r["selected_words"] for r in cell.values())} for b, cell in held.items()},
              "family_bayesian_bootstrap": {f: paired_bayes(held, FACTORS, f) for f in fields}}
    if args.predictive:
        result["predictive"] = predict_grouped(cells, features)
        result["predictive"]["runtime_versions"] = {k: version(k) for k in ("numpy", "scikit-learn", "xgboost")}
    if args.neural_report:
        neural = read_pinned(args.neural_report, NEURAL_SHA)
        if neural["fixture_sha256"] != FIXTURE_SHA:
            raise ValueError("neural fixture mismatch")
        result["matched_neural_ranking"] = observed_neural_ranking(cases, neural)
        result["matched_coverage"] = matched_coverage(neural)
    if args.ledger:
        ledger = read_pinned(args.ledger, LEDGER_SHA)
        result["full_corpus_worklist"] = coverage_ledger(ledger["rows"])
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
