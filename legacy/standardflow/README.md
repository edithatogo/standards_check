# StandardFlow legacy renderer

> **Migration status:** this repository is the historical Python/Graphviz implementation and is now a migration source for the primary StandardFlow work in [`edithatogo/standards_check`](https://github.com/edithatogo/standards_check). It remains runnable during parity work, but it is not a second source of standards authority.

This code generates research artefacts including PRISMA, CONSORT and STROBE diagrams and checklist outputs. Its schemas, fixtures, tests and Git history will be imported into the primary repository through an evidence-gated, history-preserving migration.

## Current use

```bash
git clone https://github.com/edithatogo/standardflow.git
cd standardflow
pip install -r requirements.txt
python -m src.cli generate data/prisma_data.json -o prisma-example.svg
```

Graphviz is required for diagram generation; TIFF conversion also requires ImageMagick.

## Authority and migration boundary

- The code and tests in this repository describe legacy behaviour, not authoritative standard text.
- Hard-coded PRISMA/CONSORT/STROBE classes are migration inputs for generic, validated artefact recipes and a deterministic accessible scene graph.
- The primary repository owns Canonical Standard Packs, stable requirement IDs, rights/provenance, applicability, evidence state and future Rust interfaces.
- SearchRight remains authoritative for systematic-review state and PRISMA counts.
- The user has requested a history-preserving export into the primary repository, followed by making this legacy source private and archived. The primary will retain the runnable legacy reference while Rust parity and external qualification remain separately tracked.

See [`docs/migration/STANDARDS_CHECK_ADOPTION.md`](docs/migration/STANDARDS_CHECK_ADOPTION.md) and the Conductor track under [`conductor/`](conductor/tracks.md).

## Supported legacy artefacts

- PRISMA 2020 and updated-review flow diagrams;
- CONSORT and cluster-randomised flow diagrams;
- STROBE and cohort flow diagrams;
- CONSORT, STROBE and STARD-family checklist generation;
- JSON-schema validation, CLI, Flask UI, examples and snapshot tests.

The migration inventory is machine-readable at [`integration/standards-check-adoption.json`](integration/standards-check-adoption.json).

## Run and verify the legacy reference

```bash
python -m src.cli list
python -m src.cli validate data/prisma_data.json
python -m src.cli generate data/prisma_data.json -o diagram.svg
python -m src.cli generate data/care_checklist.json -o care.md
python -m unittest discover -s tests -v
python scripts/check_primary_adoption.py
```

`--style style.json` applies a style object; `--set records_screened=800` overrides
an input field before validation. Diagrams support PNG, SVG, PDF, EPS, TIFF and
SVG-backed Typst (`.typ` plus its sibling `.svg`). A checklist `.md` target produces
one file; an extensionless target preserves the legacy section-directory output.

Canonical example notebooks live in [`examples/notebooks/`](examples/notebooks/)
and read fixtures from [`data/`](data/). Open them with their notebook directory
as the working directory. The test suite executes every notebook in an isolated
copy and checks the six generated diagram images.

The Flask interface accepts typed forms or raw JSON, returns PNG/SVG/PDF through
native download links and creates checklist ZIPs from the submitted payload.
Temporary renderer files are removed after each response. Checklist previews
show escaped Markdown text; they do not interpret user-supplied HTML.

See the [review and consolidation receipt](docs/reviews/2026-11-22-pull-request-review.md)
for exact inputs, checks and remaining gates.

## Licence

This repository is licensed under the Apache License 2.0. Imported code and notices must retain those obligations in the primary repository.
