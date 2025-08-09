# TODO — Phase 5: Create LaTeX Versions

- [ ] Quick-start (recommended): run `bash scripts/build_pandoc.sh` and review `latex/{archetypes|variants}/<name>.tex` and `pdf/{archetypes|variants}/<name>.pdf`.
- [ ] If manual control is needed: prepare `latex/_template.tex` (article class, sections, numbered list) and author `latex/{archetypes|variants}/<name>.tex`.
- [ ] Use standard packages only (keep minimal), add comments for any extras.
- [ ] Optional: compile locally (e.g., `latexmk -pdf`) to verify formatting.
- [ ] Update `source/index.yml` with `status: latex_done` and path to the LaTeX file.
