# TODO — Phase 4: Create Typst Versions

- [ ] Quick-start (recommended): run `bash scripts/build_pandoc.sh` and check `typst/{archetypes|variants}/<name>.typ` (generated if Pandoc has a Typst writer).
- [ ] If writer unavailable or refinement needed: prepare `typst/_template.typ` (title block, sections, numbered items) and hand-author `typst/{archetypes|variants}/<name>.typ`.
- [ ] Keep filenames aligned with Markdown (same `<name>`).
- [ ] Quick render check locally (Typst) to confirm layout and numbering.
- [ ] Update `source/index.yml` with `status: typst_done` and path to the Typst file.
