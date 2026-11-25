"""Fingerprint-only structural evidence for a selected JATS checklist table."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from xml.etree import ElementTree as ET

BLOCKS = {"p", "list-item", "def-item", "disp-quote", "break"}


def digest(text: str) -> str:
    normalized = " ".join(unicodedata.normalize("NFKC", text).split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def cell_content(cell: ET.Element) -> dict:
    blocks = []

    def visit(node: ET.Element, path: str, depth: int) -> str:
        if depth > 64:
            raise ValueError("cell nesting exceeds structural limit")
        block = node.tag in BLOCKS
        if block:
            blocks.append(
                {"path": path, "tag": node.tag, "text_sha256": digest("".join(node.itertext()))}
            )
        parts = [node.text or ""]
        for i, child in enumerate(node, 1):
            parts.extend((visit(child, f"{path}/{i}", depth + 1), child.tail or ""))
        text = "".join(parts)
        return " " + text + " " if block else text

    flat = digest("".join(cell.itertext()))
    bounded = digest(visit(cell, "cell", 0))
    refs = sorted(
        {
            rid
            for node in cell.iter("xref")
            if node.get("ref-type") in {"fn", "table-fn"}
            for rid in node.get("rid", "").split()
        }
    )
    return {
        "flat_text_sha256": flat,
        "block_text_sha256": bounded,
        "block_boundary_loss": flat != bounded,
        "blocks": blocks,
        "footnote_refs": refs,
    }


def describe_table(wrapper: ET.Element, numbered_rows: list[dict]) -> dict:
    """Observe the same body-row sequence as the existing pinned row extractor.

    ponytail: one bounded rectangular table; unsupported layouts are held rather
    than guessed. Existing source row hashes are not replaced by this receipt.
    """
    table_id = wrapper.get("id")
    tables = wrapper.findall(".//table")
    if not table_id or len(tables) != 1:
        raise ValueError("expected one anchored non-nested checklist table")
    table = tables[0]
    bodies = table.findall("tbody")
    if not bodies or [row for body in bodies for row in body.findall("tr")] != wrapper.findall(
        ".//tbody/tr"
    ):
        raise ValueError("unsupported checklist row grouping")
    anchors = {}
    for entry in numbered_rows:
        anchor = entry["source_anchor"]
        match = re.fullmatch(re.escape(table_id) + r":row:([1-9]\d*):item:.+", anchor)
        if not match or int(match[1]) in anchors:
            raise ValueError("invalid or duplicate numbered source row anchor")
        anchors[int(match[1])] = anchor
    issues = set()
    rows = []
    section = None
    position = 0
    for body in bodies:
        active: dict[int, tuple[int, str]] = {}
        body_rows = body.findall("tr")
        for offset, row in enumerate(body_rows):
            position += 1
            active = {col: span for col, span in active.items() if span[0] >= offset}
            inherited = sorted({span[1] for span in active.values()})
            occupied = set(active)
            cells = []
            column = 1
            for cell_number, cell in enumerate(row, 1):
                if cell.tag not in {"td", "th"}:
                    raise ValueError("unsupported row child")
                while column in occupied:
                    column += 1
                rowspan = int(cell.get("rowspan", "1"))
                colspan = int(cell.get("colspan", "1"))
                if (
                    not 1 <= rowspan <= len(body_rows) - offset
                    or not 1 <= colspan <= 128
                    or column + colspan > 129
                ):
                    raise ValueError("unsupported or invalid cell span")
                covered = set(range(column, column + colspan))
                if covered & occupied:
                    raise ValueError("overlapping cell spans")
                anchor = f"{table_id}:row:{position}:cell:{cell_number}"
                info = cell_content(cell)
                if info["block_boundary_loss"]:
                    issues.add("block_boundary_difference")
                cells.append(
                    {
                        "anchor": anchor,
                        "column": column,
                        "rowspan": rowspan,
                        "colspan": colspan,
                        "tag": cell.tag,
                        **info,
                    }
                )
                occupied.update(covered)
                if rowspan > 1:
                    active.update({col: (offset + rowspan - 1, anchor) for col in covered})
                column += colspan
            if position in anchors:
                role = "numbered_item"
            elif len(cells) == 1 and cells[0]["colspan"] > 1 and not inherited:
                role = "candidate_section"
                section = position
            else:
                role = "unclassified"
                issues.add("unclassified_row")
            rows.append(
                {
                    "row": position,
                    "role": role,
                    "source_anchor": anchors.get(position),
                    "section_row": section,
                    "inherited_cells": inherited,
                    "cells": cells,
                }
            )
    if not set(anchors) <= {row["row"] for row in rows}:
        raise ValueError("numbered source anchor missing from table structure")
    footnotes = [
        {"id": fn.get("id"), "text_sha256": digest("".join(fn.itertext()))}
        for fn in wrapper.iter("fn")
    ]
    note_ids = [note["id"] for note in footnotes if note["id"]]
    if len(set(note_ids)) != len(note_ids):
        issues.add("duplicate_footnote_id")
    if any(
        ref not in note_ids
        for row in rows
        for cell in row["cells"]
        for ref in cell["footnote_refs"]
    ):
        issues.add("unresolved_footnote_reference")
    other_blocks = [
        {"tag": node.tag, "text_sha256": digest("".join(node.itertext()))}
        for node in [
            *table.findall("thead"),
            *table.findall("tfoot"),
            *wrapper.findall("table-wrap-foot"),
        ]
    ]
    return {
        "status": "held_structural_discrepancy" if issues else "structure_observed_not_qualified",
        "issues": sorted(issues),
        "rows": rows,
        "footnotes": footnotes,
        "other_blocks": other_blocks,
    }
