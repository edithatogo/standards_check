#!/usr/bin/env python3
"""Network-free validation for the initial StandardFlow contracts and context."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "conductor/index.md",
    "conductor/product.md",
    "conductor/tech-stack.md",
    "conductor/workflow.md",
    "conductor/roadmap.md",
    "conductor/tracks.md",
    "schemas/standard-pack.v1.schema.json",
    "schemas/artifact-recipe.v1.schema.json",
    "schemas/ecosystem-evidence.v1.schema.json",
    "contracts/examples/minimal-standard-pack.v1.json",
)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"{path.relative_to(ROOT)} cannot be read as JSON: {error}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


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


for relative in REQUIRED:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing required file: {relative}")

schemas: dict[str, dict[str, Any]] = {}
for path in sorted((ROOT / "schemas").glob("*.json")):
    data = load_json(path)
    if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        fail(f"{path.relative_to(ROOT)} is not Draft 2020-12")
    try:
        Draft202012Validator.check_schema(data)
    except SchemaError as error:
        fail(f"{path.relative_to(ROOT)} is not a valid Draft 2020-12 schema: {error.message}")
    schemas[path.name] = data

pack_path = ROOT / "contracts/examples/minimal-standard-pack.v1.json"
pack = load_json(pack_path)
pack_validator = Draft202012Validator(
    schemas["standard-pack.v1.schema.json"],
    format_checker=FORMAT_CHECKER,
)
pack_errors = sorted(
    pack_validator.iter_errors(pack),
    key=lambda error: "/".join(str(part) for part in error.absolute_path),
)
if pack_errors:
    error = pack_errors[0]
    location = "/".join(str(part) for part in error.absolute_path) or "<root>"
    fail(f"{pack_path.relative_to(ROOT)} violates its schema at {location}: {error.message}")

if pack.get("schema_version") != "dev.standardflow.standard-pack.v1":
    fail("fixture schema version mismatch")
requirements = pack.get("requirements")
if not isinstance(requirements, list):
    fail("fixture requirements must be a list")
ids = [item.get("id") for item in requirements if isinstance(item, dict)]
if not ids:
    fail("fixture must contain at least one requirement")
if len(ids) != len(set(ids)):
    fail("fixture must contain unique requirement IDs")
if pack.get("rights", {}).get("status") != "cleared":
    fail("committed fixture must be rights-cleared")

for relative in (
    "conductor/tracks/00-platform-foundation/spec.md",
    "conductor/tracks/00-platform-foundation/plan.md",
    "conductor/tracks/00-platform-foundation/metadata.json",
):
    if not (ROOT / relative).is_file():
        fail(f"missing active track artefact: {relative}")

metadata = load_json(ROOT / "conductor/tracks/00-platform-foundation/metadata.json")
if metadata.get("evidence_level") not in {"contracted", "source_verified"}:
    fail("foundation evidence level exceeds available local evidence")

print("StandardFlow foundation validation passed")
