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

```sh
python -m pip install --no-deps -r requirements/standardflow-foundation.txt
npm ci --prefix api
python tests/mutation_campaign.py --output target/mutation-evidence/report.json
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

## Local observation

The local candidate based on `ba6b0888806e84276e5f54afc07e4e555220c4ea`, including the
new API identifier guard and regression tests, passed on Python 3.12.14, jsonschema 4.26.0
and Node 24.22.3. The baseline had **7 Python tests and 14 API tests**, all passing without
skips. All ten mutations were killed by assertions; there were no survivors, unviable
mutations or timeouts, and all original source hashes remained unchanged.

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
