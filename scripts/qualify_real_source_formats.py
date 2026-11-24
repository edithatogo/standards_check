"""Bounded HTML/JATS and independently parsed PDF qualification, never admission.

Read local or explicitly acquired bytes only. Report hashes/anchors, never source text.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

from .build_prisma42_candidate import EXPECTED, EXPECTED_PAGES
from .compare_prisma_source_pdf import check_pdf_fingerprint, extract_pdf_pages, numbered_rows
from .compare_ecoevo_formats import collect_rows, pdf_tables, read_bounded
from .structured_source import fingerprint, html_structure

HTML_URL = "https://link.springer.com/article/10.1186/s13643-020-01542-z/tables/1"
DOI = "10.1186/s13643-020-01542-z"
HTML_HEADERS = tuple(map(fingerprint, ("SECTION/TOPIC", "ITEM #", "CHECKLIST ITEM")))
GROUPS = {"INFORMATION SOURCES AND METHODS": [str(i) for i in range(1, 8)],
          "SEARCH STRATEGIES": [str(i) for i in range(8, 14)],
          "PEER REVIEW": ["14"], "MANAGING RECORDS": ["15", "16"]}
EMPTY = fingerprint("")
PDF_ID = re.compile(r"[0-9]{1,2}[a-z]?")
ROOT = Path(__file__).resolve().parents[1]


def html_table_receipt(structure: dict, reference: list[dict], groups: dict) -> dict:
    """Use authored table cells, ordered source headings and whole JATS row text."""
    tables = []
    for table in structure["blocks"]:
        for offset, row in enumerate(table["rows"]):
            cells = row["cells"]
            if (tuple(cell["text_sha256"] for cell in cells) == HTML_HEADERS
                    and [cell["column"] for cell in cells] == [1, 2, 3]
                    and not row["inherited_cells"]
                    and all(cell["colspan"] == cell["rowspan"] == 1 for cell in cells)):
                tables.append((table, offset))
    result = {"rows": [], "section_anchors": [], "issues": list(structure["issues"]),
              "exact_rows_and_hierarchy": False}
    if len(tables) != 1:
        result["issues"].append("missing_or_ambiguous_checklist_table")
        return result
    table, offset = tables[0]
    if offset:
        result["issues"].append("unclassified_rows_before_header")
    by_id = {r["item_id"]: r for r in reference}
    headings = {fingerprint(group): group for group in groups}
    expected_group = {item: group for group, ids in groups.items() for item in ids}
    seen_groups = []
    current = None
    structural_error = bool(offset)
    for row in table["rows"][offset + 1:]:
        cells = row["cells"]
        nonempty = [cell for cell in cells if cell["text_sha256"] != EMPTY]
        if (len(nonempty) == 1 and nonempty[0]["text_sha256"] in headings
                and nonempty[0]["column"] == 1 and not row["inherited_cells"]
                and all(cell["rowspan"] == 1 for cell in cells)):
            current = headings[nonempty[0]["text_sha256"]]
            seen_groups.append(current)
            result["section_anchors"].append({"section_sha256": fingerprint(current), "anchor": row["anchor"]})
            continue
        if ([cell["column"] for cell in cells] != [1, 2, 3] or row["inherited_cells"]
                or any(cell["colspan"] != 1 or cell["rowspan"] != 1 for cell in cells)):
            structural_error = True
            result["issues"].append("unbound_or_spanned_item_row")
            continue
        topic, identifier, requirement = cells
        item = identifier["item_id_candidate"]
        original = by_id.get(item)
        if original is None:
            structural_error = True
            result["issues"].append("unknown_or_unbound_item")
            continue
        result["rows"].append({
            "item_id": item, "identifier_anchor": identifier["anchor"],
            "requirement_anchor": requirement["anchor"], "topic_anchor": topic["anchor"],
            "section_sha256": fingerprint(current) if current else None,
            "requirement_sha256": requirement["text_sha256"],
            "topic_equal": topic["text_sha256"] == fingerprint(original["topic"]),
            "requirement_equal": requirement["text_sha256"] == fingerprint(original["text"]),
            "section_equal": current == expected_group.get(item),
        })
    result["exact_rows_and_hierarchy"] = (
        not structural_error and seen_groups == list(groups)
        and [r["item_id"] for r in result["rows"]] == [r["item_id"] for r in reference]
        and all(r["topic_equal"] and r["requirement_equal"] and r["section_equal"] for r in result["rows"])
        and not (set(structure["issues"]) - {"rendered_visibility_not_qualified"})
    )
    result["issues"] = sorted(set(result["issues"]))
    return result


def html_identity(raw: bytes) -> bool:
    from lxml import html

    root = html.document_fromstring(raw.decode("utf-8-sig"), parser=html.HTMLParser(no_network=True))
    if DOI in root.xpath("//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='citation_doi']/@content"):
        return True
    for href in root.xpath("//a/@href | //link[@rel='canonical']/@href"):
        parsed = urlsplit(href)
        if parsed.netloc in {"", "link.springer.com"} and parsed.path in {
            f"/article/{DOI}", f"/article/{DOI}/tables/1"
        }:
            return True
    return False


def compare_pdf_rows(rows: list[dict], poppler: dict, expected: list[str], pages: dict) -> dict:
    """Compare independently extracted, numbered complete rows on their actual pages."""
    counts = Counter(row["item_id"] for row in rows)
    comparisons = []
    for row in rows:
        item = row["item_id"]
        other = poppler.get(item)
        page = re.match(r"page/([0-9]+)/", row["requirement_anchor"] or "")
        page_equal = bool(page and other and int(page[1]) == other["page"] == pages.get(item))
        equal = bool(other and row["requirement_sha256"] == fingerprint(other["text"]))
        comparisons.append({**row, "page_equal": page_equal, "complete_text_equal": equal,
                            "poppler_page": other["page"] if other else None,
                            "poppler_text_sha256": fingerprint(other["text"]) if other else None})
    return {"rows": comparisons, "missing_ids": [item for item in expected if not counts[item]],
            "duplicate_ids": sorted(item for item, count in counts.items() if count > 1),
            "exact_rows": [r["item_id"] for r in rows] == expected and list(poppler) == expected
            and all(row["page_equal"] and row["complete_text_equal"] for row in comparisons)}


def pdf_receipt(raw: bytes) -> dict:
    import pdfplumber

    digest = check_pdf_fingerprint(raw)
    result = {"source_sha256": digest, "source_bytes": len(raw), "pdfplumber_version": pdfplumber.__version__,
              "normalization": "NFKC and collapse whitespace, punctuation/case preserved",
              "status": "held"}
    rows, issues, poppler = [], [], {}
    # Each parser receives the original pinned PDF, not the other's intermediate text.
    try:
        rows, issues = collect_rows(pdf_tables(raw, {"item": "id", "checklistitem": "requirement"}), PDF_ID)
    except Exception as exc:
        issues.append("pdfplumber_failed:" + type(exc).__name__)
    try:
        version = subprocess.run(["pdftotext", "-v"], capture_output=True, timeout=5, check=True)
        result["poppler_version"] = version.stderr.decode("utf-8").splitlines()[0]
        poppler = numbered_rows(extract_pdf_pages(raw))
    except Exception as exc:
        issues.append("poppler_failed:" + type(exc).__name__)
    result.update(compare_pdf_rows(rows, poppler, EXPECTED, EXPECTED_PAGES), issues=issues,
                  poppler_item_count=len(poppler), pdfplumber_item_count=len(rows))
    if result["exact_rows"] and not issues:
        result["status"] = "bounded_independent_pdf_row_agreement"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--html", type=Path, help="Explicitly acquired publisher table bytes")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root
    report = {"schema_version": 1, "canonical_packs_promoted": 0,
              "claim_boundary": "bounded authored HTML/JATS and independent PDF row diagnostics; no rights or admission",
              "html": {"url": HTML_URL, "doi": DOI, "status": "held_not_acquired"},
              "pdf": {"status": "held"}}
    try:
        report["pdf"] = pdf_receipt(read_bounded(root / "source/official/prisma-2020-checklist.pdf"))
    except Exception as exc:
        report["pdf"]["error"] = type(exc).__name__
    if args.html is not None and args.html.is_file():
        try:
            raw = read_bounded(args.html)
            from lxml import etree
            receipt = report["html"]
            receipt.update(source_sha256=hashlib.sha256(raw).hexdigest(), source_bytes=len(raw),
                           lxml_version=".".join(map(str, etree.LXML_VERSION)), identity_observed=html_identity(raw),
                           status="held")
            manifest = json.loads((root / "source/official/authoritative-article-rows.json").read_text())
            ref = next(e for e in manifest["editions"] if e["edition"] == "prisma-s-2021" and e["doi"] == DOI)
            receipt["jats_source_sha256"] = ref["source_sha256"]
            receipt["jats_ledger_sha256"] = hashlib.sha256(
                (root / "source/official/authoritative-article-rows.json").read_bytes()).hexdigest()
            _, structure = html_structure(raw)
            receipt.update(html_table_receipt(structure, ref["rows"], GROUPS))
            if receipt["identity_observed"] and receipt["exact_rows_and_hierarchy"]:
                receipt["status"] = "bounded_authored_html_row_agreement"
        except Exception as exc:
            report["html"].update(status="held", error=type(exc).__name__)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PDF:", report["pdf"]["status"], "HTML:", report["html"]["status"])


if __name__ == "__main__":
    main()
