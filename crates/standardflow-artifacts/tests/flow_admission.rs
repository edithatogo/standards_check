//! Untrusted flow and recipe documents cannot bypass arithmetic or identity gates.

use std::collections::BTreeMap;
use std::io;

use serde_json::{Value, json};
use standardflow_artifacts::{DiagramRecipe, PrismaError, parse_prisma_flow};

const FLOW: &[u8] = include_bytes!(
    "../../../contracts/examples/prisma-flow/new-databases-registers-other-sources.json"
);
const RECIPE: &[u8] =
    include_bytes!("../../../recipes/prisma-2020/new-databases-registers-other-sources.json");

#[test]
fn malformed_flow_identity_and_count_conservation_are_rejected()
-> Result<(), Box<dyn std::error::Error>> {
    for (pointer, replacement, code) in [
        ("/schema_version", json!("old"), "SF-PRISMA-001"),
        ("/review_id", json!(" "), "SF-PRISMA-002"),
        ("/review_id", json!("line\nbreak"), "SF-PRISMA-002"),
        ("/other_methods", Value::Null, "SF-PRISMA-003"),
        (
            "/previous_review",
            json!({"studies":1,"reports":1}),
            "SF-PRISMA-004",
        ),
        ("/new_included/reports", json!(1), "SF-PRISMA-005"),
        ("/total_included/reports", json!(1), "SF-PRISMA-007"),
        ("/other_methods/reports_sought", json!(0), "SF-PRISMA-020"),
        (
            "/databases_registers/reports_excluded/0/reason",
            json!(" "),
            "SF-PRISMA-032",
        ),
        (
            "/databases_registers/reports_excluded/0/reports",
            json!(0),
            "SF-PRISMA-034",
        ),
    ] {
        let mut value: Value = serde_json::from_slice(FLOW)?;
        *value
            .pointer_mut(pointer)
            .ok_or_else(|| io::Error::other(format!("missing {pointer}")))? = replacement;
        let bytes = serde_json::to_vec(&value)?;
        let flow = parse_prisma_flow(&bytes)?;
        let report = flow.validate();
        assert!(
            report.diagnostics.iter().any(|item| item.code == code),
            "{pointer}: expected {code}, observed {report:?}"
        );
        assert!(matches!(
            flow.build_scene(),
            Err(PrismaError::Validation(_))
        ));
    }
    Ok(())
}

#[test]
fn overflowing_or_duplicate_exclusions_never_become_a_valid_flow()
-> Result<(), Box<dyn std::error::Error>> {
    let mut flow = parse_prisma_flow(FLOW)?;
    let reason = flow
        .databases_registers
        .reports_excluded
        .first()
        .cloned()
        .ok_or_else(|| io::Error::other("no exclusion reason"))?;
    flow.databases_registers.reports_excluded = vec![reason.clone(), reason];
    assert!(
        flow.validate()
            .diagnostics
            .iter()
            .any(|item| item.code == "SF-PRISMA-033")
    );
    let reason = flow
        .databases_registers
        .reports_excluded
        .first_mut()
        .ok_or_else(|| io::Error::other("no exclusion reason"))?;
    reason.reports = u64::MAX;
    assert!(
        flow.validate()
            .diagnostics
            .iter()
            .any(|item| item.code == "SF-PRISMA-037")
    );
    assert!(flow.build_scene().is_err());
    Ok(())
}

#[test]
fn malformed_recipe_graphs_cannot_reach_layout() -> Result<(), Box<dyn std::error::Error>> {
    for (pointer, replacement, code) in [
        ("/schema_version", json!("old"), "SF-RECIPE-001"),
        ("/nodes", json!([]), "SF-RECIPE-015"),
        ("/recipe_id", json!("../escape"), "SF-RECIPE-003"),
        ("/title_template", json!(" "), "SF-RECIPE-002"),
        ("/nodes/0/column", json!(u32::MAX), "SF-RECIPE-005"),
        ("/nodes/0/column_span", json!(0), "SF-RECIPE-005"),
        ("/nodes/0/label_template", json!(" "), "SF-RECIPE-006"),
        ("/edges/0/id", json!("invalid/id"), "SF-RECIPE-008"),
    ] {
        let mut value: Value = serde_json::from_slice(RECIPE)?;
        *value
            .pointer_mut(pointer)
            .ok_or_else(|| io::Error::other(format!("missing {pointer}")))? = replacement;
        let recipe: DiagramRecipe = serde_json::from_value(value)?;
        assert!(
            recipe
                .validate()
                .diagnostics
                .iter()
                .any(|item| item.code == code)
        );
        assert!(recipe.build_scene(&BTreeMap::new()).is_err());
    }
    Ok(())
}
