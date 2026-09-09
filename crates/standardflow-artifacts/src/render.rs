//! Deterministic accessible SVG, text and scene-JSON renderers.

use std::fmt::Write as _;

use standardflow_core::{CanonicalError, ValidationReport, canonical_json};
use thiserror::Error;

use crate::scene::{Anchor, EdgeKind, NodeRole, Point, Scene, SceneEdge};

const NODE_PADDING: u32 = 18;
const LINE_HEIGHT: u32 = 20;
const FONT_SIZE: u32 = 14;

/// Renderer output format.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum RenderFormat {
    /// Accessible SVG.
    Svg,
    /// Plain-text equivalent.
    Text,
    /// Canonical semantic scene JSON.
    SceneJson,
}

impl RenderFormat {
    /// Parses a command-line format name.
    #[must_use]
    pub fn parse(value: &str) -> Option<Self> {
        match value {
            "svg" => Some(Self::Svg),
            "text" => Some(Self::Text),
            "scene-json" => Some(Self::SceneJson),
            _ => None,
        }
    }

    /// Returns the stable command-line format name.
    #[must_use]
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Svg => "svg",
            Self::Text => "text",
            Self::SceneJson => "scene-json",
        }
    }
}

/// Deterministic renderer failure.
#[derive(Debug, Error)]
pub enum RenderError {
    /// Scene invariants failed before rendering.
    #[error("scene validation failed with {} error(s)", .0.error_count())]
    InvalidScene(ValidationReport),
    /// An edge references a node that is absent from the validated scene.
    #[error("edge {edge_id} references missing node {node_id}")]
    MissingNode {
        /// Edge identifier.
        edge_id: String,
        /// Missing node identifier.
        node_id: String,
    },
    /// Canonical scene JSON could not be encoded.
    #[error(transparent)]
    Canonical(#[from] CanonicalError),
    /// Canonical JSON bytes were unexpectedly not UTF-8.
    #[error("canonical scene JSON was not UTF-8")]
    Utf8,
    /// Writing to the in-memory render buffer failed.
    #[error("in-memory rendering failed")]
    Formatting,
}

/// Renders one scene in the requested format.
///
/// # Errors
///
/// Returns [`RenderError`] when scene validation or deterministic encoding fails.
pub fn render(scene: &Scene, format: RenderFormat) -> Result<Vec<u8>, RenderError> {
    match format {
        RenderFormat::Svg => render_svg(scene).map(String::into_bytes),
        RenderFormat::Text => render_text(scene).map(String::into_bytes),
        RenderFormat::SceneJson => render_scene_json(scene).map(String::into_bytes),
    }
}

/// Renders an accessible, standalone SVG.
///
/// # Errors
///
/// Returns [`RenderError`] when the scene is invalid or an edge cannot be routed.
#[allow(
    clippy::too_many_lines,
    reason = "the standalone SVG writer is a linear, deterministic serialization pass with no hidden renderer state"
)]
pub fn render_svg(scene: &Scene) -> Result<String, RenderError> {
    validate_scene(scene)?;
    let mut output = String::new();
    writeln!(
        output,
        r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {} {}" width="{}" height="{}" role="img" aria-labelledby="standardflow-title standardflow-description">"#,
        scene.canvas.width,
        scene.canvas.height,
        scene.canvas.width,
        scene.canvas.height
    )
    .map_err(|_| RenderError::Formatting)?;
    writeln!(
        output,
        "  <title id=\"standardflow-title\">{}</title>",
        escape_xml(&scene.title)
    )
    .map_err(|_| RenderError::Formatting)?;
    writeln!(
        output,
        "  <desc id=\"standardflow-description\">{}</desc>",
        escape_xml(&scene.description)
    )
    .map_err(|_| RenderError::Formatting)?;
    writeln!(
        output,
        "  <metadata id=\"standardflow-text-equivalent\">{}</metadata>",
        escape_xml(&scene.text_equivalent)
    )
    .map_err(|_| RenderError::Formatting)?;
    output.push_str(
        "  <defs>\n    <marker id=\"standardflow-arrow\" markerWidth=\"10\" markerHeight=\"10\" refX=\"9\" refY=\"3\" orient=\"auto\" markerUnits=\"strokeWidth\"><path d=\"M0,0 L0,6 L9,3 z\" /></marker>\n  </defs>\n",
    );
    output.push_str(
        "  <style>\n    .standardflow-node rect { fill: white; stroke: currentColor; stroke-width: 2; }\n    .standardflow-node--exclusion rect { stroke-dasharray: 7 4; }\n    .standardflow-node--outcome rect { stroke-width: 3; }\n    .standardflow-label { fill: currentColor; font-family: system-ui, sans-serif; font-size: 14px; }\n    .standardflow-edge { fill: none; stroke: currentColor; stroke-width: 2; marker-end: url(#standardflow-arrow); }\n    .standardflow-edge--exclusion { stroke-dasharray: 7 4; }\n    .standardflow-edge-label { fill: currentColor; font-family: system-ui, sans-serif; font-size: 12px; }\n  </style>\n",
    );

    output.push_str("  <g id=\"standardflow-edges\" aria-hidden=\"true\">\n");
    for edge in &scene.edges {
        let path = edge_path(scene, edge)?;
        writeln!(
            output,
            "    <path id=\"edge-{}\" class=\"standardflow-edge standardflow-edge--{}\" d=\"{}\" />",
            escape_xml_attribute(&edge.id),
            edge_kind_class(edge.kind),
            path
        )
        .map_err(|_| RenderError::Formatting)?;
        if let Some(label) = edge.label.as_deref() {
            let (x, y) = edge_label_point(scene, edge)?;
            writeln!(
                output,
                "    <text class=\"standardflow-edge-label\" x=\"{x}\" y=\"{y}\">{}</text>",
                escape_xml(label)
            )
            .map_err(|_| RenderError::Formatting)?;
        }
    }
    output.push_str("  </g>\n");

    output.push_str("  <g id=\"standardflow-nodes\" role=\"list\">\n");
    for node in &scene.nodes {
        writeln!(
            output,
            "    <g id=\"node-{}\" class=\"standardflow-node standardflow-node--{}\" role=\"listitem\" aria-label=\"{}\">",
            escape_xml_attribute(&node.id),
            node_role_class(node.role),
            escape_xml_attribute(&node.aria_label)
        )
        .map_err(|_| RenderError::Formatting)?;
        writeln!(
            output,
            "      <rect x=\"{}\" y=\"{}\" width=\"{}\" height=\"{}\" rx=\"6\" ry=\"6\" />",
            node.rect.x, node.rect.y, node.rect.width, node.rect.height
        )
        .map_err(|_| RenderError::Formatting)?;
        let text_height = u32::try_from(node.lines.len())
            .ok()
            .and_then(|count| count.checked_mul(LINE_HEIGHT))
            .unwrap_or(node.rect.height);
        let initial_y = node
            .rect
            .y
            .saturating_add(node.rect.height.saturating_sub(text_height) / 2)
            .saturating_add(FONT_SIZE);
        writeln!(
            output,
            "      <text class=\"standardflow-label\" x=\"{}\" y=\"{initial_y}\">",
            node.rect.x.saturating_add(NODE_PADDING)
        )
        .map_err(|_| RenderError::Formatting)?;
        for (index, line) in node.lines.iter().enumerate() {
            let dy = if index == 0 { 0 } else { LINE_HEIGHT };
            writeln!(
                output,
                "        <tspan x=\"{}\" dy=\"{dy}\">{}</tspan>",
                node.rect.x.saturating_add(NODE_PADDING),
                escape_xml(line)
            )
            .map_err(|_| RenderError::Formatting)?;
        }
        output.push_str("      </text>\n    </g>\n");
    }
    output.push_str("  </g>\n</svg>\n");
    Ok(output)
}

/// Returns the complete plain-text equivalent.
///
/// # Errors
///
/// Returns [`RenderError::InvalidScene`] when scene invariants fail.
pub fn render_text(scene: &Scene) -> Result<String, RenderError> {
    validate_scene(scene)?;
    Ok(scene.text_equivalent.clone())
}

/// Returns canonical semantic scene JSON with one trailing newline.
///
/// # Errors
///
/// Returns [`RenderError`] when scene validation or canonical encoding fails.
pub fn render_scene_json(scene: &Scene) -> Result<String, RenderError> {
    validate_scene(scene)?;
    let mut bytes = canonical_json(scene)?;
    bytes.push(b'\n');
    String::from_utf8(bytes).map_err(|_| RenderError::Utf8)
}

fn validate_scene(scene: &Scene) -> Result<(), RenderError> {
    let report = scene.validate();
    if report.is_valid() {
        Ok(())
    } else {
        Err(RenderError::InvalidScene(report))
    }
}

fn edge_path(scene: &Scene, edge: &SceneEdge) -> Result<String, RenderError> {
    let start = node_anchor(scene, &edge.from, edge.from_anchor, &edge.id)?;
    let end = node_anchor(scene, &edge.to, edge.to_anchor, &edge.id)?;
    if start.x == end.x || start.y == end.y {
        return Ok(format!("M {} {} L {} {}", start.x, start.y, end.x, end.y));
    }
    if edge.from_anchor.is_vertical() && edge.to_anchor.is_vertical() {
        let middle = midpoint(start.y, end.y);
        Ok(format!(
            "M {} {} L {} {} L {} {} L {} {}",
            start.x, start.y, start.x, middle, end.x, middle, end.x, end.y
        ))
    } else {
        let middle = midpoint(start.x, end.x);
        Ok(format!(
            "M {} {} L {} {} L {} {} L {} {}",
            start.x, start.y, middle, start.y, middle, end.y, end.x, end.y
        ))
    }
}

fn edge_label_point(scene: &Scene, edge: &SceneEdge) -> Result<(u32, u32), RenderError> {
    let start = node_anchor(scene, &edge.from, edge.from_anchor, &edge.id)?;
    let end = node_anchor(scene, &edge.to, edge.to_anchor, &edge.id)?;
    Ok((
        midpoint(start.x, end.x),
        midpoint(start.y, end.y).saturating_sub(6),
    ))
}

fn node_anchor(
    scene: &Scene,
    node_id: &str,
    anchor: Anchor,
    edge_id: &str,
) -> Result<Point, RenderError> {
    scene
        .node(node_id)
        .map(|node| node.rect.anchor(anchor))
        .ok_or_else(|| RenderError::MissingNode {
            edge_id: edge_id.to_owned(),
            node_id: node_id.to_owned(),
        })
}

const fn midpoint(left: u32, right: u32) -> u32 {
    left.midpoint(right)
}

const fn node_role_class(role: NodeRole) -> &'static str {
    match role {
        NodeRole::Source => "source",
        NodeRole::Process => "process",
        NodeRole::Exclusion => "exclusion",
        NodeRole::Outcome => "outcome",
        NodeRole::Prior => "prior",
    }
}

const fn edge_kind_class(kind: EdgeKind) -> &'static str {
    match kind {
        EdgeKind::Progression => "progression",
        EdgeKind::Exclusion => "exclusion",
        EdgeKind::Merge => "merge",
        EdgeKind::Lineage => "lineage",
    }
}

fn escape_xml(value: &str) -> String {
    value
        .replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
}

fn escape_xml_attribute(value: &str) -> String {
    escape_xml(value)
        .replace('"', "&quot;")
        .replace('\'', "&apos;")
}

#[cfg(test)]
mod tests {
    use super::escape_xml_attribute;

    #[test]
    fn attribute_escaping_is_complete() {
        assert_eq!(escape_xml_attribute("<&\"'>"), "&lt;&amp;&quot;&apos;&gt;");
    }
}
