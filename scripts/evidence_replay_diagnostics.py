"""Text-free retrospective of the v3 synthetic replay; no new inference."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ARMS = ("lexical_rerank", "neural_rerank")
STATES = ("head", "expanded")
REPORT_SHA256 = "7a79c7734a6d202332fa1a65178a1fb4a9b14e83762041418574dd3a7eea2f7d"


def select_new(order, observed, limit):
    """Select unseen stable identities in existing rank order, without filling twice."""
    if type(limit) is not int or limit < 1 or len(set(order)) != len(order):
        raise ValueError("positive integer limit and unique ranking required")
    return [key for key in order if key not in observed][:limit]


def audit(report):
    rows = report["cases"]
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("nonempty unique case inventory required")
    for row in rows:
        pool = row["pool"]
        if len(set(pool)) != len(pool):
            raise ValueError("duplicate pool identity")
        for arm in ARMS:
            order = row[arm]["ranking"]
            if not set(order) <= set(pool) or len(set(order)) != len(order):
                raise ValueError("invalid duplicate or outside-pool ranking")
    incomplete = [row for row in rows if not row["states"]["expanded"]["complete"]]
    blocked = [row["id"] for row in incomplete if row["id"] + ":tail" not in row["pool"]]
    residual = []
    for row in incomplete:
        tail = row["id"] + ":tail"
        residual.append(
            {
                "id": row["id"],
                "in_pool": tail in row["pool"],
                "ranks": {
                    arm: row[arm]["ranking"].index(tail) + 1
                    if tail in row[arm]["ranking"]
                    else None
                    for arm in ARMS
                },
            }
        )
    arms = {}
    for state in STATES:
        arms[state] = {}
        for arm in ARMS:
            results = {}
            for limit in (2, 4, 6):
                gains, novel, complete, repeated = [], 0, 0, 0
                for row in rows:
                    current = row["states"][state]
                    seen = set(current["evidence_ids"])
                    order = row[arm]["ranking"]
                    selected = select_new(order, seen, limit)
                    novel += len(selected)
                    repeated += sum(key in seen for key in order[:limit])
                    recovered = row["id"] + ":tail" in selected
                    complete += int(current["complete"] or recovered)
                    if recovered and not current["complete"]:
                        gains.append(row["id"])
                results[str(limit)] = {
                    "complete_pairs": complete,
                    "gained_ids": sorted(gains),
                    "novel_fragments": novel,
                    "original_redundant_slots": repeated,
                }
            arms[state][arm] = results
    agreement = {}
    for state in (*STATES, "rule_terminal"):
        wrong = {"complete": [], "incomplete": []}
        same = 0
        for row in rows:
            current = row["states"][state]
            prediction = current["predictions"]
            if prediction["minilm"] != prediction["deberta"]:
                continue
            same += 1
            if prediction["minilm"] not in (row["reference"], "abstain"):
                wrong["complete" if current["complete"] else "incomplete"].append(row["id"])
        agreement[state] = {
            "raw_same_label": same,
            "shared_wrong_complete": len(wrong["complete"]),
            "shared_wrong_incomplete": len(wrong["incomplete"]),
            "shared_wrong_ids": wrong,
        }
    return {
        "schema_version": 1,
        "boundary": "Retrospective synthetic fragment coverage only; no new NLI or reranker scoring",
        "pairs": len(rows),
        "expanded_complete": len(rows) - len(incomplete),
        "missing_outside_pool": len(blocked),
        "missing_inside_pool": len(incomplete) - len(blocked),
        "outside_pool_ids": sorted(blocked),
        "residual": residual,
        "arms": arms,
        "agreement": agreement,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.report.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != REPORT_SHA256:
        raise ValueError("unqualified historical report bytes")
    result = audit(json.loads(raw))
    result["report_sha256"] = digest
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
