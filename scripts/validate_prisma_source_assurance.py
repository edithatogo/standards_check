#!/usr/bin/env python3
"""Fail-closed PRISMA 2020 source reconciliation readiness gate.

Offline audit of explicit PRISMA item/subitem IDs, licence metadata and evidence.
It never treats a licence statement as proof of item-level transcription parity.
"""
from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs/org.prisma/prisma/2020/pack.json"
BASE_ITEMS = tuple(str(i) for i in range(1, 28))
SUBITEMS = {"10": "ab", "13": "abcdef", "16": "ab", "20": "abcd",
            "23": "abcd", "24": "abc"}
EXPECTED = frozenset(
    f"{item}{suffix}" for item in BASE_ITEMS
    for suffix in (SUBITEMS[item] if item in SUBITEMS else ("",))
)
OFFICIAL = "https://www.prisma-statement.org/prisma-2020-checklist"
LICENCE = "https://creativecommons.org/licenses/by/4.0/"


def audit(pack: dict) -> dict:
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
    source_receipt = "source-sha256:" + authority_sha
    item_receipts = {
        match.group(1): match.group(2) for receipt in receipt_strings
        if (match := re.fullmatch(
            r"item-check:([0-9]+[a-z]?):sha256:([a-f0-9]{64})", str(receipt)
        ))
    }
    matching_receipts = all(
        item_receipts.get(str(item["display_number"])) == hashlib.sha256(
            "".join(
                c for c in unicodedata.normalize("NFKC", item.get("verbatim_text") or "")
                if not c.isspace()
            ).encode("utf-8")
        ).hexdigest()
        for item in requirements
    )
    evidence_ok = (bool(evidence.get("verified_at"))
                   and bool(evidence.get("verified_by"))
                   and re.fullmatch(r"[a-f0-9]{64}", authority_sha) is not None
                   and source_receipt in receipt_strings
                   and EXPECTED.issubset(item_receipts)
                   and matching_receipts
                   and all(str(i["source_anchor"]).strip() for i in requirements))
    # Exact-item evidence requires the full official checklist numbering, not
    # one aggregate item representing multiple required subitems.
    source_ready = bool(not missing and not extra and not duplicate
                        and not legacy_aggregate and evidence_ok and licence_ok)
    status = evidence["status"]
    errors = []
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
        "item_level_source_reconciled": source_ready,
        "pack_status": status,
        "errors": errors,
    }


def main() -> int:
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    result = audit(pack)
    print(json.dumps(result, sort_keys=True, indent=2))
    return int(bool(result["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
