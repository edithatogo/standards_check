# Plan: Platform foundation

Current status: **in progress**. Implementation: **source implemented**. Evidence: **source verified** until CI produces compiler receipts.

## Phase 1: Brownfield truth baseline

- [ ] Audit current corpus, generated outputs, placeholders, licences and tests.
- [ ] Record authority conflicts and migration debt without deleting legacy surfaces.
- [ ] Add deterministic audit tests and a retained receipt.

## Phase 2: Conductor and context

- [x] Pin the official Conductor plugin as a gitlink.
- [x] Add the local routing skill and project handshake.
- [ ] Validate the gitlink and context links in CI.

## Phase 3: Rust foundation

- [x] Add the dependency-minimal Rust workspace and initial authority/evidence types.
- [ ] Run formatting, Clippy and tests using Rust 1.98.1 in CI.
- [ ] Record the resulting compiler receipt without promoting unrelated claims.

## Phase 4: Repository standards and next track

- [x] Add immutable-pinned foundation CI and network-free contract checks.
- [ ] Reconcile the repository profile with `edithatogo/repository-standards`.
- [ ] Create Track 01 through `conductor-new-track` after the foundation PR is reviewed.
