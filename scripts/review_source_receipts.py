#!/usr/bin/env python3
"""Deterministic, text-free retrospective of source survey and reconciliation receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

# Recommendations are hypotheses/next tests, not decisions to change a source pin.
RULES = {
    "evidence_lost": (
        0,
        "Recover lost source or table evidence; never treat a reduced extraction as a valid replacement.",
    ),
    "structural_drift": (
        0,
        "Recheck nested blocks, spans and applicability against the pinned source before changing extraction rules.",
    ),
    "source_bytes_changed": (
        0,
        "Reacquire the exact edition; compare source, rows, anchors and rights before changing pins.",
    ),
    "table_or_item_drift": (
        0,
        "Compare ordered IDs, full requirement hashes, anchors and nested blocks with an independent reader.",
    ),
    "identity_or_licence_changed": (
        0,
        "Hold the edition; reconcile bibliographic identity and work-specific rights.",
    ),
    "record_missing": (
        0,
        "Check run completeness and upstream removal; do not delete a previously retained source automatically.",
    ),
    "structural_hold": (
        1,
        "Inspect unsupported rows, spans, footnotes and subitems; add a source-format regression before repairing the shared reader.",
    ),
    "provider_incomplete": (
        1,
        "Retry only incomplete provider batches within a request budget; preserve prior receipts.",
    ),
    "source_held": (
        1,
        "Check acquisition and format/identity/rights gates; prefer another official representation of the same edition.",
    ),
    "unresolved_identity": (
        2,
        "Use exact PMID/DOI resolution and registry evidence; retain ambiguous publication candidates.",
    ),
    "legacy_text_discrepancy": (
        2,
        "Compare anchored source and legacy items; separate formatting, aggregation, missing conditions and substantive differences.",
    ),
    "new_record": (
        3,
        "Queue the new identity for source and rights discovery, not automatic admission.",
    ),
    "provider_contact_missing": (
        1,
        "Configure an authorized maintainer contact for PMC ID conversion; do not guess identity.",
    ),
    "provider_budget_deferred": (
        1,
        "Revisit deferred registry observations in a subsequent bounded run.",
    ),
    "provider_conflict": (
        0,
        "Hold identity conflicts; compare exact identifiers and publisher evidence, never majority-vote.",
    ),
    "acquisition_deferred": (
        1,
        "Resume bounded acquisition from trusted receipts; prioritize unattempted sources.",
    ),
    "provider_representation_changed": (
        0,
        "Compare the newly observed source representation against its previous byte and table receipt; do not automatically repin.",
    ),
    "status_changed": (
        3,
        "Investigate the changed outcome against exact-revision receipts before interpreting it as improvement or regression.",
    ),
}


def signature(table: dict) -> tuple:
    rows = table.get("items", table.get("rows", []))
    return (
        table.get("table_id"),
        table.get("table_rows_sha256"),
        tuple(
            (r.get("item_id"), r.get("source_anchor"), r.get("normalized_text_sha256"))
            for r in rows
        ),
    )


def index(receipt: dict) -> dict:
    if not isinstance(receipt, dict):
        raise ValueError("receipt must be an object")
    if "records" in receipt:
        groups = (
            ("catalogue", "id", receipt["records"]),
            ("edition", "edition", receipt.get("priority_articles", [])),
            ("edition", "edition", receipt.get("bulk_articles", [])),
        )
    elif "editions" in receipt:
        groups = (("edition", "edition", receipt["editions"]),)
    else:
        raise ValueError("unsupported source receipt; use a survey or authoritative article report")
    result = {}
    for kind, field, rows in groups:
        if not isinstance(rows, list):
            raise ValueError("invalid receipt record array")
        for row in rows:
            name = row.get(field) if isinstance(row, dict) else None
            if not isinstance(name, str) or not name or len(name) > 300:
                raise ValueError("missing or invalid receipt identity")
            key = kind + ":" + name
            if key in result:
                raise ValueError("duplicate receipt identity")
            result[key] = row
    return result


def observed(row: dict) -> tuple:
    source = row.get("source") or row
    tables = row.get(
        "tables", [source] if "table_id" in source or "table_rows_sha256" in source else []
    )
    hashes = (row.get("source_blob_sha"), source.get("source_sha256"))
    identity = (
        row.get("pmid", row.get("resolved_pmid")),
        row.get("doi", row.get("resolved_doi")),
        row.get("pmcid"),
        source.get("article_licence_observed", source.get("licence", row.get("licence_reported"))),
    )
    return hashes, identity, tuple(signature(t) for t in tables), tables


def held_source_ids(receipt: dict) -> set[str]:
    """Retain grouped source identity holds, including rows without individual conflicts."""
    records = {row["id"] for row in receipt.get("records", [])}
    held = set()
    for entry in receipt.get("oa_source_worklist", []):
        if entry["status"] != "held_identity":
            continue
        ids = entry["source_ids"]
        if (
            not isinstance(ids, list)
            or not ids
            or any(not isinstance(value, str) or value not in records for value in ids)
        ):
            raise ValueError("unbound source-level identity hold")
        held.update(ids)
    return held


def review(current: dict, baseline: dict | None = None) -> dict:
    now = index(current)
    before = index(baseline) if baseline is not None else {}
    findings = {("provider_conflict", "catalogue:" + key) for key in held_source_ids(current)}
    evidence = current.get("provider_evidence", {}).get("records", {})
    for key, row in now.items():
        if key.startswith("catalogue:"):
            observations = evidence.get(row["id"], {})
        else:
            observations = evidence.get(key, {})
        statuses = {v.get("status") for v in observations.values()}
        if "contact_not_configured" in statuses:
            findings.add(("provider_contact_missing", key))
        if "deferred_request_budget" in statuses:
            findings.add(("provider_budget_deferred", key))
        if statuses.intersection({"identifier_conflict", "ambiguous_identifier"}):
            findings.add(("provider_conflict", key))
        status = row.get("status", "unknown")
        hashes, identity, tables, objects = observed(row)
        if row.get("provider_disagreements"):
            findings.add(("provider_conflict", key))
        if status == "deferred_acquisition_budget":
            findings.add(("acquisition_deferred", key))
        if status == "lookup_incomplete":
            findings.add(("provider_incomplete", key))
        if status in {
            "missing_identifier",
            "unresolved_identifier",
            "identifier_conflict",
            "ambiguous_identifier",
        }:
            findings.add(("unresolved_identity", key))
        if isinstance(status, str) and status.startswith("held"):
            findings.add(("source_held", key))
        for table in objects:
            structure = table.get("structure") or {}
            if structure.get("issues") or str(structure.get("status", "")).startswith("held"):
                findings.add(("structural_hold", key))
        for compare in [row.get("legacy") or {}, *(t.get("legacy") or {} for t in objects)]:
            if compare.get("source_item_count", 0) > compare.get("exact_unique_items", 0):
                findings.add(("legacy_text_discrepancy", key))
        if key in before:
            old_hashes, old_identity, old_tables, old_objects = observed(before[key])
            old_provider = (before[key].get("acquisition") or {}).get("provider")
            new_provider = (row.get("acquisition") or {}).get("provider")
            if old_provider and new_provider and old_provider != new_provider:
                findings.add(("provider_representation_changed", key))
            if any(
                a and not b
                for a, b in zip(old_hashes + old_identity, hashes + identity, strict=True)
            ) or (old_tables and not tables):
                findings.add(("evidence_lost", key))
            old_structure = {
                t.get("table_id"): t.get("structure") for t in old_objects if t.get("structure")
            }
            current_structure = {
                t.get("table_id"): t.get("structure") for t in objects if t.get("structure")
            }
            if old_structure.keys() - current_structure.keys():
                findings.add(("evidence_lost", key))
            if any(
                t.get("structure")
                and t.get("table_id") in old_structure
                and t["structure"] != old_structure[t.get("table_id")]
                for t in objects
            ):
                findings.add(("structural_drift", key))
            if any(a and b and a != b for a, b in zip(old_hashes, hashes, strict=True)):
                findings.add(("source_bytes_changed", key))
            if any(a and b and a != b for a, b in zip(old_identity, identity, strict=True)):
                findings.add(("identity_or_licence_changed", key))
            if old_tables and tables and old_tables != tables:
                findings.add(("table_or_item_drift", key))
            if before[key].get("status") != status:
                findings.add(("status_changed", key))
        elif baseline is not None:
            findings.add(("new_record", key))
    findings.update(("record_missing", key) for key in before.keys() - now.keys())
    counts = dict(sorted(Counter(code for code, _ in findings).items()))
    return {
        "schema_version": 1,
        "current_records": len(now),
        "baseline_records": len(before) if baseline is not None else None,
        "finding_counts": counts,
        "findings": [{"code": code, "record": key} for code, key in sorted(findings)],
        "recommendations": [
            {"code": code, "affected_records": counts[code], "action": RULES[code][1]}
            for code in sorted(counts, key=lambda c: (RULES[c][0], -counts[c], c))
        ],
        "canonical_packs_promoted": 0,
        "claim_boundary": "Diagnostic retrospective only; no repin, source rights or semantic admission.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    raw = args.receipt.read_bytes()
    previous = args.baseline.read_bytes() if args.baseline else None
    result = review(json.loads(raw), json.loads(previous) if previous is not None else None)
    result["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    result["baseline_sha256"] = (
        hashlib.sha256(previous).hexdigest() if previous is not None else None
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["finding_counts"], sort_keys=True))


if __name__ == "__main__":
    main()
