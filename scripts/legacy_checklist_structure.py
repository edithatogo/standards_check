"""Bounded reader for legacy checklist Markdown, not an authority or CommonMark parser."""

from __future__ import annotations

import re

TASK = re.compile(r"^([ \t]*)[-*+]\s+\[[ xX]\](?:[ \t]+(.*)|[ \t]*)$")
BOLD = re.compile(r"^\*\*([^*\n]{1,160})\*\*[ \t]*")
ITEM_ID = re.compile(r"^(s?\d{1,3}(?:\.\d{1,3})*[a-z]?)(?=$|[.):\s])", re.I)
HEADING = re.compile(r"^ {0,3}#{1,6}(?:\s|$)")
FENCE = re.compile(r"^(`{3,}|~{3,})")
OTHER_BLOCK = re.compile(r"^(?:[-*+]\s|\d+[.)]\s|>|-{3,}$|\*{3,}$|_{3,}$|\[.*\]\{)")


def split_label(text: str) -> tuple[str | None, str]:
    """Strip only a conventional leading editorial label; retain declared ID separately."""
    label = BOLD.match(text)
    if label:
        number = ITEM_ID.match(label[1])
        if number or label[1].endswith(":"):
            return number[1].lower() if number else None, text[label.end() :]
    return None, text


def parse_legacy_tasks(markdown: str) -> list[dict]:
    """Preserve task lines, indented content and task ancestry; flag lazy wrapping.

    ponytail: supported repository task-list dialect only. No semantic inference,
    rendering, or claim that every Markdown construct is understood.
    """
    rows: list[dict] = []
    stack: list[tuple[int, dict]] = []
    section_line = None
    fence = None
    fence_row = None
    blank = False
    for number, line in enumerate(markdown.splitlines(), 1):
        expanded = line.expandtabs(4)
        stripped = expanded.strip()
        indent = len(expanded) - len(expanded.lstrip())
        if fence is not None:
            if fence_row is not None:
                fence_row["parts"].append(stripped)
                fence_row["line_numbers"].append(number)
                fence_row["line_indents"].append(indent)
            if stripped.startswith(fence) and not stripped.lstrip(fence[0]).strip():
                fence = fence_row = None
            continue
        marker = FENCE.match(stripped)
        if marker:
            fence = marker[1]
            while stack and indent <= stack[-1][0]:
                stack.pop()
            if stack:
                fence_row = stack[-1][1]
                fence_row["warnings"].append("fenced_content_requires_review")
                fence_row["parts"].append(stripped)
                fence_row["line_numbers"].append(number)
                fence_row["line_indents"].append(indent)
            continue
        if not stripped:
            blank = True
            continue
        if HEADING.match(expanded):
            stack.clear()
            section_line = number
        elif task := TASK.match(expanded):
            while stack and indent <= stack[-1][0]:
                stack.pop()
            declared, text = split_label(task[2] or "")
            row = {
                "position": len(rows) + 1,
                "declared_item_id": declared,
                "parent_position": stack[-1][1]["position"] if stack else None,
                "section_line": section_line,
                "line_numbers": [number],
                "line_indents": [indent],
                "raw_first_line": task[2] or "",
                "parts": [text],
                "warnings": [],
            }
            rows.append(row)
            stack.append((indent, row))
        else:
            while stack and (
                indent < stack[-1][0]
                or indent == stack[-1][0]
                and (blank or OTHER_BLOCK.match(stripped))
            ):
                stack.pop()
            if stack:
                row = stack[-1][1]
                if indent <= stack[-1][0]:
                    if "ambiguous_unindented_continuation" not in row["warnings"]:
                        row["warnings"].append("ambiguous_unindented_continuation")
                row["parts"].append(stripped)
                row["line_numbers"].append(number)
                row["line_indents"].append(indent)
        blank = False
    for row in rows:
        parts = row.pop("parts")
        row["raw_text"] = "\n".join([row.pop("raw_first_line"), *parts[1:]]).strip()
        row["text"] = "\n".join(parts).strip()
        if not row["text"]:
            row["warnings"].append("empty_requirement")
    return rows
