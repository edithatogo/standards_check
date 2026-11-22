# StandardFlow export verification

This receipt records evidence observed before the receiving merge. Final receiving
checks, the main-branch merge and the source's private/archive settings are recorded
in the receiving pull request. These claims concern repository preservation and the
legacy runtime; they do not qualify Rust parity, source rights or methodology.

## Source repair

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

Independent receiving checks observed:

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
