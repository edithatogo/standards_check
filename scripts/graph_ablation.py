"""Retrospective E11 factorial and rewired-edge controls; never infer equivalence."""

from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path

from .costing_retrieval import evaluate, rank
from .graph_development import BONUS, edges, load_fixture, scores

EDGE_TYPES = ("parent", "crossref", "dependency")
SEEDS = tuple(range(20))


def shuffle_edges(graph, seed):
    """Conserve type-wise endpoint multisets; discard factual provenance of rewiring."""
    rng = random.Random(seed)
    result = []
    for kind in EDGE_TYPES:
        rows = [edge for edge in graph if edge["type"] == kind]
        original = [edge["to"] for edge in rows]
        if not rows:
            continue
        for _ in range(100):
            dest = original.copy()
            rng.shuffle(dest)
            if dest != original and all(
                edge["from"] != node for edge, node in zip(rows, dest, strict=True)
            ):
                break
        else:
            raise ValueError("no admissible shuffled edge control")
        result.extend(
            {
                "from": edge["from"],
                "to": node,
                "type": kind,
                "original_to": edge["to"],
                "original_anchor": edge["anchor"],
                "control_only": True,
            }
            for edge, node in zip(rows, dest, strict=True)
        )
    return result


def arm(base, context, graph, kinds, refs, universe, baseline):
    augmented = {}
    for key, row in base.items():
        signals = dict.fromkeys(universe, 0.0)
        for edge in graph:
            kind, dest = edge["type"], edge["to"]
            if kind not in kinds:
                continue
            signal = (
                context[key][dest]
                if kind == "parent"
                else row[dest] * (0.8 if kind == "crossref" else 0.6)
            )
            source = edge["from"]
            signals[source] = max(signals[source], signal)
        augmented[key] = {t: round(v + BONUS * signals[t], 6) for t, v in row.items()}
    rankings = {key: rank(row, positive=True) for key, row in augmented.items()}
    paired = []
    for key, reference in sorted(refs.items()):
        before = set(baseline[key][:5]) & reference
        after = set(rankings[key][:5]) & reference
        paired.append(
            {
                "family": key[0],
                "query": key[1],
                "gained": sorted(after - before),
                "lost": sorted(before - after),
                "scores": augmented[key],
            }
        )
    return {"evaluation": evaluate(refs, universe, rankings), "paired": paired}


def ablate(data):
    graph = edges(data)
    targets = {row["id"]: row["text"] for row in data["targets"]}
    headings = {row["id"]: row["text"] for row in data["headings"]}
    queries = {(row["family"], row["id"]): row["text"] for row in data["queries"]}
    refs = {(row["family"], row["id"]): set(row["relevant"]) for row in data["queries"]}
    if len(queries) != len(data["queries"]):
        raise ValueError("duplicate query")
    subsets = [kinds for n in range(4) for kinds in itertools.combinations(EDGE_TYPES, n)]
    controls = {seed: shuffle_edges(graph, seed) for seed in SEEDS}
    methods = {}
    for method in ("word", "char"):
        base = scores(queries, targets, method)
        context = scores(queries, headings, method)
        baseline = {key: rank(row, positive=True) for key, row in base.items()}
        arms = {
            "+".join(kinds) or "none": arm(
                base, context, graph, kinds, refs, set(targets), baseline
            )
            for kinds in subsets
        }
        effects = {
            kinds: arms["+".join(kinds) or "none"]["evaluation"]["macro_query_recall"]["5"]
            for kinds in subsets
        }
        # Inclusion-exclusion contrasts at absent levels of other factors.
        interactions = {
            "+".join(kinds): round(
                sum(
                    (-1) ** (len(kinds) - len(subset)) * effects[subset]
                    for subset in subsets
                    if set(subset) <= set(kinds)
                ),
                12,
            )
            for kinds in subsets
            if kinds
        }
        negatives = [
            {"seed": seed, **arm(base, context, rewired, EDGE_TYPES, refs, set(targets), baseline)}
            for seed, rewired in controls.items()
        ]
        methods[method] = {
            "arms": arms,
            "interactions": interactions,
            "negative_controls": negatives,
        }
    return {
        "status": "retrospective_synthetic_development",
        "equivalence_inferred": False,
        "eligible_pairs": len(targets) * len(queries),
        "reference_associations": sum(map(len, refs.values())),
        "edges": graph,
        "rewired_controls": controls,
        "methods": methods,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(ablate(load_fixture()), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
