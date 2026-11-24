# Conductor tracks

Status, implementation completeness and evidence are separate. Hosted receipts apply only to
their recorded commit. PR #60's hosted integration acceptance is recorded at
`bfe2255fda85b891c2f68044676c0b777d92c38c`; later revisions require their own checks. Compiler and synthetic-fixture checks do not establish methodological
validity, source reconciliation, external accessibility certification, rights or publication.

| ID | Track | Horizon | Depends on | Status | Implementation | Evidence | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 00 | [Platform foundation](tracks/00-platform-foundation/spec.md) | short | none | implementation complete (bounded) | Rust/Conductor foundation and brownfield controls implemented | PR #79/main receipts; registered node/baseline local specialization accepted in #30 | No new foundation logic needed; exact thin-call/template equality is not claimed or a blocker to accepted local CI |
| 01 | [Canonical Standard Pack runtime](tracks/01-canonical-standard-pack/spec.md) | short | 00 | implementation complete | source implemented; hosted integration accepted at recorded revision | runtime fixtures at PR #60; bounded 42-item source comparison at PR #83 | Strict packs, canonicalization, locks and CLI; PRISMA transcription reconciled; interpretation, migration, broader rights and external gates remain open |
| 02 | [Semantic diagram engine and PRISMA 2020 flows](tracks/02-semantic-diagram-prisma/spec.md) | short | 01 | implementation complete | source implemented; hosted integration accepted | fixture proven at recorded PR #60 revision | Four PRISMA families and 12 golden outputs; independent source, rights, accessibility, methodology and publication gates remain open |
| 03 | [History-preserving standardflow import](tracks/03-standardflow-import/spec.md) | short | 00, 01, 02 | in progress (semantic cutover) | History/source retirement, host and interactive-kernel qualification complete | #88/#92/#99/#101; exact source and nine histories verified | Historical import complete; [#82](https://github.com/edithatogo/standards_check/issues/82)/[#95](https://github.com/edithatogo/standards_check/issues/95), consumer parity and independent review remain open |
| 04 | Research ecosystem contracts | medium | 01, 02 | planned | contracted | contracted | Exact-pinned evidence exchange with SearchRight, SourceRight and AuthenText |
| 05 | [Maximal assurance, release and external validation](tracks/05-maximal-assurance/spec.md) | short to long | 00–03 now; 04 for ecosystem release | in progress (operations/release) | Bounded assurance, coverage, CodeQL fixes, ruleset and Pages repair accepted | implementation main `dd3f995`; [verification](tracks/05-maximal-assurance/verification.md); docs PR #108 | [#29](https://github.com/edithatogo/standards_check/issues/29) closed; [#30](https://github.com/edithatogo/standards_check/issues/30) updater/offline runner and broader release/external gates open |

Revision-bound receipts and open gates are retained in each active track's metadata, plan and
evidence file. PR #60's historical hosted acceptance and PR #59's merge are retained; neither is an open merge dependency.
The detailed sequencing and later capabilities remain in [`roadmap.md`](./roadmap.md).

## Current reconciliation

The accepted bounded implementation is `dd3f995c473db0cc1cd6dad9d392b3744166958b`;
its evidence documentation merged as `54456f7b88f0f926e4f1513fe3321873159489b3`
([PR #108](https://github.com/edithatogo/standards_check/pull/108)). The active
[solo-maintainer ruleset](https://github.com/edithatogo/standards_check/rules/27871801)
requires seven app-bound checks and no human approval or bypass. CodeQL readback
showed zero open alerts, with four closed as fixed. [Issue #29](https://github.com/edithatogo/standards_check/issues/29)
is closed for its bounded testing/CI scope; [#30](https://github.com/edithatogo/standards_check/issues/30)
and umbrella [#31](https://github.com/edithatogo/standards_check/issues/31) remain open
for legitimate protected updater qualification and actual offline-security execution.
A queued job is not a test result.

For new reporting checklists or diagrams, follow the single
[intake and publication checklist](../CONTENT_POPULATION_WORKFLOW.md): no catalogue-wide
copying or admission of held sources. [#82](https://github.com/edithatogo/standards_check/issues/82)
owns PRISMA interpretation and semantic migration; [#95](https://github.com/edithatogo/standards_check/issues/95)
owns the unqualified historical guideline copies. The [EQUATOR directory issue #111](https://github.com/edithatogo/standards_check/issues/111)
owns source discovery, rights-aware acquisition and the future Searchright consumer handoff.
[PR #112](https://github.com/edithatogo/standards_check/pull/112) merged the source directory; [#127](https://github.com/edithatogo/standards_check/pull/127), [#129](https://github.com/edithatogo/standards_check/pull/129) and [#130](https://github.com/edithatogo/standards_check/pull/130) merged the legacy crosswalk, source-link leads and local text triage. [#132](https://github.com/edithatogo/standards_check/pull/132) merged the retained 82-row primary article candidate ledger, and [#134–138](https://github.com/edithatogo/standards_check/pull/138) advanced bounded structural extraction and comparison. These are not additional admitted packs. [#139](https://github.com/edithatogo/standards_check/pull/139) is the catalogue-wide batch candidate; see [Track 01 Phase 5](tracks/01-canonical-standard-pack/plan.md). Track 04 remains **planned**: do not build an adapter or
scaffold until the pinned consumer contract and tests are ready.

### Earlier historical receipts


Track 00 brownfield audit and Conductor integrity checks merged through [PR #79](https://github.com/edithatogo/standards_check/pull/79) at receiving-main commit `840b8431403035be7e5dec5f22b64ad3ddb20d2b`. Exact-head PR checks passed at `baab246e62f3585237b987f87647eba743f2818e`; receiving-main checks must be recorded separately. The distinct legacy rights, profile and migration gates remain open. See [quality frontier reconciliation](quality-frontier-20261119.md).

PR #83 promoted the PRISMA pack to 42 source-reconciled checklist items at `da7e780dad139980cadfc40fb0fec44d90f6af50`. The [20 November receiving review](prisma2020-receiving-review-20261120.md) distinguishes the correct retained transcription from integration and source-gate defects and records their focused repair. Earlier 27-item descriptions are historical. The separately merged offline security caller still requires a qualified runner and an actual execution receipt; a queued job is not acceptance.
