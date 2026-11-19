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
import subprocess
import unicodedata

from scripts.build_prisma42_candidate import EXPECTED, LEDGER

PINNED_PDF_SHA256 = "2eedbd5452741f9615307a0bce21a8198c0597ce2a0a8a0fd7e140d64b08c625"
PINNED_PDF_LENGTH = 67506


def normalize(text: str) -> str:
    return "".join(
        c.casefold() for c in unicodedata.normalize("NFKC", text) if c.isalnum()
    )


def checklist_column(page_text: str, page: int) -> str:
    """Read only the item text; the two PDF pages have distinct left gutters."""
    if page not in (1, 2):
        raise ValueError("Unexpected PDF page")
    start = 30 if page == 1 else 28
    return "\n".join(line[start:] for line in page_text.splitlines())


def verify_pdf(source_bytes: bytes, text_pages: list[str], ledger: dict) -> dict:
    actual_sha = hashlib.sha256(source_bytes).hexdigest()
    if actual_sha != PINNED_PDF_SHA256 or len(source_bytes) != PINNED_PDF_LENGTH:
        raise ValueError("Authoritative PRISMA PDF bytes differ from the pinned original")
    if len(text_pages) != 2:
        raise ValueError("Expected exactly two pages of PDF-extracted text")
    if [r["number"] for r in ledger["items"]] != EXPECTED:
        raise ValueError("Incomplete or unordered PRISMA item/subitem list")
    comparisons = []
    for item in ledger["items"]:
        number, page = item["number"], item["page"]
        source = normalize(checklist_column(text_pages[page - 1], page))
        expected_text = normalize(item["verbatim_text"])
        if not expected_text or expected_text not in source:
            raise ValueError(f"Item {number} not found verbatim (word-normalized) on PDF page {page}")
        comparisons.append({
            "item": number,
            "page": page,
            "source_pdf_sha256": actual_sha,
            "word_normalized_text_sha256": hashlib.sha256(expected_text.encode()).hexdigest(),
            "word_normalized_source_match": True,
            "comparison_method": "normalized_unicode_alphanumeric_contiguous_substring",
        })
    return {
        "schema_version": "dev.standardflow.prisma-source-comparison.v1",
        "pdf_url": ledger["source_url"],
        "pdf_sha256": actual_sha,
        "pdf_length": len(source_bytes),
        "source_pages": len(text_pages),
        "item_count": len(comparisons),
        "comparisons": comparisons,
        "status": "machine_compared_source_text",
        "limitations": ["Whitespace and punctuation are normalized during comparison",
                        "Human methodological and translation evaluation are not covered"],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    pdf_bytes = args.pdf.read_bytes()
    extracted = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(args.pdf), "-"],
        check=True, capture_output=True, text=True,
    ).stdout
    pages = extracted.rstrip("\f").split("\f")
    report = verify_pdf(pdf_bytes, pages, ledger)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PRISMA source comparison passed for {report['item_count']} items")


if __name__ == "__main__":
    main()
