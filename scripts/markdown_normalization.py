"""Parser-backed, byte-preserving normalization of explicit Markdown code markers.

The finite unit lexicon is a bounded deterministic transducer. This is not a
general WFST or lossless multi-language CST, and it never resolves citations.
"""

from __future__ import annotations

import re

from .orthogonal_checks import rewrite

UNITS = {"mg": "mg", "ug": "ug", "µg": "ug", "μg": "ug", "mL": "mL", "ml": "mL"}
DOI = re.compile(r"10\.[0-9]{4,9}/[A-Za-z0-9][A-Za-z0-9._;()/:-]{0,200}")


def _target(content):
    if content.startswith("unit:"):
        value = UNITS.get(content.removeprefix("unit:"))
        return "unit:" + value if value is not None else None
    if content.startswith("doi:"):
        value = content.removeprefix("doi:").removeprefix("https://doi.org/")
        return "doi:" + value if DOI.fullmatch(value) else None
    return content


def _walk(tokens):
    for token in tokens:
        yield token
        yield from _walk(token.children or [])


def _signature(tokens, replacements):
    return [
        (
            token.type,
            token.tag,
            token.nesting,
            token.attrs,
            token.markup,
            token.info,
            token.hidden,
            token.map,
            "" if token.children else replacements.get(id(token), token.content),
            _signature(token.children or [], replacements),
        )
        for token in tokens
    ]


def normalize(raw: bytes) -> dict:
    """Normalize only uniquely located, explicitly typed code spans; hold ambiguity."""
    from markdown_it import MarkdownIt

    if len(raw) > 1_000_000:
        raise ValueError("Markdown input limit exceeded")
    parser = MarkdownIt("commonmark")
    original = parser.parse(raw.decode("utf-8"))
    edits, replacements, held = [], {}, []
    for index, token in enumerate(_walk(original)):
        if token.type != "code_inline" or not token.content.startswith(("unit:", "doi:")):
            continue
        value = _target(token.content)
        if value is None:
            held.append(index)
            continue
        if value == token.content:
            continue
        needle = bytes([96]) + token.content.encode("utf-8") + bytes([96])
        start = raw.find(needle)
        end = start + len(needle)
        if (
            start < 0
            or raw.count(needle) != 1
            or raw[start - 1 : start] == bytes([96])
            or raw[end : end + 1] == bytes([96])
        ):
            held.append(index)
            continue
        replacement = bytes([96]) + value.encode("utf-8") + bytes([96])
        edits.append((start, end, needle, replacement))
        replacements[id(token)] = value
    if held:
        return {"status": "held_ambiguous_or_unknown", "output": raw, "edited": 0, "held": held}
    if not edits:
        return {"status": "unchanged", "output": raw, "edited": 0, "held": []}
    if len(edits) > 1000:
        return {"status": "held_limit", "output": raw, "edited": 0, "held": []}
    result = rewrite(raw, edits)
    observed = parser.parse(result.decode("utf-8"))
    if _signature(original, replacements) != _signature(observed, {}):
        return {"status": "held_parse_change", "output": raw, "edited": 0, "held": []}
    return {"status": "normalized_in_scope", "output": result, "edited": len(edits), "held": []}
