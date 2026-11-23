//! Adversarial resource, schema-parity and accessibility regression tests.

use standardflow_artifacts::{
    DiagramRecipe, PrismaError, RecipeError, Scene, parse_prisma_flow, render_scene_json,
    render_svg, render_text,
};

const FLOW: &[u8] = include_bytes!(
    "../../../contracts/examples/prisma-flow/new-databases-registers-other-sources.json"
);
const RECIPE: &[u8] =
    include_bytes!("../../../recipes/prisma-2020/new-databases-registers-other-sources.json");
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
        Err(RecipeError::ResourceLimit {
            limit: 1_048_576,
            ..
        })
    ));
}

#[test]
fn rust_validation_mirrors_safe_integer_and_reason_limits() -> Result<(), Box<dyn std::error::Error>>
{
    let mut flow = parse_prisma_flow(FLOW)?;
    flow.databases_registers.databases = MAX_SAFE_JSON_INTEGER + 1;
    let report = flow.validate();
    assert!(
        report
            .diagnostics
            .iter()
            .any(|item| item.code == "SF-PRISMA-009")
    );

    let mut flow = parse_prisma_flow(FLOW)?;
    let first = flow
        .databases_registers
        .reports_excluded
        .first()
        .cloned()
        .ok_or_else(|| std::io::Error::other("fixture has no exclusion reason"))?;
    flow.databases_registers.reports_excluded = vec![first; 21];
    let report = flow.validate();
    assert!(
        report
            .diagnostics
            .iter()
            .any(|item| item.code == "SF-PRISMA-036")
    );
    Ok(())
}

#[test]
fn safe_integer_ceiling_is_inclusive_for_consistent_counts()
-> Result<(), Box<dyn std::error::Error>> {
    let flow = serde_json::json!({
        "schema_version": "dev.standardflow.prisma-flow.v1",
        "review_id": "safe-integer-boundary",
        "template": "new_databases_registers",
        "databases_registers": {
            "databases": MAX_SAFE_JSON_INTEGER,
            "registers": 0,
            "duplicate_records_removed": 0,
            "records_marked_ineligible_by_automation": 0,
            "records_removed_other_reasons": 0,
            "records_screened": MAX_SAFE_JSON_INTEGER,
            "records_excluded": 0,
            "reports_sought": MAX_SAFE_JSON_INTEGER,
            "reports_not_retrieved": 0,
            "reports_assessed": MAX_SAFE_JSON_INTEGER,
            "reports_excluded": [],
            "reports_included": MAX_SAFE_JSON_INTEGER
        },
        "other_methods": null,
        "previous_review": null,
        "new_included": {"studies": 1, "reports": MAX_SAFE_JSON_INTEGER},
        "total_included": {"studies": 1, "reports": MAX_SAFE_JSON_INTEGER}
    });
    let parsed = parse_prisma_flow(&serde_json::to_vec(&flow)?)?;
    assert!(parsed.validate().is_valid());
    assert!(parsed.build_scene()?.validate().is_valid());
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
    assert!(
        report
            .diagnostics
            .iter()
            .any(|item| item.code == "SF-RECIPE-018")
    );
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
fn svg_nodes_follow_reading_order_independently_of_storage_order()
-> Result<(), Box<dyn std::error::Error>> {
    let mut scene = parse_prisma_flow(FLOW)?.build_scene()?;
    let svg = render_svg(&scene)?;
    let text = render_text(&scene)?;
    let mut previous_position = 0;
    for id in &scene.reading_order {
        let marker = format!("<g id=\"node-{id}\"");
        let position = svg
            .find(&marker)
            .ok_or_else(|| std::io::Error::other(format!("SVG is missing node {id}")))?;
        assert!(
            position > previous_position,
            "SVG node {id} is out of reading order"
        );
        previous_position = position;
    }
    scene.nodes.reverse();
    assert!(scene.validate().is_valid());
    assert_eq!(render_svg(&scene)?, svg);
    assert_eq!(render_text(&scene)?, text);
    Ok(())
}

#[test]
fn isolated_scene_node_identifiers_obey_the_schema_limit() -> Result<(), Box<dyn std::error::Error>>
{
    let mut scene = parse_prisma_flow(FLOW)?.build_scene()?;
    scene.nodes.truncate(1);
    scene.edges.clear();
    let node = scene
        .nodes
        .first_mut()
        .ok_or_else(|| std::io::Error::other("fixture has no node"))?;
    node.id = "x".repeat(256);
    scene.reading_order = vec![node.id.clone()];
    assert!(scene.validate().is_valid());

    let node = scene
        .nodes
        .first_mut()
        .ok_or_else(|| std::io::Error::other("fixture has no node"))?;
    node.id.push('x');
    scene.reading_order = vec![node.id.clone()];
    assert!(
        scene
            .validate()
            .diagnostics
            .iter()
            .any(|item| item.code == "SF-SCENE-005")
    );
    assert!(render_svg(&scene).is_err());
    Ok(())
}

#[test]
fn xml_invalid_text_is_rejected_before_rendering() -> Result<(), Box<dyn std::error::Error>> {
    let mut scene = parse_prisma_flow(FLOW)?.build_scene()?;
    scene.title.push('\u{1}');
    assert!(render_svg(&scene).is_err());
    Ok(())
}

#[test]
fn recipe_validation_matches_identifier_and_metadata_schema_boundaries()
-> Result<(), Box<dyn std::error::Error>> {
    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
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
    assert!(
        report
            .diagnostics
            .iter()
            .any(|item| item.code == "SF-RECIPE-004")
    );
    assert!(
        report
            .diagnostics
            .iter()
            .any(|item| item.code == "SF-RECIPE-021")
    );

    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
    recipe.version = "v".repeat(129);
    recipe.input_contract = "c".repeat(257);
    recipe.source_standard = String::from("Org.PRISMA/PRISMA/2020");
    let report = recipe.validate();
    assert!(
        report
            .diagnostics
            .iter()
            .any(|item| item.code == "SF-RECIPE-017")
    );
    assert!(
        report
            .diagnostics
            .iter()
            .any(|item| item.code == "SF-RECIPE-020")
    );
    Ok(())
}

#[test]
fn optional_edge_labels_cannot_be_blank() -> Result<(), Box<dyn std::error::Error>> {
    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
    let edge = recipe
        .edges
        .first_mut()
        .ok_or_else(|| std::io::Error::other("fixture has no edge"))?;
    edge.label_template = Some(String::new());
    let report = recipe.validate();
    assert!(
        report
            .diagnostics
            .iter()
            .any(|item| item.code == "SF-RECIPE-019")
    );
    Ok(())
}

#[test]
fn compact_recipe_metrics_survive_scene_roundtrip_and_svg_rendering()
-> Result<(), Box<dyn std::error::Error>> {
    let mut recipe = single_node_recipe("First\nSecond\nThird\nFourth")?;
    recipe.layout.padding = 4;
    recipe.layout.line_height = 10;

    let scene = recipe.build_scene(&std::collections::BTreeMap::new())?;
    let json = render_scene_json(&scene)?;
    let serialized: serde_json::Value = serde_json::from_str(&json)?;
    assert_eq!(serialized.get("node_padding"), Some(&serde_json::json!(4)));
    assert_eq!(serialized.get("line_height"), Some(&serde_json::json!(10)));
    let restored: Scene = serde_json::from_str(&json)?;
    assert_eq!(restored, scene);
    let svg = render_svg(&restored)?;
    assert!(svg.contains("font-size: 10px;"));
    assert!(svg.contains("<rect x=\"40\" y=\"40\" width=\"80\" height=\"48\""));
    assert!(svg.contains("<text class=\"standardflow-label\" x=\"44\" y=\"54\">"));
    assert!(svg.contains("<tspan x=\"44\" dy=\"0\">First</tspan>"));
    for line in ["Second", "Third", "Fourth"] {
        assert!(svg.contains(&format!("<tspan x=\"44\" dy=\"10\">{line}</tspan>")));
    }
    // Four 10px lines fit between y=44 and y=84, inside the 4px node padding.
    assert_eq!(render_text(&restored)?, render_text(&scene)?);
    Ok(())
}

#[test]
fn narrow_node_interiors_bound_words_and_unbroken_labels() -> Result<(), Box<dyn std::error::Error>>
{
    let label = "ABCDEFGHIJKLMN O PQ R S";
    for (padding, capacity) in [(36, 1), (32, 2)] {
        let mut recipe = single_node_recipe(label)?;
        recipe.layout.padding = padding;
        recipe.layout.character_width = 7;
        let scene = recipe.build_scene(&std::collections::BTreeMap::new())?;
        let node = scene
            .nodes
            .first()
            .ok_or_else(|| std::io::Error::other("fixture has no node"))?;
        assert_eq!(node.rect.width, 80);
        assert!(
            node.lines
                .iter()
                .all(|line| line.chars().count() <= capacity)
        );
        assert_eq!(node.lines.concat(), "ABCDEFGHIJKLMNOPQRS");
        assert!(render_text(&scene)?.contains(label));
        assert!(render_svg(&scene).is_ok());
    }
    Ok(())
}

#[test]
fn node_spans_require_room_for_at_least_one_estimated_character()
-> Result<(), Box<dyn std::error::Error>> {
    for (padding, character_width) in [(39, 7), (40, 7), (41, 7), (36, 0)] {
        let mut recipe = single_node_recipe("Narrow")?;
        recipe.layout.padding = padding;
        recipe.layout.character_width = character_width;
        assert!(
            recipe
                .validate()
                .diagnostics
                .iter()
                .any(|item| item.code == "SF-RECIPE-022" && item.path == "/nodes/0")
        );
        assert!(matches!(
            recipe.build_scene(&std::collections::BTreeMap::new()),
            Err(RecipeError::Validation(_))
        ));
    }
    // A two-column node can fit even when a one-column node on the same grid cannot.
    let mut recipe = single_node_recipe("A wider node")?;
    recipe.layout.columns = 2;
    recipe.layout.padding = 39;
    recipe.layout.character_width = 7;
    assert!(!recipe.validate().is_valid());
    recipe
        .nodes
        .first_mut()
        .ok_or_else(|| std::io::Error::other("fixture has no node"))?
        .column_span = 2;
    assert!(recipe.validate().is_valid());
    let scene = recipe.build_scene(&std::collections::BTreeMap::new())?;
    assert!(render_svg(&scene).is_ok());
    Ok(())
}

fn single_node_recipe(label: &str) -> Result<DiagramRecipe, Box<dyn std::error::Error>> {
    let mut recipe = DiagramRecipe::from_json(RECIPE)?;
    recipe.title_template = String::from("Compact layout");
    recipe.description_template = String::from("Synthetic label geometry");
    recipe.layout.columns = 1;
    recipe.layout.column_width = 80;
    recipe.layout.minimum_node_height = 40;
    recipe.nodes.truncate(1);
    recipe.edges.clear();
    let node = recipe
        .nodes
        .first_mut()
        .ok_or_else(|| std::io::Error::other("fixture has no node"))?;
    label.clone_into(&mut node.label_template);
    node.aria_template.clone_from(&node.label_template);
    recipe.reading_order = vec![node.id.clone()];
    Ok(recipe)
}

#[test]
fn existing_scene_json_keeps_default_metrics_and_identical_outputs()
-> Result<(), Box<dyn std::error::Error>> {
    let json = include_str!(
        "../../../examples/generated/prisma-2020/new-databases-registers-other-sources.scene.json"
    );
    let scene: Scene = serde_json::from_str(json)?;
    assert!(scene.validate().is_valid());
    assert_eq!(render_scene_json(&scene)?, json);
    assert_eq!(
        render_svg(&scene)?,
        include_str!(
            "../../../examples/generated/prisma-2020/new-databases-registers-other-sources.svg"
        )
    );
    Ok(())
}

#[test]
fn isolated_scenes_reject_unsafe_or_uncontainable_text_metrics()
-> Result<(), Box<dyn std::error::Error>> {
    let scene = parse_prisma_flow(FLOW)?.build_scene()?;
    for (field, value) in [
        ("node_padding", 3_u32),
        ("node_padding", 201),
        ("node_padding", u32::MAX),
        ("line_height", 9),
        ("line_height", 101),
        ("line_height", u32::MAX),
    ] {
        let mut json = serde_json::to_value(&scene)?;
        json.as_object_mut()
            .ok_or_else(|| std::io::Error::other("scene is not an object"))?
            .insert(field.to_owned(), serde_json::Value::from(value));
        let invalid: Scene = serde_json::from_value(json)?;
        assert!(
            invalid
                .validate()
                .diagnostics
                .iter()
                .any(|item| item.code == "SF-SCENE-019")
        );
        assert!(render_svg(&invalid).is_err());
        assert!(render_text(&invalid).is_err());
        assert!(render_scene_json(&invalid).is_err());
    }
    for (width, height) in [(36, 500), (500, 1)] {
        let mut invalid = scene.clone();
        let node = invalid
            .nodes
            .first_mut()
            .ok_or_else(|| std::io::Error::other("fixture has no node"))?;
        node.rect.width = width;
        node.rect.height = height;
        assert!(
            invalid
                .validate()
                .diagnostics
                .iter()
                .any(|item| item.code == "SF-SCENE-020")
        );
        assert!(render_svg(&invalid).is_err());
    }
    Ok(())
}
