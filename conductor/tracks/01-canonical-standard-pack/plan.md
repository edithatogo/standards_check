# Plan: Canonical Standard Pack runtime

Status: **implementation complete; hosted integration accepted at the recorded revision**. Implementation: **source implemented**. Evidence: **fixture proven** for the runtime and synthetic fixtures. Hosted runtime acceptance applies to PR #60 revision `bfe2255fda85b891c2f68044676c0b777d92c38c`; exact receipts and historical verification are retained in [evidence.json](evidence.json). PR #83 subsequently promoted the PRISMA checklist to 42 source-reconciled items. That source comparison has its own bounded evidence below; receiving revisions, normalized interpretations, migration parity and external qualification require separate acceptance.

## Phase 1: Contract and rights model

- [x] Extend the pack schema with verification and item-level rights.
- [x] Add strict Rust DTOs, portable IDs and stable diagnostics.
- [x] Enforce verification, source, relationship, rights and evidence invariants.

## Phase 2: Canonicalization and lockfiles

- [x] Implement integer-only deterministic canonical JSON and SHA-256.
- [x] Implement bounded recursive pack locks with symlink rejection and mutation checks.
- [x] Add atomic lock writing and deterministic lock verification.

## Phase 3: Reference pack and interfaces

- [x] Migrate the original 27-item PRISMA 2020 corpus into a rights-aware provisional pack (historical PR #60 state; superseded by the 42-item pack in PR #83).
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
- [x] Reconcile all 42 PRISMA checklist texts to the retained official PDF, with source identity, item numbers, page anchors and item-specific receipts.
- [ ] Complete independent review of normalized interpretations and evidence expectations; retain broader legacy-corpus rights and later external/publication acceptance separately.
- [ ] Complete migration parity and independent methodological/usability/accessibility qualification.

Hosted integration acceptance is recorded for the exact revision above; it does not transfer
automatically to later changes. Checklist transcription, rights, migration parity, independent
methodological/accessibility qualification and publication have separate evidence scopes.

## PRISMA source and rights review, 19 November 2026

The initial [source and rights evidence assessment](../../prisma2020-source-rights-20261119.md) documented the official CC BY 4.0 checklist licence and correctly retained the then-27-item pack as unverified. It describes the state before PR #83, not the current pack.

## Receiving review, 20 November 2026

PR #83 merged as `da7e780dad139980cadfc40fb0fec44d90f6af50` with 42 items, `source_reconciled` status and a regenerated lock. The retained 67,506-byte official PDF has SHA-256 `2eedbd5452741f9615307a0bce21a8198c0597ce2a0a8a0fd7e140d64b08c625`. All 42 current texts match its complete numbered rows after Unicode NFKC and whitespace normalization.

The [receiving review](../../prisma2020-receiving-review-20261120.md) records the integration regressions and bounded repair: preserve the historical 27-item migration input, update current-pack test expectations while retaining unverified-fixture coverage, and bind both ledger and live pack to complete numbered PDF rows. Source reconciliation does not establish correctness of normalized interpretations, migration semantic parity, external methodological validity, accessibility or publication acceptance.

## EQUATOR discovery and trial-reporting source decisions — 23 November 2026

- [x] Accept [PR #112](https://github.com/edithatogo/standards_check/pull/112)'s
  source-pinned **719-page descriptive directory** and monthly read-only
  surveillance workflow on main `f02701c4`. One upstream page has a missing title
  and remains `metadata_status: needs_review`; no guideline text or Canonical Pack
  was admitted.
- [ ] Independently adjudicate selected editions and rights for
  [CONSORT 2025 / SPIRIT 2025 #120](https://github.com/edithatogo/standards_check/issues/120).
  [PR #121](https://github.com/edithatogo/standards_check/pull/121) corrects
  publication-date indexing, adds source-only TRIPOD+AI 2024, and labels
  unqualified source entries explicitly; it **does not** create a pack.
- [ ] Pin authoritative checklist bytes and licence scopes and reconcile all
  item/subitem text, evidence expectations and mappings independently before
  any versioned pack release. Keep [held STARD copies #95](https://github.com/edithatogo/standards_check/issues/95)
  quarantined and [PRISMA interpretation #82](https://github.com/edithatogo/standards_check/issues/82)
  open. No inherited compliance decisions on edition splits.

The intake authority is the existing
[guideline admission checklist](../../../CONTENT_POPULATION_WORKFLOW.md).
The EQUATOR metadata catalogue is a *discovery projection* and does not
replace the authoritative primary source or the pack lock.
