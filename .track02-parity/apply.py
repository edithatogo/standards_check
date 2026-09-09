#!/usr/bin/env python3
"""Apply final schema/Rust parity corrections for Track 02 hardening."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    content = read(path)
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}: {old[:120]!r}")
    write(path, content.replace(old, new, 1))


def load_json(path: str) -> dict:
    return json.loads(read(path))


def dump_json(path: str, value: dict) -> None:
    write(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


limits = "crates/standardflow-artifacts/src/limits.rs"
replace_once(
    limits,
    "/// Maximum bytes in one template, label, reason or accessible text component.\n"
    "pub const MAX_TEMPLATE_BYTES: usize = 16_384;\n",
    "/// Maximum bytes in a recipe release version.\n"
    "pub const MAX_VERSION_BYTES: usize = 128;\n"
    "/// Maximum bytes in an input-contract identifier.\n"
    "pub const MAX_CONTRACT_IDENTIFIER_BYTES: usize = 256;\n"
    "/// Maximum bytes in one template, label, reason or accessible text component.\n"
    "pub const MAX_TEMPLATE_BYTES: usize = 16_384;\n",
)

recipe = "crates/standardflow-artifacts/src/recipe.rs"
replace_once(
    recipe,
    "    MAX_IDENTIFIER_BYTES, MAX_INPUT_BYTES, MAX_NODES, MAX_PATH_IDENTIFIER_BYTES,\n"
    "    MAX_RENDERED_COMPONENT_BYTES, MAX_ROW_INDEX, MAX_TEMPLATE_BYTES, MAX_TEXT_EQUIVALENT_BYTES,\n",
    "    MAX_CONTRACT_IDENTIFIER_BYTES, MAX_IDENTIFIER_BYTES, MAX_INPUT_BYTES, MAX_NODES,\n"
    "    MAX_PATH_IDENTIFIER_BYTES, MAX_RENDERED_COMPONENT_BYTES, MAX_ROW_INDEX, MAX_TEMPLATE_BYTES,\n"
    "    MAX_TEXT_EQUIVALENT_BYTES, MAX_VERSION_BYTES,\n",
)
replace_once(
    recipe,
    '''        for (path, value) in [
            ("/recipe_id", self.recipe_id.as_str()),
            ("/version", self.version.as_str()),
            ("/source_standard", self.source_standard.as_str()),
            ("/input_contract", self.input_contract.as_str()),
            ("/title_template", self.title_template.as_str()),
            ("/description_template", self.description_template.as_str()),
        ] {
            if value.trim().is_empty() {
                report.push(Diagnostic::error(
                    "SF-RECIPE-002",
                    path,
                    "value must not be blank",
                ));
            } else if value.len() > MAX_TEMPLATE_BYTES || !is_xml_10_text(value) {
                report.push(Diagnostic::error(
                    "SF-RECIPE-017",
                    path,
                    format!(
                        "value must be valid XML 1.0 text and no more than {MAX_TEMPLATE_BYTES} UTF-8 bytes"
                    ),
                ));
            }
        }
        if !is_portable_id(&self.recipe_id)
            || self.recipe_id.len() > MAX_PATH_IDENTIFIER_BYTES
            || self.source_standard.len() > MAX_PATH_IDENTIFIER_BYTES
        {
            report.push(Diagnostic::error(
                "SF-RECIPE-003",
                "/recipe_id",
                "recipe_id must use portable identifier characters",
            ));
        }
''',
    '''        for (path, value, limit) in [
            ("/recipe_id", self.recipe_id.as_str(), MAX_PATH_IDENTIFIER_BYTES),
            ("/version", self.version.as_str(), MAX_VERSION_BYTES),
            (
                "/source_standard",
                self.source_standard.as_str(),
                MAX_PATH_IDENTIFIER_BYTES,
            ),
            (
                "/input_contract",
                self.input_contract.as_str(),
                MAX_CONTRACT_IDENTIFIER_BYTES,
            ),
            ("/title_template", self.title_template.as_str(), MAX_TEMPLATE_BYTES),
            (
                "/description_template",
                self.description_template.as_str(),
                MAX_TEMPLATE_BYTES,
            ),
        ] {
            if value.trim().is_empty() {
                report.push(Diagnostic::error(
                    "SF-RECIPE-002",
                    path,
                    "value must not be blank",
                ));
            } else if value.len() > limit || !is_xml_10_text(value) {
                report.push(Diagnostic::error(
                    "SF-RECIPE-017",
                    path,
                    format!(
                        "value must be valid XML 1.0 text and no more than {limit} UTF-8 bytes"
                    ),
                ));
            }
        }
        if !is_portable_recipe_id(&self.recipe_id) {
            report.push(Diagnostic::error(
                "SF-RECIPE-003",
                "/recipe_id",
                "recipe_id must use the portable slash-delimited recipe grammar",
            ));
        }
        if !is_source_standard_id(&self.source_standard) {
            report.push(Diagnostic::error(
                "SF-RECIPE-020",
                "/source_standard",
                "source_standard must contain at least two lowercase portable path segments",
            ));
        }
''',
)
replace_once(
    recipe,
    "            if !is_portable_id(&node.id) || !node_ids.insert(node.id.as_str()) {\n",
    "            if !is_portable_reference_id(&node.id) || !node_ids.insert(node.id.as_str()) {\n",
)
replace_once(
    recipe,
    "            if !is_portable_id(&edge.id) || !edge_ids.insert(edge.id.as_str()) {\n",
    "            if !is_portable_reference_id(&edge.id) || !edge_ids.insert(edge.id.as_str()) {\n",
)
replace_once(
    recipe,
    '''                || edge
                    .label_template
                    .as_ref()
                    .is_some_and(|label| label.len() > MAX_TEMPLATE_BYTES || !is_xml_10_text(label))
''',
    '''                || edge.label_template.as_ref().is_some_and(|label| {
                    label.trim().is_empty()
                        || label.len() > MAX_TEMPLATE_BYTES
                        || !is_xml_10_text(label)
                })
''',
)
replace_once(
    recipe,
    '''        let reading_ids = self
            .reading_order
            .iter()
            .map(String::as_str)
            .collect::<BTreeSet<_>>();
''',
    '''        if self.reading_order.iter().any(|id| {
            !is_portable_reference_id(id) || id.len() > MAX_IDENTIFIER_BYTES
        }) {
            report.push(Diagnostic::error(
                "SF-RECIPE-021",
                "/reading_order",
                "reading-order identifiers must use the bounded reference grammar",
            ));
        }
        let reading_ids = self
            .reading_order
            .iter()
            .map(String::as_str)
            .collect::<BTreeSet<_>>();
''',
)
replace_once(
    recipe,
    '''fn is_portable_id(value: &str) -> bool {
    let mut bytes = value.bytes();
    bytes
        .next()
        .is_some_and(|first| first.is_ascii_alphanumeric())
        && bytes.all(|byte| {
            byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b':' | b'-' | b'/')
        })
}
''',
    '''fn is_portable_recipe_id(value: &str) -> bool {
    let mut bytes = value.bytes();
    bytes
        .next()
        .is_some_and(|first| first.is_ascii_alphanumeric())
        && bytes.all(|byte| {
            byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b':' | b'-' | b'/')
        })
}

fn is_portable_reference_id(value: &str) -> bool {
    let mut bytes = value.bytes();
    bytes
        .next()
        .is_some_and(|first| first.is_ascii_alphanumeric())
        && bytes
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b':' | b'-'))
}

fn is_source_standard_id(value: &str) -> bool {
    let mut segment_count = 0_usize;
    for segment in value.split('/') {
        segment_count += 1;
        let mut bytes = segment.bytes();
        if !bytes
            .next()
            .is_some_and(|first| first.is_ascii_lowercase() || first.is_ascii_digit())
            || !bytes.all(|byte| {
                byte.is_ascii_lowercase()
                    || byte.is_ascii_digit()
                    || matches!(byte, b'.' | b'_' | b'-')
            })
        {
            return false;
        }
    }
    segment_count >= 2
}
''',
)

scene_schema = load_json("schemas/scene-graph.v1.schema.json")
properties = scene_schema["properties"]
properties["recipe_id"]["pattern"] = "^[A-Za-z0-9][A-Za-z0-9._:/-]*$"
properties["reading_order"]["items"] = {
    "type": "string",
    "pattern": "^[A-Za-z0-9][A-Za-z0-9._:-]*$",
    "maxLength": 256,
}
node = properties["nodes"]["items"]["properties"]
for field in ("x", "y", "width", "height"):
    node["rect"]["properties"][field]["maximum"] = 100_000
edge = properties["edges"]["items"]["properties"]
for field in ("from", "to"):
    edge[field]["pattern"] = "^[A-Za-z0-9][A-Za-z0-9._:-]*$"
dump_json("schemas/scene-graph.v1.schema.json", scene_schema)

hardening = "crates/standardflow-artifacts/tests/hardening.rs"
content = read(hardening)
addition = r'''

#[test]
fn recipe_validation_matches_identifier_and_metadata_schema_boundaries(
) -> Result<(), Box<dyn std::error::Error>> {
    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
    recipe.nodes[0].id = String::from("invalid/node");
    recipe.reading_order[0] = String::from("invalid/node");
    let report = recipe.validate();
    assert!(report.diagnostics.iter().any(|item| item.code == "SF-RECIPE-004"));
    assert!(report.diagnostics.iter().any(|item| item.code == "SF-RECIPE-021"));

    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
    recipe.version = "v".repeat(129);
    recipe.input_contract = "c".repeat(257);
    recipe.source_standard = String::from("Org.PRISMA/PRISMA/2020");
    let report = recipe.validate();
    assert!(report.diagnostics.iter().any(|item| item.code == "SF-RECIPE-017"));
    assert!(report.diagnostics.iter().any(|item| item.code == "SF-RECIPE-020"));
    Ok(())
}

#[test]
fn optional_edge_labels_cannot_be_blank() -> Result<(), Box<dyn std::error::Error>> {
    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
    recipe.edges[0].label_template = Some(String::new());
    let report = recipe.validate();
    assert!(report.diagnostics.iter().any(|item| item.code == "SF-RECIPE-019"));
    Ok(())
}
'''
if "recipe_validation_matches_identifier_and_metadata_schema_boundaries" in content:
    raise SystemExit("parity regression tests already present")
write(hardening, content + addition)

plan = "conductor/tracks/02-semantic-diagram-prisma/plan.md"
plan_text = read(plan)
old = "- [x] Mirror schema constraints in Rust and add adversarial tests.\n"
new = (
    "- [x] Mirror schema constraints in Rust and add adversarial tests.\n"
    "- [x] Separate recipe, source-standard and node-reference identifier grammars.\n"
    "- [x] Enforce version, contract-ID and optional edge-label parity.\n"
)
if plan_text.count(old) != 1:
    raise SystemExit("expected one Track 02 schema-parity task")
write(plan, plan_text.replace(old, new, 1))

print("Applied final Track 02 Rust/schema identifier and metadata parity corrections")
