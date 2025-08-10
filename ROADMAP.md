# Roadmap

This repository runs in cycles, each cycling the same pipeline: map → source → markdown → typst → latex, with minimal-maintenance publishing at the end.

## Cycle 1 — Archetypes (High-level Checklists)
Focus on canonical, widely cited checklists (e.g., PRISMA 2020, CONSORT 2010).

- Phase 1A — Map: inventory archetypes in `source/index.yml` (`level: archetype`).
- Phase 2A — Source: collect originals into `source/archetypes/` with sidecar metadata.
- Phase 3A — Markdown: create `markdown/archetypes/<name>.md` from template.
- Phase 4A — Typst: create `typst/archetypes/<name>.typ`.
- Phase 5A — LaTeX: create `latex/archetypes/<name>.tex`.

## Cycle 2 — Expand Archetypes (Additional High-level)
Discover additional high-level checklists missed in Cycle 1.

- Phase 1B — Map: extend `source/index.yml` with new `level: archetype` items.
- Phase 2B — Source: add originals to `source/archetypes/`.
- Phase 3B — Markdown: add `markdown/archetypes/<name>.md`.
- Phase 4B — Typst: add `typst/archetypes/<name>.typ`.
- Phase 5B — LaTeX: add `latex/archetypes/<name>.tex`.

## Cycle 3 — Variants (Extensions and Discipline-specific)
Enumerate and process variants (e.g., PRISMA-S, PRISMA-ScR, CONSORT extensions).

- Phase 1C — Map: add `level: variant` items to `source/index.yml` and set `variant_of`.
- Phase 2C — Source: originals in `source/variants/`.
- Phase 3C — Markdown: `markdown/variants/<name>.md`.
- Phase 4C — Typst: `typst/variants/<name>.typ`.
- Phase 5C — LaTeX: `latex/variants/<name>.tex`.

## Publishing (Minimal Maintenance)
- Surface `markdown/` via GitHub Pages (Actions-based). See `todos/phase-06-docs-publishing.md`.

## Current Status Snapshot
- Cycle 1A mapping: Complete. All archetypes are listed in `source/index.yml`.
- Sourcing: Complete. All original source files for archetypes are collected in `source/archetypes/`.
- Markdown: Complete. All markdown files for archetypes have been created.
- Typst: Complete. All Typst files for archetypes have been generated.
- LaTeX: Complete. All LaTeX files for archetypes have been generated.
- Build: CI builds LaTeX/PDF/DOCX on changes to `markdown/**`.

## Future Cycles
- **Petri Net Conversion:** Convert Markdown checklists into hierarchical Petri nets for process mining analysis.
- **Citation Generation:** Extend the `source/*.yml` files to include comprehensive metadata for building citations. Develop a workflow (potentially using Pandoc) to generate `.ris`, `.bib`, and other common citation formats from this metadata.
- **Documentation Website:** Develop a GitHub Pages website to provide a user-friendly interface for browsing, viewing, and downloading the checklists and their associated references.
