# Retained StandardFlow compatibility runtime

The repaired legacy runtime from `edithatogo/standardflow` is retained under
[`standardflow/`](standardflow/) with its complete Git history and Apache-2.0 licence.
Source revision `d89a5dbacc207cdce11f19efd667b83fdb09df18` includes the original main
and the reviewed compatibility repairs. Its exact tree is
`e48c081ff946d0fac6a1a4b65a3599c6b7aa3352`.
The imported tree is an exact snapshot, not a new canonical standards authority.
Use this repository for development and issues; the old repository is being retired.

## Run the legacy implementation

Create a separate Python 3.12 environment. Graphviz and ImageMagick are system dependencies.
From the receiving repository root:

```bash
python3.12 -m venv .venv-legacy
.venv-legacy/bin/python -m pip install --no-deps -r requirements/legacy-standardflow.txt
.venv-legacy/bin/python -m pip check
cd legacy/standardflow
../../.venv-legacy/bin/python -m src.cli generate data/prisma_data.json --output /tmp/prisma.svg
```

List the supported inputs through the same module entry point:

```bash
../../.venv-legacy/bin/python -m src.cli list
```

The original README, citation file, Dockerfile and workflows inside the snapshot are historical
source material. Only root `.github/workflows/standardflow-legacy.yml` runs receiving CI.
The receiving dependency closure includes the display helpers needed to execute notebook
examples as tests. An interactive Jupyter kernel remains optional.

## Verify the import

With a full Git checkout and the optional environment, run from the receiving root:

```bash
.venv-legacy/bin/python scripts/verify_legacy_standardflow.py --output /tmp/legacy-parity.json
```

This verifies exact ancestry/tree identity, reconstructs the source from local history, runs
52 tests in each isolated copy, including all 11 notebooks, and compares six diagram and
three checklist CLI canaries. It also verifies that invalid PRISMA input fails without output.
It has no dependency on access to the retired repository. The bounded result is behaviour
preservation in the same environment, not independent scientific or accessibility acceptance.

## Dependency ownership

Track 03 owns the optional 27-package Python closure in
`requirements/legacy-standardflow.txt`. It supports the legacy CLI/web renderer and
executes notebook fixtures in isolation from the primary runtime. Reconcile it with
source requirements when changing legacy behaviour; remove this closure only after
accepted replacement/consumer and rollback evidence permits retiring this surface.
Dependency upgrades are tracked in [#94](https://github.com/edithatogo/standards_check/issues/94).

The installed distribution metadata and shipped licence files identify these licences:

| Licence | Python distributions |
| --- | --- |
| Apache-2.0 | asttokens |
| BSD-2-Clause | Pygments |
| ISC | pexpect, ptyprocess |
| MIT | attrs, blinker, executing, graphviz, jedi, jsonschema, parso, pure_eval, pyrsistent, stack-data, wcwidth |
| BSD-3-Clause | click, Flask, ipython, ipython_pygments_lexers, itsdangerous, Jinja2, MarkupSafe, matplotlib-inline, prompt_toolkit, psutil, traitlets, Werkzeug |

System Graphviz and ImageMagick are separate dependencies. These package licences
do not establish rights to third-party checklist text.

## Preserved limitations

- The repaired runtime restores checklist/variant routing, schema validation and request-local
  web downloads. The historical main and earlier broken refactor remain available in Git history.
- Same-environment parity does not establish equivalence with the Rust implementation or
  comprehensive methodological correctness of every legacy standard.
- Checklist text lacks item-level rights/provenance receipts and must not be promoted to packs.
- Pending feature branches are retained as held work, including ten mislabelled STARD copies.

See the [source inventory](../docs/migration/standardflow/source-inventory.md),
[functional receipt](../docs/migration/standardflow/functional-parity.json), and
[Conductor track](../conductor/tracks/03-standardflow-import/plan.md).
