# Sourcing Originals

This folder stores original checklist files with sidecar metadata.

## Layout
- `archetypes/` — high-level, canonical checklists (e.g., prisma-2020.pdf).
- `variants/` — discipline-specific/extensions (e.g., prisma-s-2021.pdf).
- `index.yml` — master inventory across archetypes and variants.

## Sidecar Metadata
Create a `<name>.yml` next to each original using the template in `archetypes/_meta.template.yml`.

Required keys
- `id`, `title`, `group`, `version`, `date`, `publisher`, `source_url`,
  `retrieved_at`, `preferred_format`, `checksum`, `license`.

## Naming
- Use kebab-case for files: `<name>.<ext>` and `<name>.yml`.
- Keep `<name>` consistent across all stages (markdown/typst/latex).

## Provenance
- Prefer canonical sources (official publisher/EQUATOR page) and record `source_url`.
- Store checksums to ensure integrity.

## Workflow Snippet
1. Create a sidecar: `bash scripts/sidecar_new.sh archetypes prisma-2020 "PRISMA 2020 Checklist" prisma 2020`
2. Ingest the original: `bash scripts/ingest_source.sh archetypes prisma-2020 <URL-to-PDF-or-DOCX>` (downloads, sets checksum, sets `source_url` and `retrieved_at`).
3. Fill any remaining fields (`publisher`, `license`).
4. Proceed to Markdown transcription in `markdown/archetypes/`.
