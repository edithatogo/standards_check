//! Evidence and authority types shared across `StandardFlow` boundaries.

use serde::{Deserialize, Serialize};

/// Evidence levels used to prevent implementation and release overclaims.
#[derive(Clone, Copy, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "snake_case")]
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
    /// Returns whether this evidence level satisfies a required minimum.
    #[must_use]
    pub const fn satisfies(self, required: Self) -> bool {
        self as u8 >= required as u8
    }
}

/// Domain authority for an ecosystem evidence envelope.
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
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
