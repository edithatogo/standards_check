//! Adversarial resource, schema-parity and accessibility regression tests.

use standardflow_artifacts::{
    DiagramRecipe, PrismaError, RecipeError, parse_prisma_flow, render_svg, render_text,
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
