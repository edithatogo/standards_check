"""Order-balanced acquisition and observed semantic/proof factorials, advisory only."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from itertools import combinations, permutations, product
from pathlib import Path
from statistics import mean

from .evidence_action_replay import (
    ACTIONS,
    FIXTURE_SHA,
    acquire,
    build_replay,
    decision,
    observe,
    split_document,
)

NEURAL_SHA = "7a79c7734a6d202332fa1a65178a1fb4a9b14e83762041418574dd3a7eea2f7d"
ENDPOINTS = ("complete", "correct", "false_equivalence", "missed_equivalence", "abstained")
FIELDS = (*ENDPOINTS, "calls", "reranks", "nli_calls")


def design():
    return [
        ("".join(map(str, bits)), tuple(a for a, bit in zip(ACTIONS, bits, strict=True) if bit))
        for bits in product((0, 1), repeat=3)
    ]


def outcome(row, prediction, complete, order, calls=0, reranks=0, nli_calls=0):
    ref = row["reference"]
    return {
        "family": row["family"],
        "reference": ref,
        "prediction": prediction,
        "order": list(order),
        "complete": int(complete),
        "correct": int(prediction == ref),
        "false_equivalence": int(prediction == "equivalent" and ref != "equivalent"),
        "missed_equivalence": int(prediction != "equivalent" and ref == "equivalent"),
        "abstained": int(prediction == "abstain"),
        "calls": calls,
        "reranks": reranks,
        "nli_calls": nli_calls,
    }


def acquisition_cells(cases):
    """Reexecute the incumbent to depth two, then execute every third acquisition."""
    replay = build_replay(cases)
    by_state = {(r["id"], tuple(r["history"])): r for r in replay}
    layouts = {row["id"]: split_document(row) for row in cases}
    case_by_id = {row["id"]: row for row in cases}
    cells = {key: {} for key, _ in design()}
    for initial in replay:
        if initial["split"] != "test" or initial["history"]:
            continue
        key = initial["id"]
        corpus = {
            f"{r['id']}:{part}": layouts[r["id"]][i]
            for r in cases
            if r["family"] == initial["family"]
            for i, part in enumerate(("head", "tail"))
        }
        parents = {key + ":parent": case_by_id[key]["candidate"]} if layouts[key][2] else {}
        for bits, active in design():
            rows = []
            for order in permutations(active):
                row = by_state[(key, order[:2])]
                costs = [
                    by_state[(key, order[:i])]["transitions"][a] for i, a in enumerate(order[:2])
                ]
                seconds = sum(c["acquisition_seconds"] for c in costs)
                if len(order) == 3:
                    # No reference or future outcome reaches the acquisition function.
                    visible = {k: row[k] for k in ("id", "source", "evidence", "parent_link", "pool")}
                    started = time.perf_counter()
                    found, _, _, _ = acquire(visible, order[-1], corpus, parents, initial["pool"])
                    seconds += time.perf_counter() - started
                    row = {**row, "evidence": {**row["evidence"], **found}}
                state = observe(row)
                rows.append(
                    {
                        **outcome(
                            row, decision(state), bool(state[0]), order, len(order),
                            int("deep_rerank" in order),
                        ),
                        "evidence_ids": sorted(row["evidence"]),
                        "acquisition_seconds": seconds,
                    }
                )
            cells[bits][key] = rows
    return cells


def neural_cells(report):
    """Cross observed head/terminal evidence, lexical/NLI, proof required/not required."""
    rows = report["cases"]
    if not rows or len({r["id"] for r in rows}) != len(rows):
        raise ValueError("nonempty unique semantic cases required")
    result = {}
    for a, n, p in product((0, 1), repeat=3):
        if n:
            label = "proof_required" if p else "strict_nli"
        else:
            label = "lexical_verified" if p else "lexical"
        cell = {}
        for row in rows:
            state = row["states"]["rule_terminal" if a else "head"]
            # The original rule's second action retrieves a parent when available, else reranks.
            reranks = int(bool(a) and row["id"] + ":parent" not in state["evidence_ids"])
            cell[row["id"]] = [
                outcome(row, state["predictions"][label], state["complete"], (), 2 * a, reranks, 4 * n)
            ]
        result[f"{a}{n}{p}"] = cell
    return result


def summarize(cell):
    """Case-weighted sums of order-averaged outcomes; no permutation pseudo-replication."""
    return {
        field: sum(mean(row.get(field, 0) for row in outcomes) for outcomes in cell.values())
        for field in FIELDS
    }


def contrasts(cells, names, field):
    """Main effects and average differences of differences, in proportion units."""
    keys = ["".join(map(str, bits)) for bits in product((0, 1), repeat=len(names))]
    if set(keys) != set(cells) or not cells[keys[0]]:
        raise ValueError("incomplete factorial design")
    ids = set(cells[keys[0]])
    if any(set(cell) != ids or any(not rows for rows in cell.values()) for cell in cells.values()):
        raise ValueError("unpaired factorial cases")
    result = {}
    for size in range(1, len(names) + 1):
        for axes in combinations(range(len(names)), size):
            values = []
            for case in sorted(ids):
                values.append(
                    sum(
                        (-1) ** sum(key[i] == "0" for i in axes)
                        * mean(r[field] for r in cells[key][case])
                        for key in keys
                    )
                    / 2 ** (len(names) - size)
                )
            result[":".join(names[i] for i in axes)] = mean(values)
    return result


def order_summaries(cell):
    orders = {tuple(row["order"]) for row in next(iter(cell.values()))}
    if any({tuple(row["order"]) for row in rows} != orders for rows in cell.values()):
        raise ValueError("unpaired order inventory")
    return {
        " -> ".join(order) or "none": summarize(
            {key: [row for row in rows if tuple(row["order"]) == order] for key, rows in cell.items()}
        )
        for order in sorted(orders)
    }


def analyze(cells, names):
    families = sorted({rows[0]["family"] for rows in cells["000"].values()})
    strata = {
        family: {
            key: {case: rows for case, rows in cell.items() if rows[0]["family"] == family}
            for key, cell in cells.items()
        }
        for family in families
    }
    return {
        "factors": names,
        "n": len(cells["000"]),
        "cells": {key: summarize(cell) for key, cell in cells.items()},
        "orders": {key: order_summaries(cell) for key, cell in cells.items()},
        "contrasts": {field: contrasts(cells, names, field) for field in ENDPOINTS},
        "by_family": {
            family: {field: contrasts(group, names, field) for field in ENDPOINTS}
            for family, group in strata.items()
        },
        "case_outcomes": cells,
    }


def read_pinned(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("unqualified input bytes")
    return json.loads(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture", type=Path, default=Path("contracts/examples/semantic-reconciliation-synthetic-v1.json")
    )
    parser.add_argument("--neural-report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = read_pinned(args.fixture, FIXTURE_SHA)["cases"]
    result = {
        "schema_version": 1,
        "fixture_sha256": FIXTURE_SHA,
        "boundary": "Synthetic development; complete factorial cells, no independent references or admission",
        "acquisition": analyze(acquisition_cells(cases), list(ACTIONS)),
        "review_resolved": 0,
    }
    if args.neural_report:
        report = read_pinned(args.neural_report, NEURAL_SHA)
        if report["fixture_sha256"] != FIXTURE_SHA:
            raise ValueError("neural fixture mismatch")
        semantic = neural_cells(report)
        if {
            key: (rows[0]["family"], rows[0]["reference"]) for key, rows in semantic["000"].items()
        } != {
            key: (rows[0]["family"], rows[0]["reference"])
            for key, rows in result["acquisition"]["case_outcomes"]["000"].items()
        }:
            raise ValueError("semantic reference identity mismatch")
        result["semantic"] = analyze(
            semantic, ["acquisition_bundle", "strict_nli", "proof_requirement"]
        )
        result["neural_report_sha256"] = NEURAL_SHA
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
