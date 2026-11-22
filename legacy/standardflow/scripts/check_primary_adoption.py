#!/usr/bin/env python3
"""Validate the source-level primary-repository adoption contract."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "integration/standards-check-adoption.json"
METADATA = ROOT / "conductor/tracks/00-primary-repository-adoption/metadata.json"
HEX40 = re.compile(r"^[a-f0-9]{40}$")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
metadata = json.loads(METADATA.read_text(encoding="utf-8"))

for key in ("legacy_revision", "proposed_primary_revision"):
    value = manifest.get(key)
    if not isinstance(value, str) or HEX40.fullmatch(value) is None:
        fail(f"{key} must be an exact 40-character revision")

for key in ("automatic_revision_updates", "runtime_dependency", "default_network", "default_external_writes"):
    if manifest.get(key) is not False:
        fail(f"{key} must be false")

if manifest.get("licence") != "Apache-2.0":
    fail("legacy code licence must remain Apache-2.0")
if metadata.get("proposed_primary_revision") != manifest.get("proposed_primary_revision"):
    fail("Conductor metadata and adoption manifest pin different primary revisions")
if metadata.get("evidence_level") not in {"contracted", "source_verified"}:
    fail("migration evidence exceeds the available source-level receipt")
if not manifest.get("components") or not manifest.get("activation_gates"):
    fail("component mapping and activation gates are required")
required_gates = {"history_preserved", "apache_notice_preserved", "differential_fixtures_pass", "rollback_rehearsed"}
if not required_gates.issubset(set(manifest["activation_gates"])):
    fail("required history, licence, parity and rollback gates are missing")
if not manifest.get("claim_boundary"):
    fail("claim boundary is required")

print("StandardFlow legacy adoption validation passed")
