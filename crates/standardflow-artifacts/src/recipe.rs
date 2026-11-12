//! Data-driven diagram recipes and deterministic grid layout.

use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};
use standardflow_core::{Diagnostic, ValidationReport};
use thiserror::Error;

use crate::limits::{
    MAX_BINDING_BYTES, MAX_BINDINGS, MAX_CANVAS_DIMENSION, MAX_COLUMNS,
    MAX_CONTRACT_IDENTIFIER_BYTES, MAX_EDGES, MAX_IDENTIFIER_BYTES, MAX_INPUT_BYTES, MAX_NODES,
    MAX_PATH_IDENTIFIER_BYTES, MAX_RENDERED_COMPONENT_BYTES, MAX_ROW_INDEX, MAX_TEMPLATE_BYTES,
    MAX_TEXT_EQUIVALENT_BYTES, MAX_VERSION_BYTES, MAX_WRAPPED_LINES, is_xml_10_text,
};
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
        if bytes.len() > MAX_INPUT_BYTES {
            return Err(RecipeError::ResourceLimit {
                resource: "recipe JSON bytes",
                limit: MAX_INPUT_BYTES,
            });
        }
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
        if self.nodes.is_empty() || self.nodes.len() > MAX_NODES {
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
        for (path, value, limit) in [
            (
                "/recipe_id",
                self.recipe_id.as_str(),
                MAX_PATH_IDENTIFIER_BYTES,
            ),
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
            (
                "/title_template",
                self.title_template.as_str(),
                MAX_TEMPLATE_BYTES,
            ),
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
        validate_layout(self.layout, &mut report);

        let mut node_ids = BTreeSet::new();
        for (index, node) in self.nodes.iter().enumerate() {
            let path = format!("/nodes/{index}");
            if !is_portable_reference_id(&node.id) || !node_ids.insert(node.id.as_str()) {
                report.push(Diagnostic::error(
                    "SF-RECIPE-004",
                    format!("{path}/id"),
                    "node id must be portable and unique",
                ));
            }
            if node.row > MAX_ROW_INDEX
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
        if self.nodes.len() <= MAX_NODES {
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

        let mut edge_ids = BTreeSet::new();
        for (index, edge) in self.edges.iter().enumerate() {
            let path = format!("/edges/{index}");
            if !is_portable_reference_id(&edge.id) || !edge_ids.insert(edge.id.as_str()) {
                report.push(Diagnostic::error(
                    "SF-RECIPE-008",
                    format!("{path}/id"),
                    "edge id must be portable and unique",
                ));
            }
            if edge.id.len() > MAX_IDENTIFIER_BYTES
                || edge.from.len() > MAX_IDENTIFIER_BYTES
                || edge.to.len() > MAX_IDENTIFIER_BYTES
                || edge.label_template.as_ref().is_some_and(|label| {
                    label.trim().is_empty()
                        || label.len() > MAX_TEMPLATE_BYTES
                        || !is_xml_10_text(label)
                })
            {
                report.push(Diagnostic::error(
                    "SF-RECIPE-019",
                    path.clone(),
                    "edge identifier or label exceeds the declared safe limits",
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

        if self
            .reading_order
            .iter()
            .any(|id| !is_portable_reference_id(id) || id.len() > MAX_IDENTIFIER_BYTES)
        {
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
        validate_bindings(bindings)?;
        let title = interpolate(&self.title_template, bindings)?;
        let description = interpolate(&self.description_template, bindings)?;

        let mut prepared = Vec::with_capacity(self.nodes.len());
        let mut row_heights = BTreeMap::<u32, u32>::new();
        for node in &self.nodes {
            let label = interpolate(&node.label_template, bindings)?;
            let aria_label = interpolate(&node.aria_template, bindings)?;
            let width = node_width(self.layout, node.column_span)?;
            let lines = wrap_label(&label, self.layout, width)?;
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
            build_text_equivalent(&title, &description, &nodes, &edges, &self.reading_order)?;
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
    /// An input or generated component exceeds a declared resource limit.
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
    {
        report.push(Diagnostic::error(
            "SF-RECIPE-013",
            "/layout",
            "layout dimensions are outside the safe deterministic range",
        ));
    }
    if canvas_width(layout).is_err()
        || canvas_width(layout).is_ok_and(|width| width > MAX_CANVAS_DIMENSION)
    {
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
    let mut output = String::with_capacity(template.len().min(MAX_RENDERED_COMPONENT_BYTES));
    loop {
        let Some(open) = remaining.find("{{") else {
            if remaining.contains("}}") {
                return Err(RecipeError::MalformedTemplate);
            }
            append_bounded(
                &mut output,
                remaining,
                MAX_RENDERED_COMPONENT_BYTES,
                "interpolated text bytes",
            )?;
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

fn wrap_label(label: &str, layout: GridLayout, width: u32) -> Result<Vec<String>, RecipeError> {
    let available = width.saturating_sub(layout.padding.saturating_mul(2));
    let maximum = usize::try_from((available / layout.character_width).max(12)).unwrap_or(12);
    let mut lines = Vec::new();
    for paragraph in label.lines() {
        wrap_paragraph(paragraph, maximum, &mut lines);
    }
    if lines.is_empty() {
        lines.push(String::from(" "));
    }
    if lines.len() > MAX_WRAPPED_LINES {
        return Err(RecipeError::ResourceLimit {
            resource: "wrapped label lines",
            limit: MAX_WRAPPED_LINES,
        });
    }
    Ok(lines)
}

fn wrap_paragraph(paragraph: &str, maximum: usize, output: &mut Vec<String>) {
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

fn build_text_equivalent(
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
    append_bounded(
        &mut text,
        title,
        MAX_TEXT_EQUIVALENT_BYTES,
        "text equivalent bytes",
    )?;
    append_bounded(
        &mut text,
        "

",
        MAX_TEXT_EQUIVALENT_BYTES,
        "text equivalent bytes",
    )?;
    append_bounded(
        &mut text,
        description,
        MAX_TEXT_EQUIVALENT_BYTES,
        "text equivalent bytes",
    )?;
    append_bounded(
        &mut text,
        "

Stages:",
        MAX_TEXT_EQUIVALENT_BYTES,
        "text equivalent bytes",
    )?;
    for (index, id) in reading_order.iter().enumerate() {
        let node = lookup
            .get(id.as_str())
            .ok_or_else(|| RecipeError::MissingBinding(id.clone()))?;
        append_bounded(
            &mut text,
            &format!(
                "
{}. {}",
                index + 1,
                node.label
            ),
            MAX_TEXT_EQUIVALENT_BYTES,
            "text equivalent bytes",
        )?;
    }
    append_bounded(
        &mut text,
        "

Flow relationships:",
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
            .map_or_else(String::new, |value| format!("; label: {value}"));
        append_bounded(
            &mut text,
            &format!(
                "
{}. {} → {} ({}){}",
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
        if !is_portable_reference_id(key)
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

fn is_portable_recipe_id(value: &str) -> bool {
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
