# Repository Guidelines

## Authority and Current Work
- Read `conductor/index.md`, `conductor/workflow.md`, and the affected track before changes.
- `packs/`, `schemas/`, `contracts/`, and `recipes/` define StandardFlow's structured contracts;
  `crates/` contains the Rust core, artefact engine, and CLI.
- The document pipeline below is a legacy compatibility surface. Its generated views are not
  canonical Standard Packs and do not establish source rights or methodological validity.
- Keep exact-commit verification receipts and remaining gates in the existing Conductor tracks.
- For source acquisition, extraction changes, drift or session close-out, use `.agents/skills/source-reconciliation-retrospective/SKILL.md` and the deterministic receipt review before proposing refinements.

## Project Structure & Module Organization
- Pipeline: `source/` → `markdown/` → `typst/` → `latex/`.
- Two tracks in each stage:
  - `archetypes/` — high-level checklists (e.g., `prisma-2020`).
  - `variants/` — extensions/discipline-specific variants (e.g., `prisma-scr-2018`).
- Directories:
  - `source/{archetypes,variants}/` — originals + sidecar metadata.
  - `markdown/en/{archetypes,variants}/` — current English `.md` views; older scaffold tooling
    also supports `markdown/{archetypes,variants}/`.
  - `typst/{archetypes,variants}/` — `.typ`.
  - `latex/{archetypes,variants}/` — `.tex`.
  - `scripts/` — validation and helpers.
  - `.github/` — PR templates and automation.
- Naming: kebab-case mirrored across stages (e.g., `prisma-2020.md|.typ|.tex`).

## Build, Test, and Development Commands
- Install Python regression dependencies with `python -m pip install -r requirements/python-tests.txt`.
- Run offline regressions: `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 python -m pytest --import-mode=importlib tests test_extract_and_convert.py`.
- Validate structured contracts: `python scripts/validate_foundation.py`,
  `python scripts/validate_packs.py`, and `python scripts/validate_artifacts.py`.
- Use the exact Rust toolchain in `rust-toolchain.toml`:
  `cargo fmt --all -- --check`,
  `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings`, and
  `cargo test --workspace --all-targets --all-features --locked`.
- Run `make validate` for the legacy corpus and `make html` for its HTML views.
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
- For legacy checklist changes, verify matching names across `source/`, `markdown/en/`, `typst/`,
  and `latex/` within the appropriate archetype or variant directory.
- Regression tests must demonstrate rejection of invalid input as well as successful input.
  A validator that prints an error must return a nonzero exit status.
- Regenerate changed artefacts and compare them against the committed reference files.
- Visual/manual check: numbering, section headings, and item text must match across stages.

## Commit & Pull Request Guidelines
- Conventional Commits, e.g., `docs(markdown): add prisma-consort checklist`.
- PRs: description of source, citation/provenance, screenshots (if formatting changes), and checklist of produced artifacts.
- Keep PRs scoped to one checklist or a focused batch; update cross-links if files move.

## Security & Licensing Notes
- Do not commit proprietary content or secrets.
- Respect source licensing; include citation in the Markdown header or sidecar notes.

## Solo-maintainer assurance
- Start with the affected Conductor track, active GitHub issue and exact main revision.
- Run `make quick` before focused changes; run the applicable full CI checks before merge.
- Treat advisory scores as diagnostics, not a target to game. Preserve the required privacy,
  CodeQL, assurance and inventory checks and resolve review threads.
- Maintain one routine Renovate group, separate breaking/security updates, and verify actual
  receiving-main dependency lock, inventory and security evidence. Do not disable the
  existing Dependabot path until a protected Renovate handover has been demonstrated.
- Never treat historical or queued CI results, proposed version updates, or source candidate
  observations as current verification. Record accepted and held work separately.
