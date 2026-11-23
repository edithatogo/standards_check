"""Bounded DOCX/CSV/XLSX structural diagnostics; no source admission."""
from __future__ import annotations

import csv
import hashlib
import io
import re
import unicodedata
from zipfile import ZipFile

MAX_UNPACKED_BYTES = 64_000_000
MAX_CELLS = 100_000
MAX_DEPTH = 24
ITEM_ID = re.compile(r"(?:[Ss])?\d{1,3}(?:\.\d{1,3})*[a-zA-Z]?")


def fingerprint(text: str) -> str:
    return hashlib.sha256(" ".join(unicodedata.normalize("NFKC", text).split()).encode()).hexdigest()


def cell_fields(text: str) -> dict:
    value = text.strip()
    return {"text_sha256": fingerprint(text), "empty": not value,
            "item_id_candidate": value if ITEM_ID.fullmatch(value) else None}


def check_package(raw: bytes) -> list[str]:
    with ZipFile(io.BytesIO(raw)) as archive:
        members = archive.infolist()
        if (len(members) > 4096 or sum(item.file_size for item in members) > MAX_UNPACKED_BYTES
                or len({item.filename for item in members}) != len(members)
                or any(item.flag_bits & 1 for item in members)):
            raise ValueError("archive exceeds limits or has ambiguous/encrypted members")
        return [item.filename for item in members]


def docx_structure(raw: bytes) -> tuple[str, dict]:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.table import Table, _Cell
    from docx.text.paragraph import Paragraph

    members = check_package(raw)
    doc = Document(io.BytesIO(raw))
    issues = set()
    if any(re.match(r"word/(?:header|footer|footnotes|endnotes|comments)", name) for name in members):
        issues.add("non_body_parts_not_extracted")
    unsupported = {qn("w:" + name) for name in ("sdt", "ins", "del", "txbxContent", "drawing", "object",
                                                "altChunk", "fldSimple", "instrText", "footnoteReference",
                                                "endnoteReference", "sym")}
    if any(element.tag in unsupported for element in doc._element.iter()):
        issues.add("complex_docx_content_not_fully_extracted")
    count = 0

    def walk(parent, element, prefix: str, depth: int) -> tuple[list[dict], list[str]]:
        nonlocal count
        if depth > MAX_DEPTH:
            raise ValueError("DOCX nesting exceeds limit")
        blocks, texts = [], []
        for node in element:
            if node.tag in {qn("w:sectPr"), qn("w:tcPr")}:
                continue
            count += 1
            if count > MAX_CELLS:
                raise ValueError("DOCX structure exceeds limit")
            anchor = f"{prefix}/{len(blocks) + 1}"
            if node.tag == qn("w:p"):
                paragraph = Paragraph(node, parent)
                text = paragraph.text
                style = paragraph.style.style_id if paragraph.style else ""
                heading = re.fullmatch(r"Heading([1-9])", style)
                props = node.pPr
                num = props.numPr if props is not None else None
                if num is None and paragraph.style is not None:
                    style_props = paragraph.style.element.pPr
                    num = style_props.numPr if style_props is not None else None
                numbering = None if num is None else {
                    "id": num.numId.val if num.numId is not None else None,
                    "level": num.ilvl.val if num.ilvl is not None else None}
                if numbering is not None:
                    issues.add("rendered_numbering_not_resolved")
                blocks.append({"anchor": anchor, "kind": "paragraph", "heading_level": int(heading[1]) if heading else None,
                               "numbering": numbering, **cell_fields(text)})
                texts.append(text)
            elif node.tag == qn("w:tbl"):
                table = Table(node, parent)
                width = len(table.columns)
                active = {}
                rows = []
                for row_number, row in enumerate(table.rows, 1):
                    cells, row_text, following = [], [], {}
                    column = row._tr.grid_before + 1
                    row_anchor = f"{anchor}/r{row_number}"
                    for tc in row._tr.tc_lst:
                        count += 1
                        if count > MAX_CELLS:
                            raise ValueError("DOCX structure exceeds limit")
                        span = tc.grid_span
                        if span < 1 or column + span - 1 > width:
                            raise ValueError("invalid DOCX table grid")
                        cell_anchor = f"{row_anchor}/c{column}"
                        columns = tuple(range(column, column + span))
                        merge = tc.vMerge
                        origin = None
                        if merge == "continue":
                            origins = {active.get(c) for c in columns}
                            if len(origins) != 1 or None in origins:
                                issues.add("unbound_vertical_merge")
                            else:
                                origin = origins.pop()
                        elif merge == "restart":
                            origin = cell_anchor
                        if merge is not None and origin is not None:
                            following.update({c: origin for c in columns})
                        children, parts = walk(_Cell(tc, table), tc, cell_anchor, depth + 1)
                        text = "\n".join(parts)
                        if merge == "continue" and text.strip():
                            issues.add("nonempty_vertical_continuation")
                        cells.append({"anchor": cell_anchor, "column": column, "colspan": span,
                                      "vertical_merge": merge, "merge_origin": origin,
                                      "blocks": children, **cell_fields(text)})
                        row_text.extend(parts)
                        column += span
                    if column - 1 + row._tr.grid_after != width:
                        issues.add("incomplete_table_grid")
                    active = following
                    rows.append({"anchor": row_anchor, "grid_before": row._tr.grid_before,
                                 "grid_after": row._tr.grid_after, "cells": cells,
                                 "text_sha256": fingerprint("\n".join(row_text))})
                    texts.extend(row_text)
                blocks.append({"anchor": anchor, "kind": "table", "grid_width": width, "rows": rows})
            else:
                issues.add("unsupported_docx_block")
                blocks.append({"anchor": anchor, "kind": "unsupported"})
        return blocks, texts

    blocks, texts = walk(doc, doc._element.body, "body", 0)
    return "\n".join(texts), {"blocks": blocks, "issues": sorted(issues)}


def csv_structure(raw: bytes) -> tuple[str, dict]:
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    rows, texts, widths = [], [], set()
    previous = count = 0
    try:
        for number, values in enumerate(reader, 1):
            count += max(1, len(values))
            if count > MAX_CELLS:
                raise ValueError("CSV structure exceeds limit")
            anchor = f"row/{number}"
            cells = [{"anchor": f"{anchor}/c{col}", "column": col, **cell_fields(value)}
                     for col, value in enumerate(values, 1)]
            rows.append({"anchor": anchor, "physical_lines": [previous + 1, reader.line_num],
                         "cells": cells, "text_sha256": fingerprint(" ".join(values))})
            previous = reader.line_num
            widths.add(len(values))
            texts.append(" ".join(values))
    except csv.Error as exc:
        raise ValueError("malformed CSV") from exc
    return "\n".join(texts), {"rows": rows, "issues": ["ragged_csv_rows"] if len(widths) > 1 else []}


def xlsx_structure(raw: bytes) -> tuple[str, dict]:
    from openpyxl import load_workbook
    from openpyxl.utils import get_column_letter, range_boundaries
    from lxml import etree

    members = check_package(raw)
    issues = set()
    if any(name.startswith(("xl/drawings/", "xl/externalLinks/", "xl/comments", "xl/charts/")) for name in members):
        issues.add("non_cell_workbook_content_not_extracted")
    # Preflight actual worksheet parts before openpyxl expands merged ranges.
    preview = load_workbook(io.BytesIO(raw), read_only=True, data_only=False, keep_links=False)
    try:
        area = 0
        with ZipFile(io.BytesIO(raw)) as archive:
            for sheet in preview.worksheets:
                root = etree.fromstring(archive.read(sheet._worksheet_path),
                                        parser=etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False))
                max_row = max_col = 1
                for element in root.iter():
                    tag = etree.QName(element).localname if isinstance(element.tag, str) else ""
                    if tag not in {"dimension", "mergeCell", "c"}:
                        continue
                    address = element.get("r" if tag == "c" else "ref")
                    if not address:
                        continue
                    left, top, right, bottom = range_boundaries(address)
                    if None in (left, top, right, bottom) or not (1 <= left <= right and 1 <= top <= bottom):
                        raise ValueError("invalid XLSX cell range")
                    max_row, max_col = max(max_row, bottom), max(max_col, right)
                area += max_row * max_col
                if area > MAX_CELLS:
                    raise ValueError("XLSX grid exceeds limit")
    finally:
        preview.close()
    book = load_workbook(io.BytesIO(raw), data_only=False, keep_links=False)
    sheets, texts, count = [], [], 0
    try:
        if len(book.worksheets) != len(book.sheetnames):
            issues.add("non_worksheet_sheet_not_extracted")
        for number, sheet in enumerate(book.worksheets, 1):
            count += sheet.max_row * sheet.max_column
            if count > MAX_CELLS:
                raise ValueError("XLSX grid exceeds limit")
            rows = []
            for row_number, row in enumerate(sheet.iter_rows(), 1):
                cells, row_text = [], []
                for column, cell in enumerate(row, 1):
                    value = cell.value
                    text = "" if value is None else str(value)
                    if cell.data_type == "f":
                        issues.add("formula_cells_not_evaluated")
                    else:
                        row_text.append(text)
                    cells.append({"anchor": f"sheet/{number}/{get_column_letter(column)}{row_number}",
                                  "value_type": cell.data_type, **cell_fields(text)})
                rows.append({"anchor": f"sheet/{number}/row/{row_number}", "row": row_number, "hidden": bool(sheet.row_dimensions[row_number].hidden),
                             "cells": cells, "text_sha256": fingerprint(" ".join(row_text))})
                texts.append(" ".join(row_text))
            sheets.append({"ordinal": number, "name_sha256": fingerprint(sheet.title), "state": sheet.sheet_state,
                           "merged_ranges": sorted(str(r) for r in sheet.merged_cells.ranges),
                           "hidden_column_ranges": sorted([d.min, d.max] for d in sheet.column_dimensions.values() if d.hidden),
                           "rows": rows})
    finally:
        book.close()
    return "\n".join(texts), {"sheets": sheets, "issues": sorted(issues)}


def extract_structure(raw: bytes, suffix: str) -> tuple[str, dict]:
    readers = {".docx": docx_structure, ".csv": csv_structure, ".xlsx": xlsx_structure}
    if suffix not in readers:
        raise ValueError("unsupported structured source")
    text, report = readers[suffix](raw)
    return text, {"format": suffix[1:], "status": "held_structural_discrepancy" if report["issues"] else
                  "structure_observed_not_qualified", **report}
