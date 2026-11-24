"""Independent ruled-grid PDF candidates: native PDF geometry and Poppler pixels."""

from __future__ import annotations

import io
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

if __package__:
    from .source_reconciliation import fingerprint
    from .source_xml import parse_xml
else:
    from source_reconciliation import fingerprint
    from source_xml import parse_xml

ID = re.compile(r"\d{1,3}\.\d{1,3}")
MAX_BYTES = 20_000_000
MAX_PAGES = 80


@dataclass(frozen=True)
class Word:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str

    @property
    def x(self):
        return (self.x0 + self.x1) / 2

    @property
    def y(self):
        return (self.y0 + self.y1) / 2


def clusters(values, tolerance=1.5):
    groups = []
    for value in sorted(values):
        if groups and value - groups[-1][-1] <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [sum(group) / len(group) for group in groups]


def text_lines(words):
    lines = []
    for word in sorted(words, key=lambda w: (w.y, w.x0)):
        if lines and abs(word.y - lines[-1][0].y) <= 3:
            lines[-1].append(word)
        else:
            lines.append([word])
    return [sorted(line, key=lambda w: w.x0) for line in lines]


def phrase(words):
    return " ".join(w.text for line in text_lines(words) for w in line)


def partition_group(identifiers, words):
    """Unique contiguous line partition matching top- or centre-aligned IDs."""
    from functools import lru_cache

    lines = text_lines(words)
    if not identifiers or len(lines) < len(identifiers) or len(lines) > 160:
        return None
    tops = [min(w.y0 for w in line) for line in lines]
    bottoms = [max(w.y1 for w in line) for line in lines]
    middles = [(a + b) / 2 for a, b in zip(tops, bottoms, strict=True)]
    solutions = set()
    for mode in ("top", "center"):

        @lru_cache(None)
        def search(i, start, mode=mode):
            if i == len(identifiers):
                return [()] if start == len(lines) else []
            choices = []
            for end in range(start + 1, len(lines) - (len(identifiers) - i - 1) + 1):
                target = middles[start] if mode == "top" else (tops[start] + bottoms[end - 1]) / 2
                if abs(target - identifiers[i].y) > 3:
                    continue
                for tail in search(i + 1, end):
                    choices.append((end,) + tail)
                    if len(choices) >= 2:
                        return choices
            return choices

        solutions.update(search(0, 0))
    if len(solutions) != 1:
        return None
    ends = next(iter(solutions))
    starts = (0,) + ends[:-1]
    return [[w for line in lines[a:b] for w in line] for a, b in zip(starts, ends, strict=True)]


def fidelity_fields(words, valid):
    """Additional layout-aware digest; original strict text digest is retained."""
    if not valid:
        return {"requirement_sha256": None, "layout_normalized_sha256": None, "layout_events": {}}
    events = Counter()
    attached = {}
    removed = set()
    # Reattach smaller, raised numeric glyph boxes to their unique adjacent
    # base word; do not join ordinary baseline numerals or distant tokens.
    for number in words:
        if not re.fullmatch(r"\d+[,.;:]?", number.text):
            continue
        candidates = [
            base
            for base in words
            if base.text[-1:].isalpha()
            and -1 <= number.x0 - base.x1 <= 2
            and number.y0 < base.y0 + 0.5
            and number.y1 >= base.y0
            and number.y1 - number.y0 <= 0.85 * (base.y1 - base.y0)
        ]
        if len(candidates) != 1 or candidates[0] in attached:
            continue
        base = candidates[0]
        attached[base] = number.text
        removed.add(number)
        events["superscript_join"] += 1
        punctuation = [
            w
            for w in words
            if re.fullmatch(r"[,.;:)]", w.text)
            and -1 <= w.x0 - number.x1 <= 2
            and w.y0 <= base.y1
            and w.y1 >= base.y0
        ]
        if len(punctuation) == 1 and punctuation[0] not in removed:
            attached[base] += punctuation[0].text
            removed.add(punctuation[0])
            events["superscript_punctuation_join"] += 1
    parts = []
    for line in text_lines([w for w in words if w not in removed]):
        for i, word in enumerate(line):
            value = word.text + attached.get(word, "")
            if i == 0 and parts and parts[-1].endswith("-") and value[:1].isalpha():
                parts[-1] += value
                events["line_end_hyphen"] += 1
            else:
                parts.append(value)
    return {
        "requirement_sha256": fingerprint(phrase(words)),
        "layout_normalized_sha256": fingerprint(" ".join(parts)),
        "layout_events": dict(events),
    }


def hold(row):
    row["requirement_sha256"] = None
    row["layout_normalized_sha256"] = None


def region(words, x0, y0, x1, y1):
    return [w for w in words if x0 <= w.x < x1 and y0 <= w.y < y1]


def header(text):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\(cid:\d+\)", "", text.casefold()))


def anchor(page, x0, y0, x1, y1):
    return f"page/{page}/bbox/" + ",".join(f"{v:.2f}" for v in (x0, y0, x1, y1))


def hold_unclosed_tail(words, x0, x2, bottom, rows, issues):
    """Do not silently lose trailing text; allow only explicit page furniture."""
    footer = re.compile(
        r"https?://doi\.org/\S+\s+PRISMA[-‐–]EcoEvo\s+Checklist:\s*Page\s+\d+\s+of\s+\d+", re.I
    )
    for line in text_lines([w for w in words if w.y >= bottom]):
        if footer.fullmatch(phrase(line)):
            continue
        if any(x0 <= w.x < x2 for w in line):
            issues.add("unclosed_trailing_text")
            if rows:
                hold(rows[-1])
            break


def extract_grid(words, xs, horizontal, page, vertical=lambda x, a, b: True):
    """Require explicit column headers and closed row bands, not ID proximity."""
    candidates = []
    for x0, x1, x2 in zip(xs, xs[1:], xs[2:], strict=False):
        ys = horizontal(x0, x2)
        for i in range(min(5, len(ys) - 1)):
            for j in range(i + 1, min(i + 3, len(ys) - 1) + 1):
                if (
                    header(phrase(region(words, x0, ys[i], x1, ys[j]))) == "subitemnumber"
                    and header(phrase(region(words, x1, ys[i], x2, ys[j]))) == "subitem"
                ):
                    candidates.append((x0, x1, x2, ys, j))
    if len(candidates) != 1:
        return [], ["header_not_unique"], {"verticals": xs, "header_candidates": len(candidates)}
    x0, x1, x2, ys, start = candidates[0]
    rows, issues = [], set()
    for y0, y1 in zip(ys[start:], ys[start + 1 :], strict=False):
        identifier = phrase(region(words, x0, y0, x1, y1)).strip()
        reqwords = region(words, x1, y0, x2, y1)
        req = phrase(reqwords)
        if not identifier and not req:
            continue
        if not ID.fullmatch(identifier):
            issues.add("unbound_requirement_band")
            if not rows:
                issues.add("unbound_leading_band")
            if rows:
                hold(rows[-1])
            continue
        closed = all(vertical(x, y0, y1) for x in (x0, x1, x2))
        if not closed:
            issues.add("unclosed_row_geometry")
        rows.append(
            {
                "item_id": identifier,
                "identifier_anchor": anchor(page, x0, y0, x1, y1),
                "requirement_anchor": anchor(page, x1, y0, x2, y1),
                **fidelity_fields(reqwords, bool(req and closed)),
            }
        )
        if not req:
            issues.add("empty_requirement")
    hold_unclosed_tail(words, x0, x2, ys[-1], rows, issues)
    if not rows:
        issues.add("no_closed_rows")
    return (
        rows,
        sorted(issues),
        {
            "verticals": xs,
            "header_candidates": 1,
            "column_bounds": [x0, x1, x2],
            "row_boundaries": ys,
            "header_bottom": ys[start],
        },
    )


def header_evidence(words):
    allowed = {
        "subitem",
        "subitemnumber",
        "sub",
        "item",
        "number",
        "reported",
        "score",
        "notes",
        "checklist",
    }
    return [
        {
            "role": header(w.text) if header(w.text) in allowed else w.text,
            "bbox": [round(v, 2) for v in (w.x0, w.y0, w.x1, w.y1)],
        }
        for w in words
        if header(w.text) in allowed or ID.fullmatch(w.text)
    ][:240]


def extract_virtual(words, xs, horizontal, page, outer_closed):
    """A word-header binding plus independently observed horizontal ruling bands.

    Some tables have only outer vertical rulings. Derive virtual separators
    from explicit header/ID geometry, not from a prescribed item count.
    """
    evidence = {
        "verticals": xs,
        "header_words": header_evidence(words),
        "mode": "header_virtual_columns",
    }
    heads = [w for w in words if header(w.text) == "subitem"]
    for sub in (w for w in words if header(w.text) == "sub"):
        for item in (w for w in words if header(w.text) == "item"):
            if abs(sub.x0 - item.x0) <= 2 and 3 < item.y - sub.y <= 16:
                heads.append(
                    Word(min(sub.x0, item.x0), sub.y0, max(sub.x1, item.x1), item.y1, "subitem")
                )
    numbers = [w for w in words if header(w.text) == "number"]
    right_headers = [w for w in words if header(w.text) in {"reported", "score"}]
    candidates = []
    for left in heads:
        for right in heads:
            if not left.x < right.x or abs(left.y - right.y) > 25:
                continue
            for number in numbers:
                if abs(number.x - left.x) > 25 or not -3 <= number.y - left.y <= 25:
                    continue
                for response in right_headers:
                    if response.x <= right.x or abs(response.y - right.y) > 25:
                        continue
                    candidates.append((left, right, number, response))
    if len(candidates) != 1:
        return [], ["header_not_unique"], {**evidence, "header_candidates": len(candidates)}
    left, right, number, response = candidates[0]
    header_bottom = max(w.y1 for w in (left, right, number, response))
    ids = [
        w
        for w in words
        if w.y0 >= header_bottom - 1
        and ID.fullmatch(w.text)
        and abs(w.x - number.x) <= 25
        and w.x1 < right.x1
    ]
    if not ids:
        return [], ["no_header_bound_ids"], evidence
    x0 = min([left.x0, number.x0, *[w.x0 for w in ids]]) - 1
    id_right = max(w.x1 for w in ids)
    if right.x0 <= id_right:
        return [], ["no_requirement_column"], evidence
    x1 = (id_right + right.x0) / 2
    x2 = response.x0 - 1
    ys = horizontal(x0, response.x0 + (response.x1 - response.x0) / 2)
    first = min(w.y0 for w in ids)
    start = [i for i, y in enumerate(ys) if header_bottom - 2 <= y <= first + 1]
    evidence.update(
        column_bounds=[x0, x1, x2],
        row_boundaries=ys,
        header_bottom=header_bottom,
        header_candidates=1,
        header_bound_id_count=len(ids),
    )
    if not start or len(xs) < 2:
        return [], ["header_row_boundary_unavailable"], evidence
    rows = []
    issues = set()
    seen_ids = []
    for y0, y1 in zip(ys[start[-1] :], ys[start[-1] + 1 :], strict=False):
        idwords = region(words, x0, y0, x1, y1)
        reqwords = region(words, x1, y0, x2, y1)
        if not idwords and not reqwords:
            continue
        if not idwords or any(not ID.fullmatch(w.text) for w in idwords):
            issues.add("unbound_requirement_band")
            if rows:
                hold(rows[-1])
            else:
                issues.add("unbound_leading_band")
            continue
        # A group may hold multiple items, with IDs vertically centred on
        # paragraphs. Every word is assigned once by a unique partition.
        ordered = sorted(idwords, key=lambda w: w.y)
        closed = outer_closed(xs[0], y0, y1) and outer_closed(xs[-1], y0, y1)
        bad = not closed or any(
            w.x0 < x1 < w.x1 or w.x0 < x2 < w.x1 or w.y0 < y0 - 1 or w.y1 > y1 + 1
            for w in idwords + reqwords
        )
        parts = partition_group(ordered, reqwords)
        if parts is None:
            issues.add("ambiguous_item_line_partition")
            if not rows:
                issues.add("unbound_leading_band")
        for j, ident in enumerate(ordered):
            bound = parts[j] if parts is not None else []
            valid = not bad and bool(bound)
            if not valid:
                issues.add("unclosed_or_unaligned_virtual_band")
            seen_ids.append(ident.text)
            begin = min((w.y0 for w in bound), default=y0)
            end = max((w.y1 for w in bound), default=y1)
            rows.append(
                {
                    "item_id": ident.text,
                    "identifier_anchor": anchor(page, ident.x0, ident.y0, ident.x1, ident.y1),
                    "requirement_anchor": anchor(page, x1, begin, x2, end),
                    **fidelity_fields(bound, valid),
                }
            )
    hold_unclosed_tail(words, x0, x2, ys[-1], rows, issues)
    if Counter(seen_ids) != Counter(w.text for w in ids):
        issues.add("unbound_header_ids")
        if rows:
            hold(rows[-1])
    return rows, sorted(issues), evidence


def coverage(intervals, low, high):
    end = low
    covered = 0.0
    for a, b in sorted(intervals):
        a, b = max(low, a), min(high, b)
        if b > max(a, end):
            covered += b - max(a, end)
            end = b
    return covered / (high - low) if high > low else 0.0


def finish(parser, pages):
    rows = []
    issues = set()
    geometry = []
    for page, (items, problems, evidence) in enumerate(pages, 1):
        if rows and ("unbound_leading_band" in problems or "header_not_unique" in problems):
            hold(rows[-1])
        rows.extend(items)
        issues.update(problems)
        geometry.append({"page": page, **evidence})
    counts = Counter(r["item_id"] for r in rows)
    for row in rows:
        if counts[row["item_id"]] > 1:
            hold(row)
            issues.add("duplicate_id")
    return {"parser": parser, "rows": rows, "issues": sorted(issues), "geometry": geometry}


def extract_native(raw):
    import pdfplumber

    if not raw or len(raw) > MAX_BYTES:
        raise ValueError("PDF size limit")
    pages = []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        if not 0 < len(pdf.pages) <= MAX_PAGES:
            raise ValueError("PDF page limit")
        for page in pdf.pages:
            if len(page.edges) > 5000:
                raise ValueError("PDF edge limit")
            vertical = [e for e in page.edges if e["orientation"] == "v"]
            h_edges = [e for e in page.edges if e["orientation"] == "h"]
            xs = [
                x
                for x in clusters(e["x0"] for e in vertical)
                if coverage(
                    [(e["top"], e["bottom"]) for e in vertical if abs(e["x0"] - x) <= 1.5],
                    0,
                    page.height,
                )
                >= 0.18
            ]

            def horizontal(a, b, h_edges=h_edges):
                return [
                    y
                    for y in clusters(e["top"] for e in h_edges)
                    if coverage(
                        [(e["x0"], e["x1"]) for e in h_edges if abs(e["top"] - y) <= 1.5], a, b
                    )
                    >= 0.98
                ]

            words = [
                Word(w["x0"], w["top"], w["x1"], w["bottom"], w["text"])
                for w in page.extract_words()
            ]

            def closed(x, a, b, vertical=vertical):
                return (
                    coverage(
                        [(e["top"], e["bottom"]) for e in vertical if abs(e["x0"] - x) <= 1.5], a, b
                    )
                    >= 0.90
                )

            result = extract_grid(words, xs, horizontal, page.page_number, closed)
            if "header_not_unique" in result[1]:
                result = extract_virtual(words, xs, horizontal, page.page_number, closed)
                result[2]["native_horizontal_segments"] = [
                    (round(e["top"], 2), round(e["x0"], 2), round(e["x1"], 2))
                    for e in h_edges
                    if e["x1"] - e["x0"] > 30
                ][:400]
            pages.append(result)
    return {**finish("pdfplumber_geometry", pages), "version": pdfplumber.__version__}


def extract_poppler(raw):
    """Poppler independently renders the ruling lines and extracts word boxes."""
    import numpy as np
    from PIL import Image

    if not raw or len(raw) > MAX_BYTES:
        raise ValueError("PDF size limit")
    with TemporaryDirectory() as temp:
        root = Path(temp)
        pdf = root / "input.pdf"
        pdf.write_bytes(raw)
        output = subprocess.run(
            [
                "pdftotext",
                "-bbox-layout",
                "-enc",
                "UTF-8",
                "-f",
                "1",
                "-l",
                str(MAX_PAGES + 1),
                str(pdf),
                "-",
            ],
            capture_output=True,
            check=True,
            timeout=40,
        ).stdout
        if len(output) > 16_000_000:
            raise ValueError("Poppler output limit")
        xml = parse_xml(output, 16_000_000)
        doc_pages = list(xml.iter("{http://www.w3.org/1999/xhtml}page"))
        if not 0 < len(doc_pages) <= MAX_PAGES:
            raise ValueError("Poppler page limit")
        subprocess.run(
            [
                "pdftoppm",
                "-f",
                "1",
                "-l",
                str(len(doc_pages)),
                "-scale-to",
                "1800",
                "-gray",
                "-png",
                str(pdf),
                str(root / "page"),
            ],
            capture_output=True,
            check=True,
            timeout=80,
        )
        images = sorted(root.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
        if len(images) != len(doc_pages):
            raise ValueError("Poppler page/render mismatch")
        pages = []
        for n, (page, image) in enumerate(zip(doc_pages, images, strict=True), 1):
            width, height = float(page.attrib["width"]), float(page.attrib["height"])
            words = [
                Word(*(float(w.attrib[k]) for k in ("xMin", "yMin", "xMax", "yMax")), w.text or "")
                for w in page.iter("{http://www.w3.org/1999/xhtml}word")
            ]
            with Image.open(image) as im:
                gray = np.asarray(im.convert("L"))
                mask = gray < 235
            gradient = np.abs(np.diff(gray.astype("int16"), axis=0)) >= 30
            h, w = mask.shape
            sx = w / width
            sy = h / height
            xs = clusters([float(x) / sx for x in np.flatnonzero(mask.mean(axis=0) >= 0.18)])

            def horizontal(a, b, sx=sx, sy=sy, gradient=gradient):
                x0, x1 = round(a * sx), round(b * sx)
                if x1 - x0 < 2:
                    return []
                return clusters(
                    [
                        (float(y) + 0.5) / sy
                        for y in np.flatnonzero(gradient[:, x0:x1].mean(axis=1) >= 0.85)
                    ]
                )

            def closed(x, a, b, sx=sx, sy=sy, w=w, h=h, mask=mask):
                x0 = max(0, round(x * sx) - 2)
                x1 = min(w, round(x * sx) + 3)
                y0 = max(0, round(a * sy))
                y1 = min(h, round(b * sy))
                return bool(y1 > y0 and mask[y0:y1, x0:x1].any(axis=1).mean() >= 0.90)

            result = extract_grid(words, xs, horizontal, n, closed)
            if "header_not_unique" in result[1]:
                result = extract_virtual(words, xs, horizontal, n, closed)
            pages.append(result)
        version = (
            subprocess.run(["pdftotext", "-v"], capture_output=True, timeout=5, check=True)
            .stderr.decode()
            .splitlines()[0]
        )
        return {**finish("poppler_rendered_geometry", pages), "version": version}


def run(raw):
    import hashlib

    return {
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "native": extract_native(raw),
        "independent": extract_poppler(raw),
        "canonical_packs_promoted": 0,
    }
