"""Bounded offline policy comparison on observed synthetic acquisition transitions."""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import permutations
from pathlib import Path
from statistics import mean

from .evidence_action_replay import (
    ACTIONS,
    FIXTURE_SHA,
    REVIEW_CAP,
    build_replay,
    decision,
    observe,
    predict,
    ridge,
)
from .evidence_deficit_replay import score, visible_candidate
from .evidence_verification import formal_verdict, gate

COST = 0.1


def terminal(row):
    state = observe(row)
    raw = decision(state)
    candidate = visible_candidate(row)
    proof = formal_verdict(row["source"], candidate or "", candidate is not None)
    return raw, gate(raw, bool(state[0]), proof), bool(state[0])


def utility(row):
    _, gated, complete = terminal(row)
    return score(gated, row["reference"]) + 0.25 * complete


def feasible(row, cap):
    if len(row["history"]) >= cap:
        return []
    return [a for a in ACTIONS if a not in row["history"] and (a != "parent" or row["parent_link"])]


def features(row):
    return (*observe(row), *(int(a in row["history"]) for a in ACTIONS))


def child(row, action, lookup):
    history = (*row["history"], action)
    key = (row["id"], history)
    if (
        action not in row["transitions"]
        or row["transitions"][action]["next"] != list(history)
        or key not in lookup
    ):
        raise ValueError("missing observed action transition")
    return lookup[key]


def fit(rows, mode, cap, cost, adaptive):
    """One-step value or backward fitted Q on training-family observations only."""
    if mode not in ("bandit", "fitted_q") or cap not in (1, 2):
        raise ValueError("unsupported policy mode or horizon")
    dev = [r for r in rows if r["split"] == "dev"]
    lookup = {(r["id"], tuple(r["history"])): r for r in dev}
    weights = {}
    for depth in reversed(range(cap)):
        samples = {a: [] for a in ACTIONS}
        for row in dev:
            if len(row["history"]) != depth or (
                "parent" in row["history"] and not row["parent_link"]
            ):
                continue
            for a in feasible(row, cap):
                after = child(row, a, lookup)
                target = utility(after) - utility(row) - cost
                if mode == "fitted_q" and (remaining := feasible(after, cap)):
                    continuation = max(
                        float(predict(weights[depth + 1][b], features(after))) for b in remaining
                    )
                    target += max(0.0, continuation) if adaptive else continuation
                samples[a].append((features(row), target))
        if not all(samples.values()):
            raise ValueError("unsupported training action")
        weights[depth] = {a: ridge(*zip(*data, strict=True)) for a, data in samples.items()}
    return weights


def choose(row, weights, cap, adaptive):
    actions = feasible(row, cap)
    if not actions:
        return None
    values = weights[len(row["history"])]
    state = features(row)
    scores = {a: float(predict(values[a], state)) for a in actions}
    action = max(actions, key=scores.__getitem__)
    if adaptive and scores[action] <= 0:
        return None
    return action


def follow(row, lookup, cap, selector):
    trace = []
    while feasible(row, cap):
        action = selector(row)
        if action is None:
            break
        if action not in feasible(row, cap):
            raise ValueError("policy selected unavailable action")
        next_row = child(row, action, lookup)
        edge = row["transitions"][action]
        trace.append(
            {
                "action": action,
                "new_fragments": len(edge["new_evidence"]),
                "new_words": sum(len(v.split()) for v in edge["new_evidence"].values()),
                "reranks": edge["reranks"],
                "acquisition_seconds": edge["acquisition_seconds"],
            }
        )
        row = next_row
    return row, trace


def ordered(row, order, cap, adaptive):
    if adaptive and observe(row)[0]:
        return None
    return next((a for a in order if a in feasible(row, cap)), None)


def hindsight(initial, lookup, cap, adaptive):
    """Observed-path upper bound only; never train or select a deployable policy with it."""
    outcomes = []
    for length in range(0 if adaptive else cap, cap + 1):
        for order in permutations(ACTIONS):
            end, trace = follow(
                initial,
                lookup,
                length,
                lambda state, order=order, length=length: ordered(state, order, length, False),
            )
            if len(trace) == length:
                outcomes.append((utility(end) - COST * length, end, trace))
    return max(outcomes, key=lambda outcome: (outcome[0], -len(outcome[2])))


def policy_study(rows, *, compare_parent_first=False):
    lookup = {(r["id"], tuple(r["history"])): r for r in rows}
    if len(lookup) != len(rows):
        raise ValueError("duplicate replay state")
    dev, test = ([r for r in rows if r["split"] == s and not r["history"]] for s in ("dev", "test"))
    if not dev or not test or {r["family"] for r in dev} & {r["family"] for r in test}:
        raise ValueError("family-disjoint policy study required")
    roots = {r["id"]: r for r in (*dev, *test)}
    for row in rows:
        root = roots.get(row["id"])
        if root is None or any(
            row[k] != root[k] for k in ("split", "family", "reference", "source", "parent_link")
        ):
            raise ValueError("replay identity mismatch")
    comparisons = {}
    ceilings = {}
    fixed_orders = {}
    for cap, adaptive, name in (
        (1, False, "exact_one"),
        (2, False, "exact_two"),
        (2, True, "adaptive_two"),
    ):

        def fixed_value(order, cap=cap, adaptive=adaptive):
            return mean(
                utility(end) - COST * len(trace)
                for end, trace in (
                    follow(r, lookup, cap, lambda state: ordered(state, order, cap, adaptive))
                    for r in dev
                )
            )

        best = max(permutations(ACTIONS), key=fixed_value)
        fixed_orders[name] = list(best)
        arms = {}
        orders = {"rule": ACTIONS, "best_fixed_dev": best}
        if compare_parent_first:
            orders["parent_first"] = ("parent", "expand", "deep_rerank")
        for mode in (*orders, "bandit", "fitted_q"):
            weights = (
                fit(rows, mode, cap, COST, adaptive) if mode in ("bandit", "fitted_q") else None
            )

            def select(
                state, weights=weights, order=orders.get(mode), cap=cap, adaptive=adaptive
            ):
                if weights is not None:
                    return choose(state, weights, cap, adaptive)
                return ordered(state, order, cap, adaptive)

            cases = []
            for initial in test:
                end, trace = follow(initial, lookup, cap, select)
                raw, gated, complete = terminal(end)
                cases.append(
                    {
                        "id": end["id"],
                        "family": end["family"],
                        "reference": end["reference"],
                        "history": end["history"],
                        "evidence_ids": sorted(end["evidence"]),
                        "raw_prediction": raw,
                        "gated_prediction": gated,
                        "complete": complete,
                        "reward": utility(end) - COST * len(trace),
                        "trace": trace,
                    }
                )
            arms[mode] = {"cases": cases}
        quota = min(
            REVIEW_CAP,
            *(
                sum(r["gated_prediction"] == "abstain" for r in arm["cases"])
                for arm in arms.values()
            ),
        )
        for arm in arms.values():
            cases = arm["cases"]
            referrals = set(
                sorted(r["id"] for r in cases if r["gated_prediction"] == "abstain")[:quota]
            )
            for row in cases:
                row.update(referral=row["id"] in referrals, review_outcome=None)
            arm.update(
                complete=sum(r["complete"] for r in cases),
                raw_correct=sum(r["raw_prediction"] == r["reference"] for r in cases),
                gated_correct=sum(r["gated_prediction"] == r["reference"] for r in cases),
                raw_false_equivalence=sum(
                    r["raw_prediction"] == "equivalent" and r["reference"] != "equivalent"
                    for r in cases
                ),
                gated_false_equivalence=sum(
                    r["gated_prediction"] == "equivalent" and r["reference"] != "equivalent"
                    for r in cases
                ),
                missed_equivalence=sum(
                    r["reference"] == "equivalent" and r["gated_prediction"] != "equivalent"
                    for r in cases
                ),
                abstained=sum(r["gated_prediction"] == "abstain" for r in cases),
                calls=sum(len(r["trace"]) for r in cases),
                reranks=sum(e["reranks"] for r in cases for e in r["trace"]),
                new_words=sum(e["new_words"] for r in cases for e in r["trace"]),
                reward=sum(r["reward"] for r in cases),
                referrals=quota,
                review_resolved=0,
            )
        comparisons[name] = arms
        oracle = [hindsight(r, lookup, cap, adaptive) for r in test]
        ceilings[name] = {
            "uses_heldout_labels": True,
            "reward": sum(value for value, _, _ in oracle),
            "calls": sum(len(trace) for _, _, trace in oracle),
            "complete": sum(terminal(end)[2] for _, end, _ in oracle),
            "gated_correct": sum(terminal(end)[1] == end["reference"] for _, end, _ in oracle),
        }
        for arm in arms.values():
            arm["hindsight_regret"] = ceilings[name]["reward"] - arm["reward"]
    return {
        "boundary": "Exposed synthetic development, no semantic admission or live exploration",
        "train_families": sorted({r["family"] for r in dev}),
        "test_families": sorted({r["family"] for r in test}),
        "reward": "gated correct +1; abstain 0; wrong -1; false equivalence -4; complete +0.25; each call -0.1",
        "fixed_orders": fixed_orders,
        "comparisons": comparisons,
        "hindsight_ceiling": ceilings,
        "admission": "advisory_only",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("contracts/examples/semantic-reconciliation-synthetic-v1.json"),
    )
    parser.add_argument("--compare-parent-first", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.fixture.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SHA:
        raise ValueError("unqualified fixture bytes")
    result = policy_study(
        build_replay(json.loads(raw)["cases"]), compare_parent_first=args.compare_parent_first
    )
    result["fixture_sha256"] = FIXTURE_SHA
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
