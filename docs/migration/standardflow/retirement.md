# StandardFlow retirement and recovery record

Recorded on **22 November 2026**. `edithatogo/standards_check` remains the public
development repository and issue destination. The user authorised importing
`edithatogo/standardflow`, then making that source repository private and archived.
**Source privacy and archival are pending:** the latest settings read still
returned `private: false` and `archived: false`.

## Preserved implementation and history

The current transferred compatibility baseline is source commit
`dc51d8e392858d5cb4e653aed199563514191efb`, tree
`62d8a0e738f0255cc59822ae4e661568090a213e`, under `legacy/standardflow/`.
Receiving import
[`6c67527512ad5b603307ac6415ba214d3333c42a`](https://github.com/edithatogo/standards_check/commit/6c67527512ad5b603307ac6415ba214d3333c42a)
contains that exact subtree, and all nine current source tips are independently
verified ancestors. It retains original main `af299f724...`, the earlier PR #9
head `41c3e174...`, and initial repair `d89a5dba...` in history.
Preparation child
[`cda5469d6107fe9729f274165ba9dd01fcba25f2`](https://github.com/edithatogo/standards_check/commit/cda5469d6107fe9729f274165ba9dd01fcba25f2)
retains the transfer and records the completed import. The exact source tree and
original Apache-2.0 licence are retained. **Transfer is complete; the final main
merge and source privacy/archive settings remain pending.**

All nine receiving branches below were created and independently read back at
the listed SHAs. Each name is prefixed with `archive/standardflow/` in the
receiving repository; these are preserved snapshots, not accepted runtime changes.

| Source branch | Preserved SHA |
| --- | --- |
| `main` | `af299f724bcf456c131b43a143b3eabc1d81245b` |
| `feature/refactor-and-document` | `dc51d8e392858d5cb4e653aed199563514191efb` |
| `feature/implement-guidelines` | `f1680778b4141bb5553b0e80af22bbdf5c75c862` |
| `chore/GHA-190519-stepsecurity-remediation` | `eb7d0703b86aaa82e3cd738a273db7c60a70f6c9` |
| `dependabot/github_actions/actions/setup-python-7.1.0` | `7d2e233217d5d3d6c4ca9c5866f64158d117099e` |
| `renovate/click-8.x` | `3f850b81be3feb1a4d84d003b2ec6c166059a68e` |
| `renovate/graphviz-0.x` | `38c6327a9fe507150ee2bd655f36269345cf04a8` |
| `renovate/ipykernel-6.x` | `fb91d00d4f49d9b29e1a1a8dc73b1110b2518e00` |
| `renovate/jsonschema-4.x` | `59c119a933376d5f2e76d1b0088ad92f14d0fc60` |

All nine tips are preserved as ancestors of the completed transfer. Final
integration into receiving main must retain that ancestry, including the four
Renovate tips created after the original export. Use a **merge commit**, not
squash or rebase. Record the resulting receiving main SHA, recheck ancestry and
`HEAD:legacy/standardflow` against the pinned tree, and recheck live source refs
before retiring the source. The one-off write-capable import workflow must be
absent from receiving main; source workflows inside the retained subtree are inert.

## Acceptance and outstanding work

The [functional receipt](functional-parity.json) records current dc51 source and
receiving copies passing 52 tests each, including 11 notebooks, with all nine tips
preserved and identical
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
setup-python pins represented by PR #24/#25. Dependency PRs #26/#27/#28/#29 are held in
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
git show dc51d8e392858d5cb4e653aed199563514191efb:README.md
git rev-parse dc51d8e392858d5cb4e653aed199563514191efb^{tree}
```

The final command must return `62d8a0e738f0255cc59822ae4e661568090a213e`.
To recover a standalone source checkout without modifying receiving main:

```bash
recovery_parent=$(mktemp -d)
git worktree add --detach "$recovery_parent/standardflow" dc51d8e392858d5cb4e653aed199563514191efb
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
