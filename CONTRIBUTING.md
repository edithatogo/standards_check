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

Use Python 3.12 and install the pinned test and assurance profiles in your active
environment. Install Node.js 24, a Go toolchain for the Gitleaks hook, `shellcheck`,
and the Vale version pinned in the assurance workflow before enabling all hooks.
Vale is available from its [official releases](https://github.com/vale-cli/vale/releases);
CI verifies the exact Linux archive checksum before extracting its binary.

```bash
python -m pip install -r requirements/python-tests.txt
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
`workflow-policy` job validates the hook configuration and runs ESLint, Ruff lint and
format checks, Bandit and Vale. The hook repositories are pinned to exact commits.
The required Rust job also enforces `cargo fmt` and `cargo clippy -- -D warnings`
before measuring coverage.

Ruff owns both Python formatting and linting under `scripts/`. The hooks check
formatting without modifying files; use `ruff format scripts` for an intentional
formatting change. The ty checker covers repository and contract validators,
dependency receipts and shared XML ingress, as listed in `ty.toml`; CI runs it in
the installed Python test environment and treats warnings as failures. Optional
model and research-report modules have not yet been qualified for type enforcement.
Bandit rejects medium or high severity findings with medium or high confidence
across maintained scripts. The sole XML parsing exception is documented at the
bounded, entity-rejecting parser and covered by adversarial parser tests.

Vale checks active author prose for repeated words, product-name casing and
descriptive link labels. Its allowlist is in the hook configuration: published
specification/protocol snapshots, imported guidelines and generated pages are
outside that scope. Native Vale tests exercise both individual rules and their
activation through the project configuration.

To reproduce these checks locally:

```bash
pre-commit validate-config
for hook in eslint ruff ruff-format ty bandit vale; do
  pre-commit run "$hook" --all-files --show-diff-on-failure
done
vale test --no-global --coverage config/vale/styles
```

A configured hook is not evidence that it ran: retain the command result for the
revision being reviewed. The broader offline runner, release provenance/signing and
independent source/methodology acceptance gates remain in Conductor Track 05.
