#!/usr/bin/env python3
"""Validate all committed Canonical Standard Pack source surfaces."""
from __future__ import annotations

from datetime import date
import json
import os
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"
SCHEMAS = ROOT / "schemas"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"{path.relative_to(ROOT)} cannot be read as JSON: {error}")


FORMAT_CHECKER = FormatChecker()


@FORMAT_CHECKER.checks("date", raises=(TypeError, ValueError))
def is_canonical_date(value: object) -> bool:
    if not isinstance(value, str):
        return True
    return date.fromisoformat(value).isoformat() == value


@FORMAT_CHECKER.checks("uri")
def is_absolute_uri(value: object) -> bool:
    if not isinstance(value, str):
        return True
    parsed = urlparse(value)
    return bool(parsed.scheme and (parsed.netloc or parsed.scheme == "urn"))


def validator(schema_name: str) -> Draft202012Validator:
    schema_path = SCHEMAS / schema_name
    schema = load_json(schema_path)
    if not isinstance(schema, dict):
        fail(f"{schema_path.relative_to(ROOT)} must contain an object")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        fail(f"{schema_path.relative_to(ROOT)} is invalid: {error.message}")
    return Draft202012Validator(schema, format_checker=FORMAT_CHECKER)


def validate_document(path: Path, schema_validator: Draft202012Validator) -> dict[str, Any]:
    document = load_json(path)
    if not isinstance(document, dict):
        fail(f"{path.relative_to(ROOT)} must contain an object")
    errors = sorted(
        schema_validator.iter_errors(document),
        key=lambda error: "/".join(str(part) for part in error.absolute_path),
    )
    if errors:
        error = errors[0]
        pointer = "/".join(str(part) for part in error.absolute_path) or "<root>"
        fail(f"{path.relative_to(ROOT)} violates its schema at {pointer}: {error.message}")
    return document


def ensure_safe_tree(pack_root: Path) -> None:
    for directory, names, files in os.walk(pack_root, followlinks=False):
        current = Path(directory)
        for name in [*names, *files]:
            path = current / name
            if path.is_symlink():
                fail(f"symbolic links are prohibited in packs: {path.relative_to(ROOT)}")
            if name in {".DS_Store", "Thumbs.db"}:
                fail(f"platform metadata is prohibited in packs: {path.relative_to(ROOT)}")


def main() -> None:
    pack_validator = validator("standard-pack.v1.schema.json")
    source_validator = validator("source-manifest.v1.schema.json")
    lock_validator = validator("standardflow-lock.v1.schema.json")
    pack_paths = sorted(PACKS.glob("**/pack.json"))
    if not pack_paths:
        fail("no Canonical Standard Packs were found")
    seen_ids: set[str] = set()
    for pack_path in pack_paths:
        pack_root = pack_path.parent
        ensure_safe_tree(pack_root)
        pack = validate_document(pack_path, pack_validator)
        pack_id = pack["pack_id"]
        expected = PACKS / pack_id
        if pack_root != expected:
            fail(
                f"{pack_path.relative_to(ROOT)} declares {pack_id!r}; expected directory "
                f"{expected.relative_to(ROOT)}"
            )
        if pack_id in seen_ids:
            fail(f"duplicate pack_id: {pack_id}")
        seen_ids.add(pack_id)
        requirement_ids = [item["id"] for item in pack["requirements"]]
        if len(requirement_ids) != len(set(requirement_ids)):
            fail(f"{pack_id} contains duplicate requirement IDs")
        for required_path in (
            pack_root / "README.md",
            pack_root / "citations.csl.json",
            pack_root / "sources/manifest.json",
            pack_root / "standardflow.lock.json",
        ):
            if not required_path.is_file():
                fail(f"missing required pack file: {required_path.relative_to(ROOT)}")
        citations = load_json(pack_root / "citations.csl.json")
        if not isinstance(citations, list) or not citations:
            fail(f"{pack_id} citations.csl.json must contain a non-empty CSL array")
        validate_document(pack_root / "sources/manifest.json", source_validator)
        validate_document(pack_root / "standardflow.lock.json", lock_validator)
    print(f"Validated {len(pack_paths)} Canonical Standard Pack(s)")


if __name__ == "__main__":
    main()
