//! PRISMA 2020 flow input, arithmetic invariants and recipe binding.

use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};
use standardflow_core::{Diagnostic, ValidationReport};
use thiserror::Error;

use crate::limits::{
    MAX_EXCLUSION_REASON_CHARS, MAX_EXCLUSION_REASONS, MAX_INPUT_BYTES, MAX_SAFE_JSON_INTEGER,
    is_xml_10_text,
};
use crate::recipe::{DiagramRecipe, RecipeError};
use crate::scene::Scene;

/// Four official PRISMA 2020 flow families supported by the reference slice.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum PrismaTemplate {
    /// New review using databases and registers only.
    NewDatabasesRegisters,
    /// New review using databases/registers and other methods.
    NewDatabasesRegistersOtherSources,
    /// Updated review using databases and registers only.
    UpdatedDatabasesRegisters,
    /// Updated review using databases/registers and other methods.
    UpdatedDatabasesRegistersOtherSources,
}

impl PrismaTemplate {
    /// Returns whether the template includes the other-methods branch.
    #[must_use]
    pub const fn requires_other_sources(self) -> bool {
        matches!(
            self,
            Self::NewDatabasesRegistersOtherSources | Self::UpdatedDatabasesRegistersOtherSources
        )
    }

    /// Returns whether the template includes prior-review lineage.
    #[must_use]
    pub const fn requires_previous_review(self) -> bool {
        matches!(
            self,
            Self::UpdatedDatabasesRegisters | Self::UpdatedDatabasesRegistersOtherSources
        )
    }

    /// Returns the built-in recipe identifier.
    #[must_use]
    pub const fn recipe_id(self) -> &'static str {
        match self {
            Self::NewDatabasesRegisters => "org.prisma/prisma-2020/new-databases-registers",
            Self::NewDatabasesRegistersOtherSources => {
                "org.prisma/prisma-2020/new-databases-registers-other-sources"
            }
            Self::UpdatedDatabasesRegisters => "org.prisma/prisma-2020/updated-databases-registers",
            Self::UpdatedDatabasesRegistersOtherSources => {
                "org.prisma/prisma-2020/updated-databases-registers-other-sources"
            }
        }
    }

    const fn recipe_json(self) -> &'static str {
        match self {
            Self::NewDatabasesRegisters => {
                include_str!("../../../recipes/prisma-2020/new-databases-registers.json")
            }
            Self::NewDatabasesRegistersOtherSources => include_str!(
                "../../../recipes/prisma-2020/new-databases-registers-other-sources.json"
            ),
            Self::UpdatedDatabasesRegisters => {
                include_str!("../../../recipes/prisma-2020/updated-databases-registers.json")
            }
            Self::UpdatedDatabasesRegistersOtherSources => include_str!(
                "../../../recipes/prisma-2020/updated-databases-registers-other-sources.json"
            ),
        }
    }
}

/// One structured report-exclusion reason.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ExclusionReason {
    /// Human-readable reason.
    pub reason: String,
    /// Number of reports excluded for this reason.
    pub reports: u64,
}

/// Included study/report counts.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct IncludedCounts {
    /// Distinct studies.
    pub studies: u64,
    /// Reports describing those studies.
    pub reports: u64,
}

/// Database/register identification and screening stream.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct DatabaseRegisterStream {
    /// Records identified from databases.
    pub databases: u64,
    /// Records identified from registers.
    pub registers: u64,
    /// Duplicate records removed before screening.
    pub duplicate_records_removed: u64,
    /// Records marked ineligible by automation tools.
    pub records_marked_ineligible_by_automation: u64,
    /// Records removed for other reasons before screening.
    pub records_removed_other_reasons: u64,
    /// Records screened.
    pub records_screened: u64,
    /// Records excluded during screening.
    pub records_excluded: u64,
    /// Reports sought for retrieval.
    pub reports_sought: u64,
    /// Reports not retrieved.
    pub reports_not_retrieved: u64,
    /// Reports assessed for eligibility.
    pub reports_assessed: u64,
    /// Structured report-exclusion reasons.
    pub reports_excluded: Vec<ExclusionReason>,
    /// Reports included from this stream.
    pub reports_included: u64,
}

/// Website, organisation, citation-searching and other-methods stream.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct OtherMethodsStream {
    /// Records identified from websites.
    pub websites: u64,
    /// Records identified from organisations.
    pub organisations: u64,
    /// Records identified through citation searching.
    pub citation_searching: u64,
    /// Records identified through other methods.
    pub other_sources: u64,
    /// Reports sought for retrieval.
    pub reports_sought: u64,
    /// Reports not retrieved.
    pub reports_not_retrieved: u64,
    /// Reports assessed for eligibility.
    pub reports_assessed: u64,
    /// Structured report-exclusion reasons.
    pub reports_excluded: Vec<ExclusionReason>,
    /// Reports included from this stream.
    pub reports_included: u64,
}

/// Complete PRISMA flow evidence input.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct PrismaFlow {
    /// Input contract version.
    pub schema_version: String,
    /// Stable review-local identifier.
    pub review_id: String,
    /// Selected official PRISMA template.
    pub template: PrismaTemplate,
    /// Database/register stream.
    pub databases_registers: DatabaseRegisterStream,
    /// Other-methods stream, required only by mixed-source templates.
    pub other_methods: Option<OtherMethodsStream>,
    /// Prior-review counts, required only by updated-review templates.
    pub previous_review: Option<IncludedCounts>,
    /// New studies and reports included by this search/update.
    pub new_included: IncludedCounts,
    /// Total studies and reports represented by the resulting review.
    pub total_included: IncludedCounts,
}

impl PrismaFlow {
    /// Performs deterministic PRISMA template and arithmetic validation.
    #[must_use]
    pub fn validate(&self) -> ValidationReport {
        let mut report = ValidationReport::default();
        if self.schema_version != "dev.standardflow.prisma-flow.v1" {
            report.push(Diagnostic::error(
                "SF-PRISMA-001",
                "/schema_version",
                "schema_version must be dev.standardflow.prisma-flow.v1",
            ));
        }
        if self.review_id.trim().is_empty()
            || self.review_id.chars().count() > 200
            || self.review_id.chars().any(char::is_control)
            || !is_xml_10_text(&self.review_id)
        {
            report.push(Diagnostic::error(
                "SF-PRISMA-002",
                "/review_id",
                "review_id must contain 1 to 200 non-control characters",
            ));
        }
        if self.template.requires_other_sources() != self.other_methods.is_some() {
            report.push(Diagnostic::error(
                "SF-PRISMA-003",
                "/other_methods",
                "other_methods presence must match the selected template",
            ));
        }
        if self.template.requires_previous_review() != self.previous_review.is_some() {
            report.push(Diagnostic::error(
                "SF-PRISMA-004",
                "/previous_review",
                "previous_review presence must match the selected template",
            ));
        }

        validate_database_stream(&self.databases_registers, &mut report);
        if let Some(other) = &self.other_methods {
            validate_other_stream(other, &mut report);
        }
        validate_included_counts(self.new_included, "/new_included", &mut report);
        validate_included_counts(self.total_included, "/total_included", &mut report);
        if let Some(previous) = self.previous_review {
            validate_included_counts(previous, "/previous_review", &mut report);
        }

        let other_reports = self
            .other_methods
            .as_ref()
            .map_or(0, |stream| stream.reports_included);
        match self
            .databases_registers
            .reports_included
            .checked_add(other_reports)
        {
            Some(expected) if expected == self.new_included.reports => {}
            Some(expected) => report.push(Diagnostic::error(
                "SF-PRISMA-005",
                "/new_included/reports",
                format!(
                    "new included reports must equal reports included across source streams ({expected})"
                ),
            )),
            None => report.push(Diagnostic::error(
                "SF-PRISMA-006",
                "/new_included/reports",
                "included-report arithmetic overflowed",
            )),
        }

        if let Some(previous) = self.previous_review {
            validate_updated_totals(
                previous,
                self.new_included,
                self.total_included,
                &mut report,
            );
        } else if self.total_included != self.new_included {
            report.push(Diagnostic::error(
                "SF-PRISMA-007",
                "/total_included",
                "new-review totals must equal new included studies and reports",
            ));
        }
        report
    }

    /// Builds a renderer-neutral scene from the selected built-in recipe.
    ///
    /// # Errors
    ///
    /// Returns [`PrismaError`] for invalid arithmetic, recipe or scene construction.
    pub fn build_scene(&self) -> Result<Scene, PrismaError> {
        let report = self.validate();
        if !report.is_valid() {
            return Err(PrismaError::Validation(report));
        }
        let recipe = DiagramRecipe::from_json(self.template.recipe_json().as_bytes())?;
        if recipe.recipe_id != self.template.recipe_id() {
            return Err(PrismaError::RecipeMismatch {
                expected: self.template.recipe_id(),
                observed: recipe.recipe_id,
            });
        }
        recipe
            .build_scene(&self.bindings()?)
            .map_err(PrismaError::Recipe)
    }

    #[allow(
        clippy::too_many_lines,
        reason = "bindings intentionally enumerate the complete versioned PRISMA contract in one auditable mapping"
    )]
    fn bindings(&self) -> Result<BTreeMap<String, String>, PrismaError> {
        let database = &self.databases_registers;
        let identified = checked_sum(
            [database.databases, database.registers],
            "/databases_registers",
        )?;
        let removed = checked_sum(
            [
                database.duplicate_records_removed,
                database.records_marked_ineligible_by_automation,
                database.records_removed_other_reasons,
            ],
            "/databases_registers",
        )?;
        let mut bindings = BTreeMap::from([
            (String::from("review_id"), self.review_id.clone()),
            (String::from("db_databases"), database.databases.to_string()),
            (String::from("db_registers"), database.registers.to_string()),
            (String::from("db_identified_total"), identified.to_string()),
            (
                String::from("db_duplicates_removed"),
                database.duplicate_records_removed.to_string(),
            ),
            (
                String::from("db_automation_removed"),
                database.records_marked_ineligible_by_automation.to_string(),
            ),
            (
                String::from("db_other_removed"),
                database.records_removed_other_reasons.to_string(),
            ),
            (String::from("db_removed_total"), removed.to_string()),
            (
                String::from("db_records_screened"),
                database.records_screened.to_string(),
            ),
            (
                String::from("db_records_excluded"),
                database.records_excluded.to_string(),
            ),
            (
                String::from("db_reports_sought"),
                database.reports_sought.to_string(),
            ),
            (
                String::from("db_reports_not_retrieved"),
                database.reports_not_retrieved.to_string(),
            ),
            (
                String::from("db_reports_assessed"),
                database.reports_assessed.to_string(),
            ),
            (
                String::from("db_reports_excluded"),
                exclusion_total(
                    &database.reports_excluded,
                    "/databases_registers/reports_excluded",
                )?
                .to_string(),
            ),
            (
                String::from("db_exclusion_reasons"),
                format_exclusion_reasons(&database.reports_excluded),
            ),
            (
                String::from("db_reports_included"),
                database.reports_included.to_string(),
            ),
            (
                String::from("new_studies"),
                self.new_included.studies.to_string(),
            ),
            (
                String::from("new_reports"),
                self.new_included.reports.to_string(),
            ),
            (
                String::from("total_studies"),
                self.total_included.studies.to_string(),
            ),
            (
                String::from("total_reports"),
                self.total_included.reports.to_string(),
            ),
        ]);
        if let Some(other) = &self.other_methods {
            let identified_other = checked_sum(
                [
                    other.websites,
                    other.organisations,
                    other.citation_searching,
                    other.other_sources,
                ],
                "/other_methods",
            )?;
            bindings.extend([
                (String::from("other_websites"), other.websites.to_string()),
                (
                    String::from("other_organisations"),
                    other.organisations.to_string(),
                ),
                (
                    String::from("other_citation_searching"),
                    other.citation_searching.to_string(),
                ),
                (
                    String::from("other_sources"),
                    other.other_sources.to_string(),
                ),
                (
                    String::from("other_identified_total"),
                    identified_other.to_string(),
                ),
                (
                    String::from("other_reports_sought"),
                    other.reports_sought.to_string(),
                ),
                (
                    String::from("other_reports_not_retrieved"),
                    other.reports_not_retrieved.to_string(),
                ),
                (
                    String::from("other_reports_assessed"),
                    other.reports_assessed.to_string(),
                ),
                (
                    String::from("other_reports_excluded"),
                    exclusion_total(&other.reports_excluded, "/other_methods/reports_excluded")?
                        .to_string(),
                ),
                (
                    String::from("other_exclusion_reasons"),
                    format_exclusion_reasons(&other.reports_excluded),
                ),
                (
                    String::from("other_reports_included"),
                    other.reports_included.to_string(),
                ),
            ]);
        }
        if let Some(previous) = self.previous_review {
            bindings.extend([
                (
                    String::from("previous_studies"),
                    previous.studies.to_string(),
                ),
                (
                    String::from("previous_reports"),
                    previous.reports.to_string(),
                ),
            ]);
        }
        Ok(bindings)
    }
}

/// PRISMA parsing, arithmetic or recipe failure.
#[derive(Debug, Error)]
pub enum PrismaError {
    /// Input exceeds the bounded parser contract.
    #[error("PRISMA flow JSON exceeds the declared limit of {0} bytes")]
    ResourceLimit(usize),
    /// Input JSON could not be decoded into the strict model.
    #[error("PRISMA flow JSON is invalid: {0}")]
    Json(#[from] serde_json::Error),
    /// Template or arithmetic invariants failed.
    #[error("PRISMA flow validation failed with {} error(s)", .0.error_count())]
    Validation(ValidationReport),
    /// Data-driven recipe failed.
    #[error(transparent)]
    Recipe(#[from] RecipeError),
    /// Included recipe did not match the selected template.
    #[error("built-in recipe mismatch: expected {expected}, observed {observed}")]
    RecipeMismatch {
        /// Expected recipe identifier.
        expected: &'static str,
        /// Parsed identifier.
        observed: String,
    },
    /// Binding arithmetic overflowed after validation.
    #[error("PRISMA binding arithmetic overflowed at {0}")]
    BindingOverflow(String),
}

/// Parses a strict PRISMA flow from JSON.
///
/// # Errors
///
/// Returns [`PrismaError`] when decoding fails.
pub fn parse_prisma_flow(bytes: &[u8]) -> Result<PrismaFlow, PrismaError> {
    if bytes.len() > MAX_INPUT_BYTES {
        return Err(PrismaError::ResourceLimit(MAX_INPUT_BYTES));
    }
    serde_json::from_slice(bytes).map_err(PrismaError::Json)
}

fn validate_included_counts(counts: IncludedCounts, path: &str, report: &mut ValidationReport) {
    validate_count(counts.studies, &format!("{path}/studies"), report);
    validate_count(counts.reports, &format!("{path}/reports"), report);
    if counts.studies > counts.reports {
        report.push(Diagnostic::error(
            "SF-PRISMA-008",
            path,
            "included report count must be at least the included study count",
        ));
    }
}

fn validate_database_stream(stream: &DatabaseRegisterStream, report: &mut ValidationReport) {
    for (name, value) in [
        ("databases", stream.databases),
        ("registers", stream.registers),
        (
            "duplicate_records_removed",
            stream.duplicate_records_removed,
        ),
        (
            "records_marked_ineligible_by_automation",
            stream.records_marked_ineligible_by_automation,
        ),
        (
            "records_removed_other_reasons",
            stream.records_removed_other_reasons,
        ),
        ("records_screened", stream.records_screened),
        ("records_excluded", stream.records_excluded),
        ("reports_sought", stream.reports_sought),
        ("reports_not_retrieved", stream.reports_not_retrieved),
        ("reports_assessed", stream.reports_assessed),
        ("reports_included", stream.reports_included),
    ] {
        validate_count(value, &format!("/databases_registers/{name}"), report);
    }
    let identified = diagnostic_sum(
        [stream.databases, stream.registers],
        "/databases_registers",
        report,
    );
    let removed = diagnostic_sum(
        [
            stream.duplicate_records_removed,
            stream.records_marked_ineligible_by_automation,
            stream.records_removed_other_reasons,
        ],
        "/databases_registers",
        report,
    );
    if let (Some(identified), Some(removed)) = (identified, removed) {
        validate_difference(
            identified,
            removed,
            stream.records_screened,
            "SF-PRISMA-010",
            "/databases_registers/records_screened",
            "records screened must equal records identified minus pre-screening removals",
            report,
        );
    }
    validate_difference(
        stream.records_screened,
        stream.records_excluded,
        stream.reports_sought,
        "SF-PRISMA-011",
        "/databases_registers/reports_sought",
        "reports sought must equal records screened minus records excluded",
        report,
    );
    validate_difference(
        stream.reports_sought,
        stream.reports_not_retrieved,
        stream.reports_assessed,
        "SF-PRISMA-012",
        "/databases_registers/reports_assessed",
        "reports assessed must equal reports sought minus reports not retrieved",
        report,
    );
    validate_assessed_outcome(
        stream.reports_assessed,
        &stream.reports_excluded,
        stream.reports_included,
        "/databases_registers/reports_excluded",
        report,
    );
}

fn validate_other_stream(stream: &OtherMethodsStream, report: &mut ValidationReport) {
    for (name, value) in [
        ("websites", stream.websites),
        ("organisations", stream.organisations),
        ("citation_searching", stream.citation_searching),
        ("other_sources", stream.other_sources),
        ("reports_sought", stream.reports_sought),
        ("reports_not_retrieved", stream.reports_not_retrieved),
        ("reports_assessed", stream.reports_assessed),
        ("reports_included", stream.reports_included),
    ] {
        validate_count(value, &format!("/other_methods/{name}"), report);
    }
    let identified = diagnostic_sum(
        [
            stream.websites,
            stream.organisations,
            stream.citation_searching,
            stream.other_sources,
        ],
        "/other_methods",
        report,
    );
    if let Some(identified) = identified
        && stream.reports_sought != identified
    {
        report.push(Diagnostic::error(
            "SF-PRISMA-020",
            "/other_methods/reports_sought",
            format!(
                "reports sought must equal reports identified by other methods ({identified}) in the official reference recipe"
            ),
        ));
    }
    validate_difference(
        stream.reports_sought,
        stream.reports_not_retrieved,
        stream.reports_assessed,
        "SF-PRISMA-021",
        "/other_methods/reports_assessed",
        "reports assessed must equal reports sought minus reports not retrieved",
        report,
    );
    validate_assessed_outcome(
        stream.reports_assessed,
        &stream.reports_excluded,
        stream.reports_included,
        "/other_methods/reports_excluded",
        report,
    );
}

fn validate_assessed_outcome(
    assessed: u64,
    reasons: &[ExclusionReason],
    included: u64,
    path: &str,
    report: &mut ValidationReport,
) {
    let excluded = validate_reasons(reasons, path, report);
    if let Some(excluded) = excluded {
        match excluded.checked_add(included) {
            Some(total) if total == assessed => {}
            Some(total) => report.push(Diagnostic::error(
                "SF-PRISMA-030",
                path,
                format!(
                    "excluded reports plus included reports ({total}) must equal reports assessed ({assessed})"
                ),
            )),
            None => report.push(Diagnostic::error(
                "SF-PRISMA-031",
                path,
                "excluded/included report arithmetic overflowed",
            )),
        }
    }
}

fn validate_reasons(
    reasons: &[ExclusionReason],
    path: &str,
    report: &mut ValidationReport,
) -> Option<u64> {
    if reasons.len() > MAX_EXCLUSION_REASONS {
        report.push(Diagnostic::error(
            "SF-PRISMA-036",
            path,
            format!("at most {MAX_EXCLUSION_REASONS} exclusion reasons are permitted"),
        ));
    }
    let mut names = BTreeSet::new();
    let mut total = 0_u64;
    for (index, reason) in reasons.iter().enumerate() {
        let reason_path = format!("{path}/{index}");
        let normalized = reason.reason.trim();
        if normalized.is_empty()
            || normalized.chars().count() > MAX_EXCLUSION_REASON_CHARS
            || !is_xml_10_text(normalized)
        {
            report.push(Diagnostic::error(
                "SF-PRISMA-032",
                format!("{reason_path}/reason"),
                format!(
                    "exclusion reason must contain 1 to {MAX_EXCLUSION_REASON_CHARS} XML 1.0-compatible characters"
                ),
            ));
        } else if !names.insert(normalized) {
            report.push(Diagnostic::error(
                "SF-PRISMA-033",
                format!("{reason_path}/reason"),
                "exclusion reasons must be unique within a stream",
            ));
        }
        validate_count(reason.reports, &format!("{reason_path}/reports"), report);
        if reason.reports == 0 {
            report.push(Diagnostic::error(
                "SF-PRISMA-034",
                format!("{reason_path}/reports"),
                "zero-count exclusion reasons must be omitted",
            ));
        }
        let Some(next) = total.checked_add(reason.reports) else {
            report.push(Diagnostic::error(
                "SF-PRISMA-035",
                path,
                "report-exclusion totals overflowed",
            ));
            return None;
        };
        if next > MAX_SAFE_JSON_INTEGER {
            report.push(Diagnostic::error(
                "SF-PRISMA-037",
                path,
                "report-exclusion total exceeds the cross-language safe-integer ceiling",
            ));
            return None;
        }
        total = next;
    }
    Some(total)
}

fn validate_count(value: u64, path: &str, report: &mut ValidationReport) {
    if value > MAX_SAFE_JSON_INTEGER {
        report.push(Diagnostic::error(
            "SF-PRISMA-009",
            path,
            format!("count must not exceed {MAX_SAFE_JSON_INTEGER}"),
        ));
    }
}

fn validate_difference(
    minuend: u64,
    subtrahend: u64,
    observed: u64,
    code: &'static str,
    path: &str,
    message: &'static str,
    report: &mut ValidationReport,
) {
    match minuend.checked_sub(subtrahend) {
        Some(expected) if expected == observed => {}
        Some(expected) => report.push(Diagnostic::error(
            code,
            path,
            format!("{message}; expected {expected}, observed {observed}"),
        )),
        None => report.push(Diagnostic::error(
            code,
            path,
            format!("{message}; subtraction underflowed"),
        )),
    }
}

fn validate_updated_totals(
    previous: IncludedCounts,
    new: IncludedCounts,
    total: IncludedCounts,
    report: &mut ValidationReport,
) {
    for (name, previous_value, new_value, observed) in [
        ("studies", previous.studies, new.studies, total.studies),
        ("reports", previous.reports, new.reports, total.reports),
    ] {
        match previous_value.checked_add(new_value) {
            Some(expected) if expected == observed => {}
            Some(expected) => report.push(Diagnostic::error(
                "SF-PRISMA-040",
                format!("/total_included/{name}"),
                format!("updated-review total {name} must equal previous plus new ({expected})"),
            )),
            None => report.push(Diagnostic::error(
                "SF-PRISMA-041",
                format!("/total_included/{name}"),
                "updated-review total arithmetic overflowed",
            )),
        }
    }
}

fn diagnostic_sum<const N: usize>(
    values: [u64; N],
    path: &str,
    report: &mut ValidationReport,
) -> Option<u64> {
    let mut total = 0_u64;
    for value in values {
        let Some(next) = total.checked_add(value) else {
            report.push(Diagnostic::error(
                "SF-PRISMA-050",
                path,
                "count arithmetic overflowed",
            ));
            return None;
        };
        if next > MAX_SAFE_JSON_INTEGER {
            report.push(Diagnostic::error(
                "SF-PRISMA-051",
                path,
                "count total exceeds the cross-language safe-integer ceiling",
            ));
            return None;
        }
        total = next;
    }
    Some(total)
}

fn checked_sum<const N: usize>(values: [u64; N], path: &str) -> Result<u64, PrismaError> {
    let mut total = 0_u64;
    for value in values {
        total = total
            .checked_add(value)
            .filter(|sum| *sum <= MAX_SAFE_JSON_INTEGER)
            .ok_or_else(|| PrismaError::BindingOverflow(path.to_owned()))?;
    }
    Ok(total)
}

fn exclusion_total(reasons: &[ExclusionReason], path: &str) -> Result<u64, PrismaError> {
    let mut total = 0_u64;
    for reason in reasons {
        total = total
            .checked_add(reason.reports)
            .filter(|sum| *sum <= MAX_SAFE_JSON_INTEGER)
            .ok_or_else(|| PrismaError::BindingOverflow(path.to_owned()))?;
    }
    Ok(total)
}

fn format_exclusion_reasons(reasons: &[ExclusionReason]) -> String {
    if reasons.is_empty() {
        return String::from("None (n = 0)");
    }
    reasons
        .iter()
        .map(|reason| format!("{} (n = {})", reason.reason.trim(), reason.reports))
        .collect::<Vec<_>>()
        .join("\n")
}

#[cfg(test)]
mod tests {
    use super::{DatabaseRegisterStream, IncludedCounts, PrismaFlow, PrismaTemplate};

    fn valid_flow() -> PrismaFlow {
        PrismaFlow {
            schema_version: String::from("dev.standardflow.prisma-flow.v1"),
            review_id: String::from("review-001"),
            template: PrismaTemplate::NewDatabasesRegisters,
            databases_registers: DatabaseRegisterStream {
                databases: 100,
                registers: 20,
                duplicate_records_removed: 10,
                records_marked_ineligible_by_automation: 5,
                records_removed_other_reasons: 5,
                records_screened: 100,
                records_excluded: 60,
                reports_sought: 40,
                reports_not_retrieved: 5,
                reports_assessed: 35,
                reports_excluded: Vec::new(),
                reports_included: 35,
            },
            other_methods: None,
            previous_review: None,
            new_included: IncludedCounts {
                studies: 30,
                reports: 35,
            },
            total_included: IncludedCounts {
                studies: 30,
                reports: 35,
            },
        }
    }

    #[test]
    fn arithmetic_mismatch_is_rejected() {
        let mut flow = valid_flow();
        flow.databases_registers.records_screened = 99;
        assert!(!flow.validate().is_valid());
    }

    #[test]
    fn valid_flow_builds_a_scene() -> Result<(), Box<dyn std::error::Error>> {
        let scene = valid_flow().build_scene()?;
        assert!(scene.validate().is_valid());
        assert_eq!(
            scene.recipe_id,
            PrismaTemplate::NewDatabasesRegisters.recipe_id()
        );
        Ok(())
    }
}
