# Plan: Platform foundation

Current status: **implementation complete (bounded)**. Implementation: **source implemented and foundation merged**.
The reviewed foundation at `d8cd1f2c54934ee15400d5be047c76977adfa29b` has
**compiler-verified** hosted evidence, retained in [evidence.json](evidence.json).
PR #59 merged as `a8bfec446d219b770e76a23b44d1f08d9e00465d`.
Hosted acceptance of PR #60 revision `bfe2255fda85b891c2f68044676c0b777d92c38c` has passed;
the revision-bound foundation, document, privacy and CodeQL receipts are retained in [evidence.json](evidence.json).

## Phase 1: Brownfield truth baseline

- [x] Implement tracked-area inventory for corpus, outputs, placeholders, licences and tests (not third-party certification).
- [x] Document authority conflicts and migration debt without deleting legacy surfaces.
- [x] Add deterministic audit unit tests and CI invocation; hosted PR #79 acceptance passed at baab246e62f3585237b987f87647eba743f2818e.

## Phase 2: Conductor and context

- [x] Pin the official Conductor plugin as a gitlink.
- [x] Add the local routing skill and project handshake.
- [x] Implement exact gitlink and local context-link checks in CI; hosted PR #79 acceptance passed.

## Phase 3: Rust foundation

- [x] Add the dependency-minimal Rust workspace and initial authority/evidence types.
- [x] Run formatting, Clippy and tests using Rust 1.98.1 in CI for the reviewed foundation.
- [x] Record the resulting compiler receipt without promoting unrelated claims.

The foundation Rust/contracts receipt is
[run 43304348843](https://github.com/edithatogo/standards_check/actions/runs/43304348843).
Document and privacy receipts are recorded separately in the evidence file.
These receipts apply to their recorded commit, not automatically to later repairs or merges.

## Phase 4: Repository standards and next tracks

- [x] Add immutable-pinned foundation CI and network-free contract checks.
- [x] Reconcile the registered `node`/`baseline` requirements through the existing
  semantic-conflict review in [#30](https://github.com/edithatogo/standards_check/issues/30):
  required dependency review and maintained inventories passed on accepted main
  `dd3f995`. Keep specialized Python/Rust/API CI and OIDC checks. Exact
  reusable-call and template-byte equality remain **unclaimed** and are not
  prerequisites for the accepted local controls.
- [x] Record the implemented Track 01 and Track 02 artefacts in the Conductor registry.
- [x] Record hosted acceptance at PR #60 revision `bfe2255fda85b891c2f68044676c0b777d92c38c`.

The foundation merge completes the reproducible brownfield inventory, but does not confirm third-party rights,
prove legacy migration parity or establish publication and external acceptance.

See [brownfield-audit.md](brownfield-audit.md) for classified authority and migration debt. Exact-head PR #79 CI verified the inventory and context checks; receiving-main CI is independently tracked in the dated reconciliation.

The [19 November 2026 quality-frontier reconciliation](../../quality-frontier-20261119.md) records issue #29-31 gates and exact-head evidence. The bounded registered-policy specialization was accepted and documented through PR #108; exact upstream template delivery remains unclaimed.

## Ponytail review — 22 November 2026

- [x] Legacy validation, HTML build and current agent guidance: published at `c64c61a0a978b4b50f8d525fc76d6548d2e75718`; verification is linked below.
- [x] Retain findings, negative regressions, local receipts and outstanding gates in the [review record](../../ponytail-review-20261122.md).
