# Plan: Semantic diagram engine and PRISMA 2020 flows

Status: **implementation complete; integration acceptance pending**. Implementation: **source implemented**. Evidence: **fixture proven** for the bounded diagram invariants at original head `55bff593c6e91491ad50596baefae5626c6bf2c5`. Permanent CI receipts and the local repair boundary are retained in [evidence.json](evidence.json). Hosted checks for the final merged repair head remain pending.

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
- [ ] Obtain fresh hosted Rust, platform, schema and drift checks at the final PR #60 head.
- [ ] Complete independent PRISMA source, methodological and usability/accessibility evaluation.
- [ ] Establish publication or external acceptance through a separate retained receipt.

Passing SVG semantics and accessibility assertions establish only the tested fixture properties;
they do not certify general accessibility, methodological validity or third-party recipe safety.
