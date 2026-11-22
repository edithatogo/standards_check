# StandardFlow retirement and recovery record

Recorded on **22 November 2026**. `edithatogo/standards_check` remains the public
development repository and issue destination. The user authorised importing
`edithatogo/standardflow`, then making that source repository private and archived.
**Source privacy and archival are pending:** the latest settings read still
returned `private: false` and `archived: false`.

## Preserved implementation and history

The adopted compatibility snapshot is repaired source commit
`d89a5dbacc207cdce11f19efd667b83fdb09df18`, tree
`e48c081ff946d0fac6a1a4b65a3599c6b7aa3352`, under `legacy/standardflow/`.
It retains both original main `af299f724bcf456c131b43a143b3eabc1d81245b`
and the earlier PR #9 head `41c3e174fd7932d308992c4ef96d055273dabdbd` as ancestors.
The existing import `989f2fa5c26b22b8294e20b442a6f602d9d124ed` is reused as a
parent of receiving commit `c64c61a0a978b4b50f8d525fc76d6548d2e75718` in
[receiving PR #88](https://github.com/edithatogo/standards_check/pull/88).
Its exact source subtree and original Apache-2.0 licence are retained.

All seven receiving branches below were created and independently read back at
the listed SHAs. Each name is prefixed with `archive/standardflow/` in the
receiving repository; these are preserved snapshots, not accepted runtime changes.

| Source branch | Preserved SHA |
| --- | --- |
| `main` | `af299f724bcf456c131b43a143b3eabc1d81245b` |
| `feature/refactor-and-document` | `d89a5dbacc207cdce11f19efd667b83fdb09df18` |
| `feature/implement-guidelines` | `f1680778b4141bb5553b0e80af22bbdf5c75c862` |
| `chore/GHA-190519-stepsecurity-remediation` | `eb7d0703b86aaa82e3cd738a273db7c60a70f6c9` |
| `dependabot/github_actions/actions/setup-python-7.1.0` | `7d2e233217d5d3d6c4ca9c5866f64158d117099e` |
| `renovate/click-8.x` | `3f850b81be3feb1a4d84d003b2ec6c166059a68e` |
| `renovate/graphviz-0.x` | `38c6327a9fe507150ee2bd655f36269345cf04a8` |

Final integration must preserve all seven tips as ancestors, including the two
Renovate tips created after the original export. Use a **merge commit**, not
squash or rebase. Record the resulting receiving main SHA, recheck ancestry and
`HEAD:legacy/standardflow` against the pinned tree, and recheck live source refs
before retiring the source. The one-off write-capable import workflow must be
absent from receiving main; source workflows inside the retained subtree are inert.

## Acceptance and outstanding work

The [functional receipt](functional-parity.json) records the local source and
receiving copies passing 52 tests each, including 11 notebooks, with identical
outputs for six diagram and three checklist CLI canaries. Invalid PRISMA input
also failed without output. This is same-environment legacy behaviour evidence.
Final hosted receiving checks and the main merge are not claimed complete here.
The source's offline security check had no execution receipt; queued work is not
a passed check or a waiver.

The [source inventory](source-inventory.md) and its
[structured snapshot](source-inventory.json) preserve source issue/PR bodies,
historical reviews and receiving dispositions. Source issues #12, #13 and #14
have recorded receiving handoffs in [#29](https://github.com/edithatogo/standards_check/issues/29),
[#30](https://github.com/edithatogo/standards_check/issues/30) and
[#31](https://github.com/edithatogo/standards_check/issues/31); dependency discovery
from source #23 maps to receiving
[#76](https://github.com/edithatogo/standards_check/issues/76).
The three receiving issue bodies retain their transferred obligations. Source PR #9
supplies the repaired snapshot; the receiving workflow uses the harden-runner and
setup-python pins represented by PR #24/#25. PR #26/#27 are held in
[#94](https://github.com/edithatogo/standards_check/issues/94); unqualified guideline
datasets are held in [#95](https://github.com/edithatogo/standards_check/issues/95).
Preserving their commits does not admit their changes.

The optional runtime does not replace Rust contracts or canonical packs. Its
tests do not establish scientific correctness, Rust equivalence, independent
accessibility acceptance or production security. The 22 historical checklists
lack item-level rights/provenance receipts; the repository code licence does not
clear third-party text. The ten mislabelled STARD copies on
`feature/implement-guidelines` remain held and must not be published as accepted
standards. See the [receiving instructions](../../../legacy/README.md) and
[Conductor track](../../../conductor/tracks/03-standardflow-import/plan.md).

Known active downstream references are the repository-standards registry and
Voiage's deferred consumer link, identified in the inventory. Their actual
updates, the final receiving merge/check receipts and observed source privacy
and archive settings remain retirement completion evidence to add here.

## Recovery without access to the source repository

Use a full checkout of `edithatogo/standards_check`. If the checkout is shallow,
first run `git fetch --unshallow origin`. Fetch preserved refs from the receiving
repository and inspect the accepted source directly:

```bash
git fetch origin 'refs/heads/archive/standardflow/*:refs/remotes/origin/archive/standardflow/*'
git show d89a5dbacc207cdce11f19efd667b83fdb09df18:README.md
git rev-parse d89a5dbacc207cdce11f19efd667b83fdb09df18^{tree}
```

The final command must return `e48c081ff946d0fac6a1a4b65a3599c6b7aa3352`.
To recover a standalone source checkout without modifying receiving main:

```bash
recovery_parent=$(mktemp -d)
git worktree add --detach "$recovery_parent/standardflow" d89a5dbacc207cdce11f19efd667b83fdb09df18
```

Any preserved SHA in the table can be substituted. Original main's tree is
`a4527d66180a059883f7f6848eebf2c7e12fb94c`; it is historical recovery material,
not the repaired runtime. The local parity command in the receiving instructions
also reconstructs its source from receiving Git history, with no source network
access.

If integration must be rolled back, inspect the recorded receiving merge's
parents and revert the specific runtime integration changes in a new branch.
For a complete merge reversal, `git revert -m 1 <receiving-main-merge-sha>` is
appropriate only after confirming its first parent is the previous receiving
main; review the resulting diff because it also reverses other changes in that
merge. Preserve the archive refs and merge history. Recovery does not require
making the retired repository public or unarchiving it.
