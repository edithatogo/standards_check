"""Typed scope audit of the actual costing candidate inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .costing_retrieval import file_hash, lexical_rankings, load_inputs

ROOT = Path(__file__).resolve().parents[1]


def audit(root: Path) -> dict:
    registry, mappings, queries, targets, references, paths = load_inputs(root)
    scopes = {row["id"]: set(row["domains"]) for row in registry["instruments"]}
    ranked = lexical_rankings(queries, targets, "char")
    rows = []
    disagreements = []
    for key in sorted(queries):
        instrument, item = key
        scope = scopes[instrument]
        missing = sorted(references[key] - scope)
        if missing:
            disagreements.append({"instrument": instrument, "item": item, "domains": missing})
        ranks = {candidate: i + 1 for i, candidate in enumerate(ranked[key])}
        for domain in sorted(targets):
            rows.append(
                {
                    "instrument": instrument,
                    "item": item,
                    "domain": domain,
                    "relation": "covers_topic_candidate",
                    "rank": ranks.get(domain),
                    "editorial_association": domain in references[key],
                    "instrument_scope_summary": domain in scope,
                }
            )
    return {
        "protocol": "costing-typed-scope-audit-v1",
        "source_sha256": {path.name: file_hash(path) for path in paths},
        "reference_status": mappings["mapping_status"],
        "instrument_records": len(scopes),
        "mapped_items": len(queries),
        "target_domains": len(targets),
        "editorial_associations": sum(len(x) for x in references.values()),
        "candidate_pairs": len(rows),
        "scope_disagreements": disagreements,
        "rows": rows,
        "equivalence_candidates": 0,
        "semantic_merges": 0,
        "solver_status": "held_no_independent_typed_equivalence_constraints",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
