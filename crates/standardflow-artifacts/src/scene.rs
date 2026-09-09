//! Accessible semantic scene graph shared by deterministic renderers.

use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};
use standardflow_core::{Diagnostic, ValidationReport};

/// Canvas dimensions in integer CSS pixels.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Canvas {
    /// Canvas width.
    pub width: u32,
    /// Canvas height.
    pub height: u32,
}

/// Deterministic rectangular node bounds.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Rect {
    /// Left coordinate.
    pub x: u32,
    /// Top coordinate.
    pub y: u32,
    /// Width.
    pub width: u32,
    /// Height.
    pub height: u32,
}

impl Rect {
    /// Returns the anchor point requested by an edge.
    #[must_use]
    pub const fn anchor(self, anchor: Anchor) -> Point {
        match anchor {
            Anchor::Top => Point {
                x: self.x + self.width / 2,
                y: self.y,
            },
            Anchor::Right => Point {
                x: self.x + self.width,
                y: self.y + self.height / 2,
            },
            Anchor::Bottom => Point {
                x: self.x + self.width / 2,
                y: self.y + self.height,
            },
            Anchor::Left => Point {
                x: self.x,
                y: self.y + self.height / 2,
            },
        }
    }

    const fn right(self) -> Option<u32> {
        self.x.checked_add(self.width)
    }

    const fn bottom(self) -> Option<u32> {
        self.y.checked_add(self.height)
    }
}

/// Integer point in the scene coordinate system.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Point {
    /// Horizontal coordinate.
    pub x: u32,
    /// Vertical coordinate.
    pub y: u32,
}

/// Semantic node role, independent of visual styling.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum NodeRole {
    /// Source identification or discovery.
    Source,
    /// Review or research process stage.
    Process,
    /// Exclusion, removal or failure.
    Exclusion,
    /// Included or final outcome.
    Outcome,
    /// Prior-review state carried into an update.
    Prior,
}

/// Semantic edge role.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum EdgeKind {
    /// Normal forward progression.
    Progression,
    /// Exclusion or removal branch.
    Exclusion,
    /// Merge of two evidence streams.
    Merge,
    /// Lineage from a prior review version.
    Lineage,
}

/// Node anchor used for deterministic orthogonal routing.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Anchor {
    /// Top-centre anchor.
    Top,
    /// Right-centre anchor.
    Right,
    /// Bottom-centre anchor.
    Bottom,
    /// Left-centre anchor.
    Left,
}

impl Anchor {
    /// Returns whether this anchor starts or ends a vertical route.
    #[must_use]
    pub const fn is_vertical(self) -> bool {
        matches!(self, Self::Top | Self::Bottom)
    }
}

/// One accessible scene node.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SceneNode {
    /// Stable recipe-local identifier.
    pub id: String,
    /// Semantic role.
    pub role: NodeRole,
    /// Deterministic bounds.
    pub rect: Rect,
    /// Complete unwrapped label.
    pub label: String,
    /// Wrapped display lines.
    pub lines: Vec<String>,
    /// Accessible node label.
    pub aria_label: String,
}

/// One accessible scene edge.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SceneEdge {
    /// Stable recipe-local identifier.
    pub id: String,
    /// Source node identifier.
    pub from: String,
    /// Target node identifier.
    pub to: String,
    /// Semantic role.
    pub kind: EdgeKind,
    /// Source anchor.
    pub from_anchor: Anchor,
    /// Target anchor.
    pub to_anchor: Anchor,
    /// Optional accessible edge label.
    pub label: Option<String>,
}

/// Renderer-neutral accessible diagram scene.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Scene {
    /// Scene contract version.
    pub schema_version: String,
    /// Recipe that produced the scene.
    pub recipe_id: String,
    /// Diagram title.
    pub title: String,
    /// Diagram description.
    pub description: String,
    /// Canvas dimensions.
    pub canvas: Canvas,
    /// Positioned nodes.
    pub nodes: Vec<SceneNode>,
    /// Semantic edges.
    pub edges: Vec<SceneEdge>,
    /// Stable reading order containing every node exactly once.
    pub reading_order: Vec<String>,
    /// Complete non-visual equivalent.
    pub text_equivalent: String,
}

impl Scene {
    /// Validates structural, geometry and accessibility invariants.
    #[must_use]
    #[allow(
        clippy::too_many_lines,
        reason = "scene validation keeps the complete stable diagnostic catalogue together for auditability"
    )]
    pub fn validate(&self) -> ValidationReport {
        let mut report = ValidationReport::default();
        if self.schema_version != "dev.standardflow.scene-graph.v1" {
            report.push(Diagnostic::error(
                "SF-SCENE-001",
                "/schema_version",
                "schema_version must be dev.standardflow.scene-graph.v1",
            ));
        }
        if self.canvas.width == 0 || self.canvas.height == 0 {
            report.push(Diagnostic::error(
                "SF-SCENE-002",
                "/canvas",
                "canvas dimensions must be positive",
            ));
        }
        if self.title.trim().is_empty() || self.description.trim().is_empty() {
            report.push(Diagnostic::error(
                "SF-SCENE-003",
                "/title",
                "title and description must not be blank",
            ));
        }
        if self.text_equivalent.trim().is_empty() {
            report.push(Diagnostic::error(
                "SF-SCENE-004",
                "/text_equivalent",
                "a complete text equivalent is required",
            ));
        }

        let mut node_indexes = BTreeMap::new();
        for (index, node) in self.nodes.iter().enumerate() {
            let path = format!("/nodes/{index}");
            if !is_portable_id(&node.id) {
                report.push(Diagnostic::error(
                    "SF-SCENE-005",
                    format!("{path}/id"),
                    "node id is not portable",
                ));
            }
            if node_indexes.insert(node.id.as_str(), index).is_some() {
                report.push(Diagnostic::error(
                    "SF-SCENE-006",
                    format!("{path}/id"),
                    "duplicate node id",
                ));
            }
            if node.label.trim().is_empty()
                || node.aria_label.trim().is_empty()
                || node.lines.is_empty()
                || node.lines.iter().any(|line| line.trim().is_empty())
            {
                report.push(Diagnostic::error(
                    "SF-SCENE-007",
                    path.clone(),
                    "node labels and wrapped lines must be non-empty",
                ));
            }
            match (node.rect.right(), node.rect.bottom()) {
                (Some(right), Some(bottom))
                    if node.rect.width > 0
                        && node.rect.height > 0
                        && right <= self.canvas.width
                        && bottom <= self.canvas.height => {}
                _ => report.push(Diagnostic::error(
                    "SF-SCENE-008",
                    format!("{path}/rect"),
                    "node bounds must be positive and remain inside the canvas",
                )),
            }
        }

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

        let mut edge_ids = BTreeSet::new();
        for (index, edge) in self.edges.iter().enumerate() {
            let path = format!("/edges/{index}");
            if !is_portable_id(&edge.id) || !edge_ids.insert(edge.id.as_str()) {
                report.push(Diagnostic::error(
                    "SF-SCENE-010",
                    format!("{path}/id"),
                    "edge id must be portable and unique",
                ));
            }
            if edge.from == edge.to
                || !node_indexes.contains_key(edge.from.as_str())
                || !node_indexes.contains_key(edge.to.as_str())
            {
                report.push(Diagnostic::error(
                    "SF-SCENE-011",
                    path,
                    "edge endpoints must identify two different existing nodes",
                ));
            }
        }

        let node_ids = node_indexes.keys().copied().collect::<BTreeSet<_>>();
        let reading_ids = self
            .reading_order
            .iter()
            .map(String::as_str)
            .collect::<BTreeSet<_>>();
        if reading_ids.len() != self.reading_order.len() || reading_ids != node_ids {
            report.push(Diagnostic::error(
                "SF-SCENE-012",
                "/reading_order",
                "reading_order must contain every node exactly once",
            ));
        }
        report
    }

    /// Returns a node by stable identifier.
    #[must_use]
    pub fn node(&self, id: &str) -> Option<&SceneNode> {
        self.nodes.iter().find(|node| node.id == id)
    }
}

const fn rectangles_overlap(left: Rect, right: Rect) -> bool {
    let Some(left_right) = left.right() else {
        return true;
    };
    let Some(left_bottom) = left.bottom() else {
        return true;
    };
    let Some(right_right) = right.right() else {
        return true;
    };
    let Some(right_bottom) = right.bottom() else {
        return true;
    };
    left.x < right_right && left_right > right.x && left.y < right_bottom && left_bottom > right.y
}

fn is_portable_id(value: &str) -> bool {
    let mut bytes = value.bytes();
    bytes
        .next()
        .is_some_and(|first| first.is_ascii_alphanumeric())
        && bytes
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b':' | b'-'))
}

#[cfg(test)]
mod tests {
    use super::{Anchor, Rect};

    #[test]
    fn anchors_use_integer_centres() {
        let rect = Rect {
            x: 10,
            y: 20,
            width: 100,
            height: 80,
        };
        assert_eq!(rect.anchor(Anchor::Top).x, 60);
        assert_eq!(rect.anchor(Anchor::Right).y, 60);
        assert_eq!(rect.anchor(Anchor::Bottom).y, 100);
        assert_eq!(rect.anchor(Anchor::Left).x, 10);
    }
}
