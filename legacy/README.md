# Retained StandardFlow compatibility runtime

The repaired legacy runtime from `edithatogo/standardflow` is retained under
[`standardflow/`](standardflow/) with its complete Git history and Apache-2.0 licence.
Source revision `dc51d8e392858d5cb4e653aed199563514191efb` includes the original main
and the reviewed compatibility repairs. Its exact tree is
`62d8a0e738f0255cc59822ae4e661568090a213e`.
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
The managed root host dependency profile is tested separately from the Dockerfile, which still
installs the frozen snapshot's historical requirements. Container checks do not qualify the
managed host profile.
The receiving dependency closure includes the display helpers needed to execute notebook
examples as tests through IPython. An interactive Jupyter kernel remains optional and outside
this profile; the held ipykernel 6.31.0 update remains in Git history rather than adding a kernel
to the tested runtime.

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

Track 03 owns the optional 30-package Python closure in
`requirements/legacy-standardflow.txt`. It supports the legacy CLI/web renderer and
executes notebook fixtures in isolation from the primary runtime. Update the root closure
without modifying the exact source snapshot; remove this closure only after
accepted replacement/consumer and rollback evidence permits retiring this surface.
Dependency dispositions and exact profile/artefact hashes are recorded in the
[23 November qualification receipt](../docs/migration/standardflow/dependency-qualification-20261123.json)
for [#94](https://github.com/edithatogo/standards_check/issues/94).
Renovate discovers the managed root `requirements/*.txt` profiles and excludes the frozen,
unmanaged `legacy/standardflow` snapshot from dependency extraction. Its ignore list also retains
the shared preset's module and test directory exclusions. This boundary also prevents security
update rules from modifying the exact snapshot.

The jsonschema 4.26.0 closure uses jsonschema-specifications, referencing and rpds-py instead of
pyrsistent. Referencing requires typing-extensions on Python 3.12. These dependencies are pinned
alongside the qualified Click 8.5.1 and graphviz 0.21 updates; unrelated versions are unchanged.

The installed distribution metadata and shipped licence files identify these licences:

| Licence | Python distributions |
| --- | --- |
| Apache-2.0 | asttokens |
| BSD-2-Clause | Pygments |
| ISC | pexpect, ptyprocess |
| MIT | attrs, blinker, executing, graphviz, jedi, jsonschema, jsonschema-specifications, parso, pure_eval, referencing, rpds-py, stack-data, wcwidth |
| BSD-3-Clause | click, Flask, ipython, ipython_pygments_lexers, itsdangerous, Jinja2, MarkupSafe, matplotlib-inline, prompt_toolkit, psutil, traitlets, Werkzeug |
| PSF-2.0 | typing-extensions |

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
