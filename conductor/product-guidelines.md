# Product Guidelines

## Brand & Voice
- Professional, academic, and rigorous.
- Clear, unopinionated, and faithful to original scholarly standards and reporting checklists.

## File Organization & Naming
- Strictly adhere to `kebab-case` for file names and identifiers.
- Match structure symmetrically across formats: `source/`, `markdown/`, `typst/`, `latex/`.
- Differentiate between `archetypes/` (high-level checklists) and `variants/` (extensions).

## Data Principles
- Source authenticity must be maintained. Provide provenance, URLs, checksums, and versioning info in `sidecar.yml` files (defined by schemas).
- The pipeline follows `source/` -> `markdown/` -> outputs (`pdf`, `latex`, `typst`, `docx`).
- Interactive forms (`.textfield`, checkboxes) should be preserved wherever specified for output PDF/HTML form elements.