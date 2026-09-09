//! Data-driven diagram recipes and deterministic grid layout.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;

use serde::{Deserialize, Serialize};
use standardflow_core::{Diagnostic, ValidationReport};
use thiserror::Error;

use crate::scene::{Anchor, Canvas, EdgeKind, NodeRole, Rect, Scene, SceneEdge, SceneNode};

/// Supported artefact kind for this first renderer slice.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum ArtifactType {
    /// A standards-derived flow diagram.
    FlowDiagram,
}

/// Renderer output declared by a recipe.
#[derive(Clone, Copy, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum RecipeOutput {
    /// Renderer-neutral semantic scene JSON.
    SceneJson,
    /// Accessible SVG.
    Svg,
    /// Plain-text equivalent.
    Text,
}

/// Accessibility requirements embedded in every recipe.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct AccessibilityContract {
    /// A complete reading order is required.
    pub reading_order: bool,
    /// A complete text equivalent is required.
    pub text_equivalent: bool,
    /// Nodes are exposed as labelled groups.
    pub labelled_groups: bool,
}

/// Integer grid settings used by the deterministic layout engine.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct GridLayout {
    /// Number of columns.
    pub columns: u32,
    /// Outer canvas margin.
    pub margin: u32,
    /// Width of one column.
    pub column_width: u32,
    /// Gap between columns.
    pub column_gap: u32,
    /// Gap between rows.
    pub row_gap: u32,
    /// Minimum node height.
    pub minimum_node_height: u32,
    /// Inner node padding.
    pub padding: u32,
    /// Text line height.
    pub line_height: u32,
    /// Approximate pixel width of one character for deterministic wrapping.
    pub character_width: u32,
}

/// One data-driven node declaration.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct RecipeNode {
    /// Stable recipe-local identifier.
    pub id: String,
    /// Semantic node role.
    pub role: NodeRole,
    /// Zero-based grid row.
    pub row: u32,
    /// Zero-based grid column.
    pub column: u32,
    /// Number of columns occupied.
    pub column_span: u32,
    /// Label with `{{binding}}` placeholders.
    pub label_template: String,
    /// Accessible label template. Defaults are deliberately explicit in data.
    pub aria_template: String,
}

/// One data-driven edge declaration.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct RecipeEdge {
    /// Stable recipe-local identifier.
    pub id: String,
    /// Source node identifier.
    pub from: String,
    /// Target node identifier.
    pub to: String,
    /// Semantic edge role.
    pub kind: EdgeKind,
    /// Source anchor.
    pub from_anchor: Anchor,
    /// Target anchor.
    pub to_anchor: Anchor,
    /// Optional edge label template.
    pub label_template: Option<String>,
}

/// Complete versioned flow-diagram recipe.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct DiagramRecipe {
    /// Recipe contract version.
    pub schema_version: String,
    /// Stable recipe identifier.
    pub recipe_id: String,
    /// Recipe release version.
    pub version: String,
    /// Artefact type.
    pub artifact_type: ArtifactType,
    /// Canonical Standard Pack used by the recipe.
    pub source_standard: String,
    /// Expected input contract.
    pub input_contract: String,
    /// Diagram title template.
    pub title_template: String,
    /// Diagram description template.
    pub description_template: String,
    /// Deterministic grid settings.
    pub layout: GridLayout,
    /// Nodes.
    pub nodes: Vec<RecipeNode>,
    /// Edges.
    pub edges: Vec<RecipeEdge>,
    /// Complete node reading order.
    pub reading_order: Vec<String>,
    /// Supported outputs.
    pub outputs: Vec<RecipeOutput>,
    /// Accessibility contract.
    pub accessibility: AccessibilityContract,
}

impl DiagramRecipe {
    /// Parses a strict recipe from JSON.
    ///
    /// # Errors
    ///
    /// Returns [`RecipeError::Json`] when the JSON cannot be decoded.
    pub fn from_json(bytes: &[u8]) -> Result<Self, RecipeError> {
        serde_json::from_slice(bytes).map_err(RecipeError::Json)
    }

    /// Validates recipe structure and deterministic layout constraints.
    #[must_use]
    #[allow(
        clippy::too_many_lines,
        reason = "validation is a linear catalogue of stable recipe diagnostics kept together for auditability"
    )]
    pub fn validate(&self) -> ValidationReport {
        let mut report = ValidationReport::default();
        if self.schema_version != "dev.standardflow.artifact-recipe.v1" {
            report.push(Diagnostic::error(
                "SF-RECIPE-001",
                "/schema_version",
                "schema_version must be dev.standardflow.artifact-recipe.v1",
            ));
        }
        for (path, value) in [
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
            }
        }
        if !is_portable_id(&self.recipe_id) {
            report.push(Diagnostic::error(
                "SF-RECIPE-003",
                "/recipe_id",
                "recipe_id must use portable identifier characters",
            ));
        }
        validate_layout(self.layout, &mut report);

        let mut node_ids = BTreeSet::new();
        for (index, node) in self.nodes.iter().enumerate() {
            let path = format!("/nodes/{index}");
            if !is_portable_id(&node.id) || !node_ids.insert(node.id.as_str()) {
                report.push(Diagnostic::error(
                    "SF-RECIPE-004",
                    format!("{path}/id"),
                    "node id must be portable and unique",
                ));
            }
            if node.column_span == 0
                || node.column >= self.layout.columns
                || node
                    .column
                    .checked_add(node.column_span)
                    .is_none_or(|end| end > self.layout.columns)
            {
                report.push(Diagnostic::error(
                    "SF-RECIPE-005",
                    path.clone(),
                    "node column and span must remain inside the configured grid",
                ));
            }
            if node.label_template.trim().is_empty() || node.aria_template.trim().is_empty() {
                report.push(Diagnostic::error(
                    "SF-RECIPE-006",
                    path,
                    "label and accessible label templates must not be blank",
                ));
            }
        }
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

        let mut edge_ids = BTreeSet::new();
        for (index, edge) in self.edges.iter().enumerate() {
            let path = format!("/edges/{index}");
            if !is_portable_id(&edge.id) || !edge_ids.insert(edge.id.as_str()) {
                report.push(Diagnostic::error(
                    "SF-RECIPE-008",
                    format!("{path}/id"),
                    "edge id must be portable and unique",
                ));
            }
            if edge.from == edge.to
                || !node_ids.contains(edge.from.as_str())
                || !node_ids.contains(edge.to.as_str())
            {
                report.push(Diagnostic::error(
                    "SF-RECIPE-009",
                    path,
                    "edge endpoints must identify two different recipe nodes",
                ));
            }
        }

        let reading_ids = self
            .reading_order
            .iter()
            .map(String::as_str)
            .collect::<BTreeSet<_>>();
        if reading_ids.len() != self.reading_order.len() || reading_ids != node_ids {
            report.push(Diagnostic::error(
                "SF-RECIPE-010",
                "/reading_order",
                "reading_order must contain every node exactly once",
            ));
        }

        let output_set = self.outputs.iter().copied().collect::<BTreeSet<_>>();
        let required_outputs = [
            RecipeOutput::SceneJson,
            RecipeOutput::Svg,
            RecipeOutput::Text,
        ]
        .into_iter()
        .collect::<BTreeSet<_>>();
        if output_set.len() != self.outputs.len() || !required_outputs.is_subset(&output_set) {
            report.push(Diagnostic::error(
                "SF-RECIPE-011",
                "/outputs",
                "outputs must be unique and include scene-json, svg and text",
            ));
        }
        if !self.accessibility.reading_order
            || !self.accessibility.text_equivalent
            || !self.accessibility.labelled_groups
        {
            report.push(Diagnostic::error(
                "SF-RECIPE-012",
                "/accessibility",
                "reading order, text equivalent and labelled groups are mandatory",
            ));
        }
        report
    }

    /// Resolves bindings, lays out nodes and produces a renderer-neutral scene.
    ///
    /// # Errors
    ///
    /// Returns [`RecipeError`] for invalid recipes, missing bindings, arithmetic
    /// overflow or an invalid generated scene.
    #[allow(
        clippy::too_many_lines,
        reason = "scene construction keeps the deterministic prepare-layout-materialise pipeline visible in one auditable function"
    )]
    pub fn build_scene(&self, bindings: &BTreeMap<String, String>) -> Result<Scene, RecipeError> {
        let recipe_report = self.validate();
        if !recipe_report.is_valid() {
            return Err(RecipeError::Validation(recipe_report));
        }
        let title = interpolate(&self.title_template, bindings)?;
        let description = interpolate(&self.description_template, bindings)?;

        let mut prepared = Vec::with_capacity(self.nodes.len());
        let mut row_heights = BTreeMap::<u32, u32>::new();
        for node in &self.nodes {
            let label = interpolate(&node.label_template, bindings)?;
            let aria_label = interpolate(&node.aria_template, bindings)?;
            let width = node_width(self.layout, node.column_span)?;
            let lines = wrap_label(&label, self.layout, width);
            let content_height = u32::try_from(lines.len())
                .ok()
                .and_then(|count| count.checked_mul(self.layout.line_height))
                .and_then(|height| {
                    self.layout
                        .padding
                        .checked_mul(2)
                        .and_then(|padding| height.checked_add(padding))
                })
                .ok_or(RecipeError::LayoutOverflow)?;
            let height = content_height.max(self.layout.minimum_node_height);
            row_heights
                .entry(node.row)
                .and_modify(|existing| *existing = (*existing).max(height))
                .or_insert(height);
            prepared.push((node, label, aria_label, lines, width));
        }

        let row_count = self
            .nodes
            .iter()
            .map(|node| node.row)
            .max()
            .and_then(|row| row.checked_add(1))
            .ok_or(RecipeError::LayoutOverflow)?;
        let mut row_positions = BTreeMap::new();
        let mut current_y = self.layout.margin;
        for row in 0..row_count {
            let height = row_heights
                .get(&row)
                .copied()
                .unwrap_or(self.layout.minimum_node_height);
            row_positions.insert(row, current_y);
            current_y = current_y
                .checked_add(height)
                .and_then(|value| value.checked_add(self.layout.row_gap))
                .ok_or(RecipeError::LayoutOverflow)?;
        }
        let height = current_y
            .checked_sub(self.layout.row_gap)
            .and_then(|value| value.checked_add(self.layout.margin))
            .ok_or(RecipeError::LayoutOverflow)?;
        let width = canvas_width(self.layout)?;

        let mut nodes = Vec::with_capacity(prepared.len());
        for (node, label, aria_label, lines, node_width) in prepared {
            let x = column_x(self.layout, node.column)?;
            let y = row_positions
                .get(&node.row)
                .copied()
                .ok_or(RecipeError::LayoutOverflow)?;
            let node_height = row_heights
                .get(&node.row)
                .copied()
                .ok_or(RecipeError::LayoutOverflow)?;
            nodes.push(SceneNode {
                id: node.id.clone(),
                role: node.role,
                rect: Rect {
                    x,
                    y,
                    width: node_width,
                    height: node_height,
                },
                label,
                lines,
                aria_label,
            });
        }

        let mut edges = Vec::with_capacity(self.edges.len());
        for edge in &self.edges {
            edges.push(SceneEdge {
                id: edge.id.clone(),
                from: edge.from.clone(),
                to: edge.to.clone(),
                kind: edge.kind,
                from_anchor: edge.from_anchor,
                to_anchor: edge.to_anchor,
                label: edge
                    .label_template
                    .as_deref()
                    .map(|template| interpolate(template, bindings))
                    .transpose()?,
            });
        }

        let text_equivalent =
            build_text_equivalent(&title, &description, &nodes, &self.reading_order)?;
        let scene = Scene {
            schema_version: String::from("dev.standardflow.scene-graph.v1"),
            recipe_id: self.recipe_id.clone(),
            title,
            description,
            canvas: Canvas { width, height },
            nodes,
            edges,
            reading_order: self.reading_order.clone(),
            text_equivalent,
        };
        let scene_report = scene.validate();
        if scene_report.is_valid() {
            Ok(scene)
        } else {
            Err(RecipeError::GeneratedScene(scene_report))
        }
    }
}

/// Recipe parsing, validation or rendering failure.
#[derive(Debug, Error)]
pub enum RecipeError {
    /// Recipe JSON could not be decoded.
    #[error("recipe JSON is invalid: {0}")]
    Json(#[source] serde_json::Error),
    /// Recipe structure is invalid.
    #[error("recipe validation failed with {} error(s)", .0.error_count())]
    Validation(ValidationReport),
    /// A required template binding was not provided.
    #[error("template binding {0:?} is missing")]
    MissingBinding(String),
    /// Template delimiters are malformed.
    #[error("template contains malformed binding delimiters")]
    MalformedTemplate,
    /// Formatting into an in-memory text equivalent failed.
    #[error("formatting generated text equivalent failed")]
    Formatting,
    /// Integer layout arithmetic overflowed.
    #[error("integer layout arithmetic overflowed")]
    LayoutOverflow,
    /// Generated scene violated renderer-neutral invariants.
    #[error("generated scene validation failed with {} error(s)", .0.error_count())]
    GeneratedScene(ValidationReport),
}

fn validate_layout(layout: GridLayout, report: &mut ValidationReport) {
    if layout.columns == 0
        || layout.margin == 0
        || layout.column_width < 80
        || layout.column_gap < 8
        || layout.row_gap < 8
        || layout.minimum_node_height < 40
        || layout.padding < 4
        || layout.line_height < 10
        || layout.character_width == 0
    {
        report.push(Diagnostic::error(
            "SF-RECIPE-013",
            "/layout",
            "layout dimensions are outside the safe deterministic range",
        ));
    }
    if canvas_width(layout).is_err() {
        report.push(Diagnostic::error(
            "SF-RECIPE-014",
            "/layout",
            "layout dimensions overflow u32",
        ));
    }
}

const fn nodes_overlap(left: &RecipeNode, right: &RecipeNode) -> bool {
    if left.row != right.row {
        return false;
    }
    let Some(left_end) = left.column.checked_add(left.column_span) else {
        return true;
    };
    let Some(right_end) = right.column.checked_add(right.column_span) else {
        return true;
    };
    left.column < right_end && left_end > right.column
}

fn canvas_width(layout: GridLayout) -> Result<u32, RecipeError> {
    let columns = layout
        .column_width
        .checked_mul(layout.columns)
        .ok_or(RecipeError::LayoutOverflow)?;
    let gaps = layout
        .columns
        .checked_sub(1)
        .and_then(|count| layout.column_gap.checked_mul(count))
        .ok_or(RecipeError::LayoutOverflow)?;
    layout
        .margin
        .checked_mul(2)
        .and_then(|margins| margins.checked_add(columns))
        .and_then(|value| value.checked_add(gaps))
        .ok_or(RecipeError::LayoutOverflow)
}

fn node_width(layout: GridLayout, span: u32) -> Result<u32, RecipeError> {
    let columns = layout
        .column_width
        .checked_mul(span)
        .ok_or(RecipeError::LayoutOverflow)?;
    let gaps = span
        .checked_sub(1)
        .and_then(|count| layout.column_gap.checked_mul(count))
        .ok_or(RecipeError::LayoutOverflow)?;
    columns.checked_add(gaps).ok_or(RecipeError::LayoutOverflow)
}

fn column_x(layout: GridLayout, column: u32) -> Result<u32, RecipeError> {
    let step = layout
        .column_width
        .checked_add(layout.column_gap)
        .ok_or(RecipeError::LayoutOverflow)?;
    layout
        .margin
        .checked_add(
            step.checked_mul(column)
                .ok_or(RecipeError::LayoutOverflow)?,
        )
        .ok_or(RecipeError::LayoutOverflow)
}

#[allow(
    clippy::indexing_slicing,
    reason = "delimiter offsets come from ASCII searches and are valid UTF-8 boundaries"
)]
fn interpolate(template: &str, bindings: &BTreeMap<String, String>) -> Result<String, RecipeError> {
    let mut remaining = template;
    let mut output = String::with_capacity(template.len());
    loop {
        let Some(open) = remaining.find("{{") else {
            if remaining.contains("}}") {
                return Err(RecipeError::MalformedTemplate);
            }
            output.push_str(remaining);
            break;
        };
        output.push_str(&remaining[..open]);
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
        output.push_str(value);
        remaining = &after_open[close + 2..];
    }
    Ok(output)
}

fn wrap_label(label: &str, layout: GridLayout, width: u32) -> Vec<String> {
    let available = width.saturating_sub(layout.padding.saturating_mul(2));
    let maximum = usize::try_from((available / layout.character_width).max(12)).unwrap_or(12);
    let mut lines = Vec::new();
    for paragraph in label.lines() {
        wrap_paragraph(paragraph, maximum, &mut lines);
    }
    if lines.is_empty() {
        lines.push(String::from(" "));
    }
    lines
}

fn wrap_paragraph(paragraph: &str, maximum: usize, output: &mut Vec<String>) {
    if paragraph.trim().is_empty() {
        output.push(String::from(" "));
        return;
    }
    let mut line = String::new();
    for word in paragraph.split_whitespace() {
        let candidate_length = line
            .chars()
            .count()
            .saturating_add(usize::from(!line.is_empty()))
            .saturating_add(word.chars().count());
        if !line.is_empty() && candidate_length > maximum {
            output.push(line);
            line = String::new();
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

fn build_text_equivalent(
    title: &str,
    description: &str,
    nodes: &[SceneNode],
    reading_order: &[String],
) -> Result<String, RecipeError> {
    let lookup = nodes
        .iter()
        .map(|node| (node.id.as_str(), node))
        .collect::<BTreeMap<_, _>>();
    let mut text = format!("{title}\n\n{description}\n");
    for (index, id) in reading_order.iter().enumerate() {
        let node = lookup
            .get(id.as_str())
            .ok_or_else(|| RecipeError::MissingBinding(id.clone()))?;
        write!(&mut text, "\n{}. {}", index + 1, node.label)
            .map_err(|_| RecipeError::Formatting)?;
    }
    text.push('\n');
    Ok(text)
}

fn is_portable_id(value: &str) -> bool {
    let mut bytes = value.bytes();
    bytes
        .next()
        .is_some_and(|first| first.is_ascii_alphanumeric())
        && bytes.all(|byte| {
            byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b':' | b'-' | b'/')
        })
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::interpolate;

    #[test]
    fn interpolation_is_explicit_and_deterministic() -> Result<(), Box<dyn std::error::Error>> {
        let bindings = BTreeMap::from([
            (String::from("a"), String::from("10")),
            (String::from("b"), String::from("20")),
        ]);
        let rendered = interpolate("A={{a}}; B={{ b }}", &bindings)?;
        assert_eq!(rendered, "A=10; B=20");
        Ok(())
    }
}
