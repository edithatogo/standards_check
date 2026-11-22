# StandardFlow source inventory and pending work

Reconciled on **23 November 2026 (Australia/Brisbane)** from GitHub observations
on 22 November UTC. The historical actual-main runtime acceptance below is bound to
[`2b0c579454a1dd469cd12cfb9538d23c96785370`](https://github.com/edithatogo/standards_check/commit/2b0c579454a1dd469cd12cfb9538d23c96785370).
Those results apply to that recorded revision. PR #98 subsequently admitted three
maintained host versions at receiving main `d213085a268a4cd82d522e6e17d27f3dee15bf5f`;
its qualification and separately pending receiving-main execution are recorded below.

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
then recorded actual-main acceptance at `cf7d14da7bfb4d32c2c8746ec1111a6643c4a716`
while source authentication was pending. That earlier observation is historical;
the source is now private and archived. The completed actual-main runtime receipt
remains bound to the earlier receiving snapshot pinned above.

The imported `legacy/standardflow` tree is
`62d8a0e738f0255cc59822ae4e661568090a213e`, exactly matching repaired source
`dc51d8e392858d5cb4e653aed199563514191efb`. That source follows initial repair
`d89a5dba...` and changes three files: `web/app.py` selects fixed server-side
filenames/MIME types, `Dockerfile` starts Flask on `0.0.0.0:5000`, and the source
review document records the follow-up. The original seven review findings at
`41c3e174...` remain historical findings in the retained snapshots.

[Recorded-main workflow 45070791156](https://github.com/edithatogo/standards_check/actions/runs/45070791156)
and [job 137357038355](https://github.com/edithatogo/standards_check/actions/runs/45070791156/job/137357038355)
completed successfully at `2b0c5794...`. Every step passed, including exact
subtree/ancestry verification, provenance regressions, dependency consistency,
source/receiving parity, container tests and the default-command HTTP smoke.
The [parity artifact 14773685812](https://github.com/edithatogo/standards_check/actions/runs/45070791156/artifacts/14773685812)
retains the receiving result. At this main revision, 26 observed checks succeeded,
including deployment. [Offline-security run 45070791434](https://github.com/edithatogo/standards_check/actions/runs/45070791434)
was still queued when re-read at approximately 22:58 UTC on 22 November and has
no execution receipt.

Earlier acceptance remains separately bound to its actual revisions:

- The [earlier documentation-main job](https://github.com/edithatogo/standards_check/actions/runs/45035654999/job/137248723322)
  passed provenance, parity, container and HTTP checks at `cf7d14da...`. Its selected
  privacy, foundation and dynamic-analysis runs also succeeded; offline run
  `45035655216` remained queued at that observation.
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
at their exact manifest SHAs. All nine tips were independently verified as ancestors
of receiving main `cf7d14da...`; the latest hosted provenance check confirms their
preservation at `2b0c5794...`.

The source advertisement at **2026-11-22T20:53:25Z** contained **four live branches**. Each
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

Source main was `af299f724...`. No remaining source tip advanced and no new
source branch appeared in that observation. This four-ref snapshot is historical;
the later private/archive settings read is recorded separately below. Recovery uses
the receiving history and refs, without access to the old remote.

## Source PR and issue dispositions

Source PRs **#9 and #24 through #29 are closed**, leaving zero open source PRs.
They were closed as exported or superseded; their changes were not merged into
the old source's main branch. PR #9 supplies the repaired compatibility snapshot.
PR #24/#25 history is retained and the receiving workflow uses their audited
Harden Runner and setup-python pins. PR #26–#29 remain unmerged source history;
three corresponding host versions were separately admitted through receiving PR #98.
Optional ipykernel qualification and updater observation remain in receiving
[#94](https://github.com/edithatogo/standards_check/issues/94).
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

| Preserved dependency candidate | Receiving disposition |
| --- | --- |
| Click 8.1.3 → 8.5.1, source #26 | Maintained host version 8.5.1 admitted through PR #98; source branch remains unmerged. |
| graphviz 0.20.1 → 0.21, source #27 | Maintained host version 0.21 admitted through PR #98; source branch remains unmerged. |
| ipykernel 6.25.0 → 6.31.0, source #28 | Version 6.31.0 remains unadmitted; optional kernel qualification remains in #94. |
| jsonschema 4.17.3 → 4.26.0, source #29 | Maintained host version 4.26.0 admitted through PR #98; source branch remains unmerged. |

The export and PR #97 integration preserved these candidates without activating
them. Separate receiving [PR #98](https://github.com/edithatogo/standards_check/pull/98)
merged at `2026-11-22T23:35:27Z` as `d213085a268a4cd82d522e6e17d27f3dee15bf5f`, tree
`4a34e69ae1cd857a178cf7e28245d2953a140dec`. Its reviewed head
`08d9ffef20675efc80484d108b32f1d1ee759921` passed
[legacy run 45082189553](https://github.com/edithatogo/standards_check/actions/runs/45082189553),
with nine ordinary checks successful and two offline checks queued. Receiving-main
execution is separately pending; the earlier `2b0c5794` receipts retain their scope.

The [qualification receipt](dependency-qualification-20261123.json) binds the
maintained host profile to SHA-256
`27ba903aba19f5851baf887a177699ac1c9604c9ec5a7666edac573aefbe0568`.
The exact imported source and historical Docker dependencies remain unchanged.
Issue #94 stays open for optional interactive-kernel qualification and updater
observation. Both old/new kernel profiles passed 52 application tests, but both
startups were blocked before `kernel_info`; no cells executed. Those results do
not establish interactive-kernel parity or admit ipykernel 6.31.0.

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

The owner completed the requested source privacy and archival changes. An independent
[GitHub repository API read](https://api.github.com/repos/edithatogo/standardflow)
at **2026-11-22T22:55:19Z** returned `private: true`, `archived: true` and
`open_issues_count: 1`. Source retirement through private archival is complete.

The source observations at 20:53:25 and 21:00 UTC, when it was still public and
unarchived, are historical. The earlier visibility attempt had reached GitHub
**Confirm access**, and owner reauthentication was still outstanding then. The
structured inventory retains that blocker receipt separately from the completed
settings observation; issue relocation alone did not establish the settings change.

The [Voiage link PR #1394](https://github.com/edithatogo/voiage/pull/1394) merged
through a policy-enforced squash at `2026-11-22T23:32:28Z`, verified commit
`a921d6471822eaac7fbc22f507760bd943ba9f6a`, also read back on main. Tree
`7c0099a9c465c19648db7aca89e187141855c2c2` exactly matches reviewed head
`3bc04fdc1df6f30981765eee49c0c9dbce490cde`. The intended consumer-link replacement
is one insertion and one deletion in one file, producing blob
`4849e4fc167c7da484d95f9ef652701181b30a5b`.

At the reviewed head, all 51 hosted checks succeeded, three expected checks skipped,
and all 17 required names matched successful checks. The full local tox attempt did not pass: 13
environment checks passed, coverage had six missing-`/usr/bin/time` failures, and
docs installation stalled and was interrupted. Existing hosted coverage and docs
jobs cover the remaining required commands on the reviewed inputs. Their exact
results, toolchain differences and missing final local guard/peak-memory receipt
are in the [verification record](../../../conductor/tracks/03-standardflow-import/verification.md#voiage-downstream-merge-and-command-evidence).
The earlier unsigned head, outdated base and pending-check observations remain
historical evidence in the structured inventory.

The repository-standards registry removal is complete.
[PR #172](https://github.com/edithatogo/repository-standards/pull/172) merged through
a permitted squash at `a3cc8dccdb67e6f122c71cec713194cdec792d07`, the observed main.
Its tree `e884b86ea9bb1121422503122206041e086256ac` exactly matches tested candidate
`caed59dbcb6f4cc75a8fa17e24275d0ff1b61e6b`. Only retired `standardflow` was removed:
the registry changed from 169 entries to 168 and retained `standards_check`.
Nine PR checks succeeded and two expected PR checks skipped; required policy and
Actions/Python analysis succeeded. Local qualification recorded 311 passes and
38 capability skips. The earlier prepared-branch validation remains separately
identified in the JSON.

Retain the original Apache-2.0 code licence, authorship, history and citation
metadata. The 22 main checklist JSON files lack item-level rights/provenance
receipts; the code licence does not clear third-party checklist text. Legacy
compatibility tests do not establish scientific correctness, Rust equivalence,
independent accessibility or publication readiness. The historical adoption
manifest's source/target pins remain historical preparation evidence.

The recorded receiving import, source private archival, registry cleanup and Voiage
link update are complete. Offline security execution, legacy-to-Rust semantic
qualification, item-level rights and independent methodology/accessibility work
retain their separate gates.
