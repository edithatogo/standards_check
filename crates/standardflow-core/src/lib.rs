//! Domain boundaries for the future `StandardFlow` execution core.
#![forbid(unsafe_code)]

/// Evidence levels used to prevent implementation and release overclaims.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub enum EvidenceLevel {
    /// A requirement or interface has been specified.
    Contracted,
    /// Source and static structure have been reviewed.
    SourceVerified,
    /// The relevant code has compiled and deterministic tests have run.
    CompilerVerified,
    /// A rights-clear fixture proves the claimed behaviour.
    FixtureProven,
    /// An explicitly enabled live integration produced a retained receipt.
    LiveProven,
    /// Independent evaluation supports the bounded claim.
    ExternallyValidated,
    /// An external registry, publisher or adopter has accepted the artefact.
    PubliclyAccepted,
}

impl EvidenceLevel {
    /// Returns whether this evidence level is sufficient for a required minimum.
    #[must_use]
    pub const fn satisfies(self, required: Self) -> bool {
        self as u8 >= required as u8
    }
}

/// Domain authority for an ecosystem evidence envelope.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Authority {
    /// Informational output that cannot change assessment state.
    Advisory,
    /// Candidate evidence requiring review.
    CandidateEvidence,
    /// Evidence explicitly verified by an authorised human.
    HumanVerified,
    /// Evidence issued by the declared system of record.
    SystemOfRecord,
}

/// A stable standards identifier independent of a display number or filename.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RequirementId(String);

impl RequirementId {
    /// Creates an identifier when it contains only portable identifier characters.
    ///
    /// # Errors
    ///
    /// Returns [`IdentifierError`] when the value is empty, does not start with an ASCII
    /// alphanumeric character, or contains other non-portable characters.
    pub fn parse(value: &str) -> Result<Self, IdentifierError> {
        let mut bytes = value.bytes();
        let valid = bytes.next().is_some_and(|first| first.is_ascii_alphanumeric())
            && bytes.all(|byte| {
                byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b':' | b'-')
            });
        if valid {
            Ok(Self(value.to_owned()))
        } else {
            Err(IdentifierError)
        }
    }

    /// Returns the stable identifier as text.
    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Error returned for an invalid stable identifier.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct IdentifierError;

impl core::fmt::Display for IdentifierError {
    fn fmt(&self, formatter: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        formatter.write_str(
            "identifier must start with an ASCII letter or digit and contain only ASCII letters, digits, '.', '_', ':' or '-'",
        )
    }
}

impl std::error::Error for IdentifierError {}

#[cfg(test)]
mod tests {
    use super::{EvidenceLevel, RequirementId};

    #[test]
    fn evidence_is_monotonic() {
        assert!(EvidenceLevel::FixtureProven.satisfies(EvidenceLevel::Contracted));
        assert!(!EvidenceLevel::SourceVerified.satisfies(EvidenceLevel::LiveProven));
    }

    #[test]
    fn requirement_ids_are_portable() {
        let parsed = RequirementId::parse("CONSORT-AI:5.i");
        assert!(parsed.is_ok());
        if let Ok(identifier) = parsed {
            assert_eq!(identifier.as_str(), "CONSORT-AI:5.i");
        }
        for invalid in ["", "-local", "_local", ":local", ".local", "bad path"] {
            assert!(RequirementId::parse(invalid).is_err());
        }
    }
}
