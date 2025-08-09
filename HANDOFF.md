# Handoff Guide (Next Agent)

This repository is prepared for a two-part workflow. Your role (with internet access) is to verify sources, ingest originals, and transcribe official items.

## Current Status (offline-ready)
- Mapping complete for initial archetypes in `source/index.yml` (marked `status: mapped`).
- Sidecar metadata files exist in `source/archetypes/*.yml` with unverified placeholders (URL, date, license).
- Markdown checklist stubs exist in `markdown/archetypes/*.md` with clear sections and [TBD] items.
- Build/validation tooling is in place (`scripts/*`) and CI converts Markdown → LaTeX/PDF/DOCX on push.

## Your Tasks (with internet access)
1) Verify metadata
- For each ID in `source/index.yml`, open `source/archetypes/<id>.yml` and fill:
  - `source_url` (canonical page or direct file), `publisher`, release `date`, and `license`.
  - Set `verified: true` when confirmed.

2) Ingest originals
- Download via helper: `bash scripts/ingest_source.sh archetypes <id> <URL> [ext]`
- This saves to `source/archetypes/<id>.<ext>`, sets `retrieved_at`, and computes `checksum`.

3) Transcribe to Markdown
- Open `markdown/archetypes/<id>.md` and replace the [TBD] items with the official checklist text.
- Keep numbering/section headings consistent with the source.
- Use task lists `- [ ]` for checkbox items and `.textfield` spans for free-text inputs.

4) Validate and build
- Validate: `bash scripts/validate_index.sh` and `bash scripts/validate_md.sh`.
- Build artifacts locally (optional): `bash scripts/build_pandoc.sh`.
- Push your branch; CI will attach PDFs/LaTeX/DOCX as run artifacts.

## Reference
- Templates and filters: `templates/pandoc/latex-checklist.tex`, `filters/forms.lua`.
- Helper scripts: `scripts/sidecar_new.sh`, `scripts/ingest_source.sh`, `scripts/checksum.sh`, `scripts/build_pandoc.sh`.
- PR template: `.github/pull_request_template.md` (complete the checklist before requesting review).

