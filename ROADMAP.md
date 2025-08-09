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
- Cycle 1A mapping: in progress; initial archetypes listed and sidecars added with placeholders.
- Sourcing: pending verification and download (see `HANDOFF.md`).
- Markdown: stubs created for archetypes to ease transcription.
- Build: CI builds LaTeX/PDF/DOCX on changes to `markdown/**`.
