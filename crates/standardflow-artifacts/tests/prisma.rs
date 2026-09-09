//! Contract, arithmetic, rendering and accessibility tests for the four PRISMA 2020 variants.

use proptest::prelude::*;
use serde_json::Value;
use standardflow_artifacts::{
    DatabaseRegisterStream, ExclusionReason, IncludedCounts, PrismaError, PrismaFlow,
    PrismaTemplate, RenderFormat, parse_prisma_flow, render, render_scene_json, render_svg,
    render_text,
};

const NEW_DATABASES: &str =
    include_str!("../../../contracts/examples/prisma-flow/new-databases-registers.json");
const NEW_MIXED: &str = include_str!(
    "../../../contracts/examples/prisma-flow/new-databases-registers-other-sources.json"
);
const UPDATED_DATABASES: &str =
    include_str!("../../../contracts/examples/prisma-flow/updated-databases-registers.json");
const UPDATED_MIXED: &str = include_str!(
    "../../../contracts/examples/prisma-flow/updated-databases-registers-other-sources.json"
);

const fn fixtures() -> [&'static str; 4] {
    [NEW_DATABASES, NEW_MIXED, UPDATED_DATABASES, UPDATED_MIXED]
}

#[test]
fn all_four_prisma_templates_build_valid_scenes() -> Result<(), Box<dyn std::error::Error>> {
    for fixture in fixtures() {
        let flow = parse_prisma_flow(fixture.as_bytes())?;
        assert!(flow.validate().is_valid());
        let scene = flow.build_scene()?;
        assert!(scene.validate().is_valid());
        assert!(!scene.nodes.is_empty());
        assert!(!scene.edges.is_empty());
        assert_eq!(scene.nodes.len(), scene.reading_order.len());
    }
    Ok(())
}

#[test]
fn every_renderer_is_deterministic() -> Result<(), Box<dyn std::error::Error>> {
    for fixture in fixtures() {
        let scene = parse_prisma_flow(fixture.as_bytes())?.build_scene()?;
        for format in [
            RenderFormat::Svg,
            RenderFormat::Text,
            RenderFormat::SceneJson,
        ] {
            let first = render(&scene, format)?;
            let second = render(&scene, format)?;
            assert_eq!(first, second);
            assert!(!first.is_empty());
        }
    }
    Ok(())
}

#[test]
fn svg_has_a_complete_accessibility_surface() -> Result<(), Box<dyn std::error::Error>> {
    let scene = parse_prisma_flow(NEW_MIXED.as_bytes())?.build_scene()?;
    let svg = render_svg(&scene)?;
    assert!(svg.contains("role=\"img\""));
    assert!(svg.contains("<title id=\"standardflow-title\">"));
    assert!(svg.contains("<desc id=\"standardflow-description\">"));
    assert!(svg.contains("<metadata id=\"standardflow-text-equivalent\">"));
    assert!(svg.contains("role=\"list\""));
    assert!(svg.contains("role=\"listitem\""));
    assert!(svg.contains("aria-label="));
    Ok(())
}

#[test]
fn scene_json_and_text_preserve_semantics() -> Result<(), Box<dyn std::error::Error>> {
    let scene = parse_prisma_flow(UPDATED_MIXED.as_bytes())?.build_scene()?;
    let scene_json = render_scene_json(&scene)?;
    let parsed: Value = serde_json::from_str(&scene_json)?;
    assert_eq!(
        parsed.pointer("/schema_version"),
        Some(&Value::String(String::from(
            "dev.standardflow.scene-graph.v1"
        )))
    );
    let text = render_text(&scene)?;
    assert!(text.contains("Studies included in previous version"));
    assert!(text.contains("Total studies included in review"));
    Ok(())
}

#[test]
fn arithmetic_mismatch_fails_before_rendering() -> Result<(), Box<dyn std::error::Error>> {
    let mut value: Value = serde_json::from_str(NEW_DATABASES)?;
    let screened = value
        .pointer_mut("/databases_registers/records_screened")
        .ok_or_else(|| std::io::Error::other("records_screened fixture path is missing"))?;
    *screened = Value::from(119_u64);
    let flow: PrismaFlow = serde_json::from_value(value)?;
    assert!(matches!(
        flow.build_scene(),
        Err(PrismaError::Validation(_))
    ));
    Ok(())
}

proptest! {
    #[test]
    fn derived_database_stream_arithmetic_remains_valid(
        databases in 1_u64..1_000_000,
        registers in 0_u64..100_000,
        duplicate_candidate in 0_u64..10_000,
        automation_candidate in 0_u64..10_000,
        other_candidate in 0_u64..10_000,
        records_excluded_candidate in 0_u64..10_000,
        not_retrieved_candidate in 0_u64..1_000,
        reports_excluded_candidate in 0_u64..1_000,
    ) {
        let total = databases.saturating_add(registers);
        let duplicate_records_removed = duplicate_candidate.min(total);
        let after_duplicates = total - duplicate_records_removed;
        let records_marked_ineligible_by_automation = automation_candidate.min(after_duplicates);
        let after_automation = after_duplicates - records_marked_ineligible_by_automation;
        let records_removed_other_reasons = other_candidate.min(after_automation);
        let records_screened = after_automation - records_removed_other_reasons;
        let records_excluded = records_excluded_candidate.min(records_screened);
        let reports_sought = records_screened - records_excluded;
        let reports_not_retrieved = not_retrieved_candidate.min(reports_sought);
        let reports_assessed = reports_sought - reports_not_retrieved;
        let reports_excluded_count = reports_excluded_candidate.min(reports_assessed);
        let reports_included = reports_assessed - reports_excluded_count;
        let reports_excluded = if reports_excluded_count == 0 {
            Vec::new()
        } else {
            vec![ExclusionReason {
                reason: String::from("Fixture exclusion"),
                reports: reports_excluded_count,
            }]
        };
        let flow = PrismaFlow {
            schema_version: String::from("dev.standardflow.prisma-flow.v1"),
            review_id: String::from("property-fixture"),
            template: PrismaTemplate::NewDatabasesRegisters,
            databases_registers: DatabaseRegisterStream {
                databases,
                registers,
                duplicate_records_removed,
                records_marked_ineligible_by_automation,
                records_removed_other_reasons,
                records_screened,
                records_excluded,
                reports_sought,
                reports_not_retrieved,
                reports_assessed,
                reports_excluded,
                reports_included,
            },
            other_methods: None,
            previous_review: None,
            new_included: IncludedCounts {
                studies: reports_included,
                reports: reports_included,
            },
            total_included: IncludedCounts {
                studies: reports_included,
                reports: reports_included,
            },
        };
        prop_assert!(flow.validate().is_valid());
    }
}
