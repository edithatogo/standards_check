# Plan: Platform foundation

Current status: **in progress**. Implementation: **source implemented and foundation merged**.
The reviewed foundation at `d8cd1f2c54934ee15400d5be047c76977adfa29b` has
**compiler-verified** hosted evidence, retained in [evidence.json](evidence.json).
PR #59 merged as `a8bfec446d219b770e76a23b44d1f08d9e00465d`.
Hosted acceptance of PR #60 revision `bfe2255fda85b891c2f68044676c0b777d92c38c` has passed;
the revision-bound foundation, document, privacy and CodeQL receipts are retained in [evidence.json](evidence.json).

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
- [x] Run formatting, Clippy and tests using Rust 1.98.1 in CI for the reviewed foundation.
- [x] Record the resulting compiler receipt without promoting unrelated claims.

The foundation Rust/contracts receipt is
[run 43304348843](https://github.com/edithatogo/standards_check/actions/runs/43304348843).
Document and privacy receipts are recorded separately in the evidence file.
These receipts apply to their recorded commit, not automatically to later repairs or merges.

## Phase 4: Repository standards and next tracks

- [x] Add immutable-pinned foundation CI and network-free contract checks.
- [ ] Reconcile the repository profile with `edithatogo/repository-standards`.
- [x] Record the implemented Track 01 and Track 02 artefacts in the Conductor registry.
- [x] Record hosted acceptance at PR #60 revision `bfe2255fda85b891c2f68044676c0b777d92c38c`.

The foundation merge does not complete the brownfield audit, confirm third-party rights,
prove legacy migration parity or establish publication and external acceptance.
