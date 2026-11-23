"""Compare a fixed EcoEvo 2021 candidate cohort; never establish admission."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
from itertools import combinations
import json
from pathlib import Path
import re
import subprocess

if __package__:
    from .structured_source import cell_fields, fingerprint
else:
    from structured_source import cell_fields, fingerprint

# Printed sub-item sequences from the official checklist PDF (2021, seven pages),
# not from the legacy Markdown or any local candidate. No checklist prose copied.
REFERENCE = "https://www.prisma-statement.org/s/PRISMA-EcoEvo_PDFChecklist.pdf"
COUNTS = (6, 5, 3, 2, 4, 2, 6, 4, 2, 3, 2, 2, 5, 3, 3, 3, 1, 4, 4, 5, 1, 1, 4, 2, 6, 4, 2)
EXPECTED_IDS = [f"{i}.{j}" for i, count in enumerate(COUNTS, 1) for j in range(1, count + 1)]
COHORT = {
    "source/variants/prisma-ecoevo.csv": None,
    "source/variants/prisma-ecoevo.pdf": "PRISMA-EcoEvo_PDFChecklist.pdf",
    "source/archive/processed/PRISMA-EcoEvo_WordChecklist.docx": "PRISMA-EcoEvo_WordChecklist.docx",
    "source/archive/processed/PRISMA-EcoEvo_ExcelChecklist.xlsx": "PRISMA-EcoEvo_ExcelChecklist.xlsx",
}
ID = re.compile(r"[0-9]{1,3}\.[0-9]{1,3}")
HEADER = {fingerprint("Sub-item number"): "id", fingerprint("Sub-item"): "requirement"}
EMPTY = fingerprint("")
MAX_BYTES = 20_000_000


def read_bounded(path: Path, limit: int = MAX_BYTES) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("source exceeds limit")
    return raw


def collect_rows(structure: dict) -> tuple[list[dict], list[str]]:
    """Match explicit header roles, not arbitrary numeric-looking scoring cells."""
    records, issues = [], set()

    def visit(node: dict) -> None:
        columns = None
        for row in node.get("rows", []):
            cells = {cell.get("column", ordinal): cell for ordinal, cell in enumerate(row["cells"], 1)}
            headers = [(column, cell.get("header_role") or HEADER.get(cell.get("text_sha256")))
                       for column, cell in cells.items()]
            id_cols = [column for column, role in headers if role == "id"]
            req_cols = [column for column, role in headers if role == "requirement"]
            if id_cols or req_cols:
                columns = (id_cols[0], req_cols[0]) if len(id_cols) == len(req_cols) == 1 and id_cols != req_cols else None
                if columns is None:
                    issues.add("incomplete_or_ambiguous_header")
                continue
            if columns is None:
                continue
            identifier = cells.get(columns[0], {})
            requirement = cells.get(columns[1], {})
            item_id = identifier.get("item_id_candidate")
            if not isinstance(item_id, str) or not ID.fullmatch(item_id) or identifier.get("value_type") == "f":
                if identifier.get("text_sha256") not in {None, EMPTY} or requirement.get("text_sha256") not in {None, EMPTY}:
                    issues.add("unclassified_data_row")
                continue
            digest = requirement.get("text_sha256")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest) or digest == EMPTY or requirement.get("value_type") == "f":
                digest = None
                issues.add("missing_or_ineligible_requirement")
            records.append({"item_id": item_id, "identifier_anchor": identifier.get("anchor"),
                            "requirement_anchor": requirement.get("anchor"), "requirement_sha256": digest})
        for key in ("blocks", "sheets"):
            for child in node.get(key, []):
                visit(child)

    visit(structure)
    return records, sorted(issues)


def compare_formats(left: list[dict], right: list[dict]) -> dict:
    def unique(rows: list[dict]) -> dict:
        counts = Counter(row["item_id"] for row in rows)
        return {row["item_id"]: row["requirement_sha256"] for row in rows
                if counts[row["item_id"]] == 1 and row["requirement_sha256"] is not None}
    a, b = unique(left), unique(right)
    common = [item for item in EXPECTED_IDS if item in a and item in b]
    different = [item for item in common if a[item] != b[item]]
    return {"compared": len(common), "exact_equal": len(common) - len(different), "different_ids": different,
            "not_comparable_expected_ids": [item for item in EXPECTED_IDS if item not in common]}


def pdf_tables(raw: bytes) -> dict:
    """Bounded ruled-table experiment with the existing pdfplumber engine."""
    import pdfplumber

    blocks, count = [], 0
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        if len(pdf.pages) > 80:
            raise ValueError("PDF page limit")
        for page in pdf.pages:
            if len(page.edges) > 5000:
                raise ValueError("PDF edge limit")
            for table_number, table in enumerate(page.find_tables(), 1):
                rows = []
                for row_number, values in enumerate(table.extract(), 1):
                    count += len(values)
                    if count > 100_000:
                        raise ValueError("PDF cell limit")
                    cells = []
                    for column, value in enumerate(values, 1):
                        value = value or ""
                        header = re.sub(r"[^a-z0-9]", "", value.casefold())
                        anchor = f"page/{page.page_number}/table/{table_number}/r{row_number}/c{column}"
                        cells.append({"anchor": anchor, "column": column, **cell_fields(value),
                                      "header_role": {"subitemnumber": "id", "subitem": "requirement"}.get(header)})
                    rows.append({"cells": cells})
                blocks.append({"rows": rows})
    return {"blocks": blocks}


def layout_ids(layout: str) -> list[dict]:
    """Independent Poppler layout-field tokens, not verified full numbered rows."""
    return [{"item_id": field, "page": page, "line": line}
            for page, text in enumerate(layout.split("\f"), 1)
            for line, row in enumerate(text.splitlines(), 1)
            for field in re.split(r"\s{2,}", row.strip()) if ID.fullmatch(field)]


def benchmark(report: dict, root: Path | None = None, official: Path | None = None) -> dict:
    if report.get("schema_version") != 3 or report.get("summary", {}).get("verified_by_this_process") != 0:
        raise ValueError("unexpected source-triage receipt")
    records = [row for row in report["legacy_items"] if row["legacy_id"] == "prisma-ecoevo"]
    if len(records) != 1:
        raise ValueError("expected exactly one EcoEvo cohort")
    probes = {p["path"]: p for p in records[0]["source_probes"]}
    if len(probes) != len(records[0]["source_probes"]):
        raise ValueError("duplicate source probe")
    results = []
    for path, filename in COHORT.items():
        probe = probes.get(path, {})
        digest = probe.get("source_sha256")
        source = {"path": path, "source_sha256": digest, "official_url": f"https://www.prisma-statement.org/s/{filename}" if filename else None,
                  "identity": "local_derivative_no_official_csv" if filename is None else "official_bytes_not_checked"}
        if official is not None and filename is not None:
            try:
                downloaded = hashlib.sha256(read_bounded(official / filename)).hexdigest()
                source.update(official_sha256=downloaded, identity="official_bytes_equal" if downloaded == digest else "official_bytes_different")
            except (OSError, ValueError):
                source["identity"] = "official_bytes_unavailable"
        structure = probe.get("source_structure")
        issues = []
        raw = None
        source["local_bytes"] = "not_rechecked"
        if root is not None:
            try:
                raw = read_bounded(root / path)
                if hashlib.sha256(raw).hexdigest() != digest:
                    raise ValueError("source digest differs from probe")
                source["local_bytes"] = "digest_matches_triage"
            except (OSError, ValueError):
                raw, structure = None, None
                source["local_bytes"] = "held_unavailable_or_changed"
                issues.append("local_source_unavailable_or_changed")
        if path.endswith(".pdf") and raw is not None:
            try:
                import pdfplumber
                source["pdfplumber_version"] = pdfplumber.__version__
                structure = pdf_tables(raw)
            except Exception as exc:  # parser-specific failures remain held, no text leaked
                issues.append("pdf_table_extraction_failed:" + type(exc).__name__)
            # Run the independent parser even when the first parser fails.
            try:
                run = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", "-", "-"],
                                     input=raw, capture_output=True, timeout=20, check=True)
                if len(run.stdout) > 8_000_000:
                    raise ValueError("Poppler output exceeds limit")
                tokens = layout_ids(run.stdout.decode("utf-8"))
                token_counts = Counter(token["item_id"] for token in tokens)
                version = subprocess.run(["pdftotext", "-v"], capture_output=True, timeout=5, check=True)
                source["poppler_version"] = version.stderr.decode("utf-8").splitlines()[0] if version.stderr else "unknown"
                source["poppler_layout_tokens"] = tokens
                source["poppler_expected_id_tokens"] = sum(item in token_counts for item in EXPECTED_IDS)
                source["poppler_duplicate_id_tokens"] = sorted(item for item, count in token_counts.items() if count > 1)
            except (OSError, subprocess.SubprocessError, UnicodeError, ValueError):
                issues.append("poppler_layout_unavailable")
        rows, row_issues = collect_rows(structure) if structure is not None else ([], ["structure_unavailable"])
        counts = Counter(row["item_id"] for row in rows)
        source.update(rows=rows, structure_status=(structure or {}).get("status", "candidate_only"),
                      expected_ids_recovered=sum(item in counts for item in EXPECTED_IDS),
                      missing_ids=[item for item in EXPECTED_IDS if item not in counts],
                      extra_ids=sorted(set(counts) - set(EXPECTED_IDS)),
                      duplicate_ids=sorted(item for item, count in counts.items() if count > 1),
                      exact_expected_order=[row["item_id"] for row in rows] == EXPECTED_IDS,
                      issues=sorted(set(issues + row_issues)))
        results.append(source)
    return {"edition": "PRISMA-EcoEvo 2021 v1.0", "doi": "10.1111/brv.12721", "numbering_reference": REFERENCE,
            "expected_item_ids": EXPECTED_IDS, "claim_boundary": "candidate structural comparison; no rights, authority or admission",
            "sources": results, "pairwise": [{"left": a["path"], "right": b["path"], **compare_formats(a["rows"], b["rows"])}
                                               for a, b in combinations(results, 2)], "canonical_packs_promoted": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", type=Path, help="Optional repository checkout for the PDF experiment")
    parser.add_argument("--official-dir", type=Path, help="Optional explicitly acquired official files; no downloads here")
    args = parser.parse_args()
    raw = read_bounded(args.report, 100_000_000)
    evidence = benchmark(json.loads(raw), args.root, args.official_dir)
    evidence["triage_report_sha256"] = hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for source in evidence["sources"]:
        print(source["path"], source["expected_ids_recovered"], source["identity"])


if __name__ == "__main__":
    main()
