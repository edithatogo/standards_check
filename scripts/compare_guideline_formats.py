"""Offline cross-family checklist comparison; structural diagnostics, never admission."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
from importlib.metadata import version
from itertools import combinations
import json
from pathlib import Path

from .compare_ecoevo_formats import COHORT, EXPECTED_IDS, REFERENCE, collect_rows, compare_formats, pdf_tables, read_bounded
from .reconcile_authoritative_articles import snapshot_table
from .structured_source import ITEM_ID, extract_structure, fingerprint

ARTICLE_SPECS = "source/official/authoritative-article-editions.json"
ARTICLE_ROWS = "source/official/authoritative-article-rows.json"
PRIORITY = "source/official/priority-article-candidates.json"
HELD = "tests/fixtures/held-guidelines/source-item-identities.json"
ARCHIVE = "source/archive/processed/"
ARCHETYPE = "source/archetypes/"
VARIANT = "source/variants/"


@dataclass(frozen=True)
class Cohort:
    edition: str
    family: str
    expected_ids: tuple[str, ...]
    paths: tuple[str, ...]
    reference: str
    snapshot: bool = False
    scope: str = "printed item IDs; nested requirements not qualified"


def header_roles() -> dict[str, str]:
    # Explicit header aliases only; numeric response cells cannot become IDs.
    labels = {
        "id": ("Item number", "Item No.", "Item No", "Item ID", "Item #",
               "Sub-item number", "Subitem number", "No."),
        "requirement": ("Recommendation", "Recommendations", "Checklist item",
                        "Checklist items", "Item description", "Reporting item",
                        "Reporting requirement", "Requirement", "Description",
                        "Sub-item", "Subitem", "Checklist recommendation"),
    }
    return {fingerprint(variant): role for role, names in labels.items()
            for label in names for variant in (label, label.lower(), label.upper(), label.title())}


def load_json(root: Path, path: str):
    return json.loads(read_bounded(root / path, 20_000_000))


def profiles(root: Path) -> list[Cohort]:
    """Reuse independent printed-ID references; never infer them from legacy views."""
    priority = {x["edition"]: x for x in load_json(root, PRIORITY)}
    held = load_json(root, HELD)["editions"]
    articles = {x["edition"]: x for x in load_json(root, ARTICLE_SPECS)}
    result = [Cohort("prisma-ecoevo-2021", "prisma", tuple(EXPECTED_IDS),
                     tuple(COHORT), REFERENCE, scope="89 printed subitems; 27 main groups")]
    candidates = (
        ("prisma-p-2015", "prisma", (VARIANT + "prisma-p.pdf", ARCHIVE + "PRISMA-P-checklist.docx")),
        ("prisma-s-2021", "prisma", ()),
        ("prisma-abstracts-2020", "prisma", (ARCHIVE + "PRISMA_2020_abstract_checklist.docx",
                                             ARCHIVE + "PRISMA_2020_abstract_checklist.pdf")),
        ("cheers-2022", "cheers", (ARCHETYPE + "cheers-2022.pdf",)),
        ("arrive-2.0-2020", "arrive", (ARCHETYPE + "arrive-2020.pdf",)),
        ("consort-2025", "consort", (ARCHIVE + "CONSORT_2025_checklist.docx",
                                    ARCHIVE + "CONSORT_2025_editable_checklist.docx",
                                    ARCHIVE + "bmj-2024-081123.full.pdf")),
        ("spirit-2025", "spirit", (ARCHETYPE + "spirit-2025.docx",
                                  ARCHIVE + "bmj-2024-081477.full.pdf")),
        ("stard-2015", "stard", (ARCHETYPE + "stard-2015.pdf",)),
        ("strobe-2007", "strobe", (ARCHETYPE + "strobe-2007.pdf",)),
        ("tripod-ai-2024", "tripod", ()),
        ("srqr-2014", "srqr", (ARCHETYPE + "srqr-2014.docx", ARCHETYPE + "srqr-2014.pdf")),
        ("coreq-2007", "coreq", (ARCHETYPE + "coreq-2007.pdf",)),
        ("squire-2.0-2015", "squire", (ARCHETYPE + "squire-2016.pdf",)),
    )
    for edition, family, paths in candidates:
        if edition in articles:
            entry = articles[edition]
            ids = entry["item_ids"]
            reference = ARTICLE_SPECS + "#" + edition
            scope = "Retained primary article table; co-publication/derivative identity held"
        elif edition in priority:
            entry = priority[edition]
            ids = [item for table in entry["table_item_ids"] for item in table]
            reference = PRIORITY + "#" + edition
            scope = entry["scope"]
        else:
            entry = held[edition]
            ids = entry["item_ids"]
            reference = HELD + "#" + edition
            scope = entry["identifier_scope"]
        result.append(Cohort(edition, family, tuple(ids), paths, reference,
                             edition in articles, scope))
    return result


def summarize_source(rows: list[dict], expected: tuple[str, ...], issues: list[str]) -> dict:
    safe_rows = []
    issues = list(issues)
    for row in rows:
        record = {key: row.get(key) for key in ("item_id", "identifier_anchor",
                                               "requirement_anchor", "requirement_sha256")}
        if not record["identifier_anchor"] or not record["requirement_anchor"]:
            issues.append("missing_row_anchor")
            record["requirement_sha256"] = None
        safe_rows.append(record)
    counts = Counter(row["item_id"] for row in safe_rows)
    known = set(expected)
    return {
        "rows": safe_rows,
        "observed_row_count": len(rows),
        "expected_ids_recovered": sum(item in counts for item in expected) if expected else None,
        "missing_ids": [item for item in expected if item not in counts] if expected else None,
        "extra_ids": sorted(set(counts) - known) if expected else None,
        "duplicate_ids": sorted(item for item, n in counts.items() if n > 1),
        "exact_expected_order": [row["item_id"] for row in rows] == list(expected) if expected else None,
        "issues": sorted(set(issues)),
    }


def candidate_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError("invalid candidate path")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink candidate")
    return current


def observe_file(root: Path, path: str, cohort: Cohort) -> dict:
    source_path = candidate_path(root, path)
    suffix = source_path.suffix.lower()
    result = {"path": path, "format": suffix.lstrip("."), "source_sha256": None,
              "identity": "candidate_path_only_unverified", "status": "held_unavailable_or_unsupported"}
    rows, issues = [], []
    try:
        raw = read_bounded(source_path)
        result["source_sha256"] = hashlib.sha256(raw).hexdigest()
        if suffix == ".pdf":
            result["extractor"] = "pdfplumber_ruled_table"
            result["extractor_version"] = version("pdfplumber")
            structure = pdf_tables(raw)
        else:
            result["extractor"] = suffix.lstrip(".") + "_structured_source"
            package = {".docx": "python-docx", ".xlsx": "openpyxl", ".html": "lxml"}.get(suffix)
            if package:
                result["extractor_version"] = version(package)
            _, structure = extract_structure(raw, suffix)
        rows, issues = collect_rows(structure, identifier_pattern=ITEM_ID, header_roles=header_roles())
        issues.extend(structure.get("issues", []))
        if not rows:
            issues.append("no_explicit_numbered_requirement_rows")
        result["status"] = "held_structural_discrepancy" if issues else "structure_observed_not_qualified"
    except Exception as exc:  # Third-party parser errors stay held; no raw text.
        issues.append("extraction_failed:" + type(exc).__name__)
    summary = summarize_source(rows, cohort.expected_ids, issues)
    if summary["issues"] and result["status"] == "structure_observed_not_qualified":
        result["status"] = "held_structural_discrepancy"
    return {**result, **summary}


def observe_snapshot(root: Path, cohort: Cohort) -> dict:
    spec = next(x for x in load_json(root, ARTICLE_SPECS) if x["edition"] == cohort.edition)
    retained = next(x for x in load_json(root, ARTICLE_ROWS)["editions"] if x["edition"] == cohort.edition)
    verified = snapshot_table(retained, spec)
    rows = [{"item_id": row["item_id"], "identifier_anchor": row["source_anchor"],
             "requirement_anchor": row["source_anchor"], "requirement_sha256": fingerprint(row["text"])}
            for row in verified["rows"]]
    return {"path": ARTICLE_ROWS + "#" + cohort.edition, "format": "jats_snapshot",
            "source_sha256": verified["source_sha256"], "table_rows_sha256": verified["table_rows_sha256"],
            "identity": verified["pin_status"], "status": "retained_snapshot_not_full_structure",
            "extractor": "reconcile_authoritative_articles.snapshot_table",
            **summarize_source(rows, cohort.expected_ids, ["pinned_xml_required"])}


def benchmark(root: Path, cohorts: list[Cohort]) -> dict:
    editions = []
    seen = set()
    for cohort in sorted(cohorts, key=lambda value: value.edition):
        if (cohort.edition in seen or len(set(cohort.expected_ids)) != len(cohort.expected_ids)
                or len(set(cohort.paths)) != len(cohort.paths)
                or any(not ITEM_ID.fullmatch(item) for item in cohort.expected_ids)):
            raise ValueError("duplicate or invalid cohort reference")
        seen.add(cohort.edition)
        sources = [observe_file(root, path, cohort) for path in cohort.paths]
        if cohort.snapshot:
            sources.append(observe_snapshot(root, cohort))
        pairwise = []
        if cohort.expected_ids:
            for left, right in combinations(sources, 2):
                same_bytes = bool(left["source_sha256"] and left["source_sha256"] == right["source_sha256"])
                comparison = compare_formats(left["rows"], right["rows"], expected_ids=cohort.expected_ids)
                pairwise.append({"left": left["path"], "right": right["path"],
                                 "cross_format": left["format"] != right["format"],
                                 "identical_source_bytes": same_bytes,
                                 "independent_source_identity_verified": False,
                                 **comparison})
        editions.append({"edition": cohort.edition, "family": cohort.family,
                         "reference": cohort.reference, "scope": cohort.scope,
                         "expected_item_ids": list(cohort.expected_ids) if cohort.expected_ids else None,
                         "status": ("held_no_candidate_sources" if not sources else
                                    "held_no_independent_denominator" if not cohort.expected_ids else
                                    "candidate_comparison_only"),
                         "sources": sources, "pairwise": pairwise})
    return {"schema_version": 1, "claim_boundary": "candidate-only; edition/rights/interpretation require separate review",
            "editions": editions, "canonical_packs_promoted": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = benchmark(args.root, profiles(args.root))
    report["reference_files_sha256"] = {
        path: hashlib.sha256(read_bounded(args.root / path)).hexdigest()
        for path in (ARTICLE_SPECS, ARTICLE_ROWS, PRIORITY, HELD)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
