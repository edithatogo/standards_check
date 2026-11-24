#!/usr/bin/env python3
"""Discover upstream guideline source links. No downloads, licence or content admission."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import yaml

try:
    from .sync_equator_catalog import inventory
except ImportError:  # direct execution as scripts/equator_source_links.py
    from sync_equator_catalog import inventory

LINK_START = re.compile(r"(?<!!)\[[^\]\n]{1,200}\]\(")
BARE = re.compile(
    r"https?://\[[0-9a-fA-F:.]+\](?:/[^\s<>)\]'}\"]{0,2048})?|https?://[^\s<>\]'}\"]{1,2048}"
)
FILES = (".pdf", ".doc", ".docx", ".rtf", ".csv", ".xlsx", ".xls")
FIELDS = ("downloads", "relevant-urls", "full-bibliographic-reference")
MAX_CANDIDATES = 64


def extract_links(data: dict, page_url: str, issues: list[str] | None = None) -> list[dict]:
    """Conservatively extract hyperlinks; a URL is never evidence of checklist rights."""
    collected = []
    seen = set()
    for field in FIELDS:
        text = data.get(field) or ""
        if not isinstance(text, str):
            continue  # caller flags malformed metadata separately
        # Balance parentheses in Markdown destinations, then scan other URLs.
        # Avoid truncated duplicate URLs from the same Markdown destination.
        candidates = []
        remaining = list(text)
        for match in LINK_START.finditer(text):
            depth = 1
            for pos in range(match.end(), min(len(text), match.end() + 2048)):
                if text[pos] == "(":
                    depth += 1
                elif text[pos] == ")":
                    depth -= 1
                    if depth == 0:
                        destination = text[match.end() : pos].strip().strip("<>")
                        if destination and not any(char.isspace() for char in destination):
                            candidates.append(destination)
                            remaining[match.start() : pos + 1] = " " * (pos + 1 - match.start())
                        break
        for match in BARE.finditer("".join(remaining)):
            target = match.group()
            while target.endswith(")") and target.count(")") > target.count("("):
                target = target[:-1]
            candidates.append(target)
        for target in candidates:
            target = target.strip().rstrip(".,;:")
            try:
                resolved = urljoin(page_url, target)
                url = urlsplit(resolved)
                hostname = url.hostname
                if (
                    url.scheme not in {"https", "http"}
                    or not hostname
                    or url.username is not None
                    or url.password is not None
                    or target.startswith(("javascript:", "file:", "data:"))
                    or resolved in seen
                ):
                    continue
            except ValueError:
                if issues is not None and "malformed_candidate_url" not in issues:
                    issues.append("malformed_candidate_url")
                continue
            try:
                if not ipaddress.ip_address(hostname).is_global:
                    continue
            except ValueError:
                if hostname == "localhost" or hostname.endswith((".local", ".internal")):
                    continue
            seen.add(resolved)
            extension = url.path.lower().split("/")[-1]
            kind = (
                "source_file_candidate"
                if extension.endswith(FILES)
                else "doi_landing_candidate"
                if hostname in {"doi.org", "dx.doi.org"}
                else "interactive_page_candidate"
                if extension.endswith(".qmd")
                else "landing_page_candidate"
            )
            collected.append(
                {
                    "url": resolved,
                    "source_field": field,
                    "type": kind,
                    "qualification": "unverified_link_only",
                }
            )
    return collected


def _metadata(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8-sig")
    if not raw.startswith("---\n"):
        raise ValueError("missing frontmatter")
    block, sep, _ = raw[4:].partition("\n---\n")
    if not sep:
        raise ValueError("incomplete frontmatter")
    data = yaml.safe_load(block)
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def collect(root: Path, catalogue: dict) -> dict:
    revision, tree_entries = inventory(root)
    if catalogue.get("source_revision") != revision:
        raise ValueError("source revision differs from pinned EQUATOR catalogue")
    rows = catalogue.get("guidelines")
    if not isinstance(rows, list) or not rows or catalogue.get("published_count") != len(rows):
        raise ValueError("invalid upstream catalogue count")
    tree = dict(tree_entries)
    if len(tree) != len(rows):
        raise ValueError("source tree differs from EQUATOR catalogue")
    seen = set()
    report = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("source_path"), str):
            raise ValueError("invalid upstream entry")
        path, sha = row["source_path"], row.get("source_blob_sha")
        if (
            path not in tree
            or tree[path] != sha
            or path in seen
            or row.get("id") != "equator:" + path.split("/")[1]
            or row.get("page_url")
            != "https://equator-network.org/reporting-guidelines/" + path.split("/")[1] + "/"
        ):
            raise ValueError("source identity, path or Git blob mismatch")
        seen.add(path)
        issues = []
        try:
            metadata = _metadata(root / path)
        except (OSError, UnicodeError, yaml.YAMLError, ValueError):
            metadata = {}
            issues.append("invalid_source_frontmatter")
        if not isinstance(metadata.get("title"), str) or not metadata.get("title", "").strip():
            issues.append("missing_source_title")
        for field in FIELDS:
            if metadata.get(field) is not None and not isinstance(metadata[field], str):
                issues.append("invalid_" + field)
        links = extract_links(metadata, row["page_url"], issues)
        if len(links) > MAX_CANDIDATES:
            links = links[:MAX_CANDIDATES]
            issues.append("link_limit_exceeded")
        report.append(
            {
                "id": row["id"],
                "source_path": path,
                "source_blob_sha": sha,
                "status": "needs_review" if issues else "unverified_candidates",
                "issues": issues,
                "candidates": links,
            }
        )
    if seen != set(tree):
        raise ValueError("incomplete EQUATOR source coverage")
    return {
        "schema_version": 1,
        "authority": "candidate_links_only_no_downloads_or_rights",
        "source_revision": revision,
        "published_count": len(report),
        "summary": {
            "records_with_candidates": sum(bool(r["candidates"]) for r in report),
            "link_count": sum(len(r["candidates"]) for r in report),
            "records_needing_review": sum(r["status"] == "needs_review" for r in report),
        },
        "guidelines": report,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = collect(args.source, json.loads(args.catalogue.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"EQUATOR source links: {report['summary']}; rights and text remain unverified")


if __name__ == "__main__":
    main()
