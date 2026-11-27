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


def literal_bullet_blocks(text, anchor):
    lines = text.splitlines()
    if len(lines) < 2 or not lines[0].strip() or lines[0].startswith("• "):
        return []
    if not all(line.startswith("• ") and line[2:].strip() for line in lines[1:]):
        return []
    return [
        {
            "anchor": f"{anchor}#line:{i + 1}",
            "bullet": bool(i),
            "text_sha256": fingerprint(line[2:] if i else line),
        }
        for i, line in enumerate(lines)
    ]


def bullet_content_comparison(literal, docx):
    """Compare explicit literal bullet content to numbered Word paragraphs, not rendered glyphs."""
    result = []
    for row in literal:
        blocks = row.get("bullet_blocks", [])
        if not blocks:
            continue
        candidates = [r for r in docx if r["item_id"] == row["item_id"]]
        observed = candidates[0].get("requirement_blocks", []) if len(candidates) == 1 else []
        pairs = [
            {
                "literal_anchor": a["anchor"],
                "docx_anchor": b["anchor"],
                "equal": a["text_sha256"] == b.get("text_sha256")
                and b["kind"] == "paragraph"
                and a["bullet"] == (b.get("numbering") is not None),
                "numbering": b.get("numbering"),
            }
            for a, b in zip(blocks, observed, strict=False)
        ]
        equal = len(blocks) == len(observed) and all(p["equal"] for p in pairs)
        result.append(
            {
                "item_id": row["item_id"],
                "literal_anchor": row["requirement_anchor"],
                "status": "content_matches_numbered_blocks" if equal else "held_block_mismatch",
                "pairs": pairs,
            }
        )
    return result


def docx_markup_inventory(raw):
    """Bounded hash-only non-body and list-definition evidence; not a rendered DOCX reader."""
    import io
    from zipfile import ZipFile

    from .source_xml import parse_xml
    from .structured_source import MAX_UNPACKED_BYTES, check_package

    members = check_package(raw)
    w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with ZipFile(io.BytesIO(raw)) as archive:
        body = parse_xml(archive.read("word/document.xml"), MAX_UNPACKED_BYTES)
        refs = {
            kind: [element.get(w + "id") for element in body.iter(w + kind)]
            for kind in ("footnoteReference", "endnoteReference", "commentReference")
        }
        non_body = []
        for name in sorted(members):
            if not re.fullmatch(
                r"word/(?:header\d+|footer\d+|footnotes|endnotes|comments)\.xml", name
            ):
                continue
            content = archive.read(name)
            part = parse_xml(content, MAX_UNPACKED_BYTES)
            nodes = [node.text for node in part.iter(w + "t") if node.text and node.text.strip()]
            non_body.append(
                {
                    "member": name,
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "nonempty_text_nodes": len(nodes),
                    "text_sha256": fingerprint("\n".join(nodes)),
                    "note_ids": [
                        node.get(w + "id")
                        for kind in ("footnote", "endnote", "comment")
                        for node in part.iter(w + kind)
                    ],
                    "field_count": sum(
                        1
                        for kind in ("fldSimple", "instrText", "drawing")
                        for _ in part.iter(w + kind)
                    ),
                }
            )
        numbering = []
        if "word/numbering.xml" in members:
            root = parse_xml(archive.read("word/numbering.xml"), MAX_UNPACKED_BYTES)
            for num in root.findall(w + "num"):
                abstract_id = num.find(w + "abstractNumId")
                ident = abstract_id.get(w + "val") if abstract_id is not None else None
                defs = [
                    node
                    for node in root.findall(w + "abstractNum")
                    if node.get(w + "abstractNumId") == ident
                ]
                levels = []
                if len(defs) == 1:
                    for level in defs[0].findall(w + "lvl"):
                        fmt = level.find(w + "numFmt")
                        marker = level.find(w + "lvlText")
                        levels.append(
                            {
                                "level": level.get(w + "ilvl"),
                                "format": fmt.get(w + "val") if fmt is not None else None,
                                "marker_sha256": fingerprint(marker.get(w + "val", ""))
                                if marker is not None
                                else None,
                            }
                        )
                numbering.append(
                    {
                        "num_id": num.get(w + "numId"),
                        "abstract_id": ident,
                        "definition_count": len(defs),
                        "overrides": len(num.findall(w + "lvlOverride")),
                        "levels": levels,
                    }
                )
    return {
        "body_references": refs,
        "non_body": non_body,
        "numbering": numbering,
        "boundary": "Observed XML markup only; rendered numbering and non-body semantic coverage not established",
    }


def read_literal_array(source):
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
    return data


def literal_rows(raw, doi, expected_ids):
    if len(raw) > 128_000 or not expected_ids or len(set(expected_ids)) != len(expected_ids):
        raise ValueError("invalid bounded source or reference")
    source = raw.decode("utf-8")
    for role, marker in (("cite", doi), ("lic", "https://creativecommons.org/licenses/by/4.0/")):
        notices = re.findall(rf'<p class="tp-{role}">(.*?)</p>', source, re.S)
        if len(notices) != 1 or marker not in notices[0]:
            raise ValueError("source identity or local licence notice missing")
    data = read_literal_array(source)
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
                    "bullet_blocks": literal_bullet_blocks(item[1], item_anchor + "/1"),
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
    if name == "tripod":
        headers[fingerprint("Item")] = "id"
    rows, issues = collect_rows(structure, identifier_pattern=ITEM_ID, header_roles=headers)
    anchor_evidence = docx_anchor_evidence(structure, rows)
    diagnostics = {}
    if name == "tripod":
        diagnostics["display_content_comparison"] = compare_formats(
            [{**row, "requirement_sha256": row["display_content_sha256"]} for row in reference],
            rows,
            expected_ids=expected,
        )
        diagnostics["scope_cell_comparison"] = tripod_scope_comparison(reference, anchor_evidence)
        diagnostics["note_marker_content_comparison"] = tripod_marker_comparison(
            reference, rows, expected
        )
    elif name == "strobe":
        diagnostics["unverified_identifier_candidates"] = strobe_identifier_candidates(
            structure, reference
        )
        diagnostics["compound_candidate_comparison"] = strobe_compound_comparison(
            structure, reference
        )
    return {
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        **summarize_source(rows, tuple(expected), issues + structure["issues"]),
        **diagnostics,
        "comparison": compare_formats(
            reference if name != "strobe" else [], rows, expected_ids=expected
        ),
        "anchor_evidence": anchor_evidence,
        "bullet_content_comparison": bullet_content_comparison(reference, anchor_evidence),
        "markup_inventory": docx_markup_inventory(raw),
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


PRIORITY_PINS = {
    "tripod": (
        "tripod-ai-2024",
        "79d32ba9c806dccb617ff99b4eb6b2b9d2ad178d",
        "0087e65ff3ea8b37c309074e6ec9dab30169f015",
        "4f3b8d79689e96760df28d21bf42115839a9ee4c",
    ),
    "strobe": (
        "strobe-2007",
        "e30f0cd788751d57bbd6e4a37185d3f008143fb0",
        "6e3e758865902a03a75e45821f78e1c0f371a36c",
        "94f5b2d5f04a54eafdca508f86e2b50ad1ba58b1",
    ),
}


def priority_display_fields(content):
    """Separate observed QMD display markup from links; never normalize plain numbers."""
    links = re.compile(r"\[\[([^\[\]|]+)\|([^\[\]|]+)\]\]")
    notes = re.compile(r"<sup>([0-9]+)</sup>")
    return {
        "display_content_sha256": fingerprint(notes.sub("", links.sub(r"\1", content))),
        "literal_note_marker_sha256": fingerprint(notes.sub(r"\1", links.sub(r"\1", content))),
        "note_references": notes.findall(content),
        "link_target_sha256": [
            hashlib.sha256(match[2].encode()).hexdigest() for match in links.finditer(content)
        ],
    }


def tripod_scope_comparison(reference, observed):
    """Compare only the expected intervening cell in the pinned TRIPOD Word layout."""
    result = []
    for row in reference:
        candidates = [r for r in observed if r["item_id"] == row["item_id"]]
        receipt = {"item_id": row["item_id"], "status": "unknown", "scope_anchor": None}
        if len(candidates) == 1 and candidates[0].get("status") == "observed_not_qualified":
            candidate = candidates[0]
            prefix = re.escape(candidate["row_anchor"])
            identifier = re.fullmatch(prefix + r"/c(\d+)", candidate["identifier_anchor"])
            requirement = re.fullmatch(prefix + r"/c(\d+)", candidate["requirement_anchor"])
            if identifier and requirement and int(requirement[1]) == int(identifier[1]) + 2:
                anchor = candidate["row_anchor"] + f"/c{int(identifier[1]) + 1}"
                cells = [c for c in candidate["other_cells"] if c["anchor"] == anchor]
                if len(cells) == 1 and cells[0].get("text_sha256"):
                    receipt.update(
                        scope_anchor=anchor,
                        status=(
                            "equal"
                            if cells[0]["text_sha256"] == fingerprint(row["scope"])
                            else "different"
                        ),
                    )
        result.append(receipt)
    return result


def strobe_identifier_candidates(structure, reference):
    """Expose possible lost main IDs, including starred labels, without scoring them."""
    known = {fingerprint(row["printed_id"]): row for row in reference}
    result = []
    for table in structure["blocks"]:
        for row in table.get("rows", []):
            for cell in row["cells"]:
                candidate = known.get(cell.get("text_sha256"))
                if candidate is not None:
                    result.append(
                        {
                            "item_id": candidate["item_id"],
                            "printed_id": candidate["printed_id"],
                            "row_anchor": row["anchor"],
                            "cell_anchor": cell["anchor"],
                            "column": cell["column"],
                            "status": "unverified_cell_candidate",
                        }
                    )
    return result


def tripod_marker_comparison(reference, observed, expected):
    """Compare the two explicit display projections without inferring note linkage."""
    result = []
    for item in expected:
        refs = [r for r in reference if r["item_id"] == item]
        rows = [r for r in observed if r["item_id"] == item]
        entry = {"item_id": item, "status": "held", "note_linkage_qualified": False}
        if len(refs) == len(rows) == 1:
            ref, row = refs[0], rows[0]
            entry.update(
                literal_anchor=ref.get("requirement_anchor"),
                requirement_anchor=row.get("requirement_anchor"),
                note_references=ref["note_references"],
                observed_sha256=row.get("requirement_sha256"),
            )
            if (
                all(
                    entry.get(key)
                    for key in ("literal_anchor", "requirement_anchor", "observed_sha256")
                )
                and row.get("identifier_anchor")
            ):
                if entry["observed_sha256"] == ref["display_content_sha256"]:
                    entry["status"] = "display_content_equal"
                elif (
                    ref["note_references"]
                    and entry["observed_sha256"] == ref["literal_note_marker_sha256"]
                ):
                    entry["status"] = "explicit_marker_content_equal"
        result.append(entry)
    return result


def strobe_compound_comparison(structure, reference):
    """Pinned four-column STROBE layout diagnostic, not a generic header inference."""
    known = {fingerprint(r["printed_id"]): r for r in reference}
    groups = {r["item_id"]: [] for r in reference}
    if len(known) != len(reference) or len(groups) != len(reference):
        raise ValueError("duplicate STROBE reference identity")
    # Candidate geometry only: column 2 identity and column 3 requirement.
    # Never propagate the first table's header to a different table.
    for table in structure["blocks"]:
        if table.get("grid_width") != 4:
            continue
        current = None
        for row in table.get("rows", []):
            cells = {c["column"]: c for c in row["cells"] if c["colspan"] == 1}
            identity, requirement = cells.get(2, {}), cells.get(3, {})
            ref = known.get(identity.get("text_sha256"))
            if ref is not None and identity.get("anchor"):
                current = {
                    "identifier_anchor": identity["anchor"],
                    "table_anchor": table["anchor"],
                    "requirements": [],
                }
                groups[ref["item_id"]].append(current)
            elif not (
                current is not None
                and identity.get("empty")
                and identity.get("vertical_merge") == "continue"
                and identity.get("merge_origin") == current["identifier_anchor"]
            ):
                current = None
            if current is not None:
                current["requirements"].append(
                    {
                        "row_anchor": row["anchor"],
                        "identifier_anchor": identity.get("anchor"),
                        "identifier_merge_origin": identity.get("merge_origin"),
                        "requirement_anchor": requirement.get("anchor"),
                        "requirement_sha256": (
                            requirement.get("text_sha256")
                            if not requirement.get("empty", True)
                            and requirement.get("vertical_merge") != "continue"
                            else None
                        ),
                    }
                )
    result = []
    for ref in reference:
        candidates = groups[ref["item_id"]]
        expected = ref["subitems"]
        observed = candidates[0]["requirements"] if len(candidates) == 1 else []
        pairs = []
        if len(expected) == len(observed):
            for a, b in zip(expected, observed, strict=True):
                pairs.append(
                    {
                        **b,
                        "subitem_id": a["item_id"],
                        "literal_anchor": a["requirement_anchor"],
                        "equal": bool(
                            b["requirement_anchor"]
                            and b["requirement_sha256"] == a["display_content_sha256"]
                        ),
                    }
                )
        result.append(
            {
                "item_id": ref["item_id"],
                "printed_id": ref["printed_id"],
                "status": (
                    "candidate_content_matches" if pairs and all(p["equal"] for p in pairs) else "held"
                ),
                "expected_subitems": len(expected),
                "candidate_groups": candidates,
                "pairs": pairs,
                "note_linkage_qualified": False,
            }
        )
    return result


def priority_literal_metadata(data, name, expected):
    """Retain observed scope and subitem structure; no semantic or rights decision."""
    if name not in PRIORITY_PINS or not expected or len(set(expected)) != len(expected):
        raise ValueError("invalid source dialect or denominator")
    rows = []
    section = topic = None
    for i, value in enumerate(data):
        anchor = f"ROWS/{i}"
        if isinstance(value, str) and value.strip():
            section, topic = anchor, None
            continue
        if not isinstance(value, list) or len(value) != 4 or (section is None and name == "tripod"):
            raise ValueError("invalid priority row")
        heading, printed, scope, content = value
        if not isinstance(heading, str) or not isinstance(printed, str):
            raise ValueError("invalid topic or printed identity")
        if heading.strip():
            topic = anchor + "/0"
        if topic is None:
            raise ValueError("missing topic origin")
        item = printed.removesuffix("*") if name == "strobe" else printed
        if not ITEM_ID.fullmatch(item):
            raise ValueError("invalid item identity")
        row = {
            "item_id": item,
            "printed_id": printed,
            "identifier_anchor": anchor + "/1",
            "section_anchor": section,
            "topic_anchor": topic,
            "requirement_anchor": anchor + "/3",
        }
        if name == "tripod":
            if (
                scope not in ("D", "E", "D;E")
                or not isinstance(content, str)
                or not content.strip()
            ):
                raise ValueError("invalid scope or requirement")
            row.update(
                scope=scope,
                scope_anchor=anchor + "/2",
                requirement_sha256=fingerprint(content),
                **priority_display_fields(content),
            )
        else:
            if type(scope) is not bool or not isinstance(content, list) or not content:
                raise ValueError("invalid grouped requirement")
            subitems = []
            for j, sub in enumerate(content):
                if (
                    not isinstance(sub, list)
                    or len(sub) != 2
                    or not isinstance(sub[0], str)
                    or not re.fullmatch(re.escape(item) + r"[a-z]?", sub[0])
                    or not isinstance(sub[1], str)
                    or not sub[1].strip()
                    or sub[0] in {part["item_id"] for part in subitems}
                ):
                    raise ValueError("invalid or duplicate subitem")
                subitems.append(
                    {
                        "item_id": sub[0],
                        "requirement_anchor": f"{anchor}/3/{j}/1",
                        "requirement_sha256": fingerprint(sub[1]),
                        "display_content_sha256": fingerprint(re.sub(r"</?em>", "", sub[1])),
                    }
                )
            row.update(starred=printed.endswith("*"), literal_group_flag=scope, subitems=subitems)
        rows.append(row)
    return {"expected_order": [r["item_id"] for r in rows] == list(expected), "rows": rows}


def issuer_pdf_identity(path, pin):
    with path.open("rb") as stream:
        raw = stream.read(1_000_001)
    if len(raw) > 1_000_000 or not raw.startswith(b"%PDF-"):
        raise ValueError("invalid bounded issuer PDF")
    git_sha = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw, usedforsecurity=False).hexdigest()
    return {
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "git_blob": git_sha,
        "same_bytes_as_equator_pin": git_sha == pin,
        "bytes": len(raw),
    }


def observe_priority(source_dir, name, spec, pins):
    _, qmd_pin, docx_pin, pdf_pin = pins
    # STROBE's primary article establishes 22 ordered main IDs, not a clause denominator.
    expected = [str(i) for i in range(1, 23)] if name == "strobe" else spec["table_item_ids"][0]
    result = {
        "edition": spec["edition"],
        "doi": spec["doi"],
        "status": "source_observation_only",
        "expected_main_or_printed_ids": expected,
        "project_research_use_approved": True,
        "public_redistribution_qualified": False,
        "scientific_qualification": False,
    }
    try:
        raw = pinned_bytes(source_dir / f"{name}.qmd", qmd_pin)
        result["literal"] = {
            **priority_literal_metadata(read_literal_array(raw.decode("utf-8")), name, expected),
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob": qmd_pin,
        }
    except (OSError, ValueError) as exc:
        result["literal"] = {"status": "held", "error_type": type(exc).__name__}
    try:
        raw = pinned_bytes(source_dir / f"{name}.docx", docx_pin)
        # The existing generic Word reader deliberately holds unmatched compound rows.
        ref = result["literal"].get("rows", [])
        result["docx"] = compare_docx(raw, name, ref, expected)
        result["docx"]["git_blob"] = docx_pin
    except (OSError, ValueError, ImportError, RuntimeError) as exc:
        result["docx"] = {"status": "held", "error_type": type(exc).__name__}
    try:
        result["issuer_pdf"] = issuer_pdf_identity(source_dir / f"{name}.issuer.pdf", pdf_pin)
        if (
            name == "tripod"
            and result["issuer_pdf"]["git_blob"] == "dcdcf9ed46273432ac0f941624a48086db9b48d8"
        ):
            result["issuer_pdf"]["identity_observation"] = (
                "matches_equator_article_pdf_not_checklist_pin"
            )
    except (OSError, ValueError) as exc:
        result["issuer_pdf"] = {"status": "held", "error_type": type(exc).__name__}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--priority", action="store_true")
    args = parser.parse_args()
    specs = json.loads(Path("source/official/priority-article-candidates.json").read_text())
    editions = []
    if args.priority:
        for name, pins in PRIORITY_PINS.items():
            (spec,) = [s for s in specs if s["edition"] == pins[0]]
            editions.append(observe_priority(args.source_dir, name, spec, pins))
    else:
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
