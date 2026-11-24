//! Isolated scene admission tests independent of the recipe generator.

use std::io;

use serde_json::{Value, json};
use standardflow_artifacts::{
    Scene, parse_prisma_flow, render_scene_json, render_svg, render_text,
};

const FLOW: &[u8] = include_bytes!(
    "../../../contracts/examples/prisma-flow/new-databases-registers-other-sources.json"
);

fn fixture() -> Result<Scene, Box<dyn std::error::Error>> {
    Ok(parse_prisma_flow(FLOW)?.build_scene()?)
}

fn reject(scene: &Scene, code: &str) {
    assert!(
        scene
            .validate()
            .diagnostics
            .iter()
            .any(|item| item.code == code),
        "missing {code}"
    );
    assert!(render_svg(scene).is_err());
    assert!(render_text(scene).is_err());
    assert!(render_scene_json(scene).is_err());
}

#[test]
fn malformed_metadata_geometry_and_accessibility_fail_in_every_renderer()
-> Result<(), Box<dyn std::error::Error>> {
    let scene = serde_json::to_value(fixture()?)?;
    for (path, replacement, code) in [
        ("/schema_version", json!("old"), "SF-SCENE-001"),
        ("/recipe_id", json!("../escape"), "SF-SCENE-013"),
        ("/canvas/width", json!(0), "SF-SCENE-002"),
        ("/canvas/height", json!(100_001), "SF-SCENE-002"),
        ("/title", json!(" "), "SF-SCENE-003"),
        ("/description", json!(" "), "SF-SCENE-003"),
        ("/text_equivalent", json!(" "), "SF-SCENE-004"),
        (
            "/text_equivalent",
            json!("incomplete description"),
            "SF-SCENE-017",
        ),
        ("/nodes/0/label", json!(" "), "SF-SCENE-007"),
        ("/nodes/0/aria_label", json!("\u{1}"), "SF-SCENE-007"),
        ("/nodes/0/lines", json!([]), "SF-SCENE-007"),
        ("/nodes/0/lines", json!([" "]), "SF-SCENE-007"),
        ("/nodes/0/rect/x", json!(u32::MAX), "SF-SCENE-008"),
        ("/nodes/0/rect/height", json!(0), "SF-SCENE-008"),
        ("/edges/0/id", json!("bad/id"), "SF-SCENE-010"),
        ("/edges/0/label", json!(" "), "SF-SCENE-016"),
        ("/edges/0/from", json!("missing"), "SF-SCENE-011"),
        ("/reading_order", json!([]), "SF-SCENE-012"),
    ] {
        let mut value = scene.clone();
        *value
            .pointer_mut(path)
            .ok_or_else(|| io::Error::other(format!("missing {path}")))? = replacement;
        let invalid: Scene = serde_json::from_value(value)?;
        reject(&invalid, code);
    }
    Ok(())
}

#[test]
fn duplicate_graph_identity_and_lost_direction_are_rejected()
-> Result<(), Box<dyn std::error::Error>> {
    let original = fixture()?;
    let mut duplicate_node = original.clone();
    let first = duplicate_node
        .nodes
        .first()
        .cloned()
        .ok_or_else(|| io::Error::other("no node"))?;
    duplicate_node.nodes.push(first);
    reject(&duplicate_node, "SF-SCENE-006");
    let mut duplicate_edge = original.clone();
    let first = duplicate_edge
        .edges
        .first()
        .cloned()
        .ok_or_else(|| io::Error::other("no edge"))?;
    duplicate_edge.edges.push(first);
    reject(&duplicate_edge, "SF-SCENE-010");
    let mut self_loop = original.clone();
    let edge = self_loop
        .edges
        .first_mut()
        .ok_or_else(|| io::Error::other("no edge"))?;
    edge.to.clone_from(&edge.from);
    reject(&self_loop, "SF-SCENE-011");
    let mut lost_direction = original;
    lost_direction.text_equivalent = lost_direction
        .nodes
        .iter()
        .map(|node| node.label.clone())
        .collect::<Vec<_>>()
        .join("\n");
    reject(&lost_direction, "SF-SCENE-018");
    Ok(())
}

#[test]
fn oversized_graphs_and_overlapping_nodes_never_render() -> Result<(), Box<dyn std::error::Error>> {
    let original = fixture()?;
    let first = original
        .nodes
        .first()
        .cloned()
        .ok_or_else(|| io::Error::other("no node"))?;
    let edge = original
        .edges
        .first()
        .cloned()
        .ok_or_else(|| io::Error::other("no edge"))?;
    let mut no_nodes = original.clone();
    no_nodes.nodes.clear();
    reject(&no_nodes, "SF-SCENE-014");
    let mut excessive_nodes = original.clone();
    excessive_nodes.nodes = vec![first.clone(); 513];
    reject(&excessive_nodes, "SF-SCENE-014");
    let mut excessive_edges = original.clone();
    excessive_edges.edges = vec![edge; 2_049];
    reject(&excessive_edges, "SF-SCENE-015");
    let mut overlap = original;
    let second = overlap
        .nodes
        .get_mut(1)
        .ok_or_else(|| io::Error::other("no second node"))?;
    second.rect = first.rect;
    reject(&overlap, "SF-SCENE-009");
    Ok(())
}

#[test]
fn serialized_scene_is_an_independent_render_input() -> Result<(), Box<dyn std::error::Error>> {
    let scene = fixture()?;
    let serialized = render_scene_json(&scene)?;
    let restored: Scene = serde_json::from_str(&serialized)?;
    assert_eq!(render_svg(&restored)?, render_svg(&scene)?);
    assert_eq!(render_text(&restored)?, render_text(&scene)?);
    let mut json: Value = serde_json::from_str(&serialized)?;
    json.as_object_mut()
        .ok_or_else(|| io::Error::other("not an object"))?
        .insert(String::from("unreviewed_extension"), json!(true));
    assert!(serde_json::from_value::<Scene>(json).is_err());
    Ok(())
}
