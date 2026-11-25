# Contributing

Thank you for contributing. This repository is documents-first and pipeline-driven.

- Start with `AGENTS.md` for coding style, naming, and PR requirements.
- Start work from the [Conductor index](conductor/index.md), affected track and owning issue.
- Use [the content intake workflow](CONTENT_POPULATION_WORKFLOW.md) for source, edition, rights and interpretation decisions.

## Core workflow

Canonical Standard Packs and their schemas, contracts and locks define the structured
representation. The historical `source/index.yml` and document pipeline are compatibility
surfaces, not independent authority for pack admission. The legacy `make scaffold` command
creates missing document stubs only. Never treat it as source verification or approval.

Use the existing validators and preserve imported and frozen source bytes. A new candidate
may be held even when its software checks pass.

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

## Test performance and experiment records

The protected Python job retains native pytest timings in its log and JUnit XML in the
existing coverage artifact. Use the same test scope and coverage configuration when
comparing serial runs. Inspect the slowest cases and installation/validator durations
before changing fixtures or adding parallelism. Do not reduce required coverage, test
counts, platform checks or failure retention to improve a timing metric.

For experiment and model work, follow the [frontier evaluation record](docs/research/frontier-evaluation-20261125.md)
and [publication evidence skill](.agents/skills/publication-evidence/SKILL.md).

For the ordinary Linux Python 3.12 coverage lane, use the exact [CI wheel closure](requirements/ci-python312-linux-x86_64.lock.txt) and its [input hashes](requirements/ci-python312-linux-x86_64.inputs.sha256). The portable profiles remain the declarations; regenerate and review the platform lock when they change. The [controlled efficiency trial](docs/research/frontier-evaluation-20261125.md) supports two-worker execution with file scheduling and no worker restarts. Do not extrapolate its measured speed gain to the full pipeline or drop a required test. Other operating systems and the explicit optional reference profile are not qualified by this Linux lock.
