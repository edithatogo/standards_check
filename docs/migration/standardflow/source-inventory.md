# StandardFlow source inventory and pending work

Reconciled on **23 November 2026 (Australia/Brisbane)** from GitHub observations
on 22 November UTC. The receiving snapshot is exactly
[`cf7d14da7bfb4d32c2c8746ec1111a6643c4a716`](https://github.com/edithatogo/standards_check/commit/cf7d14da7bfb4d32c2c8746ec1111a6643c4a716).
These results apply to that recorded revision. Later dependency or runtime changes
require their own acceptance receipts.

The structured [source inventory](source-inventory.json) retains the original
five-branch and seven-branch snapshots, all nine exported tips, source issue/PR
bodies, historical reviews, receiving handoffs and the subsequent lifecycle
observations. Historical bodies and check results are not current status claims.

## Recorded receiving acceptance

**The import and reviewed improvements are merged.** Receiving PRs
[#92](https://github.com/edithatogo/standards_check/pull/92) and
[#88](https://github.com/edithatogo/standards_check/pull/88) preserve the repaired
source and all nine export histories. The integration merge is
`15184da899f21a62565cfc3145d1a4719baf4ad4`; [PR #96](https://github.com/edithatogo/standards_check/pull/96)
then records actual-main acceptance and pending source authentication at the
receiving snapshot pinned above.

The imported `legacy/standardflow` tree is
`62d8a0e738f0255cc59822ae4e661568090a213e`, exactly matching repaired source
`dc51d8e392858d5cb4e653aed199563514191efb`. That source follows initial repair
`d89a5dba...` and changes three files: `web/app.py` selects fixed server-side
filenames/MIME types, `Dockerfile` starts Flask on `0.0.0.0:5000`, and the source
review document records the follow-up. The original seven review findings at
`41c3e174...` remain historical findings in the retained snapshots.

[Recorded-main workflow 45035654999](https://github.com/edithatogo/standards_check/actions/runs/45035654999)
and [job 137248723322](https://github.com/edithatogo/standards_check/actions/runs/45035654999/job/137248723322)
completed successfully at `cf7d14da...`. Every step passed, including exact
subtree/ancestry verification, provenance regressions, dependency consistency,
source/receiving parity, container tests and the default-command HTTP smoke.
The privacy, foundation and dynamic analysis runs selected for that documentation
revision also succeeded. [Offline-security run 45035655216](https://github.com/edithatogo/standards_check/actions/runs/45035655216)
remained queued and has no execution receipt.

Earlier acceptance remains separately bound to its actual revisions:

- The [integration-main job](https://github.com/edithatogo/standards_check/actions/runs/45034583489/job/137245366320)
  verified the same source tree and nine histories, four provenance tests, 52 tests
  in each isolated source/receiving copy, 52 container tests and the default-image
  HTTP probe at `15184da8...`. PR #96 retains its recovery and hosted receipts.
- The [final PR-head legacy job](https://github.com/edithatogo/standards_check/actions/runs/45034143605/job/137244023298)
  passed those compatibility checks at `906c025d...`. That head also passed
  [201 primary Python tests](https://github.com/edithatogo/standards_check/actions/runs/45034143412/job/137244022542)
  and the [CodeQL aggregate](https://github.com/edithatogo/standards_check/runs/137244165310).
- The [functional receipt](functional-parity.json) records all 11 notebook
  examples, nine positive CLI cases and 21 byte-identical outputs, plus rejection
  of invalid PRISMA input without output. This is legacy compatibility evidence.

The source's own container test overrode the image command with unittest. The
receiving HTTP probe supplies the separate evidence that the default command
serves through the published host port. No source-test result substitutes for
receiving acceptance or qualifies a future receiving head automatically.

## Nine preserved export tips and four remaining source branches

All nine `archive/standardflow/<source-branch>` refs were independently read back
at their exact manifest SHAs. All nine tips were also independently verified as
ancestors of recorded receiving main `cf7d14da...`.

The source advertisement subsequently contains **four live branches**. Each
remaining tip matches the export manifest. Five other source refs are no longer
advertised after source PR closure; their receiving refs and ancestry remain
intact. This change in the source ref set does not represent lost history.

| Exported source branch | Preserved SHA | Live in later source observation |
| --- | --- | --- |
| `main` | `af299f724bcf456c131b43a143b3eabc1d81245b` | Yes |
| `feature/refactor-and-document` | `dc51d8e392858d5cb4e653aed199563514191efb` | Yes |
| `feature/implement-guidelines` | `f1680778b4141bb5553b0e80af22bbdf5c75c862` | Yes |
| `chore/GHA-190519-stepsecurity-remediation` | `eb7d0703b86aaa82e3cd738a273db7c60a70f6c9` | Yes |
| `dependabot/github_actions/actions/setup-python-7.1.0` | `7d2e233217d5d3d6c4ca9c5866f64158d117099e` | No |
| `renovate/click-8.x` | `3f850b81be3feb1a4d84d003b2ec6c166059a68e` | No |
| `renovate/graphviz-0.x` | `38c6327a9fe507150ee2bd655f36269345cf04a8` | No |
| `renovate/ipykernel-6.x` | `fb91d00d4f49d9b29e1a1a8dc73b1110b2518e00` | No |
| `renovate/jsonschema-4.x` | `59c119a933376d5f2e76d1b0088ad92f14d0fc60` | No |

Source main remains `af299f724...`. No remaining source tip advanced and no new
source branch appeared in this observation. Before retirement, compare the then
live source refs with the preserved manifest again, distinguishing a new/advanced
tip from an already-preserved branch that is no longer advertised. Recovery uses
the receiving history and refs, without access to the old remote.

## Source PR and issue dispositions

Source PRs **#9 and #24 through #29 are closed**, leaving zero open source PRs.
They were closed as exported or superseded; their changes were not merged into
the old source's main branch. PR #9 supplies the repaired compatibility snapshot.
PR #24/#25 history is retained and the receiving workflow uses their audited
Harden Runner and setup-python pins. PR #26–#29 remain held dependency candidates
in receiving [#94](https://github.com/edithatogo/standards_check/issues/94).
The [retirement record](retirement.md) retains the individual PR dispositions.

The source testing, security and umbrella issues have also been relocated. Their
receiving links, exact preservation evidence and Track 03 verification were
prepended before closure, and their original bodies remain historical snapshots.
The closure reason records relocation; the underlying receiving work remains open.

| Source issue | Source status | Receiving destination and responsibility |
| --- | --- | --- |
| [#12 — Testing and CI](https://github.com/edithatogo/standardflow/issues/12) | Closed as transferred | [#29](https://github.com/edithatogo/standards_check/issues/29): remaining testing and Track 05 qualification. |
| [#13 — Security and maintenance](https://github.com/edithatogo/standardflow/issues/13) | Closed as transferred | [#30](https://github.com/edithatogo/standards_check/issues/30): rulesets, managed files, coverage and updater obligations. |
| [#14 — Quality umbrella](https://github.com/edithatogo/standardflow/issues/14) | Closed as transferred | [#31](https://github.com/edithatogo/standards_check/issues/31): receiving child obligations and evidence. |
| [#23 — Dependency Dashboard](https://github.com/edithatogo/standardflow/issues/23) | Open; bot-owned body unchanged | [#76](https://github.com/edithatogo/standards_check/issues/76) and [#94](https://github.com/edithatogo/standards_check/issues/94): receiving discovery and manual qualification. |

Only source dashboard #23 remains open after those transfers. Receiving issues
#29/#30/#31 remain open. The JSON keeps the source bodies from before transfer,
the posted receiving mappings, the earlier recommendation text and the later
closure receipt separately.

## Held work and dependency qualification

The held `feature/implement-guidelines` branch labels ten datasets as AGREE,
ARRIVE, CHEERS, COREQ, PRISMA-P, RIGHT, SPIRIT, SQUIRE, SRQR and TRIPOD. Parsed-JSON
comparison found that all ten contain the same 30-item STARD array. The branch
also predates the repaired runtime. Its history remains recoverable; receiving
[#95](https://github.com/edithatogo/standards_check/issues/95) owns substantive
qualification before any dataset or pack admission.

| Preserved dependency candidate | Qualification needed |
| --- | --- |
| Click 8.1.3 → 8.5.1, source #26 | CLI overrides, errors and module entry point. |
| graphviz 0.20.1 → 0.21, source #27 | Actual output bytes, six variant goldens and notebooks. |
| ipykernel 6.25.0 → 6.31.0, source #28 | Notebook execution and interactive kernel compatibility. |
| jsonschema 4.17.3 → 4.26.0, source #29 | Accepted/rejected fixtures, references and diagnostics. |

The export preserves these four candidates without activating them. Issue #94
requires independent compatibility checks against the accepted repaired runtime;
notebook fixture execution alone does not qualify interactive kernel behaviour.
Later dependency admission must record its own exact revision and results.

## CodeQL disposition retained

The d89 receiving candidate triggered [CodeQL alert #4](https://github.com/edithatogo/standards_check/security/code-scanning/4)
on a temporary output-file read. The fixed png/svg/pdf allowlist dominated all
filesystem activity. Twenty hostile format values and a hostile-first duplicate
field were rejected before temporary-directory creation or rendering; valid
formats retained fixed names. The alert was observed dismissed as a false positive,
and that historical disposition remains in the JSON.

The subsequent dc51 code change separately selects literal filenames/MIME types
from a server-side mapping. The accepted final PR-head CodeQL aggregate succeeded.
The historical dismissal is not a replacement for scanning later code revisions.

## Privacy, downstream cleanup and remaining gates

The source API observation at **2026-11-22 20:53:25 UTC** still showed
`private: false` and `archived: false`. The last attempted visibility change
reached GitHub **Confirm access**, requiring owner reauthentication. No successful
reauthentication, privacy change or archive change has been observed. The later
source issue transfers do not alter that administrative status.

The [Voiage link PR #1394](https://github.com/edithatogo/voiage/pull/1394) remains
open at `e5351cc09fa884ce3348db1c856845d5fdaba8e4`; its later reported merge state
is `behind`. Earlier checks and the unsigned-commit policy finding remain
historical evidence. Reconcile the current base and applicable gates before
merging, without weakening repository rules.

The repository-standards registry removal is preserved on
[the prepared branch](https://github.com/edithatogo/repository-standards/tree/codex/standardflow-archive-followup-20261122)
at `caed59dbcb6f4cc75a8fa17e24275d0ff1b61e6b`. Its earlier prepared-patch validation
recorded 311 test passes, 38 capability skips and 168 schema-valid entries against
base `e6425228dea09637eb0a45a3787421e7bce42b3b`. This inventory does not rerun or
extend those results. The active registry change remains unmerged pending
observed source private/archive settings and current-base reconciliation.

Retain the original Apache-2.0 code licence, authorship, history and citation
metadata. The 22 main checklist JSON files lack item-level rights/provenance
receipts; the code licence does not clear third-party checklist text. Legacy
compatibility tests do not establish scientific correctness, Rust equivalence,
independent accessibility or publication readiness. The historical adoption
manifest's source/target pins remain historical preparation evidence.

The recorded receiving import is complete. Source retirement, downstream cleanup,
offline security execution, legacy-to-Rust semantic qualification, item-level
rights and independent methodology/accessibility work retain their separate gates.
Do not report retirement complete while the source is public and unarchived.
