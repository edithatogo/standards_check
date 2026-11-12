# Plan: Canonical Standard Pack runtime

Status: **implementation complete**. Implementation: **source implemented**. Evidence: **fixture proven** for the runtime, synthetic fixtures and provisional pack structure. Authoritative PRISMA item reconciliation remains unproven and explicitly blocked.

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
- [x] Obtain passing Linux lint/test, cross-platform test and pack-drift receipts.
- [x] Review all automated PR findings and implement bounded-read and checked-arithmetic corrections.
- [x] Add an RFC 6901 regression test while retaining the correct tilde-before-slash escape order.
- [x] Remove all one-use transfer and review workflows from the branch.

## Remaining dependency gate

- [ ] Merge foundation pull request 59, then retarget pull request 60 from `feat/standardflow-platform-foundation` to `main` and re-run the same checks.

This dependency gate affects merge sequencing, not the recorded implementation or fixture evidence. Item-by-item reconciliation of the provisional PRISMA pack is owned by a later source-verification task and is not silently promoted here.
