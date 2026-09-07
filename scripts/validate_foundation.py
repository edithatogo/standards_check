#!/usr/bin/env python3
"""Network-free validation for the initial StandardFlow contracts and context."""
from __future__ import annotations

import json
from pathlib import Path
import sys

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


for relative in REQUIRED:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing required file: {relative}")

for path in sorted((ROOT / "schemas").glob("*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        fail(f"{path.relative_to(ROOT)} is not Draft 2020-12")

pack = json.loads(
    (ROOT / "contracts/examples/minimal-standard-pack.v1.json").read_text(encoding="utf-8")
)
if pack.get("schema_version") != "dev.standardflow.standard-pack.v1":
    fail("fixture schema version mismatch")
ids = [item["id"] for item in pack.get("requirements", [])]
if not ids or len(ids) != len(set(ids)):
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

metadata = json.loads(
    (ROOT / "conductor/tracks/00-platform-foundation/metadata.json").read_text(encoding="utf-8")
)
if metadata.get("evidence_level") not in {"contracted", "source_verified"}:
    fail("foundation evidence level exceeds available local evidence")

print("StandardFlow foundation validation passed")
