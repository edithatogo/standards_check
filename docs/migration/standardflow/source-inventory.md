# StandardFlow source inventory and pending work

Refreshed on **22 November 2026**, before source retirement. The structured
[source inventory](source-inventory.json) preserves the initial five-branch
snapshot, the intervening seven-branch snapshot, and the current nine-branch
snapshot, including exact refs, source issue/PR bodies, historical reviews,
receiving handoffs and evidence boundaries.

## Current source and receiving state

Source main remains `af299f724bcf456c131b43a143b3eabc1d81245b`. Source PR #9
advanced first from `41c3e174...` to repaired revision `d89a5dba...`, then to
`dc51d8e392858d5cb4e653aed199563514191efb`. Its current tree is
`62d8a0e738f0255cc59822ae4e661568090a213e`.

The latest source commit is one commit after d89 and changes exactly three files:
`web/app.py` selects fixed output filenames and MIME types; `Dockerfile` starts
Flask explicitly on `0.0.0.0:5000`; the review document records that follow-up.
The original seven automated findings remain historical findings at `41c3e174`.
The previous snapshots retain the observations without presenting those
findings as current defects.

**Transfer is complete** at receiving commit
[`6c67527512ad5b603307ac6415ba214d3333c42a`](https://github.com/edithatogo/standards_check/commit/6c67527512ad5b603307ac6415ba214d3333c42a).
The imported `legacy/standardflow` subtree exactly matches current dc51's tree
`62d8a0e738f0255cc59822ae4e661568090a213e`, and all nine source tips are verified
ancestors. Preparation child
[`cda5469...`](https://github.com/edithatogo/standards_check/commit/cda5469d6107fe9729f274165ba9dd01fcba25f2)
retains that transfer. The [functional receipt](functional-parity.json) records
same-environment parity for this current baseline. Normal receiving-main merge
[`15184da899f21a62565cfc3145d1a4719baf4ad4`](https://github.com/edithatogo/standards_check/commit/15184da899f21a62565cfc3145d1a4719baf4ad4)
is complete; its tree matches the verified PR #88 head, with the exact source
subtree and all nine source tips retained as ancestors. Final hosted results are
24 successes, one expected deployment skip and zero hosted failures. Two offline
security jobs remain queued without execution receipts. Source retirement is
blocked on GitHub account reauthentication.

## Nine current source branches

| Source branch | Exact current head | Receiving status |
| --- | --- | --- |
| `main` | `af299f724bcf456c131b43a143b3eabc1d81245b` | Exact archive ref previously verified. |
| `feature/refactor-and-document` | `dc51d8e392858d5cb4e653aed199563514191efb` | Exact transfer and current archive ref verified. |
| `feature/implement-guidelines` | `f1680778b4141bb5553b0e80af22bbdf5c75c862` | Exact archive ref previously verified; held work in receiving #95. |
| `chore/GHA-190519-stepsecurity-remediation` | `eb7d0703b86aaa82e3cd738a273db7c60a70f6c9` | Exact archive ref previously verified; reconcile workflow equivalent. |
| `dependabot/github_actions/actions/setup-python-7.1.0` | `7d2e233217d5d3d6c4ca9c5866f64158d117099e` | Exact archive ref previously verified; receiving setup-python uses this pin. |
| `renovate/click-8.x` | `3f850b81be3feb1a4d84d003b2ec6c166059a68e` | Exact archive ref previously verified; dependency qualification in #94. |
| `renovate/graphviz-0.x` | `38c6327a9fe507150ee2bd655f36269345cf04a8` | Exact archive ref previously verified; dependency qualification in #94. |
| `renovate/ipykernel-6.x` | `fb91d00d4f49d9b29e1a1a8dc73b1110b2518e00` | Exact archive ref verified; dependency qualification in #94. |
| `renovate/jsonschema-4.x` | `59c119a933376d5f2e76d1b0088ad92f14d0fc60` | Exact archive ref verified; dependency qualification in #94. |

All **nine** receiving `archive/standardflow/<source-branch>` refs were
independently read back at their exact current source SHAs. The advanced dc51
feature ref and new ipykernel/jsonschema refs are now included. Each source tip
also passes an ancestry check against receiving import `6c675275...`; preservation
is complete both through named refs and import history. The five- and
seven-branch snapshots remain historical evidence. Recheck source refs
immediately before retirement so later work cannot be omitted.

## Source tests and receiving acceptance

The current source [application/container job](https://github.com/edithatogo/standardflow/actions/runs/45031578996/job/137236118355)
passed **52 host tests and 52 container tests**. Its checkout was synthetic PR
merge `e5bcde3c1d939b48d5ee3da24754eca6691f5b98`; independent commit inspection
confirmed its tree is identical to dc51's tree. Privacy/secrets and adoption
checks also passed. Offline AI security remained queued without an execution
receipt.

The source container command explicitly ran unittest instead of the image's
default command. It therefore does not establish that the default startup
accepts connections through a published host port. The receiving [legacy job](https://github.com/edithatogo/standards_check/actions/runs/45034143605/job/137244023298)
now supplies that separate evidence: four provenance tests, 52 source plus 52
receiving parity tests, 52 Docker tests, and the default-command HTTP smoke test
all passed. The [Python job](https://github.com/edithatogo/standards_check/actions/runs/45034143412/job/137244022542)
passed 201 tests, and the [CodeQL aggregate](https://github.com/edithatogo/standards_check/runs/137244165310)
succeeded. The initial d89 source tests and check states remain in the
seven-branch historical snapshot.

The [current source review report](https://github.com/edithatogo/standardflow/blob/dc51d8e392858d5cb4e653aed199563514191efb/docs/reviews/2026-11-22-pull-request-review.md)
records both the initial compatibility repair and this follow-up. The source
PR body still links the original receiving import
[`989f2fa...`](https://github.com/edithatogo/standards_check/commit/989f2fa5c26b22b8294e20b442a6f602d9d124ed)
and d89 validation. Those historical references do not qualify a later receiving
head automatically. No GitHub review submission at dc51 was returned by the
review API; this is an observation, not an additional invented approval gate.

## CodeQL disposition retained

At the d89 receiving candidate, CodeQL flagged a file read at
`legacy/standardflow/web/app.py:49`. The fixed `png`/`svg`/`pdf` allowlist
dominated all temporary-file operations. Twenty malicious format values and a
hostile-first duplicate field returned HTTP 400 without creating a temporary
directory or calling the renderer. Five valid/default/duplicate-field cases
retained fixed basenames and cleaned up their output; the existing targeted
tests passed with actual PNG, SVG and PDF output.

[CodeQL alert #4](https://github.com/edithatogo/standards_check/security/code-scanning/4)
was subsequently observed dismissed as a false positive. The recorded
disposition and detailed evidence remain intact in the JSON. The latest source
follow-up separately selects literal filenames from a server-side mapping.
The earlier dismissal does not substitute for the new receiving result; the
final CodeQL aggregate subsequently succeeded, as recorded above.

## Held work and four dependency candidates

The `feature/implement-guidelines` branch contains ten incorrectly labelled
datasets: AGREE, ARRIVE, CHEERS, COREQ, PRISMA-P, RIGHT, SPIRIT, SQUIRE, SRQR and
TRIPOD. Independent parsed-JSON comparison found that all ten contain the same
30-item array as `data/stard_checklist.json`. That branch also lacks the later
runtime repairs. Preserve it as held work in
[receiving #95](https://github.com/edithatogo/standards_check/issues/95); do not
promote its named datasets into canonical packs or overwrite the repaired
runtime. The equality evidence and digest remain in the JSON.

[Source PR #24](https://github.com/edithatogo/standardflow/pull/24) only adds/pins
harden-runner. [Source PR #25](https://github.com/edithatogo/standardflow/pull/25)
updates setup-python in the source adoption workflow. Record receiving
equivalents before closing those source PRs as superseded.

The manually owned [receiving dependency issue #94](https://github.com/edithatogo/standards_check/issues/94)
now carries all four dependency candidates; its amendment for PRs #28/#29 was
independently read after posting.

| Source PR | Candidate | Qualification emphasis |
| --- | --- | --- |
| [#26](https://github.com/edithatogo/standardflow/pull/26) | Click 8.1.3 → 8.5.1 | CLI overrides, errors and module entry point. |
| [#27](https://github.com/edithatogo/standardflow/pull/27) | graphviz 0.20.1 → 0.21 | Actual artifact bytes, six variant goldens and notebooks. |
| [#28](https://github.com/edithatogo/standardflow/pull/28) | ipykernel 6.25.0 → 6.31.0 | Notebook execution and interactive kernel compatibility. |
| [#29](https://github.com/edithatogo/standardflow/pull/29) | jsonschema 4.17.3 → 4.26.0 | Valid/rejected fixtures, draft/reference behavior and diagnostics. |

Each candidate changes one requirements pin. Qualify them independently against
the accepted repaired baseline, retain dependency consistency and the full
legacy suite, and record accepted or rejected outcomes. Existing notebook
fixture execution does not by itself qualify interactive kernel behavior.
Source retirement does not admit these upgrades.

## Posted receiving handoffs

| Source issue | Receiving destination | Remaining responsibility |
| --- | --- | --- |
| [#12 — Testing and CI](https://github.com/edithatogo/standardflow/issues/12) | [#29](https://github.com/edithatogo/standards_check/issues/29) | Legacy tests and applicable Track 05 obligations; exact receiving evidence. |
| [#13 — Security and maintenance](https://github.com/edithatogo/standardflow/issues/13) | [#30](https://github.com/edithatogo/standards_check/issues/30) | Security, rulesets, coverage and updater obligations, with zero mandatory human approvals. |
| [#14 — Quality umbrella](https://github.com/edithatogo/standardflow/issues/14) | [#31](https://github.com/edithatogo/standards_check/issues/31) | Receiving child links and open dispositions. |
| [#23 — Dependency Dashboard](https://github.com/edithatogo/standardflow/issues/23) | [#76](https://github.com/edithatogo/standards_check/issues/76), with [#94](https://github.com/edithatogo/standards_check/issues/94) | Imported dependency discovery and manual qualification of four candidates. |

The receiving #29/#30/#31 issue bodies retain the transferred obligations.
The bot-owned dashboard remains #76; manual dependency and held-guideline
qualification remain in #94 and #95. The structured inventory preserves the
posted mappings as well as the original recommendation text.

## Rights and retirement boundaries

Retain the source's **Apache-2.0** licence, authorship, history and attribution in
the isolated import. No separate `NOTICE` file was found. Preserve `CITATION.cff`
as historical metadata. The 22 main checklist JSON files lack recorded item-level
rights or provenance fields; the code licence does not establish rights to every
checklist description or scientific fidelity. Legacy tests and consolidation do
not qualify methodology, external accessibility, Rust parity or publication
readiness.

The historical adoption manifest retains source `76f2c27...` and target
`f1e7b6c...` preparation pins. Record receiving evidence without promoting its
separate activation gates.

The API observation at **14:48:07 UTC on 22 November 2026** confirmed that the
source remains **public and unarchived**. The retirement status is
`blocked_on_account_reauthentication`: GitHub Confirm access (sudo/passkey)
appeared before the privacy change was applied. Neither privacy nor archival
has changed; the receiving repository remains public and active. The source
inventory records four open
issues and seven open PRs. There are no observed releases, tag refs, Pages, wiki,
projects, discussions or forks. The initial settings observation found
unprotected main and no rulesets; this does not prove that external consumers
are absent.

Known references requiring reconciliation include the
[repository-standards registry](https://github.com/edithatogo/repository-standards/blob/e6425228dea09637eb0a45a3787421e7bce42b3b/registry/repositories.json)
and [Voiage's deferred optional report-consumer reference](https://github.com/edithatogo/voiage/blob/f6d80e0d7adc500e2d356627469225d1b7ae557f/conductor/tracks/agent_safe_engineering_20260907/repository-boundaries.md).
The latter does not establish a runtime integration. Preserve historical
baseline/review snapshots when updating active destinations.

The [Voiage update, PR #1394](https://github.com/edithatogo/voiage/pull/1394), is
published and all 17 required checks pass, but its unsigned commit cannot merge
while main requires verified signatures. The registry removal is prepared and
tested with 311 passes, 38 capability skips and 168 schema entries; the prepared change is not merged pending actual source
archival. Any draft publication leaves active registry/main unchanged.

Receiving-main integration and hosted compatibility receipts are complete.
To resume source retirement, the account owner must complete GitHub
reauthentication, after which the authorized privacy/archive actions can proceed
and their actual API state must be verified. Public recovery already exists in
the receiver. Do not report source retirement complete while its API settings
remain public and unarchived.
