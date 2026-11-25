#!/usr/bin/env python3
"""Validate an offline metadata release; never upload or authenticate a review."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlsplit

try:
    from scripts.source_reconciliation import validate_table_shapes
    from scripts.validate_publication_contract import (
        design_digest,
        fields,
        hexadecimal,
        nonempty,
        require,
        strings,
        timestamp,
    )
except ImportError:
    from source_reconciliation import validate_table_shapes
    from validate_publication_contract import (
        design_digest,
        fields,
        hexadecimal,
        nonempty,
        require,
        strings,
        timestamp,
    )

ROOT = Path(__file__).resolve().parents[1]
REVIEW_KINDS = ("rights", "privacy", "secrets", "benchmark_leakage")
COLUMNS = {
    **dict.fromkeys(
        "key source_revision source_blob_sha page_url doi pmcid source_sha256 "
        "status lookup_status metadata_status rights_status disposition code record".split(),
        "str",
    ),
    **dict.fromkeys("expected_rows matched_rows".split(), "int"),
    "identity_conflict": "bool",
}
STATUS_VALUES = set(
    "held lookup_incomplete metadata_only missing_identifier oa_xml_candidate "
    "identifier_conflict ambiguous_identifier expected_numbered_rows_observed "
    "deferred_acquisition_budget source_inventory_observed_not_reconciled".split()
)
release_digest = design_digest


def decode(raw: str | bytes) -> object:
    def unique(pairs: list[tuple[str, object]]) -> dict:
        result: dict = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON field: {key}")
            result[key] = value
        return result

    return json.loads(raw, object_pairs_hook=unique)


def safe_path(root: Path, value: object) -> Path:
    name = nonempty(value, "safe relative path")
    path = Path(name)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in name
        and ":" not in name
        and path.as_posix() == name
        and name != ".",
        "safe relative path without traversal required",
    )
    require(
        not any(root.joinpath(*path.parts[:n]).is_symlink() for n in range(1, len(path.parts) + 1)),
        "symlink in evidence/package path",
    )
    resolved = root / path
    require(resolved.resolve().is_relative_to(root.resolve()), "path escapes root")
    return resolved


def read_bound(root: Path, reference: dict) -> bytes:
    path = safe_path(root, reference.get("path"))
    hexadecimal(reference.get("sha256"), 64, "file sha256")
    require(
        path.is_file() and path.stat().st_size <= 10_000_000, "file absent or exceeds 10MB limit"
    )
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == reference["sha256"], f"file hash mismatch: {path}")
    return raw


def check_review(root: Path, reference: object, kind: str, digest: str) -> None:
    ref = fields(reference, "path sha256", f"{kind} review receipt")
    record = fields(
        decode(read_bound(root, ref)),
        "kind release_sha256 outcome reviewer reviewed_at summary",
        f"{kind} review",
    )
    require(record["kind"] == kind and record["outcome"] == "pass", f"{kind} review must pass")
    require(record["release_sha256"] == digest, f"{kind} review release hash mismatch")
    nonempty(record["reviewer"], "reviewer")
    nonempty(record["summary"], "review summary")
    timestamp(record["reviewed_at"])


def check_export(package: Path, item: dict) -> None:
    fields(item, "path sha256 format rows source_content_rights export_permission columns", "file")
    require(item["export_permission"] == "approved", "file needs explicit export permission")
    require(
        item["source_content_rights"] in ("unassessed", "cleared", "restricted", "not_applicable"),
        "declare source_content_rights separately from export permission",
    )
    raw = read_bound(package, item)
    columns = item["columns"]
    require(isinstance(columns, dict), "columns must declare individual export permissions")
    if item["format"] == "markdown":
        require(
            item["path"] in ("README.md", "ATTRIBUTION.md")
            and not columns
            and item["rows"] is None,
            "only reviewed README/ATTRIBUTION documentation allowed",
        )
        nonempty(raw.decode("utf-8"), "documentation")
        return
    require(
        bool(columns) and "key" in columns and set(columns).issubset(COLUMNS),
        "metadata column allowlist excludes source text, labels and item fingerprints",
    )
    require(
        all(value == "approved" for value in columns.values()),
        "every column needs explicit export permission",
    )
    if item["format"] == "jsonl":
        require(str(item["path"]).endswith(".jsonl"), "jsonl extension required")
        rows = [decode(line) for line in raw.splitlines() if line.strip()]
    elif item["format"] == "parquet":
        import polars as pl

        require(str(item["path"]).endswith(".parquet"), "parquet extension required")
        try:
            frame = pl.read_parquet(io.BytesIO(raw))
        except pl.exceptions.PolarsError as error:
            raise ValueError(f"Parquet unreadable: {error}") from error
        require(set(frame.columns) == set(columns), "unexpected analytical columns")
        rows = frame.to_dicts()
    else:
        raise ValueError("only jsonl, parquet and reviewed markdown are supported")
    require(
        type(item["rows"]) is int and item["rows"] > 0 and len(rows) == item["rows"],
        "positive exact row count required",
    )
    typed_rows = [fields(row, " ".join(columns), "analytical columns") for row in rows]
    validate_table_shapes({"metadata": typed_rows}, {"metadata": {c: COLUMNS[c] for c in columns}})
    for row in typed_rows:
        for column, value in row.items():
            if isinstance(value, str):
                require(
                    not any(char.isspace() for char in value),
                    f"{column}: free text is excluded from this metadata profile",
                )
            if column in ("status", "lookup_status") and value is not None:
                require(
                    value in STATUS_VALUES, "operational status required; relation labels excluded"
                )


def validate(contract: dict, root: Path = ROOT) -> dict:
    fields(contract, "schema_version status release reviews approval", "dataset contract")
    require(
        contract["schema_version"] == "dev.standardflow.dataset-release.v1", "unsupported schema"
    )
    require(contract["status"] in ("planned", "ready"), "status must be planned or ready")
    release = fields(
        contract["release"],
        "id version producer_revision sources destination license attribution "
        "benchmark_role package_root files",
        "release",
    )
    reviews = fields(contract["reviews"], " ".join(REVIEW_KINDS), "reviews")
    require(
        isinstance(release["sources"], list) and isinstance(release["files"], list),
        "sources and files must be lists",
    )
    require(
        all(isinstance(item, dict) for item in release["sources"] + release["files"]),
        "sources and files must contain objects",
    )
    digest = release_digest(release)
    blockers: list[str] = []

    def check(label: str, operation: Callable[[], object]) -> object | None:
        try:
            return operation()
        except (ValueError, OSError, TypeError, KeyError, ImportError) as error:
            blockers.append(f"{label}: {error}")
            return None

    def identity() -> None:
        nonempty(release["id"], "release id")
        require(
            re.fullmatch(
                r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){2}",
                nonempty(release["version"], "version"),
            )
            is not None,
            "explicit numeric semantic version without leading zeroes required",
        )
        hexadecimal(release["producer_revision"], 40, "producer revision")
        destination = fields(release["destination"], "repo_id visibility", "destination")
        segments = nonempty(destination["repo_id"], "repo_id").split("/")
        # Conservative Hub name subset; each namespace/name is bounded to 96 ASCII characters.
        require(
            len(segments) == 2
            and all(
                re.fullmatch(r"[A-Za-z0-9_](?:[A-Za-z0-9._-]{0,94}[A-Za-z0-9_])?", segment)
                is not None
                and ".." not in segment
                and "--" not in segment
                and not segment.endswith(".git")
                for segment in segments
            ),
            "Hugging Face owner/repository requires valid namespace and name",
        )
        require(
            destination["visibility"] in ("public", "private"), "declare destination visibility"
        )
        nonempty(release["license"], "license")
        strings(release["attribution"], "attribution")
        require(
            release["benchmark_role"] == "operational",
            "only operational metadata benchmark role supported",
        )
        require(bool(release["sources"]), "at least one pinned source receipt required")

    def source(item: dict) -> None:
        fields(item, "uri revision receipt", "source")
        uri = nonempty(item["uri"], "source URI")
        parsed = urlsplit(uri)
        require(
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
            and "\\" not in uri
            and not any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in uri),
            "HTTPS source URI with hostname and no credentials required",
        )
        hexadecimal(item["revision"], 40, "source revision")
        ref = fields(item["receipt"], "path sha256", "source receipt")
        read_bound(root, ref)

    check("identity", identity)
    for item in release["sources"]:
        check("source", lambda item=item: source(item))
    package = check("package_root", lambda: safe_path(root, release["package_root"]))
    if isinstance(package, Path):

        def inventory() -> None:
            require(package.is_dir(), "package directory absent")
            paths = [nonempty(item.get("path"), "file path") for item in release["files"]]
            require(
                bool(paths) and len(paths) == len(set(paths)),
                "nonempty unique file inventory required",
            )
            observed = set()
            for path in package.rglob("*"):
                require(not path.is_symlink(), "symlink in package inventory")
                if path.is_file():
                    observed.add(path.relative_to(package).as_posix())
            require(observed == set(paths), "package inventory differs from allowlisted files")

        check("inventory", inventory)
        for item in release["files"]:
            check("export", lambda item=item: check_export(package, item))
    for kind in REVIEW_KINDS:
        check(kind, lambda kind=kind: check_review(root, reviews[kind], kind, digest))
    check("approval", lambda: check_review(root, contract["approval"], "approval", digest))
    if contract["status"] == "planned":
        blockers.append("status: planned; no release declared ready")
    elif blockers:
        raise ValueError("Dataset release blocked: " + "; ".join(blockers))
    return {
        "status": contract["status"],
        "publishable": not blockers,
        "blockers": blockers,
        "release_sha256": digest,
        "files": len(release["files"]),
        "scientific_acceptance": False,
        "boundary": "Offline integrity only; no upload, proof of review authenticity, rights or scientific acceptance.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--require-publishable", action="store_true")
    args = parser.parse_args(argv)
    paths = args.paths or sorted((args.root / "contracts/datasets").glob("*.json"))
    try:
        require(bool(paths), "no dataset release contracts found")
        for path in paths:
            value = decode(path.read_bytes())
            if not isinstance(value, dict):
                raise ValueError("contract must be an object")
            receipt = validate(value, args.root)
            print(json.dumps({"contract": str(path), **receipt}, sort_keys=True))
            require(
                not args.require_publishable or receipt["publishable"],
                "Dataset release blocked: " + "; ".join(receipt["blockers"]),
            )
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
