# Plan: Canonical Standard Pack runtime

Status: **in progress**. Implementation: **source implemented**. Evidence: **source verified** until the stacked PR CI produces compiler and fixture receipts.

## Phase 1: Contract and rights model

- [x] Extend the pack schema with verification and item-level rights.
- [x] Add strict Rust DTOs, portable IDs and stable diagnostics.
- [x] Enforce verification, source, relationship, rights and evidence invariants.

## Phase 2: Canonicalization and lockfiles

- [x] Implement integer-only deterministic canonical JSON and SHA-256.
- [x] Implement symlink-safe recursive pack locks with defensive limits.
- [x] Add atomic lock writing and mutation detection.

## Phase 3: Reference pack and interfaces

- [x] Migrate the 27-item PRISMA 2020 corpus into a rights-aware provisional pack.
- [x] Add source manifest, CSL citation and conservative verification status.
- [x] Add text/JSON CLI operations and deterministic pack-validation scripts.

## Phase 4: Evidence and review

- [x] Add unit, property, lock, CLI and schema tests.
- [ ] Generate and commit the dependency lock and PRISMA content lock in CI.
- [ ] Obtain passing Linux lint/test, cross-platform test and pack-drift receipts.
- [ ] Review automated PR findings and append any required correction tasks.
