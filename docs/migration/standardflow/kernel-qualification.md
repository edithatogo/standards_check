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

## Initial execution boundary

The workspace check on 23 November 2026 passed the harness regressions but returned exit 1
for real-kernel startup: ZeroMQ could not discover local interfaces under the workspace's
permissions, and the kernel died before `kernel_info`. No restriction or validation gate
was relaxed. Positive kernel acceptance requires the actual hosted result, recorded
separately from these local checks and the earlier IPython-only fixture results.
