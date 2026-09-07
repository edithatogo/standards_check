# Diagram and artefact engine

Standards-specific Python classes are replaced by validated data plus generic Rust renderers.

```text
Evidence data + versioned recipe
  → semantic graph
  → deterministic constraint layout
  → accessible scene graph
  → SVG / PDF / PNG / TIFF / HTML / text-table projections
```

The semantic scene graph owns node roles, labels, data bindings, reading order, alt text, grouping, edge meaning, provenance and accessibility metadata. Visual layout is a projection, not the source of meaning.

## PRISMA reference slice

Implement the four official PRISMA 2020 flow families: new and updated reviews, each with a “databases/registers only” and an “other sources included” template. Validate records, reports and studies as distinct entities; removals, exclusions, retrieval failures and reasons are structured. SearchRight remains authoritative for review state and counts. StandardFlow validates and renders a versioned PRISMA ledger receipt.

## Later recipes

CONSORT participant flows and extensions; STROBE/STARD selection flows; prediction-model and diagnostic flows; schedules, timelines, intervention descriptions, evidence maps, standards relationship graphs, version-diff diagrams and workflow state machines.
