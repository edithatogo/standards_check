# StandardFlow export verification

This receipt records the preserved source, receiving main and its successful hosted
checks. The export is merged, and the owner-completed source privacy and archival
changes were verified through GitHub's repository API at `2026-11-22T22:55:19Z`.
The earlier authentication blockers below are historical. These claims concern
repository preservation and the legacy runtime; they do not qualify Rust parity,
source rights, methodology or accessibility.

## Initial source repair

- Source revision: `d89a5dbacc207cdce11f19efd667b83fdb09df18`.
- Exact tree: `e48c081ff946d0fac6a1a4b65a3599c6b7aa3352`.
- Original PR #9 failed two web tests and one TIFF test against current main
  dependencies. The repaired suite passed all 52 tests, including execution of all
  11 notebooks; the source-main baseline passed its 29 tests.
- Hosted [application and container tests](https://github.com/edithatogo/standardflow/actions/runs/45029941592),
  [privacy checks](https://github.com/edithatogo/standardflow/actions/runs/45029941603)
  and [primary-adoption checks](https://github.com/edithatogo/standardflow/actions/runs/45029941643)
  succeeded at that source revision.
- The separate offline AI-security job remained queued without a matching
  self-hosted runner. No offline-security success or exemption is claimed.

## Receiving runtime and preservation

The first history-preserving import is
`989f2fa5c26b22b8294e20b442a6f602d9d124ed`, produced by the successful
[bounded import job](https://github.com/edithatogo/standards_check/actions/runs/45030067114).
The exact source tree is at `legacy/standardflow`. The successful
[final inventory import](https://github.com/edithatogo/standards_check/actions/runs/45030821217)
preserved the two later Renovate heads at
`9da5f40f4df941e1f93feea04c035133c7f8a626`. The provenance check passed again with all
seven revisions reachable and the same exact subtree. Temporary privileged import
automation is removed from the final PR tree.

Independent receiving checks observed for export revision
`99bcad6ab7ef877645d12c79f1535055d1493d3f`, before the separate primary Ponytail fixes:

| Check | Observed result |
| --- | --- |
| Imported application suite | 52 tests passed from `legacy/standardflow`. |
| Provenance validator | Exact tree and all seven source revisions verified. |
| Validator regression suite | Four tests passed, including rejected squashes, missing ancestry and subtree drift. |
| Markdown and index validators | Passed; index contained 56 items. |
| Foundation audit | Passed with no context errors. |
| Existing primary runtime | Rust crates, PRISMA inputs, recipes and goldens unchanged from baseline. |
| Build context | Cargo.toml, Cargo.lock and the Conductor gitlink unchanged. |

Primary comparison baseline: `1aef9b5b95582d447d9b539c94d4b5dcf4366679`.
The receiving provenance tests and CI added by this PR must pass again at its final
revision; this receipt does not substitute results from an earlier head.

## Consolidated receiving evidence

PR #88 combines this export with the separately reviewed primary improvements,
without changing the exact legacy subtree. The [functional parity receipt](../../../docs/migration/standardflow/functional-parity.json)
records 52 tests in each isolated source/receiving copy, all 11 notebook examples,
and 21 byte-identical outputs from six diagram and three checklist CLI cases.
The maintained workflow also retains the independent 52-test container run and
the four provenance tests. See the [Ponytail receipt](../../ponytail-review-20261122.md)
for primary validator, HTML and SVG changes.

CodeQL [alert #4](https://github.com/edithatogo/standards_check/security/code-scanning/4)
was independently triaged and dismissed as a false positive. Its path expression
is dominated by a fixed png/svg/pdf membership check; 20 hostile values and a
hostile-first duplicate field were rejected before temporary-directory creation
or rendering. Five valid/default/duplicate-field cases kept fixed output names.
The detailed call-chain and test receipt is retained in the
[source inventory](../../../docs/migration/standardflow/source-inventory.json).
No scanner was disabled and no runtime code changed for this disposition.

## Recovery rehearsal

An independent temporary clone of the primary import used `--no-local` and had no
shared object alternates. It recreated each of the initial five source branch names
from `import.json`, removed its only remote, and checked out the repaired source
revision. Its tree matched the source tree exactly. The recovered CLI generated a
5,690-byte PRISMA SVG containing the expected labels and screened count 800, with no
configured remotes and no tracked worktree changes.

All source branch tips, including subsequent preserved dependency branches, remain
explicit in `import.json`. Recovery uses those reachable commits rather than a
future fetch from the private archived source. Root CI enforces the final manifest.

## Final source follow-up

Source `dc51d8e392858d5cb4e653aed199563514191efb`, tree
`62d8a0e738f0255cc59822ae4e661568090a213e`, follows the initial repair. It maps output
formats to fixed server-side filenames and makes the default Flask container command
listen on its exposed interface. The source application/container, privacy and adoption
checks passed at this head. Two additional Renovate branches appeared, bringing the
manifest to nine preserved source heads; dependency changes remain unapplied.
The receiving workflow adds a host-port HTTP smoke test of the default container command,
which is distinct from overriding that command with the 52-test suite. The functional
receipt is regenerated against this final source snapshot.

## Final transfer and named recovery refs

The [successful refresh job](https://github.com/edithatogo/standards_check/actions/runs/45032696354)
published `6c67527512ad5b603307ac6415ba214d3333c42a`, preserving final source
`dc51d8e392858d5cb4e653aed199563514191efb` and the two later Renovate heads as
additional parents. Its imported subtree is exactly
`62d8a0e738f0255cc59822ae4e661568090a213e`; all nine manifest revisions are ancestors.
The subsequent export preparation
`cda5469d6107fe9729f274165ba9dd01fcba25f2` removes the temporary import workflow.
The final PR #88 consolidation retains that preparation as an additional parent.

All nine named `archive/standardflow/` refs were independently read back from the
receiving repository on 22 November 2026 UTC and match `import.json`, including the
advanced repaired application and both later dependency branches. Final source/receiving
parity passed 52 tests in each copy, all 11 notebook examples, the nine positive CLI
cases and 21 identical output files against this final source snapshot. Four provenance
regressions passed again. The actual-main hosted run below subsequently verified the
new default-container HTTP smoke; this result is observed execution evidence.

## Actual-main acceptance

[Export PR #92](https://github.com/edithatogo/standards_check/pull/92) merged as
`906c025d67b03322e5c1b41a63aea88e150672e5`. Its preserved history reached main through
[integration PR #88](https://github.com/edithatogo/standards_check/pull/88), at
[`15184da899f21a62565cfc3145d1a4719baf4ad4`](https://github.com/edithatogo/standards_check/commit/15184da899f21a62565cfc3145d1a4719baf4ad4).
Both merges retained ancestry. The integrated primary validator, HTML and Rust/SVG
improvements are intentional; the earlier unchanged-primary comparison applies only
to the export preparation described above.

[Main workflow 45034583489](https://github.com/edithatogo/standards_check/actions/runs/45034583489)
completed successfully at that exact main commit on 22 November 2026 at 14:47:58 UTC.
Its [receiving job](https://github.com/edithatogo/standards_check/actions/runs/45034583489/job/137245366320)
and [parity artifact](https://github.com/edithatogo/standards_check/actions/runs/45034583489/artifacts/14758977889)
record the following results:

| Check | Observed result at receiving main |
| --- | --- |
| Source and subtree | Source `dc51d8e392858d5cb4e653aed199563514191efb` and imported tree `62d8a0e738f0255cc59822ae4e661568090a213e` match exactly. |
| History | All nine manifest source revisions are reachable ancestors. |
| Provenance regressions | Four tests passed, including rejection cases. |
| Source/receiving parity | 52 tests passed in each isolated copy, including all 11 notebooks; nine positive CLI cases produced 21 byte-identical files. Invalid PRISMA input was rejected without output. |
| Container runtime | All 52 tests passed in the built imported image. |
| Default container startup | The image's default command served HTTP through the published host port. |

An independent clone of this actual main also passed the nine-history provenance
check and all 52 imported tests. It contained no temporary write-capable import
workflow. A separate recovery checkout recreated all nine recorded source refs,
removed its only remote and checked out `dc51d8e392858d5cb4e653aed199563514191efb`;
the original tree matched `62d8a0e738f0255cc59822ae4e661568090a213e` with no shared
object alternates. Recovery therefore does not depend on access to the old remote.

The [main document build and deployment](https://github.com/edithatogo/standards_check/actions/runs/45034583564)
also succeeded. The separate
[offline AI-security run](https://github.com/edithatogo/standards_check/actions/runs/45034583761)
was still queued at 14:53 UTC; no pass or exemption is claimed for that job.

## Historical source-retirement blocker — 22 November 2026

This observation preceded the completed private/archive settings recorded below.

Source PRs #9 and #24 through #29 were closed after export, with their receiving
destinations retained in the [retirement record](../../../docs/migration/standardflow/retirement.md).
At 14:53 UTC on 22 November 2026 the source had zero open PRs and still returned
`private: false` and `archived: false`. The authorized visibility change reached
GitHub's **Confirm access** screen, which requires the owner's passkey or
authenticator. Successful reauthentication and the requested settings changes have
not been observed. Export completion does not complete this administrative step.

Actual source private/archive settings and downstream registry/consumer updates
still require receipts. Legacy-to-Rust semantic parity, item-level rights and
provenance, independent methodology and accessibility qualification remain open.

## Earlier follow-up reconciliation — 23 November 2026

This section retains the earlier receiving-main and 21:00 UTC source observations.
The later retirement and receiving-main observations below supersede their current status.

The two source-inventory files now include acceptance at recorded receiving main
`cf7d14da7bfb4d32c2c8746ec1111a6643c4a716`, whose
[legacy run 45035654999](https://github.com/edithatogo/standards_check/actions/runs/45035654999/job/137248723322)
passed every step, including provenance, parity, container tests and default web startup.
All nine export tips remain named receiving refs and ancestors of that main. Four
source branches remain after the five exported bot branches were removed; their
remaining tips still match the original manifest.

Source issues #12 through #14 now retain receiving links and original bodies and
are closed as relocated to receiving #29 through #31. The receiving obligations
remain open. Source dashboard #23 remains open and bot-owned.

At 21:00 UTC on 22 November, the API still returned source `private: false`,
`archived: false`, and one open issue. The connected browser was unavailable in
this follow-up chat. The recorded account-reauthentication requirement and the
requested source retirement remain pending; neither administrative setting is
inferred from successful code or history checks.

## Observed source retirement and latest receiving acceptance

After the repository owner applied the authorized settings, an independent
[GitHub repository API read](https://api.github.com/repos/edithatogo/standardflow)
at **2026-11-22T22:55:19Z** (23 November in Australia/Brisbane) returned
`private: true`, `archived: true` and `open_issues_count: 1`. The requested source
privacy and archival are complete. The remaining dashboard and transferred
receiving obligations are not marked complete by those settings.

The completed actual-main runtime receipt preceding PR #98 is bound to
[`2b0c579454a1dd469cd12cfb9538d23c96785370`](https://github.com/edithatogo/standards_check/commit/2b0c579454a1dd469cd12cfb9538d23c96785370).
Its [workflow 45070791156](https://github.com/edithatogo/standards_check/actions/runs/45070791156),
[job 137357038355](https://github.com/edithatogo/standards_check/actions/runs/45070791156/job/137357038355)
and [parity artifact 14773685812](https://github.com/edithatogo/standards_check/actions/runs/45070791156/artifacts/14773685812)
record successful imported-byte/ancestry verification, provenance regressions,
dependency consistency, source/receiving parity, container runtime and the
default-container HTTP smoke test. The source remains
`dc51d8e392858d5cb4e653aed199563514191efb`, with exact imported tree
`62d8a0e738f0255cc59822ae4e661568090a213e` and all nine preserved histories.
At this receiving revision, 26 observed checks succeeded, including deployment.

The separate [offline AI-security run 45070791434](https://github.com/edithatogo/standards_check/actions/runs/45070791434)
was still queued when re-read at approximately 22:58 UTC on 22 November; no execution
success is claimed.

[Repository-standards PR #172](https://github.com/edithatogo/repository-standards/pull/172)
merged through a permitted squash at `a3cc8dccdb67e6f122c71cec713194cdec792d07`.
The observed main tree `e884b86ea9bb1121422503122206041e086256ac` exactly matches
tested candidate `caed59dbcb6f4cc75a8fa17e24275d0ff1b61e6b`. Only the retired source
entry was removed (169 entries became 168); `standards_check` remains registered.
Nine PR checks succeeded and two expected PR checks skipped, including success
for required policy and Actions/Python analysis. Local qualification recorded
311 passes and 38 capability skips.

## Host dependency admission through PR #98

[PR #98](https://github.com/edithatogo/standards_check/pull/98) merged at
**2026-11-22T23:35:27Z**, commit `d213085a268a4cd82d522e6e17d27f3dee15bf5f`, tree
`4a34e69ae1cd857a178cf7e28245d2953a140dec`. It admits Click 8.5.1, graphviz 0.21
and jsonschema 4.26.0 in the maintained root host profile. Reviewed head
`08d9ffef20675efc80484d108b32f1d1ee759921` passed its
[legacy workflow 45082189553](https://github.com/edithatogo/standards_check/actions/runs/45082189553);
all nine ordinary checks succeeded and two offline checks remained queued.
Receiving-main execution subsequently passed at the admission merge in
[run 45084073642](https://github.com/edithatogo/standards_check/actions/runs/45084073642)
and retirement main `ba6b0888806e84276e5f54afc07e4e555220c4ea` in
[run 45085224983](https://github.com/edithatogo/standards_check/actions/runs/45085224983).
Job `137402195300` passed provenance, source/receiving parity, historical container tests
and default HTTP startup; artifact `14778918783` retains the parity receipt. The latter
main has eight successful ordinary checks; its offline-security job remains queued.
The earlier `2b0c5794` checks above retain their original revision and dependency scope.

The [qualification receipt](../../../docs/migration/standardflow/dependency-qualification-20261123.json)
binds the maintained profile to SHA-256
`27ba903aba19f5851baf887a177699ac1c9604c9ec5a7666edac573aefbe0568`.
The exact imported source, historical Docker dependencies and source PRs closed
without merging remain unchanged. Admission of the three host versions does not
merge the preserved source dependency branches.

At that earlier host-admission boundary, ipykernel 6.31.0 was unqualified: both local
kernel startups were blocked before `kernel_info` and no cells executed. The actual
hosted qualification below supersedes that blocker for its bounded optional use;
the earlier application-only results are not relabelled as kernel execution.

## Voiage downstream merge and command evidence

[Voiage PR #1394](https://github.com/edithatogo/voiage/pull/1394) merged through a
policy-enforced squash at **2026-11-22T23:32:28Z**, commit
[`a921d6471822eaac7fbc22f507760bd943ba9f6a`](https://github.com/edithatogo/voiage/commit/a921d6471822eaac7fbc22f507760bd943ba9f6a).
GitHub verified the merge signature, and the repository API returned that commit
on main. Its tree `7c0099a9c465c19648db7aca89e187141855c2c2` exactly equals reviewed
head `3bc04fdc1df6f30981765eee49c0c9dbce490cde`. The intended consumer-link change
affects one file, with one insertion and one deletion; its resulting blob is
`4849e4fc167c7da484d95f9ef652701181b30a5b`.

All 51 hosted checks succeeded and three expected checks skipped. All 17 required
check names explicitly matched successful results at the reviewed head; this
terminal hosted state was observed at 23:17:53 UTC. The local and hosted command
evidence has distinct scopes:

| Execution | Observed result |
| --- | --- |
| Full local tox attempt | Thirteen environment checks passed. The overall attempt did not pass. |
| Local coverage environment | 6,176 passed, six failed, 46 skipped, one expected failure and two subtests; coverage was 95.01%. All six failures required absent `/usr/bin/time`; normal installation was blocked at UID 1000. |
| Local docs environment | The docs validator and Python assertion passed. Dependency installation stalled and was interrupted; the owned session exited 130. No final guard or peak-memory receipt was produced. |
| Existing hosted coverage environment | 6,193 passed, 35 skipped, one expected failure and two subtests; 95.01% coverage met the 90% threshold. All six native cases that failed locally passed. |
| Existing hosted docs commands | Frozen pnpm installation, check and build all passed, with zero errors or warnings; output included 962 API pages and 1,085 site pages. |

Independent review verified that the existing
[Coverage Report job 137390005725](https://github.com/edithatogo/voiage/actions/runs/45081240057/job/137390005725)
executed the exact tox coverage environment at reviewed head `3bc04fdc...`.
The [docs job 137390005956](https://github.com/edithatogo/voiage/actions/runs/45081240057/job/137390005956)
in the same run executed all three remaining docs commands. It used synthetic
commit `5f50965d008daeb7900a6381828050903586add9`, whose tree was exactly
`7c0099a9c465c19648db7aca89e187141855c2c2`, including submodule
`054d11e08d8b28fd50821ede8a97f8be3ad50447`.

Hosted docs used the locked root virtual environment without installing the
project; local docs used `.[docs]` with an explicit interpreter. Both used
Python 3.15.2 and griffe 1.15.0. Hosted docs used Node 22.23.5 and pnpm 10.34.9.
These environment differences are retained alongside the exact tree and command
receipts. Combined evidence on the current inputs covers every required command
without reducing the gates. Existing hosted results were reused; this is not an
all-local pass, a separately dispatched full tox run, or a final guard/peak-memory
receipt.

Post-merge CI was only starting at approximately 23:35 UTC. Acceptance here is
bound to the successful reviewed-head checks and verified identical merged tree;
it does not claim that post-merge CI has completed.

Source private archival and the two identified downstream updates are complete.
Legacy-to-Rust semantic parity, item-level rights and provenance, independent
methodology and accessibility qualification remain open. See the
[retirement record](../../../docs/migration/standardflow/retirement.md) for recovery
and the [source inventory](../../../docs/migration/standardflow/source-inventory.json)
for the preserved historical observations.

## Completed downstream main checks

Voiage main `a921d6471822eaac7fbc22f507760bd943ba9f6a` subsequently completed
52 successful checks and three expected skips, with no failures or pending checks.
[The commit checks](https://github.com/edithatogo/voiage/commit/a921d6471822eaac7fbc22f507760bd943ba9f6a/checks)
are separate from the prior PR and local command receipts; the full local tox attempt
above remains recorded as unsuccessful.

## Parallel qualification integrated on 23 November 2026

PRs #101–#103 reached receiving main `7a6df395a2853c4c2052a492078cceb8f79f817d` while
the broader assurance candidate was being prepared. The candidate incorporates those
changes without altering the frozen source or replacing a consumer:

- [PR #101](https://github.com/edithatogo/standards_check/pull/101), merge
  `79e64cf2c36e56c088f082cc6bc933ac3ce89f06`, qualifies ipykernel 6.25.0 versus 6.31.0
  for the 11 frozen notebooks / 43 cells, tested protocol interactions and successful
  shutdown. Reviewed head `86ed3d82da24c2126708ac966606940b01a80f05` passed
  [the actual kernel job](https://github.com/edithatogo/standards_check/actions/runs/45096897786/job/137438587584).
  The [runbook](kernel-qualification-20261123.md) and closed issue #94 retain artifact
  identity and scope. The ordinary host renderer still has no kernel dependency.
- [PR #102](https://github.com/edithatogo/standards_check/pull/102), merge
  `756ac783564d7b848a7c231a542b301a39208391`, adds source-derived identifier fixtures
  and exact archived-object rejection for all ten STARD copies. Its
  [hosted foundation job](https://github.com/edithatogo/standards_check/actions/runs/45097073098/job/137439137943)
  passed the 11 focused tests and detailed rejection guard. The
  [source/rights ledger](../../../docs/migration/standardflow/held-guidelines-qualification.json)
  still holds every array; wording, editions and item-level permissions remain in #95.
- [PR #103](https://github.com/edithatogo/standards_check/pull/103), merge `7a6df395`,
  adds the [bounded legacy PRISMA contract](../../../docs/migration/standardflow/legacy-prisma-contract.md):
  two synthetic database-only examples and two explicit validation differences.
  Scene/SVG/text structural checks do not constitute assistive-technology or
  methodological acceptance. Unsupported mappings and real consumer cutover remain open.

These receipts retain their reviewed revisions. Integrated assurance and receiving-main
checks must still identify the actual revision they execute.
