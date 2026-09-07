#!/usr/bin/env python3
"""Apply the final strict-lint correction identified by the compiler matrix."""
from pathlib import Path

path = Path("crates/standardflow-core/tests/pack_contract.rs")
text = path.read_text(encoding="utf-8")
header = "//! Contract and property tests for Canonical Standard Packs.\n\n"
if not text.startswith("//!"):
    path.write_text(header + text, encoding="utf-8")
