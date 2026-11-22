# StandardFlow retirement and recovery record

Updated on **23 November 2026 (Australia/Brisbane)**. `edithatogo/standards_check` remains the public
development repository and issue destination. The user authorised importing
`edithatogo/standardflow`, then making that source repository private and archived.
**The export is merged and verified; source privacy and archival are blocked on
owner account reauthentication.** The authorized visibility change reached GitHub's
**Confirm access** screen, requiring the owner's passkey or authenticator. Successful
reauthentication has not been observed. The latest settings read still returned
`private: false` and `archived: false` at 21:00 UTC on 22 November, with zero open
source PRs and only the bot-owned dependency dashboard still open. The connected
browser was unavailable in the follow-up chat; no further settings action was applied.

## Preserved implementation and history

The current transferred compatibility baseline is source commit
`dc51d8e392858d5cb4e653aed199563514191efb`, tree
`62d8a0e738f0255cc59822ae4e661568090a213e`, under `legacy/standardflow/`.
Receiving import
[`6c67527512ad5b603307ac6415ba214d3333c42a`](https://github.com/edithatogo/standards_check/commit/6c67527512ad5b603307ac6415ba214d3333c42a)
contains that exact subtree, and all nine preserved export tips are independently
verified ancestors. It retains original main `af299f724...`, the earlier PR #9
head `41c3e174...`, and initial repair `d89a5dba...` in history.
Preparation child
[`cda5469d6107fe9729f274165ba9dd01fcba25f2`](https://github.com/edithatogo/standards_check/commit/cda5469d6107fe9729f274165ba9dd01fcba25f2)
retains the transfer and records the completed import.
[Export PR #92](https://github.com/edithatogo/standards_check/pull/92) merged as
`906c025d67b03322e5c1b41a63aea88e150672e5`; [integration PR #88](https://github.com/edithatogo/standards_check/pull/88)
then carried it to receiving main
[`15184da899f21a62565cfc3145d1a4719baf4ad4`](https://github.com/edithatogo/standards_check/commit/15184da899f21a62565cfc3145d1a4719baf4ad4).
The exact source tree and original Apache-2.0 licence are retained.

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

All nine tips are verified ancestors of receiving main `15184da8`, including the
four Renovate tips created after the original export. Normal merge commits retained
this ancestry; no squash or rebase was used. The exact `legacy/standardflow` tree
was rechecked on main. All nine live source refs matched the export inventory before
the original privacy attempt. Following source PR closure, four live source branches
remain and match their recorded tips; the five removed source refs remain recoverable
through the nine named receiving refs and main's ancestry. Temporary import workflows are
absent from receiving main; source workflows inside the retained subtree are inert.

## Acceptance and outstanding work

The [functional receipt](functional-parity.json) records current dc51 source and
receiving copies passing 52 tests each, including 11 notebooks, with all nine tips
preserved and identical
outputs for six diagram and three checklist CLI canaries. Invalid PRISMA input
also failed without output. This is same-environment legacy behaviour evidence.

[Actual-main workflow 45034583489](https://github.com/edithatogo/standards_check/actions/runs/45034583489)
passed at `15184da899f21a62565cfc3145d1a4719baf4ad4`: exact tree and all nine
histories, four provenance regressions, 52 source and 52 receiving tests, all 11
notebooks and 21 matching CLI output files. The same job passed 52 container tests
and an HTTP probe through the image's real default startup command. Its
[parity artifact](https://github.com/edithatogo/standards_check/actions/runs/45034583489/artifacts/14758977889)
retains the execution receipt. An independent actual-main clone also passed the
provenance check and 52 imported tests, and recovered the source with no configured
remote or shared object alternates. See the
[verification record](../../../conductor/tracks/03-standardflow-import/verification.md).
The source's offline security check had no execution receipt, and the receiving
[offline AI-security run](https://github.com/edithatogo/standards_check/actions/runs/45034583761)
remained queued at the observation time. Queued work is not a passed check or a waiver.

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

Source issues #12, #13 and #14 now link to receiving #29, #30 and #31 and are closed
as relocated (`not_planned` in the retired-source issue tracker). Their original
bodies remain in the issues and inventory. Testing and security obligations continue
in the open receiving issues. Source dashboard #23 remains bot-owned; no dependency
upgrade was activated by the transfer bookkeeping.

All seven source PRs were closed on 22 November 2026 after preservation. They were
closed as exported or superseded, not merged into the old source's main branch.

| Closed source PR | Receiving disposition |
| --- | --- |
| [#9: legacy compatibility repair](https://github.com/edithatogo/standardflow/pull/9) | Repaired source `dc51d8e` is preserved exactly by receiving PRs #92 and #88. |
| [#24: StepSecurity workflow hardening](https://github.com/edithatogo/standardflow/pull/24) | History retained; audited Harden Runner pin is used by the receiving workflow. |
| [#25: setup-python update](https://github.com/edithatogo/standardflow/pull/25) | History retained; audited setup-python pin is used by the receiving workflow. |
| [#26: Click update](https://github.com/edithatogo/standardflow/pull/26) | History only; dependency admission remains in receiving [#94](https://github.com/edithatogo/standards_check/issues/94). |
| [#27: graphviz update](https://github.com/edithatogo/standardflow/pull/27) | History only; dependency admission remains in receiving [#94](https://github.com/edithatogo/standards_check/issues/94). |
| [#28: ipykernel update](https://github.com/edithatogo/standardflow/pull/28) | History only; dependency admission remains in receiving [#94](https://github.com/edithatogo/standards_check/issues/94). |
| [#29: jsonschema update](https://github.com/edithatogo/standardflow/pull/29) | History only; dependency admission remains in receiving [#94](https://github.com/edithatogo/standards_check/issues/94). |

The optional runtime does not replace Rust contracts or canonical packs. Its
tests do not establish scientific correctness, Rust equivalence, independent
accessibility acceptance or production security. The 22 historical checklists
lack item-level rights/provenance receipts; the repository code licence does not
clear third-party text. The ten mislabelled STARD copies on
`feature/implement-guidelines` remain held and must not be published as accepted
standards. See the [receiving instructions](../../../legacy/README.md) and
[Conductor track](../../../conductor/tracks/03-standardflow-import/plan.md).

Known active downstream references are the repository-standards registry and
Voiage's deferred consumer link, identified in the inventory. Their reconciliation
still requires its own receipts. Source privacy and archive
settings must be applied after owner reauthentication and read back from GitHub before
retirement can be marked complete. The user has already authorized those settings;
the outstanding account check is an authentication requirement, not new scope approval.

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
