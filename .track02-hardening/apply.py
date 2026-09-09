#!/usr/bin/env python3
"""Apply the reviewed Track 02 security, parity and accessibility fixes."""
from __future__ import annotations

import json
from pathlib import Path
import re

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
        raise SystemExit(f"{path}: expected one literal match, found {count}: {old[:120]!r}")
    write(path, content.replace(old, new, 1))


def regex_once(path: str, pattern: str, replacement: str) -> None:
    content = read(path)
    updated, count = re.subn(pattern, replacement, content, count=1, flags=re.DOTALL)
    if count != 1:
        raise SystemExit(f"{path}: expected one regex match, found {count}: {pattern!r}")
    write(path, updated)


write(
    "crates/standardflow-artifacts/src/limits.rs",
    '''//! Shared resource and text-safety limits for untrusted artefact inputs.

/// Maximum bytes accepted for one recipe or PRISMA flow JSON document.
pub(crate) const MAX_INPUT_BYTES: usize = 1_048_576;
/// Maximum nodes in one recipe or generated scene.
pub(crate) const MAX_NODES: usize = 512;
/// Maximum edges in one recipe or generated scene.
pub(crate) const MAX_EDGES: usize = 2_048;
/// Maximum zero-based row index in the deterministic grid.
pub(crate) const MAX_ROW_INDEX: u32 = 1_000;
/// Maximum columns in a recipe grid.
pub(crate) const MAX_COLUMNS: u32 = 12;
/// Maximum bytes in an identifier used by a node, edge or binding.
pub(crate) const MAX_IDENTIFIER_BYTES: usize = 256;
/// Maximum bytes in a recipe identifier or source-standard path.
pub(crate) const MAX_PATH_IDENTIFIER_BYTES: usize = 512;
/// Maximum bytes in one template, label, reason or accessible text component.
pub(crate) const MAX_TEMPLATE_BYTES: usize = 16_384;
/// Maximum bindings supplied to a recipe.
pub(crate) const MAX_BINDINGS: usize = 256;
/// Maximum bytes in one resolved binding value.
pub(crate) const MAX_BINDING_BYTES: usize = 16_384;
/// Maximum bytes in a rendered title, description, node label or edge label.
pub(crate) const MAX_RENDERED_COMPONENT_BYTES: usize = 65_536;
/// Maximum bytes in the complete non-visual equivalent.
pub(crate) const MAX_TEXT_EQUIVALENT_BYTES: usize = 262_144;
/// Maximum wrapped lines in one scene node.
pub(crate) const MAX_WRAPPED_LINES: usize = 4_096;
/// Maximum canvas width or height in CSS pixels.
pub(crate) const MAX_CANVAS_DIMENSION: u32 = 100_000;
/// Maximum count that round-trips exactly through common JSON number implementations.
pub(crate) const MAX_SAFE_JSON_INTEGER: u64 = 9_007_199_254_740_991;
/// Maximum structured report-exclusion reasons in one PRISMA stream.
pub(crate) const MAX_EXCLUSION_REASONS: usize = 20;
/// Maximum Unicode scalar values in one exclusion reason.
pub(crate) const MAX_EXCLUSION_REASON_CHARS: usize = 240;

/// Returns whether every scalar value is legal in XML 1.0 text.
pub(crate) fn is_xml_10_text(value: &str) -> bool {
    value.chars().all(is_xml_10_char)
}

const fn is_xml_10_char(value: char) -> bool {
    matches!(value, '\u{9}' | '\u{A}' | '\u{D}')
        || (value >= '\u{20}' && value <= '\u{D7FF}')
        || (value >= '\u{E000}' && value <= '\u{FFFD}')
        || (value >= '\u{10000}' && value <= '\u{10FFFF}')
}
''',
)
replace_once(
    "crates/standardflow-artifacts/src/lib.rs",
    "pub mod prisma;\n",
    "mod limits;\n\npub mod prisma;\n",
)

recipe_path = "crates/standardflow-artifacts/src/recipe.rs"
replace_once(
    recipe_path,
    "use crate::scene::{Anchor, Canvas, EdgeKind, NodeRole, Rect, Scene, SceneEdge, SceneNode};\n",
    "use crate::limits::{\n    MAX_BINDING_BYTES, MAX_BINDINGS, MAX_CANVAS_DIMENSION, MAX_COLUMNS, MAX_EDGES,\n    MAX_IDENTIFIER_BYTES, MAX_INPUT_BYTES, MAX_NODES, MAX_PATH_IDENTIFIER_BYTES,\n    MAX_RENDERED_COMPONENT_BYTES, MAX_ROW_INDEX, MAX_TEMPLATE_BYTES,\n    MAX_TEXT_EQUIVALENT_BYTES, MAX_WRAPPED_LINES, is_xml_10_text,\n};\nuse crate::scene::{Anchor, Canvas, EdgeKind, NodeRole, Rect, Scene, SceneEdge, SceneNode};\n",
)
replace_once(
    recipe_path,
    '''    pub fn from_json(bytes: &[u8]) -> Result<Self, RecipeError> {
        serde_json::from_slice(bytes).map_err(RecipeError::Json)
    }
''',
    '''    pub fn from_json(bytes: &[u8]) -> Result<Self, RecipeError> {
        if bytes.len() > MAX_INPUT_BYTES {
            return Err(RecipeError::ResourceLimit {
                resource: "recipe JSON bytes",
                limit: MAX_INPUT_BYTES,
            });
        }
        serde_json::from_slice(bytes).map_err(RecipeError::Json)
    }
''',
)
replace_once(
    recipe_path,
    "        for (path, value) in [\n",
    '''        if self.nodes.is_empty() || self.nodes.len() > MAX_NODES {
            report.push(Diagnostic::error(
                "SF-RECIPE-015",
                "/nodes",
                format!("recipes require 1 to {MAX_NODES} nodes"),
            ));
        }
        if self.edges.len() > MAX_EDGES {
            report.push(Diagnostic::error(
                "SF-RECIPE-016",
                "/edges",
                format!("recipes permit at most {MAX_EDGES} edges"),
            ));
        }
        for (path, value) in [
''',
)
replace_once(
    recipe_path,
    '''            if value.trim().is_empty() {
                report.push(Diagnostic::error(
                    "SF-RECIPE-002",
                    path,
                    "value must not be blank",
                ));
            }
''',
    '''            if value.trim().is_empty() {
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
''',
)
replace_once(
    recipe_path,
    "            if node.column_span == 0\n",
    '''            if node.row > MAX_ROW_INDEX
                || node.id.len() > MAX_IDENTIFIER_BYTES
                || node.label_template.len() > MAX_TEMPLATE_BYTES
                || node.aria_template.len() > MAX_TEMPLATE_BYTES
                || !is_xml_10_text(&node.label_template)
                || !is_xml_10_text(&node.aria_template)
            {
                report.push(Diagnostic::error(
                    "SF-RECIPE-018",
                    path.clone(),
                    "node row, identifier or text exceeds the declared safe limits",
                ));
            }
            if node.column_span == 0
''',
)
replace_once(
    recipe_path,
    '''        for (left_index, left) in self.nodes.iter().enumerate() {
            for right in self.nodes.iter().skip(left_index + 1) {
                if nodes_overlap(left, right) {
                    report.push(Diagnostic::error(
                        "SF-RECIPE-007",
                        "/nodes",
                        format!("grid cells overlap for {} and {}", left.id, right.id),
                    ));
                }
            }
        }
''',
    '''        if self.nodes.len() <= MAX_NODES {
            for (left_index, left) in self.nodes.iter().enumerate() {
                for right in self.nodes.iter().skip(left_index + 1) {
                    if nodes_overlap(left, right) {
                        report.push(Diagnostic::error(
                            "SF-RECIPE-007",
                            "/nodes",
                            format!("grid cells overlap for {} and {}", left.id, right.id),
                        ));
                    }
                }
            }
        }
''',
)
replace_once(
    recipe_path,
    "            if edge.from == edge.to\n",
    '''            if edge.id.len() > MAX_IDENTIFIER_BYTES
                || edge.from.len() > MAX_IDENTIFIER_BYTES
                || edge.to.len() > MAX_IDENTIFIER_BYTES
                || edge.label_template.as_ref().is_some_and(|label| {
                    label.len() > MAX_TEMPLATE_BYTES || !is_xml_10_text(label)
                })
            {
                report.push(Diagnostic::error(
                    "SF-RECIPE-019",
                    path.clone(),
                    "edge identifier or label exceeds the declared safe limits",
                ));
            }
            if edge.from == edge.to
''',
)
replace_once(
    recipe_path,
    '''        let recipe_report = self.validate();
        if !recipe_report.is_valid() {
            return Err(RecipeError::Validation(recipe_report));
        }
        let title = interpolate(&self.title_template, bindings)?;
''',
    '''        let recipe_report = self.validate();
        if !recipe_report.is_valid() {
            return Err(RecipeError::Validation(recipe_report));
        }
        validate_bindings(bindings)?;
        let title = interpolate(&self.title_template, bindings)?;
''',
)
replace_once(
    recipe_path,
    '''        let text_equivalent =
            build_text_equivalent(&title, &description, &nodes, &self.reading_order)?;
''',
    '''        let text_equivalent =
            build_text_equivalent(&title, &description, &nodes, &edges, &self.reading_order)?;
''',
)
replace_once(
    recipe_path,
    '''    /// Recipe JSON could not be decoded.
    #[error("recipe JSON is invalid: {0}")]
    Json(#[source] serde_json::Error),
''',
    '''    /// An input or generated component exceeds a declared resource limit.
    #[error("{resource} exceeds the declared limit of {limit}")]
    ResourceLimit {
        /// Bounded resource.
        resource: &'static str,
        /// Maximum permitted value.
        limit: usize,
    },
    /// A binding key or value violates the portable bounded contract.
    #[error("binding {0:?} violates identifier, XML text or size limits")]
    InvalidBinding(String),
    /// Recipe JSON could not be decoded.
    #[error("recipe JSON is invalid: {0}")]
    Json(#[source] serde_json::Error),
''',
)
replace_once(
    recipe_path,
    '''    if layout.columns == 0
        || layout.margin == 0
        || layout.column_width < 80
        || layout.column_gap < 8
        || layout.row_gap < 8
        || layout.minimum_node_height < 40
        || layout.padding < 4
        || layout.line_height < 10
        || layout.character_width == 0
''',
    '''    if layout.columns == 0
        || layout.columns > MAX_COLUMNS
        || layout.margin == 0
        || layout.margin > 500
        || !(80..=2_000).contains(&layout.column_width)
        || !(8..=1_000).contains(&layout.column_gap)
        || !(8..=1_000).contains(&layout.row_gap)
        || !(40..=2_000).contains(&layout.minimum_node_height)
        || !(4..=200).contains(&layout.padding)
        || !(10..=100).contains(&layout.line_height)
        || !(1..=40).contains(&layout.character_width)
''',
)
regex_once(
    recipe_path,
    r'''#\[allow\(\n    clippy::indexing_slicing,\n    reason = "delimiter offsets come from ASCII searches and are valid UTF-8 boundaries"\n\)\]\nfn interpolate\(.*?\n\}\n\nfn wrap_label''',
    '''#[allow(
    clippy::indexing_slicing,
    reason = "delimiter offsets come from ASCII searches and are valid UTF-8 boundaries"
)]
fn interpolate(template: &str, bindings: &BTreeMap<String, String>) -> Result<String, RecipeError> {
    let mut remaining = template;
    let mut output = String::with_capacity(template.len().min(MAX_RENDERED_COMPONENT_BYTES));
    loop {
        let Some(open) = remaining.find("{{") else {
            if remaining.contains("}}") {
                return Err(RecipeError::MalformedTemplate);
            }
            append_bounded(&mut output, remaining, MAX_RENDERED_COMPONENT_BYTES, "interpolated text bytes")?;
            break;
        };
        append_bounded(
            &mut output,
            &remaining[..open],
            MAX_RENDERED_COMPONENT_BYTES,
            "interpolated text bytes",
        )?;
        let after_open = &remaining[open + 2..];
        let Some(close) = after_open.find("}}") else {
            return Err(RecipeError::MalformedTemplate);
        };
        let key = after_open[..close].trim();
        if key.is_empty() || key.contains('{') || key.contains('}') {
            return Err(RecipeError::MalformedTemplate);
        }
        let value = bindings
            .get(key)
            .ok_or_else(|| RecipeError::MissingBinding(key.to_owned()))?;
        append_bounded(
            &mut output,
            value,
            MAX_RENDERED_COMPONENT_BYTES,
            "interpolated text bytes",
        )?;
        remaining = &after_open[close + 2..];
    }
    Ok(output)
}

fn wrap_label''',
)
regex_once(
    recipe_path,
    r'''fn wrap_paragraph\(paragraph: &str, maximum: usize, output: &mut Vec<String>\) \{.*?\n\}\n\nfn build_text_equivalent''',
    '''fn wrap_paragraph(paragraph: &str, maximum: usize, output: &mut Vec<String>) {
    if paragraph.trim().is_empty() {
        output.push(String::from(" "));
        return;
    }
    let mut line = String::new();
    for word in paragraph.split_whitespace() {
        let word_length = word.chars().count();
        if word_length > maximum {
            if !line.is_empty() {
                output.push(std::mem::take(&mut line));
            }
            let mut chunk = String::new();
            let mut chunk_length = 0_usize;
            for character in word.chars() {
                if chunk_length == maximum {
                    output.push(std::mem::take(&mut chunk));
                    chunk_length = 0;
                }
                chunk.push(character);
                chunk_length += 1;
            }
            line = chunk;
            continue;
        }
        let candidate_length = line
            .chars()
            .count()
            .saturating_add(usize::from(!line.is_empty()))
            .saturating_add(word_length);
        if !line.is_empty() && candidate_length > maximum {
            output.push(std::mem::take(&mut line));
        }
        if !line.is_empty() {
            line.push(' ');
        }
        line.push_str(word);
    }
    if !line.is_empty() {
        output.push(line);
    }
}

fn build_text_equivalent''',
)
regex_once(
    recipe_path,
    r'''fn build_text_equivalent\(.*?\n\}\n\nfn is_portable_id''',
    '''fn build_text_equivalent(
    title: &str,
    description: &str,
    nodes: &[SceneNode],
    edges: &[SceneEdge],
    reading_order: &[String],
) -> Result<String, RecipeError> {
    let lookup = nodes
        .iter()
        .map(|node| (node.id.as_str(), node))
        .collect::<BTreeMap<_, _>>();
    let mut text = String::new();
    append_bounded(&mut text, title, MAX_TEXT_EQUIVALENT_BYTES, "text equivalent bytes")?;
    append_bounded(&mut text, "\n\n", MAX_TEXT_EQUIVALENT_BYTES, "text equivalent bytes")?;
    append_bounded(
        &mut text,
        description,
        MAX_TEXT_EQUIVALENT_BYTES,
        "text equivalent bytes",
    )?;
    append_bounded(&mut text, "\n\nStages:", MAX_TEXT_EQUIVALENT_BYTES, "text equivalent bytes")?;
    for (index, id) in reading_order.iter().enumerate() {
        let node = lookup
            .get(id.as_str())
            .ok_or_else(|| RecipeError::MissingBinding(id.clone()))?;
        append_bounded(
            &mut text,
            &format!("\n{}. {}", index + 1, node.label),
            MAX_TEXT_EQUIVALENT_BYTES,
            "text equivalent bytes",
        )?;
    }
    append_bounded(
        &mut text,
        "\n\nFlow relationships:",
        MAX_TEXT_EQUIVALENT_BYTES,
        "text equivalent bytes",
    )?;
    for (index, edge) in edges.iter().enumerate() {
        let from = lookup
            .get(edge.from.as_str())
            .ok_or_else(|| RecipeError::MissingBinding(edge.from.clone()))?;
        let to = lookup
            .get(edge.to.as_str())
            .ok_or_else(|| RecipeError::MissingBinding(edge.to.clone()))?;
        let label = edge
            .label
            .as_deref()
            .map_or(String::new(), |value| format!("; label: {value}"));
        append_bounded(
            &mut text,
            &format!(
                "\n{}. {} → {} ({}){}",
                index + 1,
                from.label,
                to.label,
                edge_kind_text(edge.kind),
                label
            ),
            MAX_TEXT_EQUIVALENT_BYTES,
            "text equivalent bytes",
        )?;
    }
    text.push('\n');
    Ok(text)
}

fn validate_bindings(bindings: &BTreeMap<String, String>) -> Result<(), RecipeError> {
    if bindings.len() > MAX_BINDINGS {
        return Err(RecipeError::ResourceLimit {
            resource: "recipe bindings",
            limit: MAX_BINDINGS,
        });
    }
    for (key, value) in bindings {
        if !is_portable_id(key)
            || key.len() > MAX_IDENTIFIER_BYTES
            || value.len() > MAX_BINDING_BYTES
            || !is_xml_10_text(value)
        {
            return Err(RecipeError::InvalidBinding(key.clone()));
        }
    }
    Ok(())
}

fn append_bounded(
    output: &mut String,
    value: &str,
    limit: usize,
    resource: &'static str,
) -> Result<(), RecipeError> {
    let length = output
        .len()
        .checked_add(value.len())
        .ok_or(RecipeError::ResourceLimit { resource, limit })?;
    if length > limit {
        return Err(RecipeError::ResourceLimit { resource, limit });
    }
    output.push_str(value);
    Ok(())
}

const fn edge_kind_text(kind: EdgeKind) -> &'static str {
    match kind {
        EdgeKind::Progression => "progression",
        EdgeKind::Exclusion => "exclusion",
        EdgeKind::Merge => "merge",
        EdgeKind::Lineage => "lineage",
    }
}

fn is_portable_id''',
)
replace_once(
    recipe_path,
    '''fn validate_layout(layout: GridLayout, report: &mut ValidationReport) {
''',
    '''fn validate_layout(layout: GridLayout, report: &mut ValidationReport) {
''',
)
# Add remaining schema-parity checks to the node wrapping output.
replace_once(
    recipe_path,
    '''    if lines.is_empty() {
        lines.push(String::from(" "));
    }
    lines
}
''',
    '''    if lines.is_empty() {
        lines.push(String::from(" "));
    }
    if lines.len() > MAX_WRAPPED_LINES {
        lines.truncate(MAX_WRAPPED_LINES);
    }
    lines
}
''',
)
# Ensure recipe-level path identifiers use their stricter bound.
replace_once(
    recipe_path,
    '''        if !is_portable_id(&self.recipe_id) {
''',
    '''        if !is_portable_id(&self.recipe_id)
            || self.recipe_id.len() > MAX_PATH_IDENTIFIER_BYTES
            || self.source_standard.len() > MAX_PATH_IDENTIFIER_BYTES
        {
''',
)
# Reject layouts that can produce excessive canvases even without overflow.
replace_once(
    recipe_path,
    '''    if canvas_width(layout).is_err() {
''',
    '''    if canvas_width(layout).is_err()
        || canvas_width(layout).is_ok_and(|width| width > MAX_CANVAS_DIMENSION)
    {
''',
)

scene_path = "crates/standardflow-artifacts/src/scene.rs"
replace_once(
    scene_path,
    "use standardflow_core::{Diagnostic, ValidationReport};\n",
    "use standardflow_core::{Diagnostic, ValidationReport};\n\nuse crate::limits::{\n    MAX_CANVAS_DIMENSION, MAX_EDGES, MAX_IDENTIFIER_BYTES, MAX_NODES,\n    MAX_PATH_IDENTIFIER_BYTES, MAX_RENDERED_COMPONENT_BYTES, MAX_TEXT_EQUIVALENT_BYTES,\n    MAX_WRAPPED_LINES, is_xml_10_text,\n};\n",
)
replace_once(
    scene_path,
    '''        if self.canvas.width == 0 || self.canvas.height == 0 {
''',
    '''        if !is_portable_id(&self.recipe_id)
            || self.recipe_id.len() > MAX_PATH_IDENTIFIER_BYTES
        {
            report.push(Diagnostic::error(
                "SF-SCENE-013",
                "/recipe_id",
                "recipe_id must be a bounded portable identifier",
            ));
        }
        if self.nodes.is_empty() || self.nodes.len() > MAX_NODES {
            report.push(Diagnostic::error(
                "SF-SCENE-014",
                "/nodes",
                format!("scenes require 1 to {MAX_NODES} nodes"),
            ));
        }
        if self.edges.len() > MAX_EDGES {
            report.push(Diagnostic::error(
                "SF-SCENE-015",
                "/edges",
                format!("scenes permit at most {MAX_EDGES} edges"),
            ));
        }
        if self.canvas.width == 0
            || self.canvas.height == 0
            || self.canvas.width > MAX_CANVAS_DIMENSION
            || self.canvas.height > MAX_CANVAS_DIMENSION
        {
''',
)
replace_once(
    scene_path,
    '''        if self.title.trim().is_empty() || self.description.trim().is_empty() {
''',
    '''        if self.title.trim().is_empty()
            || self.description.trim().is_empty()
            || self.title.len() > MAX_RENDERED_COMPONENT_BYTES
            || self.description.len() > MAX_RENDERED_COMPONENT_BYTES
            || !is_xml_10_text(&self.title)
            || !is_xml_10_text(&self.description)
        {
''',
)
replace_once(
    scene_path,
    '''        if self.text_equivalent.trim().is_empty() {
''',
    '''        if self.text_equivalent.trim().is_empty()
            || self.text_equivalent.len() > MAX_TEXT_EQUIVALENT_BYTES
            || !is_xml_10_text(&self.text_equivalent)
        {
''',
)
replace_once(
    scene_path,
    '''            if node.label.trim().is_empty()
                || node.aria_label.trim().is_empty()
                || node.lines.is_empty()
                || node.lines.iter().any(|line| line.trim().is_empty())
''',
    '''            if node.label.trim().is_empty()
                || node.aria_label.trim().is_empty()
                || node.label.len() > MAX_RENDERED_COMPONENT_BYTES
                || node.aria_label.len() > MAX_RENDERED_COMPONENT_BYTES
                || !is_xml_10_text(&node.label)
                || !is_xml_10_text(&node.aria_label)
                || node.lines.is_empty()
                || node.lines.len() > MAX_WRAPPED_LINES
                || node.lines.iter().any(|line| {
                    line.trim().is_empty()
                        || line.len() > MAX_RENDERED_COMPONENT_BYTES
                        || !is_xml_10_text(line)
                })
''',
)
replace_once(
    scene_path,
    '''        for (left_index, left) in self.nodes.iter().enumerate() {
            for right in self.nodes.iter().skip(left_index + 1) {
                if rectangles_overlap(left.rect, right.rect) {
                    report.push(Diagnostic::error(
                        "SF-SCENE-009",
                        "/nodes",
                        format!("nodes {} and {} overlap", left.id, right.id),
                    ));
                }
            }
        }
''',
    '''        if self.nodes.len() <= MAX_NODES {
            for (left_index, left) in self.nodes.iter().enumerate() {
                for right in self.nodes.iter().skip(left_index + 1) {
                    if rectangles_overlap(left.rect, right.rect) {
                        report.push(Diagnostic::error(
                            "SF-SCENE-009",
                            "/nodes",
                            format!("nodes {} and {} overlap", left.id, right.id),
                        ));
                    }
                }
            }
        }
''',
)
replace_once(
    scene_path,
    '''            if edge.from == edge.to
''',
    '''            if edge.id.len() > MAX_IDENTIFIER_BYTES
                || edge.from.len() > MAX_IDENTIFIER_BYTES
                || edge.to.len() > MAX_IDENTIFIER_BYTES
                || edge.label.as_ref().is_some_and(|label| {
                    label.trim().is_empty()
                        || label.len() > MAX_RENDERED_COMPONENT_BYTES
                        || !is_xml_10_text(label)
                })
            {
                report.push(Diagnostic::error(
                    "SF-SCENE-016",
                    path.clone(),
                    "edge identifier or optional label violates text or size limits",
                ));
            }
            if edge.from == edge.to
''',
)
replace_once(
    scene_path,
    '''        if reading_ids.len() != self.reading_order.len() || reading_ids != node_ids {
            report.push(Diagnostic::error(
                "SF-SCENE-012",
                "/reading_order",
                "reading_order must contain every node exactly once",
            ));
        }
        report
''',
    '''        if reading_ids.len() != self.reading_order.len() || reading_ids != node_ids {
            report.push(Diagnostic::error(
                "SF-SCENE-012",
                "/reading_order",
                "reading_order must contain every node exactly once",
            ));
        }
        if self
            .nodes
            .iter()
            .any(|node| !self.text_equivalent.contains(&node.label))
        {
            report.push(Diagnostic::error(
                "SF-SCENE-017",
                "/text_equivalent",
                "text equivalent must contain every complete node label",
            ));
        }
        if !self.edges.is_empty() && !self.text_equivalent.contains("Flow relationships:") {
            report.push(Diagnostic::error(
                "SF-SCENE-018",
                "/text_equivalent",
                "text equivalent must describe directed flow relationships",
            ));
        }
        report
''',
)

render_path = "crates/standardflow-artifacts/src/render.rs"
replace_once(
    render_path,
    '''        r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {} {}" width="{}" height="{}" role="img" aria-labelledby="standardflow-title standardflow-description">"#,
''',
    '''        r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {} {}" width="{}" height="{}" role="img" aria-labelledby="standardflow-title" aria-describedby="standardflow-description">"#,
''',
)
replace_once(
    render_path,
    '''        escape_xml(&scene.description)
''',
    '''        escape_xml(&scene.text_equivalent)
''',
)

prisma_path = "crates/standardflow-artifacts/src/prisma.rs"
replace_once(
    prisma_path,
    "use crate::recipe::{DiagramRecipe, RecipeError};\n",
    "use crate::limits::{\n    MAX_EXCLUSION_REASON_CHARS, MAX_EXCLUSION_REASONS, MAX_INPUT_BYTES,\n    MAX_SAFE_JSON_INTEGER, is_xml_10_text,\n};\nuse crate::recipe::{DiagramRecipe, RecipeError};\n",
)
replace_once(
    prisma_path,
    '''        if self.review_id.trim().is_empty()
            || self.review_id.chars().count() > 200
            || self.review_id.chars().any(char::is_control)
''',
    '''        if self.review_id.trim().is_empty()
            || self.review_id.chars().count() > 200
            || self.review_id.chars().any(char::is_control)
            || !is_xml_10_text(&self.review_id)
''',
)
replace_once(
    prisma_path,
    '''    /// Input JSON could not be decoded into the strict model.
    #[error("PRISMA flow JSON is invalid: {0}")]
    Json(#[from] serde_json::Error),
''',
    '''    /// Input exceeds the bounded parser contract.
    #[error("PRISMA flow JSON exceeds the declared limit of {0} bytes")]
    ResourceLimit(usize),
    /// Input JSON could not be decoded into the strict model.
    #[error("PRISMA flow JSON is invalid: {0}")]
    Json(#[from] serde_json::Error),
''',
)
replace_once(
    prisma_path,
    '''pub fn parse_prisma_flow(bytes: &[u8]) -> Result<PrismaFlow, PrismaError> {
    serde_json::from_slice(bytes).map_err(PrismaError::Json)
}
''',
    '''pub fn parse_prisma_flow(bytes: &[u8]) -> Result<PrismaFlow, PrismaError> {
    if bytes.len() > MAX_INPUT_BYTES {
        return Err(PrismaError::ResourceLimit(MAX_INPUT_BYTES));
    }
    serde_json::from_slice(bytes).map_err(PrismaError::Json)
}
''',
)
replace_once(
    prisma_path,
    '''fn validate_included_counts(counts: IncludedCounts, path: &str, report: &mut ValidationReport) {
    if counts.studies > counts.reports {
''',
    '''fn validate_included_counts(counts: IncludedCounts, path: &str, report: &mut ValidationReport) {
    validate_count(counts.studies, &format!("{path}/studies"), report);
    validate_count(counts.reports, &format!("{path}/reports"), report);
    if counts.studies > counts.reports {
''',
)
replace_once(
    prisma_path,
    '''fn validate_database_stream(stream: &DatabaseRegisterStream, report: &mut ValidationReport) {
    let identified = diagnostic_sum(
''',
    '''fn validate_database_stream(stream: &DatabaseRegisterStream, report: &mut ValidationReport) {
    for (name, value) in [
        ("databases", stream.databases),
        ("registers", stream.registers),
        ("duplicate_records_removed", stream.duplicate_records_removed),
        (
            "records_marked_ineligible_by_automation",
            stream.records_marked_ineligible_by_automation,
        ),
        ("records_removed_other_reasons", stream.records_removed_other_reasons),
        ("records_screened", stream.records_screened),
        ("records_excluded", stream.records_excluded),
        ("reports_sought", stream.reports_sought),
        ("reports_not_retrieved", stream.reports_not_retrieved),
        ("reports_assessed", stream.reports_assessed),
        ("reports_included", stream.reports_included),
    ] {
        validate_count(
            value,
            &format!("/databases_registers/{name}"),
            report,
        );
    }
    let identified = diagnostic_sum(
''',
)
replace_once(
    prisma_path,
    '''fn validate_other_stream(stream: &OtherMethodsStream, report: &mut ValidationReport) {
    let identified = diagnostic_sum(
''',
    '''fn validate_other_stream(stream: &OtherMethodsStream, report: &mut ValidationReport) {
    for (name, value) in [
        ("websites", stream.websites),
        ("organisations", stream.organisations),
        ("citation_searching", stream.citation_searching),
        ("other_sources", stream.other_sources),
        ("reports_sought", stream.reports_sought),
        ("reports_not_retrieved", stream.reports_not_retrieved),
        ("reports_assessed", stream.reports_assessed),
        ("reports_included", stream.reports_included),
    ] {
        validate_count(value, &format!("/other_methods/{name}"), report);
    }
    let identified = diagnostic_sum(
''',
)
regex_once(
    prisma_path,
    r'''fn validate_reasons\(.*?\n\}\n\nfn validate_difference''',
    '''fn validate_reasons(
    reasons: &[ExclusionReason],
    path: &str,
    report: &mut ValidationReport,
) -> Option<u64> {
    if reasons.len() > MAX_EXCLUSION_REASONS {
        report.push(Diagnostic::error(
            "SF-PRISMA-036",
            path,
            format!("at most {MAX_EXCLUSION_REASONS} exclusion reasons are permitted"),
        ));
    }
    let mut names = BTreeSet::new();
    let mut total = 0_u64;
    for (index, reason) in reasons.iter().enumerate() {
        let reason_path = format!("{path}/{index}");
        let normalized = reason.reason.trim();
        if normalized.is_empty()
            || normalized.chars().count() > MAX_EXCLUSION_REASON_CHARS
            || !is_xml_10_text(normalized)
        {
            report.push(Diagnostic::error(
                "SF-PRISMA-032",
                format!("{reason_path}/reason"),
                format!(
                    "exclusion reason must contain 1 to {MAX_EXCLUSION_REASON_CHARS} XML 1.0-compatible characters"
                ),
            ));
        } else if !names.insert(normalized) {
            report.push(Diagnostic::error(
                "SF-PRISMA-033",
                format!("{reason_path}/reason"),
                "exclusion reasons must be unique within a stream",
            ));
        }
        validate_count(reason.reports, &format!("{reason_path}/reports"), report);
        if reason.reports == 0 {
            report.push(Diagnostic::error(
                "SF-PRISMA-034",
                format!("{reason_path}/reports"),
                "zero-count exclusion reasons must be omitted",
            ));
        }
        let Some(next) = total.checked_add(reason.reports) else {
            report.push(Diagnostic::error(
                "SF-PRISMA-035",
                path,
                "report-exclusion totals overflowed",
            ));
            return None;
        };
        if next > MAX_SAFE_JSON_INTEGER {
            report.push(Diagnostic::error(
                "SF-PRISMA-037",
                path,
                "report-exclusion total exceeds the cross-language safe-integer ceiling",
            ));
            return None;
        }
        total = next;
    }
    Some(total)
}

fn validate_count(value: u64, path: &str, report: &mut ValidationReport) {
    if value > MAX_SAFE_JSON_INTEGER {
        report.push(Diagnostic::error(
            "SF-PRISMA-009",
            path,
            format!("count must not exceed {MAX_SAFE_JSON_INTEGER}"),
        ));
    }
}

fn validate_difference''',
)
replace_once(
    prisma_path,
    '''        total = next;
    }
    Some(total)
}

fn checked_sum''',
    '''        if next > MAX_SAFE_JSON_INTEGER {
            report.push(Diagnostic::error(
                "SF-PRISMA-051",
                path,
                "count total exceeds the cross-language safe-integer ceiling",
            ));
            return None;
        }
        total = next;
    }
    Some(total)
}

fn checked_sum''',
)
replace_once(
    prisma_path,
    '''        total = total
            .checked_add(value)
            .ok_or_else(|| PrismaError::BindingOverflow(path.to_owned()))?;
''',
    '''        total = total
            .checked_add(value)
            .filter(|sum| *sum <= MAX_SAFE_JSON_INTEGER)
            .ok_or_else(|| PrismaError::BindingOverflow(path.to_owned()))?;
''',
)
# The checked-add pattern appears in both checked_sum and exclusion_total.
replace_once(
    prisma_path,
    '''        total = total
            .checked_add(reason.reports)
            .ok_or_else(|| PrismaError::BindingOverflow(path.to_owned()))?;
''',
    '''        total = total
            .checked_add(reason.reports)
            .filter(|sum| *sum <= MAX_SAFE_JSON_INTEGER)
            .ok_or_else(|| PrismaError::BindingOverflow(path.to_owned()))?;
''',
)

cli_path = "crates/standardflow-cli/src/main.rs"
replace_once(cli_path, "use std::io::{self, Write};\n", "use std::io::{self, Read, Write};\n")
replace_once(
    cli_path,
    "const USAGE: &str =",
    "const MAX_DIAGRAM_INPUT_BYTES: u64 = 1_048_576;\n\nconst USAGE: &str =",
)
replace_once(
    cli_path,
    '''    let input = fs::read(&input_path).map_err(|error| {
        CliError::operation(
            "io",
            format!("cannot read {}: {error}", input_path.display()),
        )
    })?;
''',
    '''    let input = read_bounded(&input_path, MAX_DIAGRAM_INPUT_BYTES)?;
''',
)
replace_once(
    cli_path,
    "fn write_atomic(path: &Path, bytes: &[u8]) -> Result<(), CliError> {\n",
    '''fn read_bounded(path: &Path, limit: u64) -> Result<Vec<u8>, CliError> {
    let file = fs::File::open(path).map_err(|error| {
        CliError::operation("io", format!("cannot open {}: {error}", path.display()))
    })?;
    let mut reader = file.take(limit.saturating_add(1));
    let mut bytes = Vec::new();
    let _read = reader.read_to_end(&mut bytes).map_err(|error| {
        CliError::operation("io", format!("cannot read {}: {error}", path.display()))
    })?;
    let observed = match u64::try_from(bytes.len()) {
        Ok(value) => value,
        Err(_) => u64::MAX,
    };
    if observed > limit {
        return Err(CliError::operation(
            "io",
            format!("{} exceeds the {limit}-byte input limit", path.display()),
        ));
    }
    Ok(bytes)
}

fn write_atomic(path: &Path, bytes: &[u8]) -> Result<(), CliError> {
''',
)

# Schema parity and bounded cardinalities.
def load_json(path: str) -> dict:
    return json.loads(read(path))


def dump_json(path: str, value: dict) -> None:
    write(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")

recipe_schema = load_json("schemas/artifact-recipe.v1.schema.json")
props = recipe_schema["properties"]
props["recipe_id"]["maxLength"] = 512
props["version"]["maxLength"] = 128
props["source_standard"]["maxLength"] = 512
props["input_contract"]["maxLength"] = 256
props["title_template"]["maxLength"] = 16_384
props["description_template"]["maxLength"] = 16_384
props["nodes"]["maxItems"] = 512
props["edges"]["maxItems"] = 2_048
props["reading_order"]["maxItems"] = 512
node_props = recipe_schema["$defs"]["node"]["properties"]
node_props["id"]["maxLength"] = 256
node_props["label_template"]["maxLength"] = 16_384
node_props["aria_template"]["maxLength"] = 16_384
edge_props = recipe_schema["$defs"]["edge"]["properties"]
for name in ("id", "from", "to"):
    edge_props[name]["maxLength"] = 256
edge_props["label_template"] = {
    "oneOf": [
        {"type": "null"},
        {"type": "string", "minLength": 1, "maxLength": 16_384},
    ]
}
dump_json("schemas/artifact-recipe.v1.schema.json", recipe_schema)

scene_schema = load_json("schemas/scene-graph.v1.schema.json")
scene_props = scene_schema["properties"]
scene_props["recipe_id"]["maxLength"] = 512
scene_props["title"]["maxLength"] = 65_536
scene_props["description"]["maxLength"] = 65_536
scene_props["canvas"]["properties"]["width"]["maximum"] = 100_000
scene_props["canvas"]["properties"]["height"]["maximum"] = 100_000
scene_props["nodes"]["maxItems"] = 512
scene_props["edges"]["maxItems"] = 2_048
scene_props["reading_order"]["maxItems"] = 512
scene_props["text_equivalent"]["maxLength"] = 262_144
scene_node = scene_props["nodes"]["items"]["properties"]
scene_node["id"]["maxLength"] = 256
scene_node["label"]["maxLength"] = 65_536
scene_node["aria_label"]["maxLength"] = 65_536
scene_node["lines"]["maxItems"] = 4_096
scene_node["lines"]["items"]["maxLength"] = 65_536
scene_edge = scene_props["edges"]["items"]["properties"]
for name in ("id", "from", "to"):
    scene_edge[name]["maxLength"] = 256
scene_edge["label"] = {
    "oneOf": [
        {"type": "null"},
        {"type": "string", "minLength": 1, "maxLength": 65_536},
    ]
}
dump_json("schemas/scene-graph.v1.schema.json", scene_schema)

validate_path = "scripts/validate_artifacts.py"
replace_once(
    validate_path,
    '''    if root.attrib.get("aria-labelledby") != "standardflow-title standardflow-description":
        fail(f"{path.relative_to(ROOT)} must link its title and description")
''',
    '''    if root.attrib.get("aria-labelledby") != "standardflow-title":
        fail(f"{path.relative_to(ROOT)} must identify its title")
    if root.attrib.get("aria-describedby") != "standardflow-description":
        fail(f"{path.relative_to(ROOT)} must identify its complete accessible description")
''',
)
replace_once(
    validate_path,
    '''    for selector in ("svg:title", "svg:desc", "svg:metadata"):
        element = root.find(selector, namespace)
        if element is None or not "".join(element.itertext()).strip():
            fail(f"{path.relative_to(ROOT)} is missing non-empty {selector}")
''',
    '''    for selector in ("svg:title", "svg:desc", "svg:metadata"):
        element = root.find(selector, namespace)
        if element is None or not "".join(element.itertext()).strip():
            fail(f"{path.relative_to(ROOT)} is missing non-empty {selector}")
    description = root.find("svg:desc", namespace)
    if description is None or "Flow relationships:" not in "".join(description.itertext()):
        fail(f"{path.relative_to(ROOT)} accessible description omits flow relationships")
''',
)

write(
    "crates/standardflow-artifacts/tests/hardening.rs",
    '''//! Adversarial resource, schema-parity and accessibility regression tests.

use standardflow_artifacts::{
    DiagramRecipe, PrismaError, RecipeError, parse_prisma_flow, render_svg, render_text,
};

const FLOW: &[u8] = include_bytes!(
    "../../../contracts/examples/prisma-flow/new-databases-registers-other-sources.json"
);
const RECIPE: &[u8] = include_bytes!(
    "../../../recipes/prisma-2020/new-databases-registers-other-sources.json"
);
const MAX_SAFE_JSON_INTEGER: u64 = 9_007_199_254_740_991;

#[test]
fn parsers_reject_documents_above_the_byte_limit() {
    let oversized = vec![b' '; 1_048_577];
    assert!(matches!(
        parse_prisma_flow(&oversized),
        Err(PrismaError::ResourceLimit(1_048_576))
    ));
    assert!(matches!(
        DiagramRecipe::from_json(&oversized),
        Err(RecipeError::ResourceLimit { limit: 1_048_576, .. })
    ));
}

#[test]
fn rust_validation_mirrors_safe_integer_and_reason_limits(
) -> Result<(), Box<dyn std::error::Error>> {
    let mut flow = parse_prisma_flow(FLOW)?;
    flow.databases_registers.databases = MAX_SAFE_JSON_INTEGER + 1;
    let report = flow.validate();
    assert!(report.diagnostics.iter().any(|item| item.code == "SF-PRISMA-009"));

    let mut flow = parse_prisma_flow(FLOW)?;
    let first = flow
        .databases_registers
        .reports_excluded
        .first()
        .cloned()
        .ok_or_else(|| std::io::Error::other("fixture has no exclusion reason"))?;
    flow.databases_registers.reports_excluded = vec![first; 21];
    let report = flow.validate();
    assert!(report.diagnostics.iter().any(|item| item.code == "SF-PRISMA-036"));
    Ok(())
}

#[test]
fn recipes_reject_excessive_rows_before_layout() -> Result<(), Box<dyn std::error::Error>> {
    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
    let node = recipe
        .nodes
        .first_mut()
        .ok_or_else(|| std::io::Error::other("fixture has no node"))?;
    node.row = 1_001;
    let report = recipe.validate();
    assert!(report.diagnostics.iter().any(|item| item.code == "SF-RECIPE-018"));
    Ok(())
}

#[test]
fn long_unbroken_tokens_are_wrapped_inside_nodes() -> Result<(), Box<dyn std::error::Error>> {
    let mut flow = parse_prisma_flow(FLOW)?;
    let reason = flow
        .databases_registers
        .reports_excluded
        .first_mut()
        .ok_or_else(|| std::io::Error::other("fixture has no exclusion reason"))?;
    reason.reason = "x".repeat(240);
    let scene = flow.build_scene()?;
    assert!(
        scene
            .nodes
            .iter()
            .flat_map(|node| &node.lines)
            .all(|line| line.chars().count() <= 80)
    );
    Ok(())
}

#[test]
fn text_and_svg_describe_directed_relationships() -> Result<(), Box<dyn std::error::Error>> {
    let scene = parse_prisma_flow(FLOW)?.build_scene()?;
    let text = render_text(&scene)?;
    assert!(text.contains("Flow relationships:"));
    assert!(text.contains('→'));
    let svg = render_svg(&scene)?;
    assert!(svg.contains("aria-describedby=\"standardflow-description\""));
    assert!(svg.contains("Flow relationships:"));
    Ok(())
}

#[test]
fn xml_invalid_text_is_rejected_before_rendering() -> Result<(), Box<dyn std::error::Error>> {
    let mut scene = parse_prisma_flow(FLOW)?.build_scene()?;
    scene.title.push('\u{1}');
    assert!(render_svg(&scene).is_err());
    Ok(())
}
''',
)

write(
    "crates/standardflow-cli/tests/diagram_limits.rs",
    '''//! End-to-end bounded-input regression tests for the diagram CLI.

use std::fs;
use std::path::PathBuf;
use std::process::Command;
use std::sync::atomic::{AtomicU64, Ordering};

use serde_json::Value;

static COUNTER: AtomicU64 = AtomicU64::new(0);

fn temporary_path(name: &str) -> PathBuf {
    let counter = COUNTER.fetch_add(1, Ordering::Relaxed);
    std::env::temp_dir().join(format!(
        "standardflow-diagram-limit-{}-{counter}-{name}",
        std::process::id()
    ))
}

#[test]
fn cli_rejects_oversized_diagram_input_before_json_parsing(
) -> Result<(), Box<dyn std::error::Error>> {
    let input = temporary_path("oversized.json");
    let output = temporary_path("output.svg");
    fs::write(&input, vec![b' '; 1_048_577])?;
    let response = Command::new(env!("CARGO_BIN_EXE_standardflow"))
        .args(["--json", "diagram", "prisma"])
        .arg(&input)
        .args(["--format", "svg", "--output"])
        .arg(&output)
        .output()?;
    let _ignored = fs::remove_file(&input);
    let _ignored = fs::remove_file(&output);
    assert_eq!(response.status.code(), Some(1));
    let error: Value = serde_json::from_slice(&response.stderr)?;
    assert_eq!(error.pointer("/error/kind"), Some(&Value::String(String::from("io"))));
    assert!(error
        .pointer("/error/message")
        .and_then(Value::as_str)
        .is_some_and(|message| message.contains("1048576-byte input limit")));
    Ok(())
}
''',
)

# Record the review-fix phase without claiming external evidence.
plan_path = "conductor/tracks/02-semantic-diagram-prisma/plan.md"
plan = read(plan_path)
if "## Review fixes: bounded inputs and complete non-visual flow" not in plan:
    plan += '''

## Review fixes: bounded inputs and complete non-visual flow

- [x] Define shared parser, cardinality, layout and text limits.
- [x] Mirror schema constraints in Rust and add adversarial tests.
- [x] Reject XML-invalid content before SVG serialization.
- [x] Include directed edge relationships in the text equivalent and SVG description.
- [x] Add bounded CLI reads and regenerate all reference artefacts.
- [ ] Retain an observed permanent-CI receipt for Linux, macOS and Windows.
'''
    write(plan_path, plan)

print("Applied Track 02 diagram security and accessibility hardening")
