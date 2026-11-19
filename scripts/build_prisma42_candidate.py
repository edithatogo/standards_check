#!/usr/bin/env python3
"""Build a non-authoritative 42-item PRISMA candidate and legacy alias manifest.

Never silently promote draft web transcription to source_reconciled.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "conductor/source-reconciliation/prisma-2020-checklist-draft.json"
ORIGINAL = ROOT / "contracts/examples/prisma-2020-legacy27.pack.json"
LEGACY_PACK_SHA256 = "2c4ca02e5c8fb65f046b6eb1cf131769288f07d1f92f16a50f721a03be3c429b"
OFFICIAL_PDF_URL = "https://www.prisma-statement.org/s/PRISMA_2020_checklist-ab3g.pdf"
PINNED_PDF_SHA256 = "2eedbd5452741f9615307a0bce21a8198c0597ce2a0a8a0fd7e140d64b08c625"
PINNED_PDF_LENGTH = 67506
SPLIT = {"10": "ab", "13": "abcdef", "16": "ab",
         "20": "abcd", "23": "abcd", "24": "abc"}
EXPECTED = [
    (f"{i}{suffix}" if str(i) in SPLIT else str(i))
    for i in range(1, 28)
    for suffix in (SPLIT[str(i)] if str(i) in SPLIT else ("",))
]
EXPECTED_PAGES = {
    number: 1 if int(re.match(r"\d+", number).group()) <= 15 else 2
    for number in EXPECTED
}


def normalize(text: str) -> str:
    """Apply Unicode NFKC normalization and remove whitespace only."""
    return "".join(c for c in unicodedata.normalize("NFKC", text) if not c.isspace())


def checked_ledger_items(ledger: dict) -> dict[str, dict]:
    """Bind the complete item sequence and page anchors to the fixed source."""
    if ledger.get("source_url") != OFFICIAL_PDF_URL or ledger.get("source_pages") != 2:
        raise ValueError("Expected the pinned official two-page PRISMA PDF")
    source = ledger.get("items", [])
    if [entry.get("number") for entry in source] != EXPECTED:
        raise ValueError("PRISMA numbered and lettered item sequence must contain all 42 in order")
    for entry in source:
        number = entry["number"]
        if not isinstance(entry.get("verbatim_text"), str) or not entry["verbatim_text"].strip():
            raise ValueError(f"Missing source text for item {number}")
        page = EXPECTED_PAGES[number]
        if type(entry.get("page")) is not int or entry["page"] != page:
            raise ValueError(f"Item {number} must refer to official PDF page {page}")
        if entry.get("source_anchor") != f"{OFFICIAL_PDF_URL}#page={page}":
            raise ValueError(f"Item {number} must have the complete official PDF page anchor")
    return {entry["number"]: entry for entry in source}


def load_legacy_pack() -> dict:
    """Read the exact pre-promotion pack; never use the live 42-item pack."""
    source = ORIGINAL.read_bytes()
    if hashlib.sha256(source).hexdigest() != LEGACY_PACK_SHA256:
        raise ValueError("The immutable 27-item legacy pack fixture has changed")
    return json.loads(source)


def preview(old: dict, ledger: dict) -> dict:
    if ledger.get("source_bytes_verified") is not False or ledger.get("source_bytes_sha256") is not None:
        raise ValueError("Draft ledger must not assert source-byte verification")
    if ledger.get("transcription_status") != "draft_transcribed_from_official_web_pdf_text_and_visual":
        raise ValueError("Unexpected transcription evidence boundary")
    source = list(checked_ledger_items(ledger).values())
    original = {item["display_number"]: item for item in old["requirements"]}
    if len(old["requirements"]) != 27 or set(original) != {str(i) for i in range(1, 28)}:
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
        load_legacy_pack(),
        json.loads(LEDGER.read_text(encoding="utf-8")),
    )
    content = json.dumps(candidate, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
