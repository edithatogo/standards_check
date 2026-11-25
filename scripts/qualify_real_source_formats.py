"""Explicit local publisher HTML and independent pinned PDF comparison; never admission."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from .build_prisma42_candidate import EXPECTED, EXPECTED_PAGES
from .compare_ecoevo_formats import collect_rows, pdf_tables, read_bounded
from .compare_prisma_source_pdf import check_pdf_fingerprint, extract_pdf_pages, numbered_rows
from .reconcile_authoritative_articles import snapshot_table
from .structured_source import fingerprint, html_structure

DOI = "10.1186/s13643-020-01542-z"
HTML_HEADERS = tuple(map(fingerprint, ("SECTION/TOPIC", "ITEM #", "CHECKLIST ITEM")))
GROUPS = {
    "INFORMATION SOURCES AND METHODS": [str(i) for i in range(1, 8)],
    "SEARCH STRATEGIES": [str(i) for i in range(8, 14)],
    "PEER REVIEW": ["14"],
    "MANAGING RECORDS": ["15", "16"],
}
EMPTY = fingerprint("")
PDF_ID = re.compile(r"[0-9]{1,2}[a-z]?")
PDF_HEADERS = {fingerprint("Item"): "id", fingerprint("Checklist item"): "requirement"}
ROOT = Path(__file__).resolve().parents[1]


def html_table_receipt(structure: dict, reference: list[dict], groups: dict) -> dict:
    """Compare ordered, unspanned item rows and authored section headings."""
    result = {"rows": [], "section_anchors": [], "issues": list(structure["issues"])}
    matches = []
    for table in structure["blocks"]:
        for index, row in enumerate(table["rows"]):
            cells = row["cells"]
            if (
                tuple(cell["text_sha256"] for cell in cells) == HTML_HEADERS
                and [cell["column"] for cell in cells] == [1, 2, 3]
                and not row["inherited_cells"]
                and all(cell["colspan"] == cell["rowspan"] == 1 for cell in cells)
            ):
                matches.append((table, index))
    if len(matches) != 1:
        result["issues"].append("missing_or_ambiguous_checklist_table")
        return {**result, "exact_rows_and_hierarchy": False}
    table, offset = matches[0]
    if offset:
        result["issues"].append("unclassified_rows_before_header")
    by_id = {row["item_id"]: row for row in reference}
    headings = {fingerprint(group): group for group in groups}
    expected_group = {item: group for group, items in groups.items() for item in items}
    current = None
    seen_groups = []
    for row in table["rows"][offset + 1 :]:
        cells = row["cells"]
        nonempty = [cell for cell in cells if cell["text_sha256"] != EMPTY]
        if (
            len(nonempty) == 1
            and nonempty[0]["text_sha256"] in headings
            and nonempty[0]["column"] == 1
            and not row["inherited_cells"]
            and all(cell["rowspan"] == 1 for cell in cells)
        ):
            current = headings[nonempty[0]["text_sha256"]]
            seen_groups.append(current)
            result["section_anchors"].append(
                {"section_sha256": fingerprint(current), "anchor": row["anchor"]}
            )
            continue
        if (
            [cell["column"] for cell in cells] != [1, 2, 3]
            or row["inherited_cells"]
            or any(cell["colspan"] != 1 or cell["rowspan"] != 1 for cell in cells)
        ):
            result["issues"].append("unbound_or_spanned_item_row")
            continue
        topic, identifier, requirement = cells
        item = identifier["item_id_candidate"]
        original = by_id.get(item)
        if original is None:
            result["issues"].append("unknown_or_unbound_item")
            continue
        result["rows"].append(
            {
                "item_id": item,
                "identifier_anchor": identifier["anchor"],
                "requirement_anchor": requirement["anchor"],
                "topic_anchor": topic["anchor"],
                "section_sha256": fingerprint(current) if current else None,
                "requirement_sha256": requirement["text_sha256"],
                "topic_equal": topic["text_sha256"] == fingerprint(original["topic"]),
                "requirement_equal": requirement["text_sha256"] == fingerprint(original["text"]),
                "section_equal": current == expected_group.get(item),
            }
        )
    result["issues"] = sorted(set(result["issues"]))
    exact = (
        seen_groups == list(groups)
        and [row["item_id"] for row in result["rows"]] == [row["item_id"] for row in reference]
        and all(
            row["topic_equal"] and row["requirement_equal"] and row["section_equal"]
            for row in result["rows"]
        )
        and not (set(result["issues"]) - {"rendered_visibility_not_qualified"})
    )
    return {**result, "exact_rows_and_hierarchy": exact}


def html_identity(raw: bytes) -> bool:
    """Require explicit DOI metadata or an exact HTTPS publisher canonical link."""
    from lxml import html

    root = html.document_fromstring(
        raw.decode("utf-8-sig"), parser=html.HTMLParser(no_network=True)
    )
    metadata = root.xpath(
        "//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')"
        "='citation_doi']/@content"
    )
    if DOI in metadata:
        return True
    for href in root.xpath("//link[@rel='canonical']/@href"):
        parsed = urlsplit(href)
        if (
            parsed.scheme == "https"
            and parsed.netloc == "link.springer.com"
            and parsed.path in {f"/article/{DOI}", f"/article/{DOI}/tables/1"}
        ):
            return True
    return False


def compare_pdf_rows(rows: list[dict], poppler: dict, expected: list[str], pages: dict) -> dict:
    """Require complete numbered rows, order, page binding and whole-text equality."""
    counts = Counter(row["item_id"] for row in rows)
    comparisons = []
    for row in rows:
        item = row["item_id"]
        other = poppler.get(item)
        page = re.match(r"page/([0-9]+)/", row["requirement_anchor"] or "")
        comparisons.append(
            {
                **row,
                "page_equal": bool(
                    page and other and int(page[1]) == other["page"] == pages.get(item)
                ),
                "complete_text_equal": bool(
                    other and row["requirement_sha256"] == fingerprint(other["text"])
                ),
                "poppler_page": other["page"] if other else None,
                "poppler_text_sha256": fingerprint(other["text"]) if other else None,
            }
        )
    return {
        "rows": comparisons,
        "missing_ids": [item for item in expected if not counts[item]],
        "duplicate_ids": sorted(item for item, count in counts.items() if count > 1),
        "exact_rows": [row["item_id"] for row in rows] == expected
        and list(poppler) == expected
        and all(row["page_equal"] and row["complete_text_equal"] for row in comparisons),
    }


def pdf_receipt(raw: bytes) -> dict:
    digest = check_pdf_fingerprint(raw)
    rows, issues = collect_rows(
        pdf_tables(raw), identifier_pattern=PDF_ID, header_roles=PDF_HEADERS
    )
    poppler = numbered_rows(extract_pdf_pages(raw))
    result = compare_pdf_rows(rows, poppler, EXPECTED, EXPECTED_PAGES)
    return {
        **result,
        "source_sha256": digest,
        "source_bytes": len(raw),
        "issues": issues,
        "poppler_item_count": len(poppler),
        "pdfplumber_item_count": len(rows),
        "status": "bounded_independent_pdf_row_agreement"
        if result["exact_rows"] and not issues
        else "held",
    }


def html_receipt(raw: bytes, spec: dict, retained: dict) -> dict:
    reference = snapshot_table(retained, spec)
    _, structure = html_structure(raw)
    result = html_table_receipt(structure, reference["rows"], GROUPS)
    identity = html_identity(raw)
    return {
        **result,
        "identity_observed": identity,
        "html_sha256": hashlib.sha256(raw).hexdigest(),
        "jats_source_sha256": reference["source_sha256"],
        "jats_table_rows_sha256": reference["table_rows_sha256"],
        "status": "bounded_authored_html_row_agreement"
        if identity and result["exact_rows_and_hierarchy"]
        else "held",
    }


def report(root: Path, html: Path | None = None) -> dict:
    result = {
        "schema_version": 1,
        "canonical_packs_promoted": 0,
        "claim_boundary": "candidate-only authored HTML and independent PDF row diagnostics",
        "html": {"status": "held_not_acquired"},
        "pdf": {"status": "held"},
    }
    try:
        result["pdf"] = pdf_receipt(
            read_bounded(root / "source/official/prisma-2020-checklist.pdf")
        )
    except Exception as exc:  # parser failures remain held; no raw source text
        result["pdf"]["error"] = type(exc).__name__
    if html is not None:
        try:
            official = root / "source/official"
            specs = json.loads(read_bounded(official / "authoritative-article-editions.json"))
            snapshots = json.loads(read_bounded(official / "authoritative-article-rows.json"))
            spec = next(
                row for row in specs if row["edition"] == "prisma-s-2021" and row["doi"] == DOI
            )
            retained = next(
                row for row in snapshots["editions"] if row["edition"] == spec["edition"]
            )
            result["html"] = html_receipt(read_bounded(html), spec, retained)
        except Exception as exc:  # missing bytes or pins cannot qualify
            result["html"] = {"status": "held", "error": type(exc).__name__}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--html", type=Path, help="Explicitly acquired publisher table bytes")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report(args.root, args.html), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
