#!/usr/bin/env python3
"""Correct reviewed parity-patch defects before compiler verification."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    content = target.read_text(encoding="utf-8")
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}: {old[:120]!r}")
    target.write_text(content.replace(old, new, 1), encoding="utf-8")


replace_once(
    "crates/standardflow-artifacts/src/recipe.rs",
    "        if !is_portable_id(key)\n",
    "        if !is_portable_reference_id(key)\n",
)

hardening = "crates/standardflow-artifacts/tests/hardening.rs"
replace_once(
    hardening,
    '''    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
    recipe.nodes[0].id = String::from("invalid/node");
    recipe.reading_order[0] = String::from("invalid/node");
    let report = recipe.validate();
''',
    '''    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
    let node = recipe
        .nodes
        .first_mut()
        .ok_or_else(|| std::io::Error::other("fixture has no node"))?;
    node.id = String::from("invalid/node");
    let reading_id = recipe
        .reading_order
        .first_mut()
        .ok_or_else(|| std::io::Error::other("fixture has no reading-order entry"))?;
    *reading_id = String::from("invalid/node");
    let report = recipe.validate();
''',
)
replace_once(
    hardening,
    '''    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
    recipe.edges[0].label_template = Some(String::new());
    let report = recipe.validate();
''',
    '''    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
    let edge = recipe
        .edges
        .first_mut()
        .ok_or_else(|| std::io::Error::other("fixture has no edge"))?;
    edge.label_template = Some(String::new());
    let report = recipe.validate();
''',
)

print("Corrected binding-key grammar and removed direct indexing from parity tests")
