# Optional legacy kernel qualification

Track 03 / issue #94 owns this bounded comparison of preserved ipykernel 6.25.0 and
6.31.0. It extends the maintained 30-package host profile for qualification only.
The frozen source requirements and the ordinary host profile remain separate.

## Acceptance

The existing legacy workflow runs each version in a fresh Python 3.12 virtual environment.
Each environment must contain exactly the same 41 other packages, pass dependency
consistency, and pass the existing 52-test / 21-file application canary suite.

The runner then deletes any pre-existing notebook images and executes all 11 original
notebooks / 43 code cells through real TCP-loopback kernels. Saved notebook outputs are
unused. Every kernel must identify the selected interpreter and ipykernel version.
Visible streams, MIME data and presentation metadata, and six newly created PNGs must
match across the two profiles. Protocol IDs, execution counts and stream chunk boundaries
are transport details, so the comparison excludes those fields only.

A protocol smoke checks kernel information, completion, inspection, a deliberate error
and recovery, interruption of an executing cell, and restart with cleared state. Every
notebook must receive a shutdown reply and its owned process must exit successfully.
Timeouts, nonzero exit, missing cells, changed outputs or incomplete receipts fail the job.
Forced termination is failure cleanup and cannot qualify a successful shutdown.

The comparison establishes compatibility for these frozen notebooks and protocol probes.
It does not establish a notebook GUI/browser result, arbitrary notebook support, server
deployment, Rust parity, clinical-method validation, content rights or offline security.

## Reproduce

Install Graphviz and ImageMagick. From the repository root, create separate Python 3.12
environments for `6.25.0` and `6.31.0`, then run the following with each environment's Python:

```bash
python -m pip install --no-deps -r requirements/legacy-standardflow.txt \
  -r requirements/legacy-kernel-qualification.txt ipykernel==6.31.0
python -m scripts.qualify_legacy_kernel --expected-version 6.31.0 \
  --output /tmp/standardflow-kernels/6.31.0/receipt.json
```

Use the corresponding version and output directory for the baseline. Compare the two
completed receipts with the standard-library-only comparison mode:

```bash
python -m scripts.qualify_legacy_kernel --compare \
  /tmp/standardflow-kernels/6.25.0/receipt.json \
  /tmp/standardflow-kernels/6.31.0/receipt.json \
  --output /tmp/standardflow-kernels/comparison.json
```

The GitHub job retains both receipts, per-notebook kernel logs and the comparison receipt,
including on failure. Its read-only checkout requires complete imported Git history.

## Dependency responsibility

`requirements/legacy-kernel-qualification.txt` contains the eleven optional additions;
the workflow explicitly selects the two historical kernel pins. These are required by the
real kernel and its native Jupyter client, rather than a separate notebook execution framework.
Track 03 owns the profile. Remove it when this comparison is retired or superseded by a
replacement consumer qualification. The maintained host renderer does not require it.

Declared licence metadata was inspected from the exact installed distributions:

| Packages | Declared licence |
| --- | --- |
| comm, jupyter-client, jupyter-core, python-dateutil, pyzmq, ipykernel | BSD-3-Clause |
| nest-asyncio | BSD (distribution label) |
| debugpy, platformdirs | MIT |
| packaging | Apache-2.0 OR BSD-2-Clause |
| tornado, tzdata | Apache-2.0 |

These are dependency metadata observations. Third-party reporting-guideline rights are
a separate gate. Renovate discovers the optional requirements file through the existing
receiving `requirements/*.txt` rule; the source snapshot remains excluded.

## Hosted execution receipt — 23 November 2026

The initial implementation at commit `950e451e00d769e72b29bbedad13b849ef47809a`
(tree `0222130794789be204ef03eaa382f4b9e652086b`) passed the actual
[kernel job](https://github.com/edithatogo/standards_check/actions/runs/45096243764/job/137436570311)
on GitHub's Ubuntu 24.04 runner with Python 3.12.16. Both version receipts and the
comparison report say `pass`. The integrator downloaded the
[retained artifact](https://github.com/edithatogo/standards_check/actions/runs/45096243764/artifacts/14783531226)
and verified archive SHA-256
`5d4ad57f1106e05450757391c32e28646e09e1179e5e582a779244c091d3dfab`.

| Evidence | Observed result |
| --- | --- |
| Kernel versions | 6.25.0 and 6.31.0; 41 other installed packages identical |
| Notebook execution | 11 notebooks and 43 code cells per version; saved outputs unused |
| Lifecycle | 11 acknowledged shutdowns and successful process exits per version |
| Protocol probes | Information, completion, inspection, error/recovery, interrupt/recovery and restart/state reset passed; protocol 5.3 |
| Output comparison | Notebook-visible data matched; six fresh PNGs and 21 CLI output files identical |
| Application exercise | 52 tests passed in each environment |
| Frozen import | Exact tree `62d8a0e738f0255cc59822ae4e661568090a213e`; all nine source histories present |
| Host profile SHA-256 | `27ba903aba19f5851baf887a177699ac1c9604c9ec5a7666edac573aefbe0568` |
| Optional profile SHA-256 | `b205079d09753f08724bb7fe594860266a4ab2c01fb8517fd95a4a4730d2d717` |

All 12 ordinary hosted jobs at that head, plus the CodeQL aggregate, succeeded;
deployment was intentionally skipped for the pull request. The two separate
offline-security jobs remained queued. That pending external execution is not
part of this kernel acceptance. The receipt records the executed implementation
head; subsequent documentation changes require their own normal checks.

This qualifies ipykernel 6.31.0 for the frozen notebook fixtures and the protocol
probes above. It does not add a kernel to the maintained host renderer or change
the historical source requirements. The wider exclusions in Acceptance still apply.

## Receiving-main input evidence

Before this new job, receiving main `ba6b0888806e84276e5f54afc07e4e555220c4ea`
passed all eight hosted jobs, including
[legacy execution](https://github.com/edithatogo/standards_check/actions/runs/45085224983/job/137402195300),
the exact source/history checks, host comparison, 52 Docker tests and default
container HTTP startup. Its
[parity artifact](https://github.com/edithatogo/standards_check/actions/runs/45085224983/artifacts/14778918783)
has archive SHA-256 `500482392a7efd16f7f35cce0370922edd34d19f55e16748d79a6855c30725bc`.
That is input-runtime evidence, separate from the kernel result above. PR #100
owns the shared Track 03 receiving-main and broader-assurance reconciliation;
this dedicated receipt avoids competing edits to its index, metadata and plan.

## Earlier workspace execution boundary

The workspace check on 23 November 2026 passed the harness regressions but returned exit 1
for real-kernel startup: ZeroMQ could not discover local interfaces under the workspace's
permissions, and the kernel died before `kernel_info`. No restriction or validation gate
was relaxed. The positive hosted result above supersedes that environment-blocked
attempt for this bounded kernel comparison. The local failure and earlier
IPython-only fixture results remain separately scoped observations.
