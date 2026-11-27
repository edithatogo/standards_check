"""Bounded, source-receipt-preserving continuation of the existing bulk survey."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

DEFERRED = "deferred_acquisition_budget"
HELD = "held"
OBSERVED = "source_inventory_observed_not_reconciled"


def resume(prior, root, limit, survey, *, retry_held=False):
    """Retain all previous rows; attempt only explicitly eligible selected PMCID identities."""
    if type(limit) is not int or not 1 <= limit <= 24:
        raise ValueError("invalid acquisition budget")
    rows = prior["bulk_articles"]
    old = {row["pmcid"]: row for row in rows}
    records = prior["records"]
    blobs = {row["id"]: row["source_blob_sha"] for row in records}
    work = [
        r for r in prior["oa_source_worklist"] if r["status"] == "candidate_pending_acquisition"
    ]
    if len(old) != len(rows) or len(blobs) != len(records) or len(work) != len(old):
        raise ValueError("invalid checkpoint inventory")
    if {r["pmcid"] for r in work} != set(old):
        raise ValueError("checkpoint worklist inventory mismatch")
    for candidate in work:
        row = old[candidate["pmcid"]]
        binding = [[key, blobs[key]] for key in sorted(candidate["source_ids"])]
        if (
            row["source_blobs"] != binding
            or candidate["identity_pairs"] != [[row["doi"], row["pmid"]]]
            or row["status"] not in (DEFERRED, HELD, OBSERVED)
            or row.get("canonical_packs_promoted") != 0
        ):
            raise ValueError("checkpoint source binding mismatch")
    statuses = (DEFERRED, HELD) if retry_held else (DEFERRED,)
    selected = sorted(
        (r for r in work if old[r["pmcid"]]["status"] in statuses),
        key=lambda r: (old[r["pmcid"]]["status"] != DEFERRED, r["pmcid"]),
    )[:limit]
    expected = {r["pmcid"] for r in selected}
    new = (
        survey({**prior, "oa_source_worklist": selected}, [prior], root, limit) if selected else []
    )
    if len(new) != len(expected) or {r["pmcid"] for r in new} != expected:
        raise ValueError("batch result inventory mismatch")
    attempted = []
    latest = dict(old)
    for row in new:
        key = row["pmcid"]
        if any(
            row.get(k) != old[key].get(k)
            for k in ("edition", "pmcid", "doi", "pmid", "source_blobs")
        ):
            raise ValueError("batch result source binding mismatch")
        if row["status"] == DEFERRED:
            continue
        if row["status"] not in (HELD, OBSERVED) or row.get("canonical_packs_promoted") != 0:
            raise ValueError("invalid acquisition outcome")
        attempted.append(key)
        latest[key] = row
    inventory = [latest[key] for key in sorted(latest)]
    counts = dict(Counter(row["status"] for row in inventory))
    return {
        **prior,
        "bulk_articles": inventory,
        "summary": {**prior["summary"], "bulk_status_counts": counts},
        "resume": {
            "budget": limit,
            "retry_held": retry_held,
            "selected": [row["pmcid"] for row in selected],
            "attempted": sorted(attempted),
            "remaining_unattempted": counts.get(DEFERRED, 0),
            "held": counts.get(HELD, 0),
            "observed_not_reconciled": counts.get(OBSERVED, 0),
            "canonical_packs_promoted": 0,
        },
    }


def main():
    from .survey_equator_articles import bulk_survey

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--retry-held", action="store_true")
    args = parser.parse_args()
    raw = args.previous.read_bytes()
    if len(raw) > 16_000_000 or hashlib.sha256(raw).hexdigest() != args.expected_sha256:
        raise ValueError("prior receipt size or digest mismatch")
    result = resume(
        json.loads(raw), Path.cwd(), args.limit, bulk_survey, retry_held=args.retry_held
    )
    result["resume"]["previous_sha256"] = args.expected_sha256
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["resume"], sort_keys=True))


if __name__ == "__main__":
    main()
