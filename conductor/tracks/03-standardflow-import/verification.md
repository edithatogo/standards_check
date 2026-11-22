# StandardFlow export verification

This receipt records evidence observed before the receiving merge. Final receiving
checks, the main-branch merge and the source's private/archive settings are recorded
in the receiving pull request. These claims concern repository preservation and the
legacy runtime; they do not qualify Rust parity, source rights or methodology.

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
regressions passed again. The new default-container HTTP smoke still requires the
final receiving hosted run; no result is inferred from its configuration.
