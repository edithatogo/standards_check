//! Negative contract cases for provenance, rights and evidence admission.

use std::io;

use serde_json::{Value, json};
use standardflow_core::{EvidenceLevel, PackError, StandardPack, parse_pack};

const FIXTURE: &str = include_str!("../../../contracts/examples/minimal-standard-pack.v1.json");

fn changed(pointer: &str, replacement: Value) -> Result<Value, Box<dyn std::error::Error>> {
    let mut value: Value = serde_json::from_str(FIXTURE)?;
    *value
        .pointer_mut(pointer)
        .ok_or_else(|| io::Error::other(format!("fixture lacks {pointer}")))? = replacement;
    Ok(value)
}

fn rejects(value: Value, code: &str) -> Result<(), Box<dyn std::error::Error>> {
    // Both entry points must refuse to turn invalid semantics into canonical bytes.
    let encoded = serde_json::to_vec(&value)?;
    let decoded: StandardPack = serde_json::from_value(value)?;
    assert!(decoded.canonical_bytes().is_err());
    let result = parse_pack(&encoded);
    assert!(
        matches!(result, Err(PackError::Validation(report))
        if report.diagnostics.iter().any(|item| item.code == code)),
        "missing {code}"
    );
    Ok(())
}

#[test]
fn blank_or_unbound_source_claims_cannot_be_canonicalized() -> Result<(), Box<dyn std::error::Error>>
{
    for (pointer, value, code) in [
        ("/schema_version", "unrecognized", "SF-PACK-003"),
        ("/version", " \t", "SF-PACK-001"),
        ("/title", "\n", "SF-PACK-002"),
        ("/authority/publisher", " ", "SF-SOURCE-001"),
        ("/authority/source_sha256", "ABCDEF", "SF-SOURCE-004"),
        ("/authority/retrieved_at", "2025-02-29", "SF-SOURCE-003"),
        ("/requirements/0/section", " ", "SF-REQ-003"),
        ("/requirements/0/normalized_requirement", " ", "SF-REQ-004"),
        ("/requirements/0/source_anchor", " ", "SF-REQ-005"),
        ("/requirements/0/display_number", " ", "SF-REQ-008"),
        ("/requirements/0/guidance", " ", "SF-REQ-010"),
        ("/requirements/0/verbatim_text", " ", "SF-RIGHTS-006"),
    ] {
        rejects(changed(pointer, json!(value))?, code)?;
    }
    Ok(())
}

#[test]
fn verification_requires_accountability_without_promoting_imports()
-> Result<(), Box<dyn std::error::Error>> {
    for status in ["source_reconciled", "externally_validated"] {
        let mut value = changed("/verification/status", json!(status))?;
        parse_pack(&serde_json::to_vec(&value)?)?;
        for (member, code) in [
            ("verified_by", "SF-VERIFY-004"),
            ("evidence", "SF-VERIFY-005"),
        ] {
            let mut invalid = value.clone();
            *invalid
                .pointer_mut(&format!("/verification/{member}"))
                .ok_or_else(|| io::Error::other("missing verification member"))? = json!([]);
            rejects(invalid, code)?;
        }
        *value
            .pointer_mut("/verification/status")
            .ok_or_else(|| io::Error::other("missing verification status"))? =
            json!("imported_unverified");
        rejects(value, "SF-VERIFY-002")?;
    }
    for (pointer, code) in [
        ("/verification/verified_by", "SF-VERIFY-006"),
        ("/verification/evidence", "SF-VERIFY-007"),
        ("/requirements/0/evidence_expectations", "SF-REQ-006"),
    ] {
        for values in [json!([" "]), json!(["evidence", "evidence"])] {
            rejects(changed(pointer, values)?, code)?;
        }
    }
    rejects(changed("/requirements", json!([]))?, "SF-REQ-001")?;
    rejects(
        changed("/requirements/0/evidence_expectations", json!([]))?,
        "SF-REQ-007",
    )?;
    Ok(())
}

#[test]
fn explicit_item_rights_cannot_borrow_pack_clearance() -> Result<(), Box<dyn std::error::Error>> {
    let fixture: Value = serde_json::from_str(FIXTURE)?;
    let rights = fixture
        .get("rights")
        .ok_or_else(|| io::Error::other("missing rights"))?;
    // Explicit rights have their own validation, including redistribution terms.
    let valid = changed("/requirements/0/rights", rights.clone())?;
    parse_pack(&serde_json::to_vec(&valid)?)?;
    for (pointer, replacement, code) in [
        ("/rights/status", json!("review_required"), "SF-RIGHTS-007"),
        ("/rights/redistribution", json!(" "), "SF-RIGHTS-001"),
        ("/rights/spdx", json!(" "), "SF-RIGHTS-002"),
        ("/rights/license_url", json!(" "), "SF-RIGHTS-002"),
        ("/rights/attribution", json!(" "), "SF-RIGHTS-002"),
        ("/rights/spdx", json!("MIT"), "SF-RIGHTS-004"),
        (
            "/requirements/0/rights/inherit_from_pack",
            json!(false),
            "SF-RIGHTS-005",
        ),
    ] {
        rejects(changed(pointer, replacement)?, code)?;
    }
    let mut uncleared = rights.clone();
    *uncleared
        .get_mut("status")
        .ok_or_else(|| io::Error::other("missing rights status"))? = json!("link_only");
    rejects(
        changed("/requirements/0/rights", uncleared)?,
        "SF-RIGHTS-007",
    )?;
    let mut missing_license = changed("/rights/spdx", Value::Null)?;
    *missing_license
        .pointer_mut("/rights/license_url")
        .ok_or_else(|| io::Error::other("missing license URL"))? = Value::Null;
    rejects(missing_license, "SF-RIGHTS-003")?;
    Ok(())
}

#[test]
fn duplicate_display_numbers_warn_but_stable_identity_conflicts_fail()
-> Result<(), Box<dyn std::error::Error>> {
    let fixture: Value = serde_json::from_str(FIXTURE)?;
    let original = fixture
        .pointer("/requirements/0")
        .ok_or_else(|| io::Error::other("missing requirement"))?;
    rejects(
        changed("/requirements", json!([original, original]))?,
        "SF-REQ-002",
    )?;
    let mut second = original.clone();
    *second
        .get_mut("id")
        .ok_or_else(|| io::Error::other("missing id"))? = json!("EXAMPLE-2");
    let valid = changed("/requirements", json!([original, second]))?;
    let result = parse_pack(&serde_json::to_vec(&valid)?)?;
    assert_eq!(result.report().error_count(), 0);
    assert_eq!(result.report().warning_count(), 1);
    assert_eq!(result.into_pack().requirements.len(), 2);
    rejects(
        changed(
            "/relationships",
            json!([
                {"predicate":"extends", "target":"example/minimal-reporting-standard"}
            ]),
        )?,
        "SF-REL-001",
    )?;
    let relation = json!({"predicate":"use_with", "target":"example/other-standard"});
    rejects(
        changed("/relationships", json!([relation, relation]))?,
        "SF-REL-002",
    )?;
    Ok(())
}

#[test]
fn lower_evidence_levels_never_satisfy_stronger_claims() {
    let levels = [
        EvidenceLevel::Contracted,
        EvidenceLevel::SourceVerified,
        EvidenceLevel::CompilerVerified,
        EvidenceLevel::FixtureProven,
        EvidenceLevel::LiveProven,
        EvidenceLevel::ExternallyValidated,
        EvidenceLevel::PubliclyAccepted,
    ];
    for (observed_index, observed) in levels.iter().enumerate() {
        for (required_index, required) in levels.iter().enumerate() {
            assert_eq!(
                observed.satisfies(*required),
                observed_index >= required_index
            );
        }
    }
}
