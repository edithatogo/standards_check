# Remaining migration qualification — 23 November 2026

## Completed receiving changes

The source repository remains private and archived. The active receiving repository is
`edithatogo/standards_check`; these changes preserve the frozen source and imported history.

| Qualification | Accepted change and tested revision | Hosted evidence |
| --- | --- | --- |
| Real optional kernels | PR #101, reviewed `86ed3d82da24c2126708ac966606940b01a80f05`, merged `79e64cf2c36e56c088f082cc6bc933ac3ce89f06` | [Kernel job](https://github.com/edithatogo/standards_check/actions/runs/45096897786/job/137438587584); both versions passed |
| Held guideline identities | PR #102, reviewed `93edaebfcb26976592b90914e25140261ccab042`, merged `756ac783564d7b848a7c231a542b301a39208391` | [Foundation job](https://github.com/edithatogo/standards_check/actions/runs/45097073098/job/137439137943); 11 tests and all ten expected rejections passed |
| Bounded Python/Rust PRISMA counts and artifact fidelity | PR #103, reviewed `c181590a8e3c9d147fc22a79e6e38c0113ce42f1`, merged `7a6df395a2853c4c2052a492078cceb8f79f817d` | [Dual-CLI job](https://github.com/edithatogo/standards_check/actions/runs/45097252721/job/137439697495); 16 tests, two accepted pairs and two intentional rejection pairs passed |
| Complete qualification runtimes | PR #104, reviewed `3be93adaf444c3f5ad301ac275342532b7b189f7`, merged `5f3f2883b4cbfc7809d5dc5c2e9769b8890d86d0` | [Actual-main dual-CLI job](https://github.com/edithatogo/standards_check/actions/runs/45098696002/job/137444248028); clean main checkout and full bounded qualification passed |

All ordinary checks passed on each reviewed head. The offline-security jobs remained queued.
The receiving-main executions below are separate evidence from those pull-request results.

## Actual-main receipts

The [real-kernel job on main](https://github.com/edithatogo/standards_check/actions/runs/45097444156/job/137440298947)
at `79e64cf2c36e56c088f082cc6bc933ac3ce89f06` passed both exactly pinned 42-package profiles:
11 notebooks, 43 code cells, 11 acknowledged successful process exits, explicit protocol
probes, 52 application tests, six fresh matching PNGs and 21 matching CLI outputs per version.
All relevant kernel/profile/source bytes remain identical through main `5f3f2883`.
Issue #94 is closed with all four preserved dependency candidates dispositioned. The ordinary
30-package host profile still does not install a kernel. See the [kernel runbook](kernel-qualification-20261123.md).

The first PRISMA job on receiving main `7a6df395` failed before either CLI ran: the minimal
Rust installation deferred the repository-declared formatter/linter components to the first
Cargo command, which hit a `bin/cargo-fmt` conflict. Its fallback correctly reported `not_run`.
PR #104 explicitly provisions `rustfmt,clippy`, matching `rust-toolchain.toml`. The fresh job
on exact main `5f3f2883b4cbfc7809d5dc5c2e9769b8890d86d0` then passed, with a clean checkout,
two accepted fixture pairs, eight output hashes and both deliberate Rust conservation rejections.

The evidence archives were downloaded and their hashes verified:

| Actual-main artifact | Archive SHA-256 |
| --- | --- |
| [Kernel receipts/logs, 14783174909](https://github.com/edithatogo/standards_check/actions/runs/45097444156/artifacts/14783174909) | `ead560b81f3777854192c716fcad27f6f8e7927b30b77143cf106bd7cf11b7f3` |
| [PRISMA receipt/log, 14784122750](https://github.com/edithatogo/standards_check/actions/runs/45098696002/artifacts/14784122750) | `7f951a8083422ab251077edc499808154f44f12750003ab7fad948f7edecdb32` |

The [PRISMA contract](../../../docs/migration/standardflow/legacy-prisma-contract.md) retains
its synthetic database-only conditions, record/report/study distinctions, stricter Rust
rejections and excluded quantitative-synthesis claim. The improved SVG/text checks establish
structural fidelity; they do not certify browser or assistive-technology behavior.

Issue #95 remains open. The [source/rights ledger](../../../docs/migration/standardflow/held-guidelines-qualification.json)
and independent identifier fixtures reject the ten copied STARD arrays. Complete wording,
intended editions, permissions, methodology and pack admission require their specified evidence.

## Integration with the existing assurance work

PR #100 owns the broader assurance work and shared Conductor reconciliation. Its current
head `d67d9e992d7b9438ff2ae1404f2f5fea9e20370c` already incorporates the first three migration
PRs and measures the actual dual-CLI qualification in the renamed `ci.yml` workflow.
This follow-up preserves that integration and brings in main's PR #104 repairs, then requests
the complete declared Rust components in both assurance toolchain setups. Rust coverage also
retains its existing `llvm-tools-preview` component. It does not rewrite the owner's new API,
SBOM, coverage, mutation, policy or Conductor work.

The integration risk was measured before that owner update. A local projection of the earlier
PR #100 head `12b7b00737124aa7c0feaead893c930124332489` plus the three migration increments
passed 245 tests and six validators but covered only 1,869 / 2,674 line/branch opportunities,
or **69.90%**. Adding genuine dual-CLI execution raised this to 2,019 / 2,674, or **75.50%**,
with all 27 modules and the 75% floor unchanged. The coherent local report's SHA-256 is
`1c4935b7ba2d5e18bcd5b76544d9614cecd31865e1ad5775bd79ad6a20cf8167`.
That is an explicitly scoped historical projection, not the newer owner's denominator or
a hosted result. The newer measurement is retained in the owner's Track 05 coverage receipt.

The earlier [boundary mutation baseline](https://github.com/edithatogo/standards_check/actions/runs/45096059220/job/137435997658)
also failed before any mutation ran: its clean Python 3.12 environment lacked
`typing-extensions`, required by pinned `referencing` below Python 3.13. The failure was
reproduced; adding the existing `typing-extensions==4.16.0` pin produced a compatible closure
and ten actual assertion kills, with no survivors/timeouts or source changes. PR #104 makes
that dependency conditional in the foundation profile. The owner's newer boundary job uses
Python 3.14 and checks dependency consistency; that choice and its failure classification remain
unchanged. The corrected profile also supports the declared Python 3.12 callers.

## Preservation and remaining acceptance

Main `5f3f2883b4cbfc7809d5dc5c2e9769b8890d86d0` has tree
`6d2aefc0f68dcbffc1e971b41ae811d9ce68fac9`. Fresh import checks and actual runtime receipts
retain source `dc51d8e392858d5cb4e653aed199563514191efb`, frozen subtree
`62d8a0e738f0255cc59822ae4e661568090a213e` and all nine recorded source ancestors.

This focused follow-up needs its own hosted check receipt. Shared Track 03/05 metadata and
wider ruleset/updater acceptance retain their existing owner. No consumer cutover, general
Python/Rust equivalence, scientific-method approval, content-rights clearance, external
accessibility acceptance or release certification is claimed here.

Offline security remains unexecuted. Issue #30 records the concrete upstream image-preparation
failure and the unassigned receiving job. A qualified image/digest, complete controls/model
assets, separate runner acceptance and actual consumer execution remain necessary.
