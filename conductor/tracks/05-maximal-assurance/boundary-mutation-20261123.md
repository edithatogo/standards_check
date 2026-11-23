# Bounded schema and API mutation qualification, 23 November 2026

`tests/mutation_campaign.py` exercises ten hand-selected mutations against the canonical
pack validator/schema and checklist API. It copies the required sources, corpus and installed
API dependencies into a temporary directory. The original checkout is never mutated.
Each exact replacement site must occur once; a changed site fails the campaign for review.

The Python regressions cover a valid pack and rejection of a missing required title,
duplicate requirement IDs, a mismatched pack directory and a symlink outside the pack.
The API regressions exercise the real app, corpus and HTTP responses; CORS tests use the
production CORS configuration. A separate outcome test prevents import errors, mixed failures,
killed processes and timeouts from being counted as regression assertion kills.

## Execution contract

Use Python 3.14, matching the existing foundation, pack and diagram validation workflows,
and Node 24. The five-package foundation closure below is qualified for that Python runtime.

```sh
python3.14 -m venv target/assurance-venv
target/assurance-venv/bin/python -m pip install --no-deps -r requirements/standardflow-foundation.txt
target/assurance-venv/bin/python -m pip check
npm ci --prefix api --ignore-scripts --no-audit --no-fund
target/assurance-venv/bin/python tests/mutation_campaign.py --output target/mutation-evidence/report.json
```

Only the existing foundation `jsonschema` closure, Node and the API's locked dependencies
are needed. The driver uses Python's standard library and POSIX process groups. Each process
has a 60-second default limit; on timeout the complete owned process group is terminated.

Both unmutated baselines must pass without skips. Each mutation must have valid Python,
JSON or JavaScript syntax and fail through test assertions. Survivors, source-site drift,
syntax/runtime errors and timeouts have distinct outcomes and fail the campaign. The report
records the base Git revision, hashes of every copied source input, runtime versions, commands,
timings, source-preservation result and each mutation's replacement and outcome. Baseline and
mutation logs are retained beside it. CI must retain that whole output directory for its
exact checked-out revision.

## Historical local observation

The local candidate based on `ba6b0888806e84276e5f54afc07e4e555220c4ea`, including the
new API identifier guard and regression tests, passed on Python 3.12.14, jsonschema 4.26.0
and Node 24.22.3. The baseline had **7 Python tests and 14 API tests**, all passing without
skips. All ten mutations were killed by assertions; there were no survivors, unviable
mutations or timeouts, and all original source hashes remained unchanged.

That Python 3.12 environment already included `typing-extensions==4.16.0`. It was not a
clean five-package foundation environment: `referencing==0.37.0` requires the additional
dependency on Python versions below 3.13. These historical results do not establish that
the five-package closure alone works on Python 3.12.

| Mutated contract | Operator | Outcome |
| --- | --- | --- |
| Pack title required | Remove the top-level required title member | Assertion kill |
| Unique requirement IDs | Disable duplicate rejection | Assertion kill |
| Declared pack directory | Disable identity/directory comparison | Assertion kill |
| Pack symlinks prohibited | Disable symlink rejection | Assertion kill |
| API identifier validation | Disable the strict identifier guard | Assertion kill |
| Unknown checklist status | Change 404 to 200 | Assertion kill |
| Collection read failure status | Change 500 to 200 | Assertion kill |
| Individual read failure status | Change 500 to 200 | Assertion kill |
| CORS explicit origin list | Reflect all origins | Assertion kill |
| CORS wildcard configuration | Disable wildcard rejection | Assertion kill |

The generated local report has SHA-256
`24fc71b76fc9de77e566649db12a12b41f0f4673364e4d9bfda72f306786684f`. Its source hashes,
rather than the unchanged base commit alone, identify this uncommitted candidate. Hosted
execution must receive its own revision-bound receipt. This is a finite contract campaign;
the ten selected operators do not establish a repository-wide mutation score, exhaustive
schema/security coverage or methodological validity of checklist content.

## Clean foundation-profile correction

The first hosted campaign at PR #100 head
`12b7b00737124aa7c0feaead893c930124332489` failed on Python 3.12.16 before mutation.
[Job 137435997658](https://github.com/edithatogo/standards_check/actions/runs/45096059220/job/137435997658)
and [artifact 14783297063](https://github.com/edithatogo/standards_check/actions/runs/45096059220/artifacts/14783297063)
retain the failed Python import and successful 14-test API baseline. The missing conditional
`typing-extensions` dependency made `referencing` fall back to Python 3.12's `TypeVar`,
which rejects its `default` argument. Zero mutations ran; the aggregate correctly failed.

The boundary job now uses Python 3.14, matching all three existing foundation-profile
consumers, and checks dependency consistency after the unchanged `--no-deps` installation.
The profile, mutation operators, outcome classifier and acceptance threshold are unchanged.

A fresh isolated Python **3.14.10** environment installed exactly the five packages from
`requirements/standardflow-foundation.txt` plus the pip installer. It had no
`typing-extensions` distribution, and `pip check` passed. Profile SHA-256:
`7a60ee248424ca12315dbc663ae83f9eaf5068b239dcd32d6a08950d64797be9`.

The focused campaign ran against a separate clean worktree of the published
`12b7b00737124aa7c0feaead893c930124332489` revision with Node **24.22.3**. Both baselines
passed without skips; all **ten mutations were assertion kills**, with no survivors,
unviable cases or timeouts, and original source hashes stayed unchanged. The new report
SHA-256 is `6770f47988c76ef498d0c1f1aaea35617f5a287cd30115317743fbc5add907e5`.
This isolates the setup correction from later API changes; each subsequent candidate needs
its own hosted campaign receipt.

## API security follow-up

After adding the shared checklist request budget and constant-format error logging, the clean
Python 3.14.10 / Node 24.22.3 campaign passed again over base
`12b7b00737124aa7c0feaead893c930124332489`. Both baselines passed, all ten mutations were
assertion kills, and original source hashes remained unchanged. The report SHA-256 is
`78f978f51b39877692b2057684e5981b2d8159c05e645b0593b422b94dfab514`. The changed API inputs are identified
by the report's source hashes and the separate API security receipt. These ten operators test
the original schema, identifier, response-status and CORS contracts; the separate clock-controlled
HTTP test qualifies the newly added request budget. Hosted acceptance remains revision-specific.
