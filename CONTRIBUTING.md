# Contributing

Thank you for contributing. This repository is documents-first and pipeline-driven.

- Start with `AGENTS.md` for coding style, naming, and PR requirements.
- Use `ROADMAP.md` and `todos/` to pick the next task.
- If you have internet access, follow `HANDOFF.md` to verify sources, ingest originals, and transcribe items.

## Core Workflow

This project uses a data-driven approach to manage checklists. All checklist information is stored in YAML files under the `source/` directory. The primary file is `source/index.yml`, which contains a master list of all checklists and their metadata.

To add a new checklist, you must first add a new entry to `source/index.yml`. Then, run the following command to generate the necessary files:

`make scaffold`

This will create the markdown file, citation file, and other necessary assets based on the information in `source/index.yml`. **Do not create these files manually.**

## Quick Commands
- `make validate`: Run all local validators.
- `make build`: Generate PDF/LaTeX/DOCX from Markdown.
- `make scaffold`: Create missing Markdown stubs from the index.
- `make list-tbd`: Find all placeholder "TBD" values.
- `make index`: Regenerate `markdown/index.md`.
- `make clean`: Remove generated artifacts.

## PR Checklist
- Use the provided PR template and complete all boxes.
- Keep PRs focused (one checklist or a small batch).
- Include artifacts (PDF/DOCX) via CI run links when helpful.

## Local commit checks

Install `pre-commit`, a Go toolchain for its Gitleaks environment, and the `shellcheck`
executable before enabling the hooks:

```bash
python -m pip install --no-deps -r requirements/assurance-tools.txt
python -m pip check
pre-commit install
pre-commit run --files path/to/changed-file
```

The hooks scan staged changes for secrets, check shell scripts, and fix whitespace in
maintained text files. Formatting hooks exclude original source material, archives, assets
and generated document directories, and preserve Markdown hard linebreaks. The configured
ESLint safety profile covers maintained JavaScript in `api/`, `scripts/` and `tests/`,
using the same pinned hook locally and in the required `assurance` workflow. Its
`workflow-policy` job validates the hook configuration and runs ESLint on all tracked
maintained JavaScript with warnings treated as errors. The required Rust job also
enforces `cargo fmt` and `cargo clippy -- -D warnings` before measuring coverage.

Install Node.js 24 for the ESLint hook. To reproduce its CI check locally:

```bash
pre-commit validate-config
pre-commit run eslint --all-files --show-diff-on-failure
```

A configured hook is not evidence that it ran: retain the command result for the
revision being reviewed. The broader offline runner, release provenance/signing and
independent source/methodology acceptance gates remain in Conductor Track 05.
