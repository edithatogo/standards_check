# TODO — Phase 3: Create Markdown Versions

- [ ] Getting started: copy `markdown/_template.md` into `markdown/{archetypes|variants}/<name>.md` and fill Title, Scope, Items, Reference, Version.
- [ ] Use task lists (`- [ ] Item`) and `.textfield` spans for notes; these become PDF form fields via the Lua filter.
- [ ] For each index entry, create `markdown/{archetypes|variants}/<name>.md` from the template.
- [ ] Preserve numbering and section headings matching the source.
- [ ] Include citation/provenance at the top or bottom of the file.
- [ ] Run `bash scripts/validate_md.sh` and fix any issues.
- [ ] Link-check internal references and relative asset paths.
- [ ] Verify CI builds (see `.github/workflows/build-docs.yml`) and download artifacts (PDF/LaTeX/DOCX) from the Action run.
- [ ] Update `source/index.yml` with `status: markdown_done` and path to the Markdown file.
