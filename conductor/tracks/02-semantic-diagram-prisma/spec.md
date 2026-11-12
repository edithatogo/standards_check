# Semantic diagram engine and PRISMA 2020 flows

## Objective

Implement a generic, data-driven diagram kernel that converts validated evidence plus a versioned artefact recipe into a deterministic, accessible semantic scene and renders that scene as SVG, plain text or canonical JSON. Prove the kernel with all four official PRISMA 2020 flow families.

## Authority boundaries

- SearchRight remains the system of record for review state and PRISMA counts.
- StandardFlow validates arithmetic and renders a receipt; it does not alter screening decisions or invent missing counts.
- Recipe JSON and scene JSON are machine contracts. SVG and text are generated projections.
- The PRISMA reporting pack remains `imported_unverified`; rendering tests do not claim item-by-item methodological validation.
- No model is required for layout, arithmetic, accessibility or rendering.

## Acceptance assertions

1. A strict recipe schema represents semantic nodes, edges, reading order, bindings, layout and supported outputs.
2. Four strict PRISMA input variants enforce template presence and deterministic records/reports/studies arithmetic.
3. The layout engine uses integer arithmetic and produces the same scene on repeated runs.
4. Scene validation rejects duplicate IDs, missing endpoints, overlap, out-of-bounds geometry and incomplete reading order.
5. SVG exposes an image title, description, full text equivalent and labelled list-item nodes.
6. Plain-text output is complete without requiring the visual diagram.
7. Canonical scene JSON validates against a versioned schema.
8. Twelve generated reference artefacts remain drift-free in CI.
9. Linux strict Clippy/tests and Linux/macOS/Windows tests pass before evidence promotion.
