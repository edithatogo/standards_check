# Plan: Semantic diagram engine and PRISMA 2020 flows

Status: **implementation complete; hosted integration accepted**. Implementation: **source implemented**. Evidence: **fixture proven** for the bounded diagram invariants and four synthetic PRISMA families. Hosted acceptance applies to PR #60 revision `bfe2255fda85b891c2f68044676c0b777d92c38c`; exact receipts and historical verification are retained in [evidence.json](evidence.json). Independent source, rights, migration, methodological, usability/accessibility and publication obligations remain open.

## Phase 1: Semantic contracts

- [x] Define strict recipe, PRISMA-flow and scene-graph schemas.
- [x] Define renderer-neutral Rust scene types and invariants.
- [x] Define template bindings and deterministic grid layout.

## Phase 2: PRISMA reference recipes

- [x] Implement new-review databases/registers only.
- [x] Implement new-review databases/registers plus other sources.
- [x] Implement updated-review databases/registers only.
- [x] Implement updated-review databases/registers plus other sources.
- [x] Add structured exclusion reasons and records/reports/studies arithmetic.

## Phase 3: Renderers and interfaces

- [x] Implement accessible standalone SVG.
- [x] Implement complete plain text and canonical scene JSON.
- [x] Add the `standardflow diagram prisma` CLI surface.
- [x] Add valid synthetic fixtures for all four templates.

## Phase 4: Evidence and review

- [x] Add unit, property, integration, accessibility and CLI tests.
- [x] Add schema, XML and generated-output validation.
- [x] Commit all 12 golden outputs and verify their byte-for-byte regeneration in permanent CI for the original head.
- [x] Obtain green strict Rust, cross-platform, schema and drift receipts for the recorded original head.
- [x] Review bounded-input and non-visual-flow findings and retain the correction tasks in `review-hardening.md`.


## Review fixes: bounded inputs and complete non-visual flow

- [x] Define shared parser, cardinality, layout and text limits.
- [x] Mirror schema constraints in Rust and add adversarial tests.
- [x] Separate recipe, source-standard and node-reference identifier grammars.
- [x] Enforce version, contract-ID and optional edge-label parity.
- [x] Reject XML-invalid content before SVG serialization.
- [x] Include directed edge relationships in the text equivalent and SVG description.
- [x] Add bounded CLI reads and regenerate all reference artefacts.
- [x] Retain original-head permanent-CI receipt [43308301190](https://github.com/edithatogo/standards_check/actions/runs/43308301190) for Linux, macOS and Windows.

## Current integration and external gates

- [x] Reconcile the existing diagram implementation with the repaired pack and CLI runtime.
- [x] Record passing hosted Rust, platform, schema and drift checks at `bfe2255fda85b891c2f68044676c0b777d92c38c`.
- [ ] Complete independent PRISMA source, methodological and usability/accessibility evaluation.
- [ ] Confirm item-level rights and migration parity through separate retained evidence.
- [ ] Establish publication or external acceptance through a separate retained receipt.

Passing SVG semantics and accessibility assertions establish only the tested fixture properties;
they do not certify general accessibility, methodological validity or third-party recipe safety.

## Ponytail review — 22 November 2026

- [x] SVG reading order, accessibility gate and identifier bounds: published at `c64c61a0a978b4b50f8d525fc76d6548d2e75718`; verification is linked below.
- [x] Retain findings, negative regressions, local receipts and outstanding gates in the [review record](../../ponytail-review-20261122.md).

## Recipe text-metric correction — 23 November 2026

- [x] Carry recipe padding and line height through the scene contract into SVG rendering.
- [x] Reject invalid metrics and text boxes that cannot contain their declared line geometry.
- [x] Bound word and token wrapping by each node's computed inner width, rejecting impossible character capacity before layout.
- [x] Verify compact multiline labels and scene JSON round-trips while retaining all 12 default golden bytes.
- [ ] Record exact-revision hosted acceptance separately from local synthetic checks.

Local evidence and wire-compatibility details are recorded in
[the text-metric correction receipt](recipe-text-metrics-20261123.md).

## Candidate CONSORT/SPIRIT diagrams — 23 November 2026

- [x] Retain original **synthetic** CONSORT-informed participant flow and
  SPIRIT-informed assessment schedule with text equivalents and
  failure-on-count-mutation regression in
  [PR #121](https://github.com/edithatogo/standards_check/pull/121).
  These examples are not copies of official figures, operative recipe contracts
  or methodological/accessibility acceptance.
- [ ] Before accepting a real CONSORT 2025 flow, define a versioned input
  contract with groupwise enrolment/allocation/receipt/follow-up/analysis counts,
  reasons and overlap semantics, then check conservation using actual
  participant-state provenance. Follow-up loss and intervention discontinuation
  need not equal exclusions from the analysis set.
- [ ] Before accepting a SPIRIT 2025 schedule, define typed visit windows,
  optional/conditional activities and temporal ordering, with an accessible
  text equivalent and explicit protocol provenance.
- [ ] Reuse the existing recipe/scene/SVG/text engine, rather than creating
  a CONSORT-only renderer. Pin source edition, figure rights and
  item-by-item review under [issue #120](https://github.com/edithatogo/standards_check/issues/120).
  No change to four qualified PRISMA recipe families or 12 golden outputs.
