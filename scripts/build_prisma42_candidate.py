#!/usr/bin/env python3
"""Build a non-authoritative 42-item PRISMA candidate and legacy alias manifest.

Never silently promote draft web transcription to source_reconciled.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "conductor/source-reconciliation/prisma-2020-checklist-draft.json"
ORIGINAL = ROOT / "packs/org.prisma/prisma/2020/pack.json"
SPLIT = {"10": "ab", "13": "abcdef", "16": "ab",
         "20": "abcd", "23": "abcd", "24": "abc"}
EXPECTED = [
    (f"{i}{suffix}" if str(i) in SPLIT else str(i))
    for i in range(1, 28)
    for suffix in (SPLIT[str(i)] if str(i) in SPLIT else ("",))
]


def preview(old: dict, ledger: dict) -> dict:
    if ledger.get("source_bytes_verified") is not False or ledger.get("source_bytes_sha256") is not None:
        raise ValueError("Draft ledger must not assert source-byte verification")
    if ledger.get("transcription_status") != "draft_transcribed_from_official_web_pdf_text_and_visual":
        raise ValueError("Unexpected transcription evidence boundary")
    source = ledger.get("items", [])
    identifiers = [entry["number"] for entry in source]
    if identifiers != EXPECTED:
        raise ValueError("PRISMA numbered and lettered item sequence must contain all 42 in order")
    if any(not entry["verbatim_text"].strip() or entry["page"] not in (1, 2) for entry in source):
        raise ValueError("Missing source text or PDF page anchor")
    if any(not entry["source_anchor"].startswith(ledger["source_url"] + "#page=") for entry in source):
        raise ValueError("Every draft item must point to the official PDF page")
    original = {item["display_number"]: item for item in old["requirements"]}
    if set(original) != {str(i) for i in range(1, 28)}:
        raise ValueError("Expected exactly 27 original legacy item identifiers")
    items = []
    alias = {}
    for entry in source:
        number = entry["number"]
        parent = re.match(r"\d+", number).group()
        original_item = original[parent]
        candidate = deepcopy(original_item)
        candidate.update(
            id=f"PRISMA-2020:{number}",
            display_number=number,
            verbatim_text=entry["verbatim_text"],
            source_anchor=f"prisma-2020-checklist:item:{number}",
        )
        # A split changes what a requirement covers. Do not silently reuse
        # the old aggregate's narrower or broader interpretation as approved.
        if parent in SPLIT:
            candidate["normalized_requirement"] = entry["verbatim_text"]
            candidate["guidance"] = None
        items.append(candidate)
        alias.setdefault(original_item["id"], []).append(candidate["id"])
    return {
        "schema_version": "dev.standardflow.prisma-candidate-preview.v1",
        "authority": {
            "source_url": ledger["source_url"],
            "source_sha256": None,
            "source_bytes_verified": False,
        },
        "verification": {"status": "imported_unverified", "item_text_review": "pending"},
        "rights": old["rights"],
        "requirements": items,
        "migration": {
            "legacy_to_candidate": alias,
            "split_requires_semantic_reassessment": [
                f"PRISMA-2020:{parent}" for parent in SPLIT
            ],
            "legacy_identifiers_must_not_be_reused_as_one_to_one": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional preview destination")
    args = parser.parse_args()
    candidate = preview(
        json.loads(ORIGINAL.read_text(encoding="utf-8")),
        json.loads(LEDGER.read_text(encoding="utf-8")),
    )
    content = json.dumps(candidate, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
