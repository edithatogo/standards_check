"""Opt-in replay of retained semantic decisions at observed evidence states."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import zipfile
from itertools import product
from pathlib import Path

from .evidence_action_replay import (
    FIXTURE_SHA,
    REVIEW_CAP,
    build_replay,
    decision,
    observe,
    predict,
    ridge,
)
from .lfm_development import metrics, paired
from .task_framing import compile_witness

ARTIFACT_SHA = "d796bdbc6a84830a7e3c702fbc6d08ce9fe9430175db5a4610b0ad0dfa2c2ae9"
MODELS = ("minilm", "deberta")
LABELS = {"equivalent", "narrower", "broader", "contradictory", "indeterminate", "abstain"}
BUDGET = 4


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def bind_predictions(cases, records):
    """Match opaque identity, source/target bytes and family; ignore receipt gold labels."""
    by_id = {r["id"]: r for r in records}
    if len(by_id) != len(records) or len(by_id) != len(cases):
        raise ValueError("semantic receipt coverage mismatch")
    bound = {}
    for case in cases:
        key = digest(json.dumps([case["id"], case["source"], case["candidate"]]))
        row = by_id.get(key, {})
        if (
            row.get("source_sha256") != digest(case["source"])
            or row.get("candidate_sha256") != digest(case["candidate"])
            or row.get("family") != case["family"]
            or row.get("split") != case["split"]
        ):
            raise ValueError("semantic receipt identity mismatch")
        pred = {model: row["predictions"].get(model) for model in MODELS}
        if not set(pred.values()) <= LABELS:
            raise ValueError("invalid cached prediction")
        bound[case["id"]] = (row["candidate_sha256"], pred)
    return bound


def visible_candidate(row):
    key = row["id"]
    evidence = row["evidence"]
    if key + ":parent" in evidence:
        return evidence[key + ":parent"]
    if all(key + suffix in evidence for suffix in (":head", ":tail")):
        return " ".join(evidence[key + suffix] for suffix in (":head", ":tail"))
    return None


def score(label, reference):
    if label == reference:
        return 1
    if label == "abstain":
        return 0
    return -4 if label == "equivalent" else -1


def replay(cases, cache):
    """Fixed first expansion; compare second-stage selection, then actual cached outcomes."""
    rows = build_replay(cases)
    by_state = {(r["id"], tuple(r["history"])): r for r in rows}
    stages = [r for r in rows if r["history"] == ["expand"]]
    states = {}
    for row in stages:
        key = row["id"]
        state = observe(row)
        second = "parent" if state[1] else "deep_rerank"
        after = by_state[(key, ("expand", second))]
        visible = visible_candidate(row)
        # Gate the action on exact currently available text, not the stored prediction.
        eligible = visible is not None and digest(visible) == cache[key][0]
        states[key] = {
            "features": state,
            "initial": decision(state),
            "second": second,
            "baseline": decision(observe(after)),
            "eligible": eligible,
            "split": row["split"],
            "reference": row["reference"],
        }
    train = [key for key, s in states.items() if s["split"] == "dev" and s["eligible"]]
    test = [key for key, s in states.items() if s["split"] == "test"]
    eligible = [key for key in test if states[key]["eligible"]]
    if not train or not test or len(eligible) < BUDGET:
        raise ValueError("insufficient matched-budget eligible cases")
    selections = {"search_again": (None, set())}
    for model in MODELS:
        # The learner uses only development-family observed action rewards.
        x = [states[key]["features"] for key in train]
        y = [
            score(cache[key][1][model], states[key]["reference"])
            - score(states[key]["baseline"], states[key]["reference"])
            for key in train
        ]
        weights = ridge(x, y)
        priorities = {
            "fixed": lambda key: (0, digest(key)),
            "deficit": lambda key: (states[key]["initial"] != "abstain", digest(key)),
            "learned": lambda key, weights=weights: (
                -float(predict(weights, states[key]["features"])),
                digest(key),
            ),
        }
        for name, priority in priorities.items():
            selections[f"{name}_{model}"] = (
                model,
                set(sorted(eligible, key=priority)[:BUDGET]),
            )
        selections[f"early_{model}"] = (
            model,
            {key for key in eligible if states[key]["initial"] == "abstain"},
        )
    details = {}
    for name, (model, selected) in selections.items():
        details[name] = {}
        for key in test:
            state = states[key]
            if key in selected:
                action, label = model, cache[key][1][model]
            elif name.startswith("early_") and state["initial"] != "abstain":
                action, label = "stop", state["initial"]
            else:
                action, label = state["second"], state["baseline"]
            details[name][key] = {
                "action": action,
                "prediction": label,
                "eligible": state["eligible"],
                "initial": state["initial"],
            }
    quota = min(
        REVIEW_CAP,
        *(sum(r["prediction"] == "abstain" for r in arm.values()) for arm in details.values()),
    )
    reference = {key: states[key]["reference"] for key in test}
    incumbent = {key: row["prediction"] for key, row in details["search_again"].items()}
    arms = {}
    for name, arm in details.items():
        pred = {key: row["prediction"] for key, row in arm.items()}
        referrals = sorted((key for key in test if pred[key] == "abstain"), key=digest)[:quota]
        for key, row in arm.items():
            row.update(referral=key in referrals, review_outcome=None)
        arms[name] = {
            **metrics(reference, pred),
            "paired_vs_search": paired(reference, incumbent, pred),
            "retrieval_calls": len(test) + sum(r["action"] in ("parent", "deep_rerank") for r in arm.values()),
            "semantic_calls": sum(r["action"] in MODELS for r in arm.values()),
            "stops": sum(r["action"] == "stop" for r in arm.values()),
            "referrals": quota,
            "review_resolved": 0,
            "missed_matches": sum(reference[k] == "equivalent" and pred[k] != "equivalent" for k in test),
            "gained_ids": sorted(k for k in test if pred[k] == reference[k] != incumbent[k]),
            "lost_ids": sorted(k for k in test if incumbent[k] == reference[k] != pred[k]),
        }
    return {
        "claim_boundary": "Historically exposed synthetic development; cached full-pair inference only",
        "training_eligible": len(train),
        "test_eligible": len(eligible),
        "matched_semantic_budget": BUDGET,
        "arms": arms,
        "details": details,
        "reference": reference,
    }


def formal_controls():
    """Separate finite truth-table controls; no neural predictions for these inputs."""
    forms = (
        ("implication", "alpha implies beta", "beta implies alpha", lambda a, b: not a or b, lambda a, b: not b or a),
        ("opposite_conjunctions", "alpha is true and beta is false", "beta is true and alpha is false", lambda a, b: a and not b, lambda a, b: b and not a),
        ("opposite_disjunctions", "alpha is true or beta is false", "beta is true or alpha is false", lambda a, b: a or not b, lambda a, b: b or not a),
        ("commutative_conjunction", "alpha is true and beta is true", "beta is true and alpha is true", lambda a, b: a and b, lambda a, b: b and a),
    )
    results = []
    for key, a_text, b_text, a_rule, b_rule in forms:
        worlds = list(product((False, True), repeat=2))
        a_set = {i for i, world in enumerate(worlds) if a_rule(*world)}
        b_set = {i for i, world in enumerate(worlds) if b_rule(*world)}
        reference = compile_witness(*( "yes" if x else "no" for x in (a_set - b_set, b_set - a_set, a_set & b_set)))
        prefix = "A report complies if and only if "
        source, candidate = prefix + a_text + ".", prefix + b_text + "."
        state = observe({"id": key, "source": source, "evidence": {key + ":parent": candidate}, "parent_link": True})
        results.append({"id": key, "source": source, "candidate": candidate, "a_worlds": sorted(a_set), "b_worlds": sorted(b_set), "reference": reference, "lexical": decision(state), "semantic": None})
    return results


def load(fixture, artifact):
    raw = fixture.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SHA:
        raise ValueError("fixture hash mismatch")
    if hashlib.sha256(artifact.read_bytes()).hexdigest() != ARTIFACT_SHA:
        raise ValueError("semantic artifact hash mismatch")
    cases = json.loads(raw)["cases"]
    with zipfile.ZipFile(artifact) as archive:
        report = json.loads(archive.read("report.json"))
    if (
        report["fixture_bytes_sha256"] != FIXTURE_SHA
        or report["relation_orientation"] != "legacy-B-relative-to-A"
    ):
        raise ValueError("semantic receipt protocol mismatch")
    return cases, bind_predictions(cases, report["records"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture", type=Path, default=Path("contracts/examples/semantic-reconciliation-synthetic-v1.json")
    )
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    cases, cache = load(args.fixture, args.artifact)
    report = replay(cases, cache)
    report.update(artifact_sha256=ARTIFACT_SHA, fixture_sha256=FIXTURE_SHA, formal_controls=formal_controls(), seconds=time.perf_counter() - started)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
