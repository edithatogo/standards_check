# Standards Checklists

Simple pipeline for academic publication checklists:
1) Collect originals into `source/`.
2) Produce edited Markdown in `markdown/`.
3) Produce Typst in `typst/`.
4) Produce LaTeX in `latex/`.

## Structure
- `source/` — raw checklists (PDF/HTML/DOCX/CSV) + provenance notes.
  - `archetypes/` high-level checklists; `variants/` discipline-specific variants.
- `markdown/` — first canonical form (`.md`).
  - `archetypes/` and `variants/` mirrored structure.
- `typst/` — Typst format (`.typ`).
  - `archetypes/` and `variants/` mirrored structure.
- `latex/` — LaTeX format (`.tex`).
  - `archetypes/` and `variants/` mirrored structure.
- `scripts/` — helper tools (validation, conversion stubs).

## Quickstart
1. Start with archetypes: add a source file to `source/archetypes/` (use kebab-case names).
2. Create `markdown/archetypes/<name>.md` with clear sections (Title, Scope, Items, Reference).
3. Translate to `typst/archetypes/<name>.typ` and `latex/archetypes/<name>.tex`, keeping numbering/headings aligned.
4. Validate Markdown: `bash scripts/validate_md.sh`.

## Helper Scripts
- `scripts/sidecar_new.sh <track> <id> <title> <group> <version>`: create a sidecar template in `source/<track>/<id>.yml`.
- `scripts/checksum.sh <file> [sidecar.yml]`: compute SHA-256; optionally write `checksum:` into a sidecar.
- `scripts/build_pandoc.sh`: convert all Markdown files to LaTeX (`latex/`), PDF (`pdf/`), and DOCX (`docx/`). If your Pandoc includes a Typst writer, it will also generate `.typ`.
- `scripts/ingest_source.sh <track> <id> <url> [ext]`: download an original into `source/<track>/<id>.<ext>`, compute checksum, and update the sidecar.
- `scripts/validate_repo.sh`: run all local validations (Markdown, index, sidecars).
- `scripts/scaffold_from_index.sh`: create missing Markdown stubs from `source/index.yml`.
- `scripts/generate_markdown_index.sh`: generate `markdown/index.md` with links to all checklists.

## Pandoc-Based Builds
- Install Pandoc locally. Optional: LaTeX engine (e.g., TeX Live) for PDF output.
- Run: `bash scripts/build_pandoc.sh`.
- Template: `templates/pandoc/latex-checklist.tex` wraps the document in a PDF `Form` environment. For fully interactive checkboxes/text fields, add raw LaTeX form commands or a Lua filter (see notes below).

### Interactive PDF Notes
- Pandoc can produce interactive PDFs via LaTeX form fields (`hyperref` provides `\TextField`, `\CheckBox`, etc.).
- Two approaches:
  - Embed raw LaTeX in Markdown for specific fields.
  - Use the included Pandoc Lua filter (`filters/forms.lua`) to turn task list items and textfield spans into form fields automatically.

#### Raw LaTeX in Markdown (simple and explicit)
Example (inline raw for LaTeX only):

```markdown
## Item 1

```{=latex}
\mkCheckBox[name=consort_item_1,width=1em]{} Item 1 met?
\mkTextField[name=consort_item_1_notes,width=12cm]{Notes}
```
```

- The template defines `\mkCheckBox`/`\mkTextField` that map to `hyperref` by default, or to AcroTeX `eforms` if you build with `FORMS=eforms`.
- Build with eForms: `FORMS=eforms bash scripts/build_pandoc.sh`.

#### Using the Lua Filter (simplest authoring)
- Task lists become checkboxes:
  - `- [ ] Item text` → checkbox with label “Item text”.
  - `- [x] Completed item` → checkbox initially checked.
- Text fields via spans with attributes:
  - Markdown: `[Notes]{.textfield name=consort_item_1_notes width=12cm}`
  - Filter outputs: `\mkTextField[name=consort_item_1_notes,width=12cm]{Notes}`
- The build script auto-loads the filter if `filters/forms.lua` exists.

## CI Conversion (Minimal Automation)
- GitHub Actions workflow: `.github/workflows/build-docs.yml`.
- Triggers on pushes and PRs that modify `markdown/**`, the Pandoc template, or the build script.
- Produces artifacts:
  - `pdf/` → downloadable PDFs
  - `latex/` → generated `.tex`
  - `docx/` → generated Word files
- Access artifacts: open a run in the Actions tab, download the artifacts bundle(s).

## Make Targets
- `make validate` → run all validators
- `make build` → run Pandoc conversions
- `make scaffold` → create missing Markdown files from index
- `make index` → generate `markdown/index.md`
- `make list-tbd` → Find all placeholder "TBD" values that need to be filled.
- `make clean` → Remove all generated build artifacts.

## Roadmap & Tasks
- High-level phases are tracked in `ROADMAP.md`.
- Detailed, actionable tasks per phase are in `todos/`.

## Handoff
- See `HANDOFF.md` for next-agent instructions (verification, ingestion, transcription, build, and PR steps).

## Publishing (Low Maintenance)
- Planned: GitHub Pages serves `markdown/` directly via Actions.
- See `todos/phase-06-docs-publishing.md` for setup steps.

## Cycles
- Cycle 1: Archetypes (high-level checklists only).
- Cycle 2: Expand archetypes (discover additional high-level checklists).
- Cycle 3: Variants (iterate through all extensions/variants by checklist type).

## Contribution & Standards
- Read `AGENTS.md` for style, naming, and PR requirements.
- PR template enforces artifact checklist.

## License & Changelog
- Licensing: CC BY 4.0 for documentation; MIT for code (see `LICENSE.md`).
- Changes are tracked in `CHANGELOG.md`.
- Note: The first content step after mapping is sourcing originals into `source/{archetypes|variants}/` (use `scripts/ingest_source.sh`). Only then transcribe into Markdown.
