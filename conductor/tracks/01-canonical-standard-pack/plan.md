# Plan: Canonical Standard Pack runtime

Status: **implementation complete; hosted integration accepted**. Implementation: **source implemented**. Evidence: **fixture proven** for the runtime, synthetic fixtures and provisional pack structure. Hosted acceptance applies to PR #60 revision `bfe2255fda85b891c2f68044676c0b777d92c38c`; exact receipts and historical verification are retained in [evidence.json](evidence.json). Independent source, rights, migration, methodological, usability/accessibility and publication obligations remain open.

## Phase 1: Contract and rights model

- [x] Extend the pack schema with verification and item-level rights.
- [x] Add strict Rust DTOs, portable IDs and stable diagnostics.
- [x] Enforce verification, source, relationship, rights and evidence invariants.

## Phase 2: Canonicalization and lockfiles

- [x] Implement integer-only deterministic canonical JSON and SHA-256.
- [x] Implement bounded recursive pack locks with symlink rejection and mutation checks.
- [x] Add atomic lock writing and deterministic lock verification.

## Phase 3: Reference pack and interfaces

- [x] Migrate the 27-item PRISMA 2020 corpus into a rights-aware provisional pack.
- [x] Add source manifest, CSL citation and conservative verification status.
- [x] Add text/JSON CLI operations and deterministic pack-validation scripts.

## Phase 4: Evidence and review

- [x] Add unit, property, lock, CLI and schema tests.
- [x] Generate and commit the dependency lock and PRISMA content lock in CI.
- [x] Obtain passing Linux lint/test, cross-platform test and pack-drift receipts for the recorded original head.
- [x] Review automated PR findings and implement bounded-read, checked-arithmetic, required-field, URI and portable-path corrections.
- [x] Add regression tests for pack/lock input limits and atomic temporary-file ownership.
- [x] Add an RFC 6901 regression test while retaining the correct tilde-before-slash escape order.
- [x] Remove all one-use transfer and review workflows from the branch.

## Integration and remaining evidence gates

- [x] Merge foundation PR #59 into main as `a8bfec446d219b770e76a23b44d1f08d9e00465d`.
- [x] Retarget PR #60 from the former foundation branch to `main`.
- [x] Reconcile the repaired runtime with current-main legacy, dependency and workflow changes.
- [x] Record passing hosted checks at `bfe2255fda85b891c2f68044676c0b777d92c38c`, including Linux, macOS and Windows.
- [ ] Reconcile the provisional PRISMA pack item-by-item to the authoritative source.
- [ ] Retain independent item-level rights confirmation and later external/publication acceptance.
- [ ] Complete migration parity and independent methodological/usability/accessibility qualification.

Hosted integration acceptance is recorded for the exact revision above; it does not transfer
automatically to later changes. Source reconciliation, rights, migration parity, independent
methodological/accessibility qualification and publication remain separate obligations.

## PRISMA source and rights review, 19 November 2026

The [source and rights evidence assessment](../../prisma2020-source-rights-20261119.md) verifies the official CC BY 4.0 checklist licence. Full transcription remains **unverified**: the provisional pack contains 27 aggregate items whereas the official checklist has 42 independently numbered items/subitems. The new CI validator prevents unjustified promotion; 42-item migration, independent text comparison, source checksum receipt, lock regeneration and mapping parity remain outstanding. This is not acceptance of the source-reconciliation gate.
