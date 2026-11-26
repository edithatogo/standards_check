"""Advisory source-bound evidence inventory and masked identity retrieval."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter

from .costing_retrieval import lexical_rankings

LINK = re.compile(r"\bitem\s+#(\d+[a-z]?)\b", re.IGNORECASE)


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def inventory(raw, expected):
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("source pack digest mismatch")
    pack = json.loads(raw)
    if (
        pack["rights"]["status"] != "cleared"
        or pack["verification"]["status"] != "source_reconciled"
    ):
        raise ValueError("only eligible source-reconciled packs are permitted")
    rows = pack["requirements"]
    ids = {r["id"] for r in rows}
    numbers = {r["display_number"].casefold(): r["id"] for r in rows}
    anchors = {r["source_anchor"] for r in rows}
    if not rows or len(ids) != len(rows) or len(numbers) != len(rows) or len(anchors) != len(rows):
        raise ValueError("nonunique evidence identity")
    units, edges, unresolved = [], [], []
    for row in rows:
        if not row["rights"].get("inherit_from_pack") or not row["source_anchor"]:
            raise ValueError("ineligible item rights or anchor")
        text = row["verbatim_text"]
        if not isinstance(text, str) or not text.strip():
            raise ValueError("empty source evidence")
        units.append({"id": row["id"], "anchor": row["source_anchor"], "section": row["section"],
                      "text_sha256": digest(text), "declared_evidence_kinds": row["evidence_expectations"]})
        for match in LINK.finditer(text):
            number = match.group(1).casefold()
            edge = {"from": row["id"], "type": "explicit_cross_reference", "anchor": row["source_anchor"],
                    "span": list(match.span()), "target_number": number}
            if number not in numbers or numbers[number] == row["id"]:
                unresolved.append(edge)
            else:
                edges.append({**edge, "to": numbers[number]})
    return {"pack_id": pack["pack_id"], "source_pack_sha256": expected, "units": units,
            "edges": edges, "unresolved_references": unresolved,
            "claim_boundary": "declared_item_inventory_not_independent_clause_or_manuscript_reference"}


def closure(inv, seeds, budget):
    ids = {r["id"] for r in inv["units"]}
    if type(budget) is not int or budget < 1 or len(set(seeds)) != len(seeds) or not set(seeds) <= ids or len(seeds) > budget:
        raise ValueError("invalid evidence identity or closure budget")
    neighbors = {key: set() for key in ids}
    for edge in inv["edges"]:
        neighbors[edge["from"]].add(edge["to"])
    result = list(seeds)
    for key in result:
        for target in sorted(neighbors[key]):
            if target not in result and len(result) < budget:
                result.append(target)
    return result


def certificate(inv, observed, expected):
    ids = {r["id"] for r in inv["units"]}
    if (len(set(observed)) != len(observed) or len(set(expected)) != len(expected)
        or not set(observed) <= ids or not set(expected) <= ids or not expected):
        raise ValueError("invalid certificate identity")
    missing = sorted(set(expected) - set(observed))
    unresolved = [edge for edge in inv["unresolved_references"] if edge["from"] in expected]
    return {"source_pack_sha256": inv["source_pack_sha256"], "expected": sorted(expected),
            "observed": sorted(observed), "missing": missing, "unresolved_references": unresolved,
            "structural_coverage_complete": not missing and not unresolved,
            "semantic_completeness": "not_established", "admission": "advisory_only"}


def baseline(raw, expected):
    inv = inventory(raw, expected)
    pack = json.loads(raw)
    targets = {r["id"]: r["verbatim_text"] for r in pack["requirements"]}
    queries = {key: " ".join(value.split()[::2]) for key, value in targets.items()}
    methods = {}
    for method in ("word", "char"):
        rankings = lexical_rankings(queries, targets, method)
        rows = []
        for key in targets:
            order = rankings[key]
            closed = closure(inv, order[:3], 5)
            rows.append({"expected": key, "rank": order.index(key) + 1 if key in order else None,
                         "top5": order[:5], "closed_top3_budget5": closed})
        methods[method] = {"rows": rows, "hits": {str(k): sum(r["rank"] is not None and r["rank"] <= k for r in rows) for k in (1, 3, 5)},
                           "closed_hits": sum(r["expected"] in r["closed_top3_budget5"] for r in rows),
                           "ranked_count": dict(Counter(len(rankings[key]) for key in targets))}
    return {"claim_boundary": "masked_source_identity_recovery_not_semantic_relevance", "queries": len(queries),
            "candidate_pairs": len(queries) * len(targets), "inventory": inv,
            "certificate": certificate(inv, list(targets), list(targets)), "methods": methods}
