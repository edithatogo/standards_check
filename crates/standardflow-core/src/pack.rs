//! Canonical Standard Pack data model and semantic validation.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt;
use std::path::Path;

use serde::de::Error as DeError;
use serde::{Deserialize, Deserializer, Serialize};
use thiserror::Error;

use crate::canonical::{CanonicalError, canonical_json, sha256_hex};
use crate::diagnostic::{Diagnostic, ValidationReport};

/// Maximum accepted `pack.json` size for file-based loading.
pub const MAX_PACK_JSON_BYTES: u64 = 16 * 1024 * 1024;

/// Stable pack identifier.
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(transparent)]
pub struct PackId(String);

impl PackId {
    /// Parses a portable lower-case path-like identifier.
    ///
    /// # Errors
    ///
    /// Returns [`IdentifierError`] for an empty, absolute, traversal-capable or
    /// non-portable identifier.
    pub fn parse(value: &str) -> Result<Self, IdentifierError> {
        let portable = !value.is_empty()
            && !value.starts_with('/')
            && !value.ends_with('/')
            && value.bytes().all(|byte| {
                byte.is_ascii_lowercase()
                    || byte.is_ascii_digit()
                    || matches!(byte, b'.' | b'_' | b'/' | b'-')
            })
            && value
                .split('/')
                .all(|segment| !segment.is_empty() && segment != "." && segment != "..");
        if portable {
            Ok(Self(value.to_owned()))
        } else {
            Err(IdentifierError::Pack)
        }
    }

    /// Returns the identifier text.
    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl<'de> Deserialize<'de> for PackId {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value = String::deserialize(deserializer)?;
        Self::parse(&value).map_err(D::Error::custom)
    }
}

/// Stable requirement identifier independent of display numbering.
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(transparent)]
pub struct RequirementId(String);

impl RequirementId {
    /// Parses a portable requirement identifier.
    ///
    /// # Errors
    ///
    /// Returns [`IdentifierError`] if the value is empty, does not begin with an
    /// ASCII alphanumeric character, or contains unsupported characters.
    pub fn parse(value: &str) -> Result<Self, IdentifierError> {
        let mut bytes = value.bytes();
        let portable = bytes
            .next()
            .is_some_and(|first| first.is_ascii_alphanumeric())
            && bytes.all(|byte| {
                byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b':' | b'-')
            });
        if portable {
            Ok(Self(value.to_owned()))
        } else {
            Err(IdentifierError::Requirement)
        }
    }

    /// Returns the identifier text.
    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl<'de> Deserialize<'de> for RequirementId {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value = String::deserialize(deserializer)?;
        Self::parse(&value).map_err(D::Error::custom)
    }
}

/// Identifier validation error.
#[derive(Clone, Copy, Debug, Eq, Error, PartialEq)]
pub enum IdentifierError {
    /// A pack identifier is unsafe or not portable.
    #[error(
        "pack identifier must be a relative lower-case portable path without empty, '.' or '..' segments"
    )]
    Pack,
    /// A requirement identifier is unsafe or not portable.
    #[error(
        "requirement identifier must begin with an ASCII letter or digit and contain only ASCII letters, digits, '.', '_', ':' or '-'"
    )]
    Requirement,
}

/// Standard category.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum StandardKind {
    /// Reporting guideline.
    Reporting,
    /// Protocol guideline.
    Protocol,
    /// Research-conduct guideline.
    Conduct,
    /// Critical-appraisal instrument.
    Appraisal,
    /// Risk-of-bias instrument.
    RiskOfBias,
    /// Regulatory requirement.
    Regulatory,
    /// Metadata standard.
    Metadata,
    /// Journal, funder, registry or institutional profile.
    Profile,
}

/// Source authority and immutable retrieval evidence.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SourceAuthority {
    /// Owning or publishing organization.
    pub publisher: String,
    /// Canonical source URL or URN.
    pub source_url: String,
    /// ISO date on which the source was retrieved.
    pub retrieved_at: String,
    /// SHA-256 of the retrieved source bytes.
    pub source_sha256: String,
}

/// Pack transcription-verification status.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum VerificationStatus {
    /// Imported from a legacy representation and not yet reconciled to the source.
    ImportedUnverified,
    /// Reconciled item-by-item against the authoritative source.
    SourceReconciled,
    /// Independently evaluated beyond source reconciliation.
    ExternallyValidated,
}

/// Evidence supporting a pack's transcription status.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Verification {
    /// Current verification status.
    pub status: VerificationStatus,
    /// Date of the completed verification, when applicable.
    pub verified_at: Option<String>,
    /// People or accountable roles that performed the verification.
    #[serde(default)]
    pub verified_by: Vec<String>,
    /// Stable evidence references.
    #[serde(default)]
    pub evidence: Vec<String>,
}

/// Rights status for a pack or one requirement.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum RightsStatus {
    /// Reproduction and transformation are cleared under the recorded terms.
    Cleared,
    /// Only a link and metadata may be redistributed.
    LinkOnly,
    /// Local normalized requirements may be stored, but source text may not.
    ParaphraseOnly,
    /// Rights require review before redistribution.
    ReviewRequired,
}

/// Machine-actionable rights statement.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Rights {
    /// Rights status.
    pub status: RightsStatus,
    /// SPDX expression when one accurately represents the terms.
    pub spdx: Option<String>,
    /// Canonical licence or terms URL.
    pub license_url: Option<String>,
    /// Required attribution text.
    pub attribution: Option<String>,
    /// Plain-language redistribution rule.
    pub redistribution: String,
}

/// Explicit marker that a requirement inherits pack rights.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct InheritedRights {
    /// Must be true.
    pub inherit_from_pack: bool,
}

/// Requirement-level rights, either inherited or explicit.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(untagged)]
pub enum RequirementRights {
    /// Inherit all pack-level terms.
    Inherited(InheritedRights),
    /// Override with an item-specific statement.
    Explicit(Rights),
}

/// Relationship between standards packs.
#[derive(Clone, Copy, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum RelationshipPredicate {
    /// This pack is an edition of a standards family.
    EditionOf,
    /// This pack supersedes another edition.
    Supersedes,
    /// This pack extends another standard.
    Extends,
    /// This pack should be used alongside another standard.
    UseWith,
    /// This pack is a profile of another pack.
    ProfileOf,
    /// This pack cannot be used with another pack.
    IncompatibleWith,
    /// This pack is semantically equivalent to another pack.
    EquivalentTo,
    /// This pack partially maps to another pack.
    PartiallyMapsTo,
    /// This pack is a translation of another pack.
    TranslationOf,
}

/// One standards relationship.
#[derive(Clone, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Relationship {
    /// Relationship predicate.
    pub predicate: RelationshipPredicate,
    /// Target pack identifier.
    pub target: PackId,
}

/// One stable standards requirement.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Requirement {
    /// Stable semantic identifier.
    pub id: RequirementId,
    /// Source-facing display number.
    pub display_number: Option<String>,
    /// Human section label.
    pub section: String,
    /// Authoritative text where redistribution is permitted.
    pub verbatim_text: Option<String>,
    /// Machine-oriented normalized requirement.
    pub normalized_requirement: String,
    /// Explanatory guidance distinct from the requirement.
    pub guidance: Option<String>,
    /// Stable source locator.
    pub source_anchor: String,
    /// Rights for this item.
    pub rights: RequirementRights,
    /// Types of evidence that can support assessment.
    #[serde(default)]
    pub evidence_expectations: Vec<String>,
}

/// Canonical Standard Pack source document.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct StandardPack {
    /// Contract version.
    pub schema_version: String,
    /// Stable pack identifier.
    pub pack_id: PackId,
    /// Pack release version.
    pub version: String,
    /// Standard category.
    pub kind: StandardKind,
    /// Display title.
    pub title: String,
    /// Source authority.
    pub authority: SourceAuthority,
    /// Transcription verification.
    pub verification: Verification,
    /// Default pack rights.
    pub rights: Rights,
    /// Relationships to other packs.
    #[serde(default)]
    pub relationships: Vec<Relationship>,
    /// Stable requirements.
    pub requirements: Vec<Requirement>,
}

impl StandardPack {
    /// Performs deterministic semantic validation.
    #[must_use]
    pub fn validate(&self) -> ValidationReport {
        let mut report = ValidationReport::default();
        validate_non_empty(&self.version, "/version", "SF-PACK-001", &mut report);
        validate_non_empty(&self.title, "/title", "SF-PACK-002", &mut report);
        if self.schema_version != "dev.standardflow.standard-pack.v1" {
            report.push(Diagnostic::error(
                "SF-PACK-003",
                "/schema_version",
                "schema_version must be dev.standardflow.standard-pack.v1",
            ));
        }
        validate_source_authority(&self.authority, &mut report);
        validate_verification(&self.verification, &mut report);
        validate_rights(&self.rights, "/rights", &mut report);
        validate_relationships(self, &mut report);
        validate_requirements(self, &mut report);
        report
    }

    /// Produces canonical JSON bytes after successful semantic validation.
    ///
    /// # Errors
    ///
    /// Returns [`PackError::Validation`] when semantic errors exist or a canonical
    /// encoding error otherwise.
    pub fn canonical_bytes(&self) -> Result<Vec<u8>, PackError> {
        let report = self.validate();
        if !report.is_valid() {
            return Err(PackError::Validation(report));
        }
        canonical_json(self).map_err(PackError::Canonical)
    }

    /// Returns the SHA-256 of canonical JSON.
    ///
    /// # Errors
    ///
    /// Returns the same errors as [`Self::canonical_bytes`].
    pub fn canonical_sha256(&self) -> Result<String, PackError> {
        self.canonical_bytes().map(|bytes| sha256_hex(&bytes))
    }
}

/// A semantically valid pack together with non-blocking warnings.
#[derive(Clone, Debug)]
pub struct ValidatedPack {
    pack: StandardPack,
    report: ValidationReport,
}

impl ValidatedPack {
    /// Returns the validated pack.
    #[must_use]
    pub const fn pack(&self) -> &StandardPack {
        &self.pack
    }

    /// Returns warnings retained during validation.
    #[must_use]
    pub const fn report(&self) -> &ValidationReport {
        &self.report
    }

    /// Consumes the wrapper and returns the pack.
    #[must_use]
    pub fn into_pack(self) -> StandardPack {
        self.pack
    }
}

/// Pack parsing or semantic-validation failure.
#[derive(Debug, Error)]
pub enum PackError {
    /// JSON could not be decoded into the strict pack model.
    #[error("pack JSON is invalid: {0}")]
    Json(#[from] serde_json::Error),
    /// Semantic validation failed.
    #[error("pack validation failed with {} error(s)", .0.error_count())]
    Validation(ValidationReport),
    /// Canonical JSON encoding failed.
    #[error(transparent)]
    Canonical(#[from] CanonicalError),
    /// File-system loading failed.
    #[error("cannot read {path}: {source}")]
    Io {
        /// Affected path.
        path: String,
        /// Underlying error.
        #[source]
        source: std::io::Error,
    },
    /// File loading was rejected by a security limit.
    #[error("pack file {path} exceeds the {limit}-byte limit")]
    TooLarge {
        /// Affected path.
        path: String,
        /// Configured byte limit.
        limit: u64,
    },
    /// Symlinked pack files are rejected.
    #[error("pack file {0} must not be a symbolic link")]
    Symlink(String),
}

/// Parses and semantically validates a pack.
///
/// # Errors
///
/// Returns [`PackError`] when JSON decoding or semantic validation fails.
pub fn parse_pack(bytes: &[u8]) -> Result<ValidatedPack, PackError> {
    let pack: StandardPack = serde_json::from_slice(bytes)?;
    let report = pack.validate();
    if report.is_valid() {
        Ok(ValidatedPack { pack, report })
    } else {
        Err(PackError::Validation(report))
    }
}

/// Loads and validates one `pack.json` without following a symlink.
///
/// # Errors
///
/// Returns [`PackError`] for file-system, size, JSON or semantic failures.
pub fn load_pack(path: &Path) -> Result<ValidatedPack, PackError> {
    let metadata = std::fs::symlink_metadata(path).map_err(|source| PackError::Io {
        path: path.display().to_string(),
        source,
    })?;
    if metadata.file_type().is_symlink() {
        return Err(PackError::Symlink(path.display().to_string()));
    }
    if metadata.len() > MAX_PACK_JSON_BYTES {
        return Err(PackError::TooLarge {
            path: path.display().to_string(),
            limit: MAX_PACK_JSON_BYTES,
        });
    }
    let bytes = std::fs::read(path).map_err(|source| PackError::Io {
        path: path.display().to_string(),
        source,
    })?;
    parse_pack(&bytes)
}

fn validate_source_authority(authority: &SourceAuthority, report: &mut ValidationReport) {
    validate_non_empty(
        &authority.publisher,
        "/authority/publisher",
        "SF-SOURCE-001",
        report,
    );
    if !is_absolute_source(&authority.source_url) {
        report.push(Diagnostic::error(
            "SF-SOURCE-002",
            "/authority/source_url",
            "source_url must be an absolute http, https or urn URI",
        ));
    }
    if !is_iso_date(&authority.retrieved_at) {
        report.push(Diagnostic::error(
            "SF-SOURCE-003",
            "/authority/retrieved_at",
            "retrieved_at must be a valid YYYY-MM-DD date",
        ));
    }
    if !is_sha256(&authority.source_sha256) {
        report.push(Diagnostic::error(
            "SF-SOURCE-004",
            "/authority/source_sha256",
            "source_sha256 must contain 64 lower-case hexadecimal characters",
        ));
    }
}

fn validate_verification(verification: &Verification, report: &mut ValidationReport) {
    match verification.status {
        VerificationStatus::ImportedUnverified => {
            report.push(Diagnostic::warning(
                "SF-VERIFY-001",
                "/verification/status",
                "legacy transcription has not yet been reconciled item-by-item to the source",
            ));
            if verification.verified_at.is_some() || !verification.verified_by.is_empty() {
                report.push(Diagnostic::error(
                    "SF-VERIFY-002",
                    "/verification",
                    "imported_unverified packs must not carry verified_at or verified_by claims",
                ));
            }
        }
        VerificationStatus::SourceReconciled | VerificationStatus::ExternallyValidated => {
            if verification
                .verified_at
                .as_deref()
                .is_none_or(|value| !is_iso_date(value))
            {
                report.push(Diagnostic::error(
                    "SF-VERIFY-003",
                    "/verification/verified_at",
                    "verified_at is required and must be a valid YYYY-MM-DD date",
                ));
            }
            if verification.verified_by.is_empty() {
                report.push(Diagnostic::error(
                    "SF-VERIFY-004",
                    "/verification/verified_by",
                    "at least one accountable verifier is required",
                ));
            }
            if verification.evidence.is_empty() {
                report.push(Diagnostic::error(
                    "SF-VERIFY-005",
                    "/verification/evidence",
                    "at least one stable verification-evidence reference is required",
                ));
            }
        }
    }
    validate_unique_non_empty(
        &verification.verified_by,
        "/verification/verified_by",
        "SF-VERIFY-006",
        report,
    );
    validate_unique_non_empty(
        &verification.evidence,
        "/verification/evidence",
        "SF-VERIFY-007",
        report,
    );
}

fn validate_rights(rights: &Rights, path: &str, report: &mut ValidationReport) {
    validate_non_empty(
        &rights.redistribution,
        &format!("{path}/redistribution"),
        "SF-RIGHTS-001",
        report,
    );
    for (field, value) in [
        ("spdx", rights.spdx.as_deref()),
        ("license_url", rights.license_url.as_deref()),
        ("attribution", rights.attribution.as_deref()),
    ] {
        if value.is_some_and(|item| item.trim().is_empty()) {
            report.push(Diagnostic::error(
                "SF-RIGHTS-002",
                format!("{path}/{field}"),
                "optional rights fields must be omitted rather than blank",
            ));
        }
    }
    if rights.status == RightsStatus::Cleared {
        let is_cc0 = rights.spdx.as_deref() == Some("CC0-1.0");
        if rights.spdx.is_none() && rights.license_url.is_none() {
            report.push(Diagnostic::error(
                "SF-RIGHTS-003",
                path,
                "cleared rights require an SPDX expression or licence URL",
            ));
        }
        if !is_cc0 && rights.attribution.is_none() {
            report.push(Diagnostic::error(
                "SF-RIGHTS-004",
                format!("{path}/attribution"),
                "cleared non-CC0 content requires explicit attribution",
            ));
        }
    }
}

fn validate_relationships(pack: &StandardPack, report: &mut ValidationReport) {
    let mut seen = BTreeSet::new();
    for (index, relationship) in pack.relationships.iter().enumerate() {
        let path = format!("/relationships/{index}");
        if relationship.target == pack.pack_id {
            report.push(Diagnostic::error(
                "SF-REL-001",
                format!("{path}/target"),
                "a pack must not relate to itself",
            ));
        }
        if !seen.insert((relationship.predicate, relationship.target.clone())) {
            report.push(Diagnostic::error(
                "SF-REL-002",
                path,
                "duplicate standards relationship",
            ));
        }
    }
}

fn validate_requirements(pack: &StandardPack, report: &mut ValidationReport) {
    if pack.requirements.is_empty() {
        report.push(Diagnostic::error(
            "SF-REQ-001",
            "/requirements",
            "a pack must contain at least one requirement",
        ));
        return;
    }
    let mut ids = BTreeSet::new();
    let mut display_numbers: BTreeMap<&str, usize> = BTreeMap::new();
    for (index, requirement) in pack.requirements.iter().enumerate() {
        let path = format!("/requirements/{index}");
        if !ids.insert(requirement.id.clone()) {
            report.push(Diagnostic::error(
                "SF-REQ-002",
                format!("{path}/id"),
                "duplicate requirement identifier",
            ));
        }
        validate_non_empty(
            &requirement.section,
            &format!("{path}/section"),
            "SF-REQ-003",
            report,
        );
        validate_non_empty(
            &requirement.normalized_requirement,
            &format!("{path}/normalized_requirement"),
            "SF-REQ-004",
            report,
        );
        validate_non_empty(
            &requirement.source_anchor,
            &format!("{path}/source_anchor"),
            "SF-REQ-005",
            report,
        );
        validate_unique_non_empty(
            &requirement.evidence_expectations,
            &format!("{path}/evidence_expectations"),
            "SF-REQ-006",
            report,
        );
        if requirement.evidence_expectations.is_empty() {
            report.push(Diagnostic::error(
                "SF-REQ-007",
                format!("{path}/evidence_expectations"),
                "at least one evidence expectation is required",
            ));
        }
        if requirement
            .display_number
            .as_deref()
            .is_some_and(|value| value.trim().is_empty())
        {
            report.push(Diagnostic::error(
                "SF-REQ-008",
                format!("{path}/display_number"),
                "display_number must be omitted rather than blank",
            ));
        }
        if let Some(number) = requirement.display_number.as_deref()
            && let Some(previous) = display_numbers.insert(number, index)
        {
            report.push(Diagnostic::warning(
                "SF-REQ-009",
                format!("{path}/display_number"),
                format!("display number duplicates requirement index {previous}"),
            ));
        }
        if requirement
            .guidance
            .as_deref()
            .is_some_and(|value| value.trim().is_empty())
        {
            report.push(Diagnostic::error(
                "SF-REQ-010",
                format!("{path}/guidance"),
                "guidance must be omitted rather than blank",
            ));
        }
        validate_requirement_rights(pack, requirement, &path, report);
    }
}

fn validate_requirement_rights(
    pack: &StandardPack,
    requirement: &Requirement,
    path: &str,
    report: &mut ValidationReport,
) {
    let effective_rights = match &requirement.rights {
        RequirementRights::Inherited(inherited) => {
            if !inherited.inherit_from_pack {
                report.push(Diagnostic::error(
                    "SF-RIGHTS-005",
                    format!("{path}/rights/inherit_from_pack"),
                    "inherit_from_pack must be true",
                ));
            }
            &pack.rights
        }
        RequirementRights::Explicit(rights) => {
            validate_rights(rights, &format!("{path}/rights"), report);
            rights
        }
    };

    if let Some(verbatim) = requirement.verbatim_text.as_deref() {
        if verbatim.trim().is_empty() {
            report.push(Diagnostic::error(
                "SF-RIGHTS-006",
                format!("{path}/verbatim_text"),
                "verbatim_text must be omitted rather than blank",
            ));
        }
        if effective_rights.status != RightsStatus::Cleared {
            report.push(Diagnostic::error(
                "SF-RIGHTS-007",
                format!("{path}/verbatim_text"),
                "verbatim text is prohibited unless effective item rights are cleared",
            ));
        }
    }
}

fn validate_non_empty(value: &str, path: &str, code: &'static str, report: &mut ValidationReport) {
    if value.trim().is_empty() {
        report.push(Diagnostic::error(code, path, "value must not be blank"));
    }
}

fn validate_unique_non_empty(
    values: &[String],
    path: &str,
    code: &'static str,
    report: &mut ValidationReport,
) {
    let mut seen = BTreeSet::new();
    for (index, value) in values.iter().enumerate() {
        if value.trim().is_empty() {
            report.push(Diagnostic::error(
                code,
                format!("{path}/{index}"),
                "value must not be blank",
            ));
        } else if !seen.insert(value.as_str()) {
            report.push(Diagnostic::error(
                code,
                format!("{path}/{index}"),
                "duplicate value",
            ));
        }
    }
}

fn is_sha256(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
}

fn is_absolute_source(value: &str) -> bool {
    value.starts_with("https://") || value.starts_with("http://") || value.starts_with("urn:")
}

fn is_iso_date(value: &str) -> bool {
    let mut parts = value.split('-');
    let Some(year_text) = parts.next() else {
        return false;
    };
    let Some(month_text) = parts.next() else {
        return false;
    };
    let Some(day_text) = parts.next() else {
        return false;
    };
    if parts.next().is_some()
        || year_text.len() != 4
        || month_text.len() != 2
        || day_text.len() != 2
    {
        return false;
    }
    let Some(year) = parse_decimal(year_text.as_bytes()) else {
        return false;
    };
    let Some(month) = parse_decimal(month_text.as_bytes()) else {
        return false;
    };
    let Some(day) = parse_decimal(day_text.as_bytes()) else {
        return false;
    };
    let max_day = match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 if is_leap_year(year) => 29,
        2 => 28,
        _ => return false,
    };
    (1..=max_day).contains(&day)
}

fn parse_decimal(bytes: &[u8]) -> Option<u32> {
    let mut value = 0_u32;
    for byte in bytes {
        if !byte.is_ascii_digit() {
            return None;
        }
        value = value.checked_mul(10)?.checked_add(u32::from(byte - b'0'))?;
    }
    Some(value)
}

const fn is_leap_year(year: u32) -> bool {
    year.is_multiple_of(4) && (!year.is_multiple_of(100) || year.is_multiple_of(400))
}

#[cfg(test)]
mod decimal_tests {
    use super::parse_decimal;

    #[test]
    fn decimal_parser_rejects_overflow() {
        assert_eq!(parse_decimal(b"999999999999999999999"), None);
    }
}

impl fmt::Display for ValidationReport {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            formatter,
            "{} error(s), {} warning(s)",
            self.error_count(),
            self.warning_count()
        )
    }
}

#[cfg(test)]
mod tests {
    use super::{PackId, RequirementId, is_iso_date};

    #[test]
    fn pack_ids_reject_traversal() {
        for invalid in ["", "/root", "root/", "root//child", "root/../child", "Root"] {
            assert!(PackId::parse(invalid).is_err());
        }
        assert!(PackId::parse("org.prisma/prisma/2020").is_ok());
    }

    #[test]
    fn requirement_ids_match_the_contract() {
        assert!(RequirementId::parse("PRISMA-2020:1").is_ok());
        for invalid in ["", "-local", "_local", ".local", ":local", "bad path"] {
            assert!(RequirementId::parse(invalid).is_err());
        }
    }

    #[test]
    fn date_validation_handles_leap_years() {
        assert!(is_iso_date("2024-02-29"));
        assert!(!is_iso_date("2023-02-29"));
        assert!(!is_iso_date("2026-13-01"));
        assert!(!is_iso_date("2026-01-00"));
    }
}
