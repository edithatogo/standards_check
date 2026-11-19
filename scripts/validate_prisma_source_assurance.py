#!/usr/bin/env python3
"""Fail-closed PRISMA 2020 source reconciliation readiness gate.

Offline audit of explicit PRISMA item/subitem IDs, licence metadata and evidence.
It never treats a licence statement as proof of item-level transcription parity.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

if __package__:
    from .build_prisma42_candidate import (
        EXPECTED as EXPECTED_ORDER, LEDGER, OFFICIAL_PDF_URL, PINNED_PDF_SHA256,
        SPLIT as SUBITEMS, checked_ledger_items, normalize,
    )
else:
    from build_prisma42_candidate import (
        EXPECTED as EXPECTED_ORDER, LEDGER, OFFICIAL_PDF_URL, PINNED_PDF_SHA256,
        SPLIT as SUBITEMS, checked_ledger_items, normalize,
    )

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs/org.prisma/prisma/2020/pack.json"
BASE_ITEMS = tuple(str(i) for i in range(1, 28))
EXPECTED = frozenset(EXPECTED_ORDER)
OFFICIAL = "https://www.prisma-statement.org/prisma-2020-checklist"
LICENCE = "https://creativecommons.org/licenses/by/4.0/"


def audit(pack: dict, ledger: dict) -> dict:
    """Check a pack against independent ledger data, not its self-declared hashes.

    The authoritative-PDF job separately checks this same ledger and pack against
    complete numbered rows extracted from the pinned source bytes.
    """
    ledger_error = None
    try:
        source_items = checked_ledger_items(ledger)
    except ValueError as error:
        source_items = {}
        ledger_error = str(error)
    requirements = pack["requirements"]
    numbers = [str(item["display_number"]) for item in requirements]
    seen = set(numbers)
    legacy_aggregate = sorted(x for x in seen if x in SUBITEMS)
    missing = sorted(EXPECTED - seen, key=lambda x: (int(re.match(r"\d+", x).group()), x))
    extra = sorted(seen - EXPECTED)
    duplicate = len(numbers) != len(seen)
    rights = pack["rights"]
    licence_ok = (rights.get("status") == "cleared"
                  and rights.get("spdx") == "CC-BY-4.0"
                  and rights.get("license_url") == LICENCE
                  and bool(rights.get("attribution")))
    evidence = pack["verification"]
    receipt_strings = evidence.get("evidence", [])
    authority_sha = pack.get("authority", {}).get("source_sha256", "")
    source_identity_ok = (
        authority_sha == PINNED_PDF_SHA256
        and pack.get("authority", {}).get("source_url") == OFFICIAL_PDF_URL
    )
    source_receipt = "source-sha256:" + PINNED_PDF_SHA256
    item_receipts = {
        match.group(1): match.group(2) for receipt in receipt_strings
        if (match := re.fullmatch(
            r"item-check:([0-9]+[a-z]?):sha256:([a-f0-9]{64})", str(receipt)
        ))
    }
    matching_receipts = all(
        item_receipts.get(str(item["display_number"])) == hashlib.sha256(
            normalize(item.get("verbatim_text") or "").encode("utf-8")
        ).hexdigest()
        for item in requirements
    )
    matching_source_text = ledger_error is None and all(
        str(item["display_number"]) in source_items
        and normalize(item.get("verbatim_text") or "") == normalize(
            source_items[str(item["display_number"])]["verbatim_text"]
        )
        for item in requirements
    )
    matching_source_anchors = all(
        item.get("source_anchor") == f"prisma-2020-checklist:item:{item['display_number']}"
        for item in requirements
    )
    matching_source_identifiers = all(
        item.get("id") == f"PRISMA-2020:{item['display_number']}"
        for item in requirements
    )
    evidence_ok = (bool(evidence.get("verified_at"))
                   and bool(evidence.get("verified_by"))
                   and source_identity_ok
                   and source_receipt in receipt_strings
                   and EXPECTED.issubset(item_receipts)
                   and matching_receipts
                   and matching_source_text
                   and matching_source_anchors
                   and matching_source_identifiers)
    # Exact-item evidence requires the full official checklist numbering, not
    # one aggregate item representing multiple required subitems.
    source_ready = bool(not missing and not extra and not duplicate
                        and not legacy_aggregate and evidence_ok and licence_ok)
    status = evidence["status"]
    errors = []
    if ledger_error is not None:
        errors.append(f"PRISMA source ledger is invalid: {ledger_error}")
    if not licence_ok:
        errors.append("PRISMA pack licence metadata is not cleared CC BY 4.0 with attribution")
    if status != "imported_unverified" and not source_ready:
        errors.append("Source status promoted without complete item/subitem reconciliation")
    if status == "externally_validated":
        errors.append("External validation requires an independent external acceptance receipt")
    return {
        "schema_version": "dev.standardflow.prisma-source-audit.v1",
        "source": OFFICIAL,
        "licence": LICENCE,
        "expected_subitems": len(EXPECTED),
        "actual_entries": len(requirements),
        "missing_subitems": missing,
        "aggregate_entries_requiring_split": legacy_aggregate,
        "unexpected_identifiers": extra,
        "duplicate_identifiers": duplicate,
        "licence_metadata_complete": licence_ok,
        "source_identity_matches_pin": source_identity_ok,
        "item_text_matches_source_ledger": matching_source_text,
        "source_anchors_match_items": matching_source_anchors,
        "source_identifiers_match_items": matching_source_identifiers,
        "item_level_source_reconciled": source_ready,
        "pack_status": status,
        "errors": errors,
    }


def main() -> int:
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    result = audit(pack, ledger)
    print(json.dumps(result, sort_keys=True, indent=2))
    return int(bool(result["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
