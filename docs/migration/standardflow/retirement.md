# StandardFlow retirement and recovery record

Updated on **23 November 2026 (Australia/Brisbane)**. `edithatogo/standards_check` remains the public
development repository and issue destination. The user authorised importing
`edithatogo/standardflow`, then making that source repository private and archived.
**The export is merged and verified, and the source is now private and archived.**
After the owner applied the authorized settings, an independent
[GitHub repository API read](https://api.github.com/repos/edithatogo/standardflow)
at **2026-11-22T22:55:19Z** returned `private: true`, `archived: true` and
`open_issues_count: 1`. The registry cleanup is also merged through
[repository-standards PR #172](https://github.com/edithatogo/repository-standards/pull/172).
Voiage's separate consumer-link change still awaits its current checks and merge.

The earlier authentication blocker is historical: the first visibility attempt
reached GitHub's **Confirm access** screen, and the 21:00 UTC settings read still
showed `private: false` and `archived: false`. The connected browser was unavailable
in that follow-up chat. Those observations are retained in the structured inventory;
the later API read above establishes the completed source settings.

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

The latest accepted receiving main is
[`2b0c579454a1dd469cd12cfb9538d23c96785370`](https://github.com/edithatogo/standards_check/commit/2b0c579454a1dd469cd12cfb9538d23c96785370).
[Actual-main workflow 45070791156](https://github.com/edithatogo/standards_check/actions/runs/45070791156),
[job 137357038355](https://github.com/edithatogo/standards_check/actions/runs/45070791156/job/137357038355)
and [parity artifact 14773685812](https://github.com/edithatogo/standards_check/actions/runs/45070791156/artifacts/14773685812)
record successful provenance, source/receiving parity, container and default-command
HTTP checks. The exact legacy tree and all nine histories remain preserved. At that
main revision, 26 observed checks succeeded, including deployment. The separate
[offline AI-security run 45070791434](https://github.com/edithatogo/standards_check/actions/runs/45070791434)
was still queued when re-read at approximately 22:58 UTC on 22 November and has
no execution receipt.

Earlier integration acceptance remains bound to its original revision:

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

The repository-standards registry cleanup merged at
`a3cc8dccdb67e6f122c71cec713194cdec792d07`; observed main tree
`e884b86ea9bb1121422503122206041e086256ac` equals the tested candidate tree exactly.
The only registry change removes retired `standardflow`, reducing 169 entries to
168 while retaining `standards_check`. Nine PR checks succeeded and two expected
checks skipped; required policy and Actions/Python analysis succeeded. Local
qualification recorded 311 passes and 38 capability skips.

[Voiage PR #1394](https://github.com/edithatogo/voiage/pull/1394) is verified signed
and current with main at `3bc04fdc1df6f30981765eee49c0c9dbce490cde`, containing the
intended one-line consumer link. Hosted checks and its required local gate remain
pending before merge. The [structured inventory](source-inventory.json) retains
the exact candidate tree and earlier downstream observations. Source private
archival and registry completion do not qualify the pending downstream, security,
rights or semantic-migration work.

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
