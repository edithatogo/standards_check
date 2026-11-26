"""Bounded literal EQUATOR checklist data; no JavaScript execution or source admission."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from .compare_guideline_formats import summarize_source
from .structured_source import ITEM_ID, fingerprint

UPSTREAM = "388e294f05d4d55cf6fc01ddf56b6ad48577b190"
PINS = {
    "consort": (
        "9fb87d664eedb2751072a99983be23834dabb8ea",
        "40a1c80d2db176c65e4f3e5df25a22ed292d3137",
    ),
    "spirit": (
        "2c12bb6421e74ef2e4ce335ded679ab7f715b27e",
        "8d8009c03050b05902f4887b251cf7413e77b7a2",
    ),
}


def literal_rows(raw, doi, expected_ids):
    if len(raw) > 128_000 or not expected_ids or len(set(expected_ids)) != len(expected_ids):
        raise ValueError("invalid bounded source or reference")
    source = raw.decode("utf-8")
    for role, marker in (("cite", doi), ("lic", "https://creativecommons.org/licenses/by/4.0/")):
        notices = re.findall(rf'<p class="tp-{role}">(.*?)</p>', source, re.S)
        if len(notices) != 1 or marker not in notices[0]:
            raise ValueError("source identity or local licence notice missing")
    matches = list(re.finditer(r"(?m)^[ \t]*const ROWS = [ \t]*", source))
    if len(matches) != 1:
        raise ValueError("ambiguous literal rows")
    try:
        data, end = json.JSONDecoder().raw_decode(source, matches[0].end())
    except RecursionError as exc:
        raise ValueError("nested literal exceeds bounds") from exc
    if not re.match(r"[ \t]*;[ \t]*(?:\r?\n|$)", source[end:]):
        raise ValueError("expected a literal array, not a computed expression")
    if not isinstance(data, list) or not 0 < len(data) <= 1000:
        raise ValueError("invalid literal row array")
    rows, groups = [], []
    section = label = None
    for i, value in enumerate(data):
        anchor = f"ROWS/{i}"
        if isinstance(value, str) and value.strip():
            section, label = anchor, None
            groups.append({"kind": "section", "anchor": anchor, "text_sha256": fingerprint(value)})
            continue
        if not isinstance(value, list) or section is None:
            raise ValueError("unbound or malformed row group")
        if len(value) == 2 and value[0] == "L" and isinstance(value[1], str) and value[1].strip():
            label = anchor + "/1"
            groups.append({"kind": "label", "anchor": label, "text_sha256": fingerprint(value[1])})
            continue
        if len(value) != 3:
            raise ValueError("invalid topic group")
        topic, indent, items = value
        if (
            not isinstance(topic, str)
            or not topic.strip()
            or type(indent) is not bool
            or not isinstance(items, list)
            or not items
            or (indent and label is None)
        ):
            raise ValueError("invalid topic or indentation")
        if not indent:
            label = None
        groups.append(
            {
                "kind": "topic",
                "anchor": anchor + "/0",
                "text_sha256": fingerprint(topic),
                "section_anchor": section,
                "label_anchor": label,
                "indented": indent,
            }
        )
        for j, item in enumerate(items):
            if (
                not isinstance(item, list)
                or len(item) != 2
                or not isinstance(item[0], str)
                or not ITEM_ID.fullmatch(item[0])
                or not isinstance(item[1], str)
                or not item[1].strip()
            ):
                raise ValueError("invalid numbered requirement")
            item_anchor = f"{anchor}/2/{j}"
            rows.append(
                {
                    "item_id": item[0],
                    "identifier_anchor": item_anchor + "/0",
                    "requirement_anchor": item_anchor + "/1",
                    "requirement_sha256": fingerprint(item[1]),
                    "verbatim_sha256": hashlib.sha256(item[1].encode()).hexdigest(),
                    "section_anchor": section,
                    "topic_anchor": anchor + "/0",
                    "label_anchor": label,
                    "indented": indent,
                }
            )
    result = summarize_source(rows, tuple(expected_ids), [])
    return {
        **result,
        "rows": rows,
        "groups": groups,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "notice_observed": "CC-BY-4.0",
        "status": (
            "held_structural_discrepancy"
            if result["issues"]
            else "structure_observed_not_qualified"
        ),
        "canonical_packs_promoted": 0,
    }


def pinned_bytes(path, expected):
    with path.open("rb") as stream:
        raw = stream.read(128_001)
    header = f"blob {len(raw)}\0".encode()
    # Git blob identity, not a security-strength source digest; also retain SHA-256.
    if (
        len(raw) > 128_000
        or hashlib.sha1(header + raw, usedforsecurity=False).hexdigest() != expected
    ):
        raise ValueError("source Git blob identity mismatch")
    return raw


def docx_anchor_evidence(structure, rows):
    """Fingerprint-only context and block evidence, not inferred hierarchy or equivalence."""
    # ponytail: native DOCX body tables already supply all collected row anchors.
    row_by_cell = {
        cell["anchor"]: row
        for table in structure["blocks"]
        for row in table.get("rows", [])
        for cell in row["cells"]
    }
    cells = {
        cell["anchor"]: cell
        for table in structure["blocks"]
        for row in table.get("rows", [])
        for cell in row["cells"]
    }
    result = []
    for row in rows:
        requirement = row["requirement_anchor"]
        identifier = row["identifier_anchor"]
        table_row = row_by_cell.get(requirement)
        receipt = {"item_id": row["item_id"], "requirement_anchor": requirement}
        if table_row is None or row_by_cell.get(identifier) is not table_row:
            result.append({**receipt, "status": "unbound"})
            continue
        other_cells = []
        for cell in table_row["cells"]:
            if cell["anchor"] in (identifier, requirement):
                continue
            origin = cell.get("merge_origin")
            other_cells.append(
                {
                    "anchor": cell["anchor"],
                    "text_sha256": cell["text_sha256"],
                    "merge_origin": origin,
                    "origin_text_sha256": cells.get(origin, {}).get("text_sha256"),
                }
            )
        result.append(
            {
                **receipt,
                "status": "observed_not_qualified",
                "row_anchor": table_row["anchor"],
                "identifier_anchor": identifier,
                "requirement_blocks": [
                    {
                        k: block[k]
                        for k in ("anchor", "kind", "text_sha256", "numbering")
                        if k in block
                    }
                    for block in cells[requirement]["blocks"]
                ],
                "other_cells": other_cells,
            }
        )
    return result


def compare_docx(raw, name, reference, expected):
    from .compare_ecoevo_formats import collect_rows, compare_formats
    from .compare_guideline_formats import header_roles
    from .structured_source import check_package, docx_structure

    _, structure = docx_structure(raw)
    headers = {
        **header_roles(),
        fingerprint("No"): "id",
        fingerprint("Checklist item description"): "requirement",
        fingerprint(f"{name.upper()} 2025 checklist item description"): "requirement",
    }
    rows, issues = collect_rows(structure, identifier_pattern=ITEM_ID, header_roles=headers)
    return {
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        **summarize_source(rows, tuple(expected), issues + structure["issues"]),
        "comparison": compare_formats(reference, rows, expected_ids=expected),
        "anchor_evidence": docx_anchor_evidence(structure, rows),
        "non_body_members": sorted(
            name
            for name in check_package(raw)
            if re.match(r"word/(?:header|footer|footnotes|endnotes|comments)", name)
        ),
        "independent_issuer_identity_verified": False,
    }


def observe_pair(source_dir, name, spec, pins):
    qmd_pin, docx_pin = pins
    expected = [item for table in spec["table_item_ids"] for item in table]
    result = {
        "edition": spec["edition"],
        "doi": spec["doi"],
        "qmd_git_blob": qmd_pin,
        "docx_git_blob": docx_pin,
        "status": "held",
        "expected_ids": expected,
    }
    try:
        raw = pinned_bytes(source_dir / f"{name}.qmd", qmd_pin)
        result["literal"] = literal_rows(raw, spec["doi"], expected)
        raw_docx = pinned_bytes(source_dir / f"{name}.docx", docx_pin)
        result["docx"] = compare_docx(raw_docx, name, result["literal"]["rows"], expected)
        comparison = result["docx"]["comparison"]
        result["status"] = (
            "held_structural_discrepancy"
            if result["literal"]["issues"]
            or result["docx"]["issues"]
            or comparison["different_ids"]
            or comparison["not_comparable_expected_ids"]
            else "source_observation_only"
        )
    except (ValueError, OSError, ImportError, RuntimeError) as exc:
        result["error_type"] = type(exc).__name__
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    specs = json.loads(Path("source/official/priority-article-candidates.json").read_text())
    editions = []
    for name, pins in PINS.items():
        (spec,) = [s for s in specs if s["edition"] == name + "-2025"]
        editions.append(observe_pair(args.source_dir, name, spec, pins))
    result = {
        "upstream_revision": UPSTREAM,
        "editions": editions,
        "scientific_qualification": False,
        "canonical_packs_promoted": 0,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
