"""Exact-byte, issuer-specific main-ID geometry diagnostic (not source admission)."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
from collections import Counter
from pathlib import Path

ID = re.compile(r"[1-9][0-9]?\*?")
PROFILES = {
    "arrive": {
        "sha256": "91e191d495f96472c0896ae3e489e9a12953648179f2a2a06b7035bb97a7327c",
        "pages": [
            ((0.185, 0.228, 0.214, 0.965), [str(i) for i in range(1, 11)]),
            ((0.201, 0.164, 0.237, 0.776), [str(i) for i in range(11, 22)]),
        ],
    },
    "strobe": {
        "sha256": "63c2af4d91d04f5b211f4277a267a23da5d313fe927753c08f98139a8aab41b8",
        "pages": [
            (
                (0.285, 0.137, 0.320, 0.850),
                [f"{i}*" if i == 8 else str(i) for i in range(1, 13)],
            ),
            (
                (0.210, 0.105, 0.250, 0.674),
                [f"{i}*" if i <= 15 else str(i) for i in range(13, 23)],
            ),
        ],
    },
}


def summarize_ids(lines, expected):
    observed = [line for line in lines if ID.fullmatch(line)]
    missing = [item for item in expected if item not in observed]
    extra = sorted(set(observed) - set(expected))
    duplicates = sorted(key for key, count in Counter(observed).items() if count > 1)
    non_identifier_count = len(lines) - len(observed)
    exact = observed == expected and not non_identifier_count
    issues = []
    for name, value in (
        ("duplicate_ids", duplicates),
        ("unexpected_ids", extra),
        ("missing_ids", missing),
        ("non_identifier_lines", non_identifier_count),
        ("expected_order_not_recovered", not exact),
    ):
        if value:
            issues.append(name)
    return {
        "observed_ids": observed,
        "missing_ids": missing,
        "unexpected_ids": extra,
        "duplicate_ids": duplicates,
        "non_identifier_count": non_identifier_count,
        "exact_order": exact,
        "issues": issues,
    }


def inspect_page(words, width, height, bounds, expected, page):
    from .ecoevo_pdf_grid import anchor, region, text_lines

    if not all(math.isfinite(v) and 0 < v < 3000 for v in (width, height)):
        raise ValueError("invalid page dimensions")
    x0, y0, x1, y1 = bounds
    crop = (x0 * width, y0 * height, x1 * width, y1 * height)
    lines, anchors = [], []
    for line in text_lines(region(words, *crop)):
        tokens = [w.text for w in line]
        text = " ".join(tokens)
        if len(tokens) == 2 and tokens[1] == "*":
            text = "".join(tokens)
        lines.append(text)
        if ID.fullmatch(text):
            anchors.append(
                {
                    "printed_id": text,
                    "anchor": anchor(
                        page,
                        min(w.x0 for w in line),
                        min(w.y0 for w in line),
                        max(w.x1 for w in line),
                        max(w.y1 for w in line),
                    ),
                }
            )
    return {**summarize_ids(lines, expected), "page": page, "anchors": anchors}


def observe(pdf, bbox, family):
    import pdfplumber

    from .ecoevo_pdf_grid import Word
    from .source_xml import parse_xml

    profile = PROFILES[family]
    if not 0 < pdf.stat().st_size <= 8_000_000:
        raise ValueError("PDF byte limit")
    raw = pdf.read_bytes()
    if hashlib.sha256(raw).hexdigest() != profile["sha256"]:
        raise ValueError("issuer bytes differ from frozen source")
    if not 0 < bbox.stat().st_size <= 16_000_000:
        raise ValueError("bbox byte limit")
    layout = bbox.read_bytes()
    xml = parse_xml(layout, 16_000_000)
    ns = "{http://www.w3.org/1999/xhtml}"
    pages = list(xml.iter(ns + "page"))
    native, independent = [], []
    with pdfplumber.open(io.BytesIO(raw)) as doc:
        if len(doc.pages) != len(pages) or len(pages) != len(profile["pages"]):
            raise ValueError("unexpected page count")
        for i, (page, other, (bounds, expected)) in enumerate(
            zip(doc.pages, pages, profile["pages"], strict=True), 1
        ):
            left = [
                Word(w["x0"], w["top"], w["x1"], w["bottom"], w["text"])
                for w in page.extract_words()
            ]
            right = [
                Word(*(float(w.attrib[k]) for k in ("xMin", "yMin", "xMax", "yMax")), w.text or "")
                for w in other.iter(ns + "word")
            ]
            native.append(inspect_page(left, page.width, page.height, bounds, expected, i))
            independent.append(
                inspect_page(
                    right,
                    float(other.attrib["width"]),
                    float(other.attrib["height"]),
                    bounds,
                    expected,
                    i,
                )
            )
    exact = all(row["exact_order"] for row in native + independent)
    return {
        "family": family,
        "source_sha256": profile["sha256"],
        "bbox_sha256": hashlib.sha256(layout).hexdigest(),
        "pdfplumber": native,
        "poppler": independent,
        "all_main_ids_match": exact,
        "scientific_qualification": False,
        "canonical_packs_promoted": 0,
        "claim_boundary": "Printed main identifiers only; nested rows, scope, rights held.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=PROFILES, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--bbox", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = observe(args.pdf, args.bbox, args.family)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"family": args.family, "all_main_ids_match": receipt["all_main_ids_match"]}))


if __name__ == "__main__":
    main()
