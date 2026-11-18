//! Stable validation diagnostics for humans, CI and agent consumers.

use serde::Serialize;

/// Diagnostic severity.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Severity {
    /// The pack cannot be accepted.
    Error,
    /// The pack is structurally usable but carries unresolved evidence debt.
    Warning,
}

/// One stable validation finding.
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct Diagnostic {
    /// Stable machine-readable code.
    pub code: &'static str,
    /// JSON-pointer-like location.
    pub path: String,
    /// Human-readable explanation.
    pub message: String,
    /// Finding severity.
    pub severity: Severity,
}

impl Diagnostic {
    /// Creates an error finding.
    #[must_use]
    pub fn error(code: &'static str, path: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code,
            path: path.into(),
            message: message.into(),
            severity: Severity::Error,
        }
    }

    /// Creates a warning finding.
    #[must_use]
    pub fn warning(
        code: &'static str,
        path: impl Into<String>,
        message: impl Into<String>,
    ) -> Self {
        Self {
            code,
            path: path.into(),
            message: message.into(),
            severity: Severity::Warning,
        }
    }
}

/// Complete semantic validation result.
#[derive(Clone, Debug, Default, Eq, PartialEq, Serialize)]
pub struct ValidationReport {
    /// Ordered findings.
    pub diagnostics: Vec<Diagnostic>,
}

impl ValidationReport {
    /// Adds a finding.
    pub fn push(&mut self, diagnostic: Diagnostic) {
        self.diagnostics.push(diagnostic);
    }

    /// Returns whether the report contains no errors.
    #[must_use]
    pub fn is_valid(&self) -> bool {
        !self
            .diagnostics
            .iter()
            .any(|diagnostic| diagnostic.severity == Severity::Error)
    }

    /// Counts error findings.
    #[must_use]
    pub fn error_count(&self) -> usize {
        self.diagnostics
            .iter()
            .filter(|diagnostic| diagnostic.severity == Severity::Error)
            .count()
    }

    /// Counts warning findings.
    #[must_use]
    pub fn warning_count(&self) -> usize {
        self.diagnostics
            .iter()
            .filter(|diagnostic| diagnostic.severity == Severity::Warning)
            .count()
    }
}
