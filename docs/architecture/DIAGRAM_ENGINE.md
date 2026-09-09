# StandardFlow semantic diagram engine

## Pipeline

```text
validated evidence + versioned recipe
  → explicit template bindings
  → deterministic integer layout
  → renderer-neutral semantic scene graph
  → SVG / text / canonical scene JSON
```

The recipe, input and scene are versioned machine contracts. SVG and text are generated projections and never write back into canonical standards or review state.

## Scene semantics

A scene records:

- semantic node roles: source, process, exclusion, prior and outcome;
- semantic edge roles: progression, exclusion, lineage and merge;
- stable IDs, integer geometry and orthogonal anchors;
- complete reading order;
- unwrapped labels, deterministic display lines and accessible labels;
- title, description and complete non-visual text equivalent.

Scene validation fails closed for duplicate or unsafe IDs, missing edge endpoints, self-edges, overlapping nodes, overflow/out-of-bounds geometry and incomplete reading order.

## Deterministic rendering

The reference layout uses no browser, Graphviz, font metric service, model or network call. Recipe dimensions and an integer character-width approximation determine wrapping and geometry. Edges are routed orthogonally between explicit anchors. Repeated rendering of the same validated scene produces byte-identical output.

SVG uses `role="img"`, linked `<title>` and `<desc>` elements, a metadata text equivalent, and labelled node groups exposed as a list. The plain-text renderer is a first-class output rather than an afterthought. Canonical scene JSON supports downstream PDF, DOCX, Typst, LaTeX, WASM and publisher adapters without reparsing SVG.

## PRISMA 2020 reference slice

Four built-in recipes cover:

1. new review using databases and registers only;
2. new review using databases/registers plus other methods;
3. updated review using databases and registers only;
4. updated review using databases/registers plus other methods.

The input distinguishes records, reports and studies; pre-screening removals; retrieval failures; structured report-exclusion reasons; prior-review lineage; newly included studies/reports; and total included studies/reports. Arithmetic is validated before binding or rendering.

SearchRight remains authoritative for review state and count provenance. StandardFlow consumes a validated count envelope and can reject or render it; it cannot change screening decisions or silently repair inconsistent counts.

## Next extensions

CONSORT participant flows, STROBE/STARD selection flows, prediction-model and diagnostic pathways, timelines, standards relationship graphs and state-machine diagrams should reuse the same scene contract. PDF/raster output should derive from the semantic scene while preserving accessibility and provenance, not from bespoke standard-specific classes.
