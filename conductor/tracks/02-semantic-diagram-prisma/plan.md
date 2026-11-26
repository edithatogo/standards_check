# Plan: Semantic diagram engine and PRISMA 2020 flows

Status: **implementation complete; hosted integration accepted**. Implementation: **source implemented**. Evidence: **fixture proven** for the bounded diagram invariants and four synthetic PRISMA families. Hosted acceptance applies to PR #60 revision `bfe2255fda85b891c2f68044676c0b777d92c38c`; exact receipts and historical verification are retained in [evidence.json](evidence.json). Independent source, rights, migration, methodological, usability/accessibility and publication obligations remain open.

## Phase 1: Semantic contracts

- [x] **T02.001** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Define strict recipe, PRISMA-flow and scene-graph schemas.
- [x] **T02.002** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Define renderer-neutral Rust scene types and invariants.
- [x] **T02.003** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Define template bindings and deterministic grid layout.

## Phase 2: PRISMA reference recipes

- [x] **T02.004** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Implement new-review databases/registers only.
- [x] **T02.005** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Implement new-review databases/registers plus other sources.
- [x] **T02.006** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Implement updated-review databases/registers only.
- [x] **T02.007** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Implement updated-review databases/registers plus other sources.
- [x] **T02.008** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add structured exclusion reasons and records/reports/studies arithmetic.

## Phase 3: Renderers and interfaces

- [x] **T02.009** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Implement accessible standalone SVG.
- [x] **T02.010** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Implement complete plain text and canonical scene JSON.
- [x] **T02.011** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add the `standardflow diagram prisma` CLI surface.
- [x] **T02.012** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add valid synthetic fixtures for all four templates.

## Phase 4: Evidence and review

- [x] **T02.013** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add unit, property, integration, accessibility and CLI tests.
- [x] **T02.014** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add schema, XML and generated-output validation.
- [x] **T02.015** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Commit all 12 golden outputs and verify their byte-for-byte regeneration in permanent CI for the original head.
- [x] **T02.016** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Obtain green strict Rust, cross-platform, schema and drift receipts for the recorded original head.
- [x] **T02.017** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Review bounded-input and non-visual-flow findings and retain the correction tasks in `review-hardening.md`.


## Review fixes: bounded inputs and complete non-visual flow

- [x] **T02.018** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Define shared parser, cardinality, layout and text limits.
- [x] **T02.019** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Mirror schema constraints in Rust and add adversarial tests.
- [x] **T02.020** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Separate recipe, source-standard and node-reference identifier grammars.
- [x] **T02.021** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Enforce version, contract-ID and optional edge-label parity.
- [x] **T02.022** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Reject XML-invalid content before SVG serialization.
- [x] **T02.023** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Include directed edge relationships in the text equivalent and SVG description.
- [x] **T02.024** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add bounded CLI reads and regenerate all reference artefacts.
- [x] **T02.025** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Retain original-head permanent-CI receipt [43308301190](https://github.com/edithatogo/standards_check/actions/runs/43308301190) for Linux, macOS and Windows.

## Current integration and external gates

- [x] **T02.026** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Reconcile the existing diagram implementation with the repaired pack and CLI runtime.
- [x] **T02.027** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Record passing hosted Rust, platform, schema and drift checks at `bfe2255fda85b891c2f68044676c0b777d92c38c`.
- [ ] **T02.028** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Complete independent PRISMA source, methodological and usability/accessibility evaluation.
- [ ] **T02.029** ([#95](https://github.com/edithatogo/standards_check/issues/95)) Confirm item-level rights and migration parity through separate retained evidence.
- [ ] **T02.030** ([#158](https://github.com/edithatogo/standards_check/issues/158)) Establish publication or external acceptance through a separate retained receipt.

Passing SVG semantics and accessibility assertions establish only the tested fixture properties;
they do not certify general accessibility, methodological validity or third-party recipe safety.

## Ponytail review — 22 November 2026

- [x] **T02.031** ([#82](https://github.com/edithatogo/standards_check/issues/82)) SVG reading order, accessibility gate and identifier bounds: published at `c64c61a0a978b4b50f8d525fc76d6548d2e75718`; verification is linked below.
- [x] **T02.032** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Retain findings, negative regressions, local receipts and outstanding gates in the [review record](../../ponytail-review-20261122.md).

## Recipe text-metric correction — 23 November 2026

- [x] **T02.033** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Carry recipe padding and line height through the scene contract into SVG rendering.
- [x] **T02.034** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Reject invalid metrics and text boxes that cannot contain their declared line geometry.
- [x] **T02.035** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Bound word and token wrapping by each node's computed inner width, rejecting impossible character capacity before layout.
- [x] **T02.036** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Verify compact multiline labels and scene JSON round-trips while retaining all 12 default golden bytes.
- [ ] **T02.037** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Record exact-revision hosted acceptance separately from local synthetic checks.

Local evidence and wire-compatibility details are recorded in
[the text-metric correction receipt](recipe-text-metrics-20261123.md).

## Candidate CONSORT/SPIRIT diagrams — 23 November 2026

- [x] **T02.040** ([#120](https://github.com/edithatogo/standards_check/issues/120)) Retain original **synthetic** CONSORT-informed participant flow and
  SPIRIT-informed assessment schedule with text equivalents and
  failure-on-count-mutation regression in
  [PR #121](https://github.com/edithatogo/standards_check/pull/121).
  These examples are not copies of official figures, operative recipe contracts
  or methodological/accessibility acceptance.
- [ ] **T02.041** ([#120](https://github.com/edithatogo/standards_check/issues/120)) Before accepting a real CONSORT 2025 flow, define a versioned input
  contract with groupwise enrolment/allocation/receipt/follow-up/analysis counts,
  reasons and overlap semantics, then check conservation using actual
  participant-state provenance. Follow-up loss and intervention discontinuation
  need not equal exclusions from the analysis set.
- [ ] **T02.042** ([#120](https://github.com/edithatogo/standards_check/issues/120)) Before accepting a SPIRIT 2025 schedule, define typed visit windows,
  optional/conditional activities and temporal ordering, with an accessible
  text equivalent and explicit protocol provenance.
- [ ] **T02.043** ([#120](https://github.com/edithatogo/standards_check/issues/120)) Reuse the existing recipe/scene/SVG/text engine, rather than creating
  a CONSORT-only renderer. Pin source edition, figure rights and
  item-by-item review under [issue #120](https://github.com/edithatogo/standards_check/issues/120).
  No change to four qualified PRISMA recipe families or 12 golden outputs.
## Subsequent representations

- [ ] **T02.038** ([#128](https://github.com/edithatogo/standards_check/issues/128)) Evaluate optional Mermaid and GraphML projections from validated scenes with identity/edge conservation and explicit accessibility limits.
- [ ] **T02.039** ([#120](https://github.com/edithatogo/standards_check/issues/120)) Qualify CONSORT/SPIRIT source packs and trial-flow examples against their actual edition, source rights and methodological boundaries.


## Orthogonal format and net assurance

- [ ] **T02.060** ([#82](https://github.com/edithatogo/standards_check/issues/82), [#158](https://github.com/edithatogo/standards_check/issues/158)) Qualify bounded PNML marking reachability, invariants and witnesses; compare native/PM4Py outputs; evaluate lossless CST and deterministic normalization with original span, identifier and format conservation before adding dependencies.

See the [orthogonal assurance design](../../../docs/research/orthogonal-assurance-20261126.md); an exhausted search or unsupported format is held, not accepted.
