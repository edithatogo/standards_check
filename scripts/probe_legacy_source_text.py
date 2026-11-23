#!/usr/bin/env python3
"""Triangulate existing local original-document text with legacy items (never certify)."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import unicodedata

import yaml

try:
    from .reconcile_equator_sources import scan_local, scan_alias_assets
except ImportError:
    from reconcile_equator_sources import scan_local, scan_alias_assets

MAX_SOURCE_BYTES = 20_000_000
MAX_PAGES = 80


def normalise(text: str) -> str:
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))


def source_text(path: Path) -> tuple[str, str, str]:
    source = path.read_bytes()
    if len(source) > MAX_SOURCE_BYTES:
        raise ValueError("source_too_large")
    if path.suffix == ".pdf":
        import pdfplumber
        with pdfplumber.open(io.BytesIO(source)) as pdf:
            if len(pdf.pages) > MAX_PAGES:
                raise ValueError("too_many_pages")
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        method = "pdfplumber_text_only_no_ocr"
    elif path.suffix == ".docx":
        from docx import Document
        doc = Document(io.BytesIO(source))
        text = "\n".join([*(p.text for p in doc.paragraphs),
                          *(cell.text for table in doc.tables for row in table.rows for cell in row.cells)])
        method = "python_docx_paragraphs_and_tables"
    elif path.suffix == ".csv":
        text = "\n".join(" ".join(row) for row in csv.reader(io.StringIO(source.decode("utf-8-sig"))))
        method = "stdlib_csv"
    elif path.suffix == ".txt":
        text = source.decode("utf-8")
        method = "stdlib_text"
    else:
        raise ValueError("unsupported_document_format")
    return text, method, hashlib.sha256(source).hexdigest()


def fidelity_normalise(text: str) -> str:
    """Retain case and punctuation, normalizing Unicode and whitespace only."""
    return " ".join(unicodedata.normalize("NFKC", text).split())


def phrase_occurrences(source: str, phrase: str) -> int:
    if not phrase:
        return 0
    # Word boundaries prevent partial-token hits; lookahead counts overlaps.
    return sum(1 for _ in re.finditer(r"(?<!\w)(?=" + re.escape(phrase) + r"(?!\w))", source))


def evaluate_text(extracted: str, legacy_items: list[str]) -> dict:
    # ponytail: Phrase diagnostics only, not complete row or semantic equality.
    normalized = normalise(extracted)
    fidelity = fidelity_normalise(extracted)
    # Legacy Markdown sometimes prepends a bold item number and section title,
    # while the original PDF/DOCX arranges that label separately.
    label = re.compile(r"^\s*\*\*\d+[a-z]?(?:\.\d+)?[.)]?\s+[^*]{1,160}\*\*\s*", re.I)
    items = [label.sub("", item) for item in legacy_items]
    comparisons = []
    for ordinal, item in enumerate(items, 1):
        lexical = normalise(item)
        strict = fidelity_normalise(item)
        lexical_count = phrase_occurrences(normalized, lexical)
        fidelity_count = phrase_occurrences(fidelity, strict)
        short = len(lexical) < 40
        if not lexical:
            outcome = "empty_lexical"
        elif not lexical_count:
            outcome = "absent"
        elif lexical_count > 1 or fidelity_count > 1:
            outcome = "repeated"
        elif not fidelity_count:
            outcome = "lexical_only"
        else:
            outcome = "fidelity_phrase_present"
        comparisons.append({"legacy_ordinal": ordinal,
                            "legacy_fidelity_sha256": hashlib.sha256(strict.encode()).hexdigest(),
                            "short_for_legacy_metric": short,
                            "lexical_occurrences": lexical_count,
                            "fidelity_occurrences": fidelity_count,
                            "outcome": outcome})
    # Retain historical substring metric for comparability; it is not token-bounded.
    meaningful = [row for row in comparisons if not row["short_for_legacy_metric"]]
    return {"normalized_source_sha256": hashlib.sha256(normalized.encode()).hexdigest(),
            "fidelity_source_sha256": hashlib.sha256(fidelity.encode()).hexdigest(),
            "normalized_characters": len(normalized),
            "meaningful_legacy_items": len(meaningful),
            "exact_substring_matches": sum(len(lexical) >= 40 and lexical in normalized
                                           for lexical in map(normalise, items)),
            "token_bounded_legacy_matches": sum(row["lexical_occurrences"] > 0 for row in meaningful),
            "fidelity_legacy_matches": sum(row["fidelity_occurrences"] > 0 for row in meaningful),
            "item_comparisons": comparisons,
            "status": "triage_only_not_edition_verification"}


def legacy_items_from_markdown(path: Path) -> list[str]:
    return re.findall(r"^\s*[-*] \[[ xX]\]\s*(.+)$", path.read_text(encoding="utf-8"), re.M)


def audit(root: Path) -> dict:
    index = yaml.safe_load((root / "source/index.yml").read_text(encoding="utf-8"))
    items = index["items"]
    ids = {item["id"] for item in items}
    records = []
    for item in items:
        originals, views, _ = scan_local(root, item)
        if not originals:
            originals = scan_alias_assets(root, item, ids)
        legacy = legacy_items_from_markdown(root / views[0]) if views else []
        probes = []
        for original in originals:
            path = root / original["path"]
            if path.is_symlink():
                continue
            entry = {"path": original["path"], "source_sha256": original["sha256"],
                     "identity_basis": original.get("match_basis", "exact_filename_unverified"),
                     "rights": "unassessed"}
            try:
                extracted, method, digest = source_text(path)
                if digest != original["sha256"]:
                    raise ValueError("source_changed_since_inventory")
                entry.update(evaluate_text(extracted, legacy))
                entry["extractor"] = method
                if not extracted.strip():
                    entry["status"] = "empty_extraction_requires_review"
            except Exception as exc:  # third-party PDF/DOCX parser exceptions vary
                entry["status"] = "extraction_failed_or_unsupported"
                entry["error_type"] = type(exc).__name__
            probes.append(entry)
        records.append({"legacy_id": item["id"], "legacy_view_count": len(views),
                        "legacy_item_count": len(legacy), "source_probes": probes,
                        "qualification": "unverified_original_and_legacy_text"})
    return {"schema_version": 1, "authority": "no_source_or_legacy_content_admission",
            "legacy_item_count": len(records),
            "summary": {"records_with_original_candidates": sum(bool(row["source_probes"]) for row in records),
                        "source_probes": sum(len(row["source_probes"]) for row in records),
                        "successfully_extracted": sum(
                            p["status"] == "triage_only_not_edition_verification"
                            for row in records for p in row["source_probes"]),
                        "verified_by_this_process": 0},
            "legacy_items": records}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = audit(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Unverified local source text probes: {report['summary']}")


if __name__ == "__main__":
    main()
