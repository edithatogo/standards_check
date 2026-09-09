# Plan: Semantic diagram engine and PRISMA 2020 flows

Status: **in progress**. Implementation: **source implemented**. Evidence: **source verified** until stacked pull-request CI produces compiler and fixture receipts.

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
- [ ] Generate and commit all 12 golden outputs in the branch bootstrap workflow.
- [ ] Obtain green strict Rust, cross-platform, schema and drift receipts.
- [ ] Review automated PR findings and append correction tasks where required.


## Review fixes: bounded inputs and complete non-visual flow

- [x] Define shared parser, cardinality, layout and text limits.
- [x] Mirror schema constraints in Rust and add adversarial tests.
- [x] Reject XML-invalid content before SVG serialization.
- [x] Include directed edge relationships in the text equivalent and SVG description.
- [x] Add bounded CLI reads and regenerate all reference artefacts.
- [ ] Retain an observed permanent-CI receipt for Linux, macOS and Windows.
