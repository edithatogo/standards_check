# StandardFlow source inventory and pending work

Refreshed on **22 November 2026**, before source retirement. The structured
[source inventory](source-inventory.json) retains both the initial and current
snapshots, exact refs, issue/PR bodies, historical review comments and proposed
receiving dispositions. Source compatibility evidence and receiving acceptance
are separate observations.

## Snapshot history

The initial observation found five branches and three open PRs. PR #9 then pointed
to `41c3e174fd7932d308992c4ef96d055273dabdbd`, had merge conflicts, and carried
seven current automated review findings.

The refresh found **seven branches and five open PRs**. PR #9 advanced to
`d89a5dbacc207cdce11f19efd667b83fdb09df18`; that repair has the original PR head
and unchanged source main as its two parents. Its hosted application/container,
privacy and adoption checks passed. The old seven findings remain attached to
`41c3e174`; their current REST line values are null. They are retained as
historical findings, not asserted as current defects.

Source main remains `af299f724bcf456c131b43a143b3eabc1d81245b`. Renovate also
created two new dependency branches and PRs. Recheck source refs immediately
before retirement so further work cannot be omitted.

## Preserve all seven current source branches

| Source branch | Exact current head | Disposition |
| --- | --- | --- |
| `main` | `af299f724bcf456c131b43a143b3eabc1d81245b` | Preserve historical main and its licence. |
| `feature/refactor-and-document` | `d89a5dbacc207cdce11f19efd667b83fdb09df18` | Repaired runnable legacy import candidate; receiving acceptance is conditional. |
| `feature/implement-guidelines` | `f1680778b4141bb5553b0e80af22bbdf5c75c862` | Held candidate based on old PR #9; excludes the new repair and must not replace it. |
| `chore/GHA-190519-stepsecurity-remediation` | `eb7d0703b86aaa82e3cd738a273db7c60a70f6c9` | Preserve PR #24; reconcile equivalent receiving workflow protection. |
| `dependabot/github_actions/actions/setup-python-7.1.0` | `7d2e233217d5d3d6c4ca9c5866f64158d117099e` | Preserve PR #25; receiving setup-python already uses this pin. |
| `renovate/click-8.x` | `3f850b81be3feb1a4d84d003b2ec6c166059a68e` | Preserve PR #26; Click 8.1.3 to 8.5.1 remains receiving dependency work. |
| `renovate/graphviz-0.x` | `38c6327a9fe507150ee2bd655f36269345cf04a8` | Preserve PR #27; graphviz 0.20.1 to 0.21 remains receiving dependency work. |

All seven receiving refs, `archive/standardflow/<source-branch>`, were
independently read through the receiving repository's matching-refs API and
matched to the exact heads above. The JSON records each archival ref, its link
and a stable receiving commit link. The old `41c3e174...` head remains in the
repaired head's ancestry and the historical snapshot.

The observed receiving candidate
[`c64c61a...`](https://github.com/edithatogo/standards_check/commit/c64c61a0a978b4b50f8d525fc76d6548d2e75718)
has repaired import `989f2fa...` as a parent. Receiving main was still
`1aef9b5b...` at this observation. Archive-ref preservation is complete for the
seven observed source heads; main admission and source retirement are not
asserted by this snapshot.

## Repaired source acceptance is conditional

[PR #9](https://github.com/edithatogo/standardflow/pull/9) now records the repair,
52 changed files against current main, and the proposed receiving import
[`989f2fa...`](https://github.com/edithatogo/standards_check/commit/989f2fa5c26b22b8294e20b442a6f602d9d124ed).

The source [hosted job log](https://github.com/edithatogo/standardflow/actions/runs/45029941592/job/137231094572)
was independently inspected: **52 host tests and 52 container tests passed** at
`d89a5dba...`. These are observed source runs. Receiving acceptance must record
exact imported tree identity, ancestry, final receiving test results and a
rollback receipt. Offline AI security was queued without an execution receipt.

The receiving candidate's hosted test and CodeQL analysis jobs succeeded, but
its separate [CodeQL result check](https://github.com/edithatogo/standards_check/runs/137233716761)
reported one new high-severity path alert at `legacy/standardflow/web/app.py:49`.
Independent inspection supports a false-positive disposition: a strict
`png`/`svg`/`pdf` membership guard precedes all temporary-file operations, and
the selected format never changes afterward. Twenty malicious format values
and a hostile-first duplicate field all returned HTTP 400 without creating a
temporary directory or calling the renderer. Five valid/default/duplicate-field
cases kept the expected fixed basename and cleaned up their output. The two
existing targeted web tests also passed with actual PNG, SVG and PDF output.
No remote alert dismissal is asserted; the structured inventory retains the
check state, code reasoning and probe details. No source patch is recommended
for this finding. The failed temporary preservation job does not negate the
seven exact archive refs subsequently verified through the API.

The [source repair report](https://github.com/edithatogo/standardflow/blob/d89a5dbacc207cdce11f19efd667b83fdb09df18/docs/reviews/2026-11-22-pull-request-review.md)
records restored checklist/variant dispatch, styles, PRISMA counts, raw JSON and
typed forms, format handling and cleaned examples. No new GitHub code-review
receipt for the repaired head was returned by the review API. This does not
transform historical findings into new defects or substitute for receiving
qualification.

## Unaccepted work and dependency candidates

The `feature/implement-guidelines` branch adds ten incorrectly labelled datasets:
AGREE, ARRIVE, CHEERS, COREQ, PRISMA-P, RIGHT, SPIRIT, SQUIRE, SRQR and TRIPOD.
Independent parsed-JSON comparison found all ten contain the same 30-item array
as `data/stard_checklist.json`. Preserve that branch as held receiving work;
those names must not be promoted into canonical packs or validated standards.
The exact equality evidence and digest remain in the JSON inventory.

[PR #24](https://github.com/edithatogo/standardflow/pull/24) only adds/pins
harden-runner. [PR #25](https://github.com/edithatogo/standardflow/pull/25) updates
setup-python in the source adoption workflow. Record receiving equivalents
before closing these as superseded.

[PR #26](https://github.com/edithatogo/standardflow/pull/26) and
[PR #27](https://github.com/edithatogo/standardflow/pull/27) each change one
dependency pin in `requirements.txt`. Preserve their branches and open one
focused receiving follow-up to qualify the candidates independently against the
accepted legacy tree. Check dependency consistency, CLI behavior, actual format
bytes, all six variant goldens and notebook execution. Retiring the source does
not admit either dependency upgrade.

## Proposed destinations for four source issues

| Source issue | Existing receiving destination | Remaining responsibility |
| --- | --- | --- |
| [#12 — Testing and CI](https://github.com/edithatogo/standardflow/issues/12) | [#29](https://github.com/edithatogo/standards_check/issues/29) | Receiving legacy tests and applicable Track 05 work; replace the stale zero-workflow snapshot with actual receipts. |
| [#13 — Security and maintenance](https://github.com/edithatogo/standardflow/issues/13) | [#30](https://github.com/edithatogo/standards_check/issues/30) | Applicable security, ruleset, coverage and updater obligations, with zero mandatory human approvals. |
| [#14 — Quality umbrella](https://github.com/edithatogo/standardflow/issues/14) | [#31](https://github.com/edithatogo/standards_check/issues/31) | Link receiving children and preserve their open dispositions. |
| [#23 — Dependency Dashboard](https://github.com/edithatogo/standardflow/issues/23) | [#76](https://github.com/edithatogo/standards_check/issues/76) | Discover imported requirements and route PR #26/#27 to a manually owned follow-up. |

These are recommendations, not claims that issue handoffs were posted. The JSON
contains ready-to-use receiving issue text. Prefer the existing quality issues
over duplicate umbrellas; keep manually owned acceptance tasks outside the
Renovate-generated dashboard body.

## Rights and evidence boundaries

Retain the source's **Apache-2.0** licence, authorship, history and attribution in
the isolated import. No separate `NOTICE` file was found. Preserve its
`CITATION.cff` as historical metadata.

The main corpus has 22 checklist JSON files without recorded item-level rights
or provenance fields. The repository's code licence does not establish rights
to every checklist description or scientific fidelity. Keep those materials
under review. Legacy tests, repaired rendering and repository consolidation do
not qualify source accuracy, methodology, external accessibility, Rust parity
or publication readiness.

The historical adoption manifest still contains source `76f2c27...` and target
`f1e7b6c...` preparation pins. Record exact receiving evidence without silently
promoting its separate activation gates.

## Retirement dependencies

The refreshed live source remains **public and unarchived**. The source has no
observed releases, tag refs, Pages, wiki, projects, discussions or forks.
The initial settings read found unprotected main and no rulesets. This is not
proof that unknown external consumers do not exist.

Known active references requiring reconciliation are the
[repository-standards registry](https://github.com/edithatogo/repository-standards/blob/e6425228dea09637eb0a45a3787421e7bce42b3b/registry/repositories.json),
which lists StandardFlow as active, and
[Voiage's deferred optional report-consumer reference](https://github.com/edithatogo/voiage/blob/f6d80e0d7adc500e2d356627469225d1b7ae557f/conductor/tracks/agent_safe_engineering_20260907/repository-boundaries.md).
No runtime integration is established by the latter. Preserve historical
baseline/review snapshots and add receiving references rather than rewriting
their observations.

Before reporting retirement complete, recheck that no source heads have
advanced beyond the seven already preserved, record legacy acceptance with
exact final-head evidence, establish pending-work destinations, reconcile
known active references and observe the actual visibility/archive settings.
Public recovery must point to the receiving repository once the source is
private. Methodological and external accessibility claims remain separate.


## Posted receiving handoffs

Source issues #12/#13/#14 are carried in receiving #29/#30/#31, whose bodies now retain the transferred obligations. The bot-owned dependency dashboard remains #76; manually owned dependency qualification is #94 and held guideline qualification is #95. CodeQL alert #4 was observed dismissed as a false positive with the guard/canary evidence above. Source retirement and final receiving-main acceptance remain pending.
