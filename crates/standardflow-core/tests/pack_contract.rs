//! Contract and property tests for Canonical Standard Packs.

use std::io;

use proptest::prelude::*;
use serde_json::Value;
use standardflow_core::{PackError, PackId, RequirementId, parse_pack, sha256_hex};

const MINIMAL_PACK: &str =
    include_str!("../../../contracts/examples/minimal-standard-pack.v1.json");
const PRISMA_PACK: &str = include_str!("../../../packs/org.prisma/prisma/2020/pack.json");

#[test]
fn minimal_pack_round_trips_canonically() -> Result<(), Box<dyn std::error::Error>> {
    let validated = parse_pack(MINIMAL_PACK.as_bytes())?;
    let first = validated.pack().canonical_bytes()?;
    let reparsed = parse_pack(&first)?;
    let second = reparsed.pack().canonical_bytes()?;
    assert_eq!(first, second);
    assert_eq!(sha256_hex(&first), reparsed.pack().canonical_sha256()?);
    Ok(())
}

#[test]
fn prisma_reference_pack_has_stable_items_and_explicit_warning()
-> Result<(), Box<dyn std::error::Error>> {
    let validated = parse_pack(PRISMA_PACK.as_bytes())?;
    assert_eq!(validated.pack().requirements.len(), 27);
    assert_eq!(validated.report().error_count(), 0);
    assert_eq!(validated.report().warning_count(), 1);
    assert_eq!(validated.pack().pack_id.as_str(), "org.prisma/prisma/2020");
    Ok(())
}

#[test]
fn reordered_json_has_the_same_canonical_digest() -> Result<(), Box<dyn std::error::Error>> {
    let value: Value = serde_json::from_str(MINIMAL_PACK)?;
    let object = value
        .as_object()
        .ok_or_else(|| io::Error::other("pack fixture must be an object"))?;
    let mut reverse = object.iter().collect::<Vec<_>>();
    reverse.reverse();
    let reversed = reverse
        .into_iter()
        .map(|(key, value)| (key.clone(), value.clone()))
        .collect::<serde_json::Map<_, _>>();
    let encoded = serde_json::to_vec(&Value::Object(reversed))?;
    let reparsed = parse_pack(&encoded)?;
    let original = parse_pack(MINIMAL_PACK.as_bytes())?;
    assert_eq!(
        original.pack().canonical_sha256()?,
        reparsed.pack().canonical_sha256()?
    );
    Ok(())
}

#[test]
fn non_cleared_verbatim_text_is_rejected() -> Result<(), Box<dyn std::error::Error>> {
    let mut value: Value = serde_json::from_str(MINIMAL_PACK)?;
    let rights = value
        .pointer_mut("/rights/status")
        .ok_or_else(|| io::Error::other("fixture rights status is missing"))?;
    *rights = Value::String(String::from("link_only"));
    let result = parse_pack(&serde_json::to_vec(&value)?);
    assert!(matches!(result, Err(PackError::Validation(_))));
    Ok(())
}

#[test]
fn required_nullable_members_must_be_present() -> Result<(), Box<dyn std::error::Error>> {
    for (parent, member) in [
        ("/verification", "verified_at"),
        ("/verification", "verified_by"),
        ("/verification", "evidence"),
        ("/rights", "spdx"),
        ("/rights", "license_url"),
        ("/rights", "attribution"),
        ("/requirements/0", "display_number"),
        ("/requirements/0", "verbatim_text"),
        ("/requirements/0", "guidance"),
        ("/requirements/0", "evidence_expectations"),
    ] {
        let mut value: Value = serde_json::from_str(PRISMA_PACK)?;
        let object = value
            .pointer_mut(parent)
            .and_then(Value::as_object_mut)
            .ok_or_else(|| io::Error::other("fixture member parent is missing"))?;
        object.remove(member);
        assert!(
            matches!(
                parse_pack(&serde_json::to_vec(&value)?),
                Err(PackError::Json(_))
            ),
            "missing {parent}/{member} must fail decoding"
        );
    }
    Ok(())
}

#[test]
fn explicit_null_remains_valid_for_nullable_members() -> Result<(), Box<dyn std::error::Error>> {
    let mut value: Value = serde_json::from_str(PRISMA_PACK)?;
    for pointer in [
        "/verification/verified_at",
        "/rights/license_url",
        "/requirements/0/display_number",
        "/requirements/0/verbatim_text",
        "/requirements/0/guidance",
    ] {
        let member = value
            .pointer_mut(pointer)
            .ok_or_else(|| io::Error::other("fixture nullable member is missing"))?;
        *member = Value::Null;
    }
    parse_pack(&serde_json::to_vec(&value)?)?;
    Ok(())
}

#[test]
fn pack_ids_match_the_declared_schema() {
    for invalid in [
        "single",
        "_org/family",
        "org/_family",
        "org/.family",
        "org/-family",
    ] {
        assert!(PackId::parse(invalid).is_err(), "accepted {invalid}");
    }
    assert!(PackId::parse("org.example/standard-1/2026").is_ok());
}

#[test]
fn source_uris_require_a_valid_supported_absolute_uri() -> Result<(), Box<dyn std::error::Error>> {
    for source in [
        "https://",
        "https:///example.invalid",
        "https:example.invalid",
        "https://example.invalid/%zz",
        "https://example.invalid/a b",
        "https://example.invalid/\\wrong",
        "urn:",
        "urn:example:",
        "urn:example",
        "relative/source.pdf",
        "ftp://example.invalid/source.pdf",
    ] {
        let mut value: Value = serde_json::from_str(MINIMAL_PACK)?;
        let member = value
            .pointer_mut("/authority/source_url")
            .ok_or_else(|| io::Error::other("fixture source URL is missing"))?;
        *member = Value::String(source.to_owned());
        assert!(
            matches!(
                parse_pack(&serde_json::to_vec(&value)?),
                Err(PackError::Validation(_))
            ),
            "accepted malformed or unsupported URI {source}"
        );
    }
    for source in [
        "https://example.invalid/source.pdf?version=1#section",
        "http://[::1]:8080/source.pdf",
        "urn:example:standard-v1",
    ] {
        let mut value: Value = serde_json::from_str(MINIMAL_PACK)?;
        let member = value
            .pointer_mut("/authority/source_url")
            .ok_or_else(|| io::Error::other("fixture source URL is missing"))?;
        *member = Value::String(source.to_owned());
        parse_pack(&serde_json::to_vec(&value)?)?;
    }
    Ok(())
}

#[test]
fn licence_uris_and_dates_obey_the_wire_contract() -> Result<(), Box<dyn std::error::Error>> {
    for (pointer, invalid) in [
        ("/rights/license_url", "https://"),
        ("/authority/retrieved_at", "0000-01-01"),
        ("/verification/verified_at", "0000-01-01"),
    ] {
        let mut value: Value = serde_json::from_str(MINIMAL_PACK)?;
        let member = value
            .pointer_mut(pointer)
            .ok_or_else(|| io::Error::other("fixture member is missing"))?;
        *member = Value::String(invalid.to_owned());
        assert!(
            matches!(
                parse_pack(&serde_json::to_vec(&value)?),
                Err(PackError::Validation(_))
            ),
            "accepted invalid value at {pointer}"
        );
    }
    Ok(())
}

proptest! {
    #[test]
    fn valid_requirement_identifiers_round_trip(
        first in "[A-Za-z0-9]",
        rest in "[A-Za-z0-9._:-]{0,48}",
    ) {
        let value = format!("{first}{rest}");
        let parsed = RequirementId::parse(&value);
        prop_assert!(parsed.is_ok());
        if let Ok(identifier) = parsed {
            prop_assert_eq!(identifier.as_str(), value.as_str());
        }
    }

    #[test]
    fn portable_pack_ids_round_trip(
        namespace in "[a-z0-9][a-z0-9._-]{0,16}",
        family in "[a-z0-9][a-z0-9._-]{0,16}",
        edition in "[a-z0-9][a-z0-9._-]{0,16}",
    ) {
        let value = format!("{namespace}/{family}/{edition}");
        let parsed = PackId::parse(&value);
        prop_assert!(parsed.is_ok());
        if let Ok(identifier) = parsed {
            prop_assert_eq!(identifier.as_str(), value.as_str());
        }
    }
}
