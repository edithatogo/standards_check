//! Rust authority for Canonical Standard Packs and evidence-safe artefacts.
#![forbid(unsafe_code)]

pub mod canonical;
pub mod diagnostic;
pub mod evidence;
pub mod lock;
pub mod pack;

pub use canonical::{CanonicalError, canonical_json, sha256_hex};
pub use diagnostic::{Diagnostic, Severity, ValidationReport};
pub use evidence::{Authority, EvidenceLevel};
pub use lock::{
    LockError, LockLimits, LockVerification, LockedFile, PackLock, build_pack_lock,
    verify_pack_lock, write_pack_lock,
};
pub use pack::{
    IdentifierError, InheritedRights, PackError, PackId, Relationship, RelationshipPredicate,
    Requirement, RequirementId, RequirementRights, Rights, RightsStatus, SourceAuthority,
    StandardKind, StandardPack, ValidatedPack, Verification, VerificationStatus, load_pack,
    parse_pack,
};
