"""Opt-in synthetic evidence-action experiment; no semantic admission authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np

from .blind_adjudication import classify_nli
from .costing_retrieval import lexical_rankings, parse_reranker_results, rank
from .lexical_text import normalise, term_counts
from .lfm_development import metrics, paired
from .semantic_benchmark import LABELS, validate_cases
from .task_framing import strict_agreement

ACTIONS = ("expand", "parent", "deep_rerank")
HORIZON = 2
REVIEW_CAP = 6
FEATURES = ("complete", "parent_link", "word_jaccard", "char_jaccard", "source_subset",
            "candidate_subset", "negation_difference", "number_difference", "exact_text")
STOP = {"the", "a", "an", "of", "in", "is", "was", "were", "and", "that", "for", "to"}
NEG = {"not", "no", "never", "excludes", "without"}
NUM = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"}
FIXTURE_SHA = "55d1dd465c413a4d64890974de42a9719c63b7a711f8172eb70b35160b28c3d0"


def tokens(text):
    return set(normalise(text).split()) - STOP


def jaccard(a, b):
    return len(a & b) / max(1, len(a | b))


def observe(row):
    """Only visible source, retrieved target fragments, and public link metadata."""
    key = row["id"]
    evidence = row["evidence"]
    head, tail, parent = (evidence.get(f"{key}:{part}") for part in ("head", "tail", "parent"))
    target = parent if parent is not None else " ".join(x for x in (head, tail) if x is not None)
    a, b = tokens(row["source"]), tokens(target)
    def nums(ts):
        return {t for t in ts if t.isdecimal() or t in NUM}

    return (int(parent is not None or (head is not None and tail is not None)),
            int(row["parent_link"]), jaccard(a, b),
            jaccard(set(term_counts(row["source"], "char")), set(term_counts(target, "char"))),
            int(bool(a) and a <= b), int(bool(b) and b <= a), int((a & NEG) != (b & NEG)),
            int(nums(a) != nums(b)), int(normalise(row["source"]) == normalise(target)))


def decision(state):
    """Frozen lexical candidate rule, never an NLI probability or formal witness."""
    complete, _, word, char, a_sub, b_sub, neg, num, exact = state
    if complete < 0.5:
        return "abstain"
    if exact >= 0.5:
        return "equivalent"
    if (neg >= 0.5 or num >= 0.5) and word >= 0.33:
        return "contradictory"
    if a_sub >= 0.5 and b_sub < 0.5:
        return "narrower"
    if b_sub >= 0.5 and a_sub < 0.5:
        return "broader"
    return strict_agreement(["equivalent" if word >= 0.8 else "indeterminate" if word < 0.3 else "abstain",
                             "equivalent" if char >= 0.8 else "indeterminate" if char < 0.3 else "abstain"])


def split_document(row):
    words = row["candidate"].split()
    if len(words) < 2:
        raise ValueError("synthetic layout needs two nonempty fragments")
    number = int(hashlib.sha256(row["id"].encode()).hexdigest()[:8], 16)
    pivot = min(len(words) - 1, 3 + number % 3)
    return " ".join(words[:pivot]), " ".join(words[pivot:]), number % 3 != 0


def available(history):
    return [action for action in ACTIONS if action not in history] if len(history) < HORIZON else []


def reference(row):
    return classify_nli(*(tuple(float(label == row[d]) for label in LABELS)
                          for d in ("forward", "reverse")))


def acquire(row, action, corpus, parents, pool):
    """Execute an actual local search/lookup or fixed-pool lexical reranker."""
    seen = row["evidence"]
    queried = row["source"]
    if action == "parent":
        parent_id = row["id"] + ":parent"
        found = {parent_id: parents[parent_id]} if row["parent_link"] else {}
        return found, [], 0, queried
    if action == "expand":
        missing = sorted(tokens(queried) - tokens(" ".join(v for k, v in seen.items() if k.startswith(row["id"] + ":"))))
        queried += " " + " ".join(missing * 2)
        ranking = lexical_rankings({"q": queried}, {k: v for k, v in corpus.items() if k not in seen}, "word")["q"]
    else:
        order = lexical_rankings({"q": queried}, {k: corpus[k] for k in pool}, "char")["q"]
        scores = {k: float(len(order) - i) for i, k in enumerate(order)}
        bound = parse_reranker_results(pool, [{"index": i, "relevance_score": scores.get(k, 0.0)}
                                               for i, k in enumerate(pool)])
        ranking = rank(bound, positive=True)
    return {k: corpus[k] for k in ranking if k not in seen and k in ranking[:2]}, ranking, int(action == "deep_rerank"), queried


def build_replay(cases):
    validate_cases(cases)
    layouts = {r["id"]: split_document(r) for r in cases}
    rows = []
    for case in cases:
        key = case["id"]
        corpus = {f"{r['id']}:{part}": layouts[r["id"]][i]
                  for r in cases if r["family"] == case["family"]
                  for i, part in enumerate(("head", "tail"))}
        parents = {key + ":parent": case["candidate"]} if layouts[key][2] else {}
        pool = lexical_rankings({"q": case["source"]}, corpus, "word")["q"][:6]
        gold = reference(case)

        def visit(history, evidence, *, key=key, case=case, pool=pool, gold=gold, corpus=corpus, parents=parents):
            row = {"id": key, "family": case["family"], "split": case["split"], "source": case["source"],
                   "history": history, "evidence": evidence, "parent_link": layouts[key][2],
                   "pool": pool, "reference": gold, "transitions": {}}
            rows.append(row)
            before = decision(observe(row))
            for action in available(history):
                action_start = time.perf_counter()
                found, ranking, reranks, query = acquire(row, action, corpus, parents, pool)
                elapsed = time.perf_counter() - action_start
                child = visit([*history, action], {**evidence, **found})
                after = decision(observe(child))
                row["transitions"][action] = {"next": child["history"], "new_evidence": found, "ranking": ranking,
                                              "query": query, "retrieval_calls": 1, "reranks": reranks,
                                              "acquisition_seconds": elapsed,
                                              "resolved": before != gold and after == gold}
            for action in ("abstain", "review"):
                row["transitions"][action] = {"retrieval_calls": 0, "reranks": 0, "referrals": int(action == "review"),
                                              "review_outcome": None, "resolved": False}
            return row

        visit([], {key + ":head": corpus[key + ":head"]})
    return rows


def ridge(x, y):
    design = np.column_stack((np.ones(len(x)), np.asarray(x)))
    return np.linalg.solve(design.T @ design + np.eye(design.shape[1]), design.T @ np.asarray(y))


def predict(weights, state):
    return np.asarray([1, *state]) @ weights


def forecast(weights, state, action):
    return tuple(np.clip(predict(weights[action], state), 0, 1).tolist())


def utility(state):
    return 2 * state[0] + int(decision(state) != "abstain")


def reward(state, gold):
    result = decision(state)
    if result == gold:
        return 1.0
    if result == "abstain":
        return 0.0
    return -4.0 if result == "equivalent" else -1.0


def fit_critic(initial, lookup, weights, imagined):
    """Two-horizon fitted Q critic; greedy actor, no full Dreamer architecture."""
    samples = {1: {a: [] for a in ACTIONS}, 2: {a: [] for a in ACTIONS}}
    branches = []
    for row in initial:
        state = observe(row)
        for action in ACTIONS:
            child = lookup[(row["id"], (action,))]
            middle = forecast(weights, state, action) if imagined else observe(child)
            branches.append((row, state, action, middle))
            for second in available([action]):
                terminal = forecast(weights, middle, second) if imagined else observe(lookup[(row["id"], (action, second))])
                samples[1][second].append((middle, reward(terminal, row["reference"])))
    one = {a: ridge(*zip(*points, strict=True)) for a, points in samples[1].items()}
    for _, state, action, middle in branches:
        samples[2][action].append((state, max(float(predict(one[b], middle)) for b in available([action]))))
    two = {a: ridge(*zip(*points, strict=True)) for a, points in samples[2].items()}
    return {1: one, 2: two}


def forecast_evaluation(test, lookup, weights, means):
    outcomes = []
    for row in test:
        state = observe(row)
        for action in available(row["history"]):
            actual = observe(lookup[(row["id"], (*row["history"], action))])
            outcomes.append((actual, forecast(weights, state, action), state, means[action]))
    values = np.asarray(outcomes)
    return {"n": len(outcomes), "feature_names": FEATURES,
            "mae": {name: np.abs(values[:, 0] - values[:, i]).mean(axis=0).tolist()
                    for i, name in enumerate(("learned", "persistence", "action_mean"), 1)},
            "complete_accuracy": float(np.mean((values[:, 1, 0] >= 0.5) == values[:, 0, 0]))}


def experiment(cases, replay=None):
    started = time.perf_counter()
    rows = build_replay(cases) if replay is None else replay
    lookup = {(r["id"], tuple(r["history"])): r for r in rows}
    dev, test = ([r for r in rows if r["split"] == split] for split in ("dev", "test"))
    training = {a: [(observe(r), observe(lookup[(r["id"], (*r["history"], a))]))
                    for r in dev if a in available(r["history"])] for a in ACTIONS}
    weights = {a: ridge(*zip(*samples, strict=True)) for a, samples in training.items()}
    means = {a: np.mean([y for _, y in samples], axis=0) for a, samples in training.items()}
    critics = {name: fit_critic([r for r in dev if not r["history"]], lookup, weights, imagined)
               for name, imagined in (("imagined_critic", True), ("observed_critic", False))}
    predictions, details, runtime = {}, {}, {}
    initial = [r for r in test if not r["history"]]
    for arm in ("rule", "forecast", *critics):
        arm_started = time.perf_counter()
        details[arm] = {}
        predictions[arm] = {}
        for row in initial:
            trace = []
            # Exact acquisition budget on the common initially weak cohort; no early stopping.
            weak = decision(observe(row)) == "abstain"
            while weak and (choices := available(row["history"])):
                state = observe(row)
                if arm == "rule":
                    action = "expand" if "expand" in choices else "parent" if state[1] and "parent" in choices else choices[-1]
                elif arm == "forecast":
                    action = max(choices, key=lambda a: utility(forecast(weights, state, a)))
                else:
                    action = max(choices, key=lambda a: float(predict(critics[arm][HORIZON-len(row["history"])][a], state)))
                edge = row["transitions"][action]
                trace.append({"action": action, **edge})
                row = lookup[(row["id"], tuple(edge["next"]))]
            predictions[arm][row["id"]] = decision(observe(row))
            details[arm][row["id"]] = {"trace": trace, "state": observe(row)}
        runtime[arm] = time.perf_counter() - arm_started
    # Match realised referral workload without using labels; excess unresolved cases abstain.
    quota = min(REVIEW_CAP, *(sum(v == "abstain" for v in p.values()) for p in predictions.values()))
    gold = {r["id"]: r["reference"] for r in initial}
    arms = {}
    for arm, pred in predictions.items():
        review = sorted((k for k, v in pred.items() if v == "abstain"), key=lambda k: (details[arm][k]["state"][0], k))[:quota]
        for key, d in details[arm].items():
            d.update(prediction=pred[key], referral=key in review, review_outcome=None, reference=gold[key])
        traces = [edge for d in details[arm].values() for edge in d["trace"]]
        arms[arm] = {**metrics(gold, pred), "referrals": len(review), "review_resolved": 0,
                     "pure_abstentions": sum(v == "abstain" for v in pred.values()) - len(review),
                     "missed_matches": sum(v == "equivalent" and pred[k] != v for k, v in gold.items()),
                     "retrieval_calls": sum(e["retrieval_calls"] for e in traces), "reranks": sum(e["reranks"] for e in traces),
                     "new_fragments": sum(len(e["new_evidence"]) for e in traces), "policy_seconds": runtime[arm],
                     "recorded_acquisition_seconds": sum(e["acquisition_seconds"] for e in traces),
                     "paired_vs_rule": paired(gold, predictions["rule"], pred),
                     "gained_ids": sorted(k for k in gold if pred[k] == gold[k] != predictions["rule"][k]),
                     "lost_ids": sorted(k for k in gold if predictions["rule"][k] == gold[k] != pred[k])}
    return {"claim_boundary": "Synthetic development only; no independently adjudicated review or admission",
            "primary": "false equivalences at matched retrieval calls and referral workload; correctness guardrail",
            "family_split": {s: sorted({r["family"] for r in rows if r["split"] == s}) for s in ("dev", "test")},
            "states": len(rows), "training_transitions": sum(map(len, training.values())), "review_cap": REVIEW_CAP,
            "forecast": forecast_evaluation(test, lookup, weights, means), "arms": arms, "details": details,
            "seconds": time.perf_counter() - started, "python": platform.python_version(), "numpy": np.__version__}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=Path("contracts/examples/semantic-reconciliation-synthetic-v1.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.fixture.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SHA:
        raise ValueError("only the pinned original synthetic fixture is permitted")
    cases = json.loads(raw)["cases"]
    started = time.perf_counter()
    replay = build_replay(cases)
    report = experiment(cases, replay)
    report.update(fixture_sha256=FIXTURE_SHA, replay_seconds=time.perf_counter() - started - report["seconds"])
    args.output.write_text(json.dumps({"report": report, "replay": replay}, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
