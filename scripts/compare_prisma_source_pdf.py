#!/usr/bin/env python3
"""Compare 42 draft PRISMA checklist items with a pinned authoritative PDF.

This requires an explicitly acquired local PDF and pdftotext. No network calls
are made by this validator, and no verification status is silently promoted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

if __package__:
    from .build_prisma42_candidate import (
        EXPECTED, EXPECTED_PAGES, LEDGER, PINNED_PDF_LENGTH, PINNED_PDF_SHA256,
        checked_ledger_items, normalize,
    )
    from .validate_prisma_source_assurance import PACK, audit
else:
    from build_prisma42_candidate import (
        EXPECTED, EXPECTED_PAGES, LEDGER, PINNED_PDF_LENGTH, PINNED_PDF_SHA256,
        checked_ledger_items, normalize,
    )
    from validate_prisma_source_assurance import PACK, audit

GUTTERS = {1: 30, 2: 28}


def checklist_column(page_text: str, page: int) -> str:
    """Read only the item text; the two PDF pages have distinct left gutters."""
    if page not in GUTTERS:
        raise ValueError("Unexpected PDF page")
    start = GUTTERS[page]
    return "\n".join(line[start:] for line in page_text.splitlines())


def check_pdf_fingerprint(source_bytes: bytes) -> str:
    actual_sha = hashlib.sha256(source_bytes).hexdigest()
    if actual_sha != PINNED_PDF_SHA256 or len(source_bytes) != PINNED_PDF_LENGTH:
        raise ValueError("Authoritative PRISMA PDF bytes differ from the pinned original")
    return actual_sha


def numbered_rows(text_pages: list[str]) -> dict[str, dict]:
    """Extract whole numbered rows, preserving the PDF's item/page binding."""
    if len(text_pages) != 2:
        raise ValueError("Expected exactly two pages of PDF-extracted text")
    rows = {}
    for page, page_text in enumerate(text_pages, 1):
        current = None
        for line in page_text.splitlines():
            if line.startswith("From:"):
                break
            match = re.search(r"\b([0-9]{1,2}[a-z]?)\s*$", line[:GUTTERS[page]])
            if match:
                number = match.group(1)
                if number not in EXPECTED_PAGES or EXPECTED_PAGES[number] != page:
                    raise ValueError(f"Unexpected item {number} on PDF page {page}")
                if number in rows:
                    raise ValueError(f"Duplicate PDF item {number}")
                current = number
                rows[number] = {"page": page, "parts": []}
            text = checklist_column(line, page).strip()
            if current is not None and text:
                rows[current]["parts"].append(text)
    if list(rows) != EXPECTED:
        raise ValueError("PDF must contain all 42 numbered item rows in order")
    return {
        number: {"page": row["page"], "text": "\n".join(row["parts"])}
        for number, row in rows.items()
    }


def extract_pdf_pages(source_bytes: bytes) -> list[str]:
    """Extract the exact bytes checked above, without reopening a mutable path."""
    check_pdf_fingerprint(source_bytes)
    extracted = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", "-", "-"],
        input=source_bytes, check=True, capture_output=True,
    ).stdout.decode("utf-8")
    return extracted.rstrip("\f").split("\f")


def verify_pdf(source_bytes: bytes, text_pages: list[str], ledger: dict, pack: dict) -> dict:
    actual_sha = check_pdf_fingerprint(source_bytes)
    source_items = checked_ledger_items(ledger)
    rows = numbered_rows(text_pages)
    comparisons = []
    for item in source_items.values():
        number, page = item["number"], item["page"]
        source = normalize(rows[number]["text"])
        expected_text = normalize(item["verbatim_text"])
        if rows[number]["page"] != page or expected_text != source:
            raise ValueError(f"Item {number} does not match the complete numbered PDF row on page {page}")
        comparisons.append({
            "item": number,
            "page": page,
            "source_pdf_sha256": actual_sha,
            "whitespace_normalized_text_sha256": hashlib.sha256(expected_text.encode()).hexdigest(),
            "whitespace_normalized_source_match": True,
            "comparison_method": "unicode_nfkc_whitespace_ignored_numbered_row_equality",
        })
    pack_audit = audit(pack, ledger)
    if pack_audit["errors"] or not pack_audit["item_level_source_reconciled"]:
        raise ValueError("Canonical PRISMA pack is not bound to the verified PDF item texts and source identity")
    return {
        "schema_version": "dev.standardflow.prisma-source-comparison.v1",
        "pdf_url": ledger["source_url"],
        "pdf_sha256": actual_sha,
        "pdf_length": len(source_bytes),
        "source_pages": len(text_pages),
        "item_count": len(comparisons),
        "pack_id": pack["pack_id"],
        "pack_version": pack["version"],
        "pack_item_source_parity": True,
        "comparisons": comparisons,
        "status": "machine_compared_source_text",
        "limitations": ["Comparison applies Unicode NFKC normalization and ignores whitespace",
                        "Human methodological and translation evaluation are not covered"],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--ledger", type=Path, default=LEDGER)
    p.add_argument("--pack", type=Path, default=PACK)
    args = p.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    pdf_bytes = args.pdf.read_bytes()
    pages = extract_pdf_pages(pdf_bytes)
    report = verify_pdf(pdf_bytes, pages, ledger, pack)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PRISMA source comparison passed for {report['item_count']} items")


if __name__ == "__main__":
    main()
