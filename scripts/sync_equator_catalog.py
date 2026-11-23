#!/usr/bin/env python3
"""Index EQUATOR's versioned public directory metadata, not checklist text."""

import argparse
import json
import re
import subprocess
from pathlib import Path

import yaml

UPSTREAM = "https://github.com/EQUATOR-Network/equator-website"
PAGE_BASE = "https://equator-network.org/reporting-guidelines/"
INDEX_PATH = re.compile(r"^reporting-guidelines/([^/]+)/index\.qmd$")
DOI = re.compile(r"^10\.\d{4,9}/\S+$", re.I)
PMID = re.compile(r"(?<!\d)\d{7,9}(?!\d)")


def git(source: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(source), *args],
        check=True, text=True, capture_output=True,
    ).stdout.strip()


def inventory(source: Path) -> tuple[str, list[tuple[str, str]]]:
    revision = git(source, "rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("EQUATOR source revision must be a full commit SHA")
    if git(source, "status", "--porcelain", "--", "reporting-guidelines"):
        raise ValueError("EQUATOR reporting-guidelines checkout is modified")
    records = []
    for line in git(source, "ls-tree", "-r", "HEAD", "--", "reporting-guidelines").splitlines():
        left, path = line.split("\t", 1)
        match = INDEX_PATH.fullmatch(path)
        if match and match.group(1) != "under-development":
            mode, kind, blob_sha = left.split()
            if mode != "100644" or kind != "blob":
                raise ValueError(f"Unexpected upstream entry type: {path}")
            records.append((path, blob_sha))
    if not records:
        raise ValueError("No published EQUATOR guideline pages found")
    return revision, sorted(records)


def _frontmatter(path: Path) -> dict:
    source = path.read_text(encoding="utf-8-sig")
    if not source.startswith("---\n"):
        raise ValueError(f"Missing YAML frontmatter: {path}")
    header, sep, _ = source[4:].partition("\n---\n")
    if not sep:
        raise ValueError(f"Unterminated YAML frontmatter: {path}")
    data = yaml.safe_load(header)
    if not isinstance(data, dict) or not isinstance(data.get("title"), str) or not data["title"].strip():
        raise ValueError(f"Missing guideline title: {path}")
    return data


def _list_field(data: dict, name: str) -> list[str]:
    value = data.get(name) or []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"Unexpected {name} list in EQUATOR source")
    return list(dict.fromkeys(item.strip() for item in value if item.strip()))


def _identifiers(data: dict) -> tuple[str | None, str | None]:
    raw_doi = (data.get("rg-doi") or "").strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/"):
        if raw_doi.lower().startswith(prefix):
            raw_doi = raw_doi[len(prefix):]
            break
    doi = raw_doi if DOI.fullmatch(raw_doi) else None
    ids = set(PMID.findall(str(data.get("pmid-id") or "")))
    if not ids:
        ids = set(PMID.findall(str(data.get("pmid-url") or "")))
    return doi, next(iter(ids)) if len(ids) == 1 else None


def build_catalog(source: Path, revision: str, records: list[tuple[str, str]], *, metadata: bool) -> dict:
    rows = []
    for path, blob_sha in records:
        match = INDEX_PATH.fullmatch(path)
        if not match or match.group(1) == "under-development":
            raise ValueError(f"Not a published guideline page: {path}")
        slug = match.group(1)
        row = {
            "id": f"equator:{slug}",
            "page_url": f"{PAGE_BASE}{slug}/",
            "source_path": path,
            "source_blob_sha": blob_sha,
            "metadata_status": "extracted_unverified" if metadata else "not_extracted",
        }
        if metadata:
            file = source / path
            if not file.is_file():
                raise ValueError(f"Missing source page (check sparse checkout): {path}")
            data = _frontmatter(file)
            doi, pmid = _identifiers(data)
            row.update({
                "title": data["title"].strip(),
                "acronym": str(data.get("acronym") or "").strip() or None,
                "doi": doi,
                "pmid": pmid,
                "study_types": _list_field(data, "categories"),
                "clinical_areas": _list_field(data, "clinical-specialty"),
                "report_sections": _list_field(data, "report-section"),
            })
        rows.append(row)
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate EQUATOR guideline ID")
    return {
        "schema_version": 1,
        "source_repository": UPSTREAM,
        "source_revision": revision,
        "source_directory": "reporting-guidelines",
        "rights_status": "not_assessed_for_individual_guidelines",
        "published_count": len(rows),
        "guidelines": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Local EQUATOR Git checkout")
    parser.add_argument("--mode", choices=("discover", "catalogue"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="Fail on output drift; do not write")
    args = parser.parse_args()
    revision, paths = inventory(args.source)
    result = build_catalog(args.source, revision, paths, metadata=args.mode == "catalogue")
    output = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != output:
            parser.error("EQUATOR catalogue differs from pinned source")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(output)
    print(f"{args.mode}: {result['published_count']} records at {revision}")


if __name__ == "__main__":
    main()
