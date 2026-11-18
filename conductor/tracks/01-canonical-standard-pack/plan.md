# Plan: Canonical Standard Pack runtime

Status: **implementation complete; integration acceptance pending**. Implementation: **source implemented**. Evidence: **fixture proven** for the runtime, synthetic fixtures and provisional pack structure at the revisions listed in [evidence.json](evidence.json). Original head `55bff593c6e91491ad50596baefae5626c6bf2c5` has hosted Linux, macOS and Windows receipts. Repair commit `f41888832c2b169528b30fe99df6aa7a85aff153` has local Linux evidence. Authoritative PRISMA item reconciliation remains unproven and explicitly blocked.

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
- [ ] Obtain passing hosted checks at the final merged repair head, including Linux, macOS and Windows.
- [ ] Reconcile the provisional PRISMA pack item-by-item to the authoritative source.
- [ ] Retain independent item-level rights confirmation and later external/publication acceptance.

Earlier successful receipts are revision-bound. The current merge gate remains open until fresh
checks cover the final PR head. Source reconciliation and rights are separate obligations and are
not promoted by compiler, fixture or merge evidence.
