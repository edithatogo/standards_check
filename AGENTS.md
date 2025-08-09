# Repository Guidelines

## Project Structure & Module Organization
- Pipeline: `source/` → `markdown/` → `typst/` → `latex/`.
- Two tracks in each stage:
  - `archetypes/` — high-level checklists (e.g., `prisma-2020`).
  - `variants/` — extensions/discipline-specific variants (e.g., `prisma-scr-2018`).
- Directories:
  - `source/{archetypes,variants}/` — originals + sidecar metadata.
  - `markdown/{archetypes,variants}/` — canonical `.md`.
  - `typst/{archetypes,variants}/` — `.typ`.
  - `latex/{archetypes,variants}/` — `.tex`.
  - `scripts/` — validation and helpers.
  - `.github/` — PR templates and automation.
- Naming: kebab-case mirrored across stages (e.g., `prisma-2020.md|.typ|.tex`).

## Build, Test, and Development Commands
- Validate Markdown basics: `bash scripts/validate_md.sh` (checks H1 + naming, nested folders).
- Manual flow:
  1) Place raw files in `source/` with a short `README` block at top or sidecar notes.
  2) Create cleaned `.md` in `markdown/` using consistent sections (Title, Purpose, Items).
  3) Convert to `.typ` in `typst/` (maintain item numbers and headings).
  4) Convert to `.tex` in `latex/` (use standard article class unless specified).
 - Build via Pandoc: `bash scripts/build_pandoc.sh` (produces LaTeX/PDF/DOCX; Typst if available). Use `FORMS=eforms` for richer PDF widgets.

## Coding Style & Naming Conventions
- Markdown: one H1 (`# Title`) per file; sentence case; `-` for bullets; wrap ~100 chars.
- Checklists: use numbered sections; include a brief “Scope” and “Reference”.
- Typst/LaTeX: keep identifiers/kebab-case filenames matching the Markdown source.
- Links: prefer relative paths; embed images from `assets/` when needed.

## Testing Guidelines
- Run `scripts/validate_md.sh` and `scripts/validate_index.sh` before PRs.
- Ensure file triplets exist per checklist within the correct track: `source/{archetypes|variants}/<name>.*`, `markdown/{archetypes|variants}/<name>.md`, `typst/{archetypes|variants}/<name>.typ`, `latex/{archetypes|variants}/<name>.tex`.
- Visual/manual check: numbering, section headings, and item text must match across stages.

## Commit & Pull Request Guidelines
- Conventional Commits, e.g., `docs(markdown): add prisma-consort checklist`.
- PRs: description of source, citation/provenance, screenshots (if formatting changes), and checklist of produced artifacts.
- Keep PRs scoped to one checklist or a focused batch; update cross-links if files move.

## Security & Licensing Notes
- Do not commit proprietary content or secrets.
- Respect source licensing; include citation in the Markdown header or sidecar notes.
