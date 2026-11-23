# Track 05 verification

## Evidence boundary, 23 November 2026

The local assurance candidate is based on `ba6b0888806e84276e5f54afc07e4e555220c4ea`;
the individual receipts bind its changed inputs by hash. Its published head and receiving-main
CI require fresh observations. At the reviewed base, eight ordinary checks passed and the
offline-security job remained queued. Downstream Voiage main
`a921d6471822eaac7fbc22f507760bd943ba9f6a` completed 52 successful checks and three expected
skips. Those results complete earlier consolidation verification, not this new candidate.

## Technique applicability

| Technique | Current application and evidence | Limits or justified exclusion |
| --- | --- | --- |
| Property testing | Eight Rust properties, 256 cases each under seeds 0, 721114987 and 20261123: 6,144 generated cases. [Bounds and replay](rust-qualification-20261123.md). | Covers the recorded generators, not every input. The finite read-only API and Python schema rejection cases use direct contracts instead of adding another property framework. |
| Metamorphic testing | Canonical key-order/whitespace invariance and idempotence; lock construction order, reversible content/rename changes; count redistribution; renderer reading order; API list/item equality. | Identifier split mappings do not establish reversible semantic migration or equivalence with the imported legacy renderer. |
| Mutation testing | Native six-function Rust campaign: 26 selected, two initial misses repaired, 25 viable caught in the final full rerun; one explicitly unviable excluded. [Ten schema/API operators](boundary-mutation-20261123.md) all assertion-killed. | Finite selections, no repository-wide score. Changed inventories, unresolved viable mutants and unexpected infrastructure failures require review. |
| Contracts | Schema/pack guards, CLI errors, actual HTTP/CORS behavior, source-PDF comparison, lock checks and 12 diagram reference outputs. | The separate legacy 52-test/parity receipt qualifies the preserved Python runtime; it does not certify Rust semantic parity or standard-content validity. |
| Deterministic simulation | Excluded for this synchronous Rust slice and read-only API. | Neither has a distributed scheduler, virtual clock, retry queue, replica or persistent concurrent state machine. Reassess when that behavior is introduced. Filesystem failure/race tests and real HTTP tests remain required. |

The [Rust receipt](rust-qualification-20261123.json) retains native outcomes, initial misses and
input hashes. The [boundary receipt](boundary-mutation-20261123.md) explains the standard-library
driver and its assertion-only classification. Rust mutation runs are scheduled/manual in the
existing canonical-property workflow; bounded property checks remain available on relevant PRs.

## Coverage and CI

| Component | Local observation | Enforced floor |
| --- | --- | --- |
| Rust workspace | 2,742/3,430 lines, 79.94169096209912% | 79% lines |
| Maintained API | 99.22% lines, 94.59% branches; 38 tests passed | 98% lines, 90% branches |
| Maintained Python | 1,174/1,507 lines and 381/544 branches; 75.82% combined; 211 tests passed | 75% combined |

The [coverage receipt](coverage-20261123.json) retains per-file counts, source/report hashes and
the full denominator. Python keeps all 24 maintained modules, including two at zero coverage.
The Rust source-file report includes embedded unit-test code and has no stable-toolchain branch
measurement. Static API generation and browser JavaScript remain outside the API component.

`assurance.yml` emits separate Python XML and Rust/API LCOV artifacts, hashes each report and
binds it to the checked-out commit. The separate trusted Codecov job verifies that identity and
requests OIDC only there; fork PRs do not receive that upload permission. Codecov action 7.1.1
and CLI 11.3.2 are pinned. Configuration passed the official validation endpoint, but actual
uploads and project/patch statuses remain unobserved. Local component floors apply independently
of the external service; the configured Codecov patch target is 80%.

Workflow lint uses actionlint 1.7.12 and offline zizmor 1.33.1. PR dependency review uses the
pinned 5.0.1 action with a low-severity threshold. These configured jobs require exact-head
hosted acceptance. Existing CodeQL, privacy and offline-security evidence remain distinct;
a queued offline job is not a completed security assessment.

## Policy and remaining gates

The [managed-file receipt](managed-file-drift-20261123.json) compares exact upstream
`repository-standards@a3cc8dccdb67e6f122c71cec713194cdec792d07`, records local extensions and
Unicode findings, and separates live dependency discovery from update/merge qualification.
Root `SECURITY.md` preserves the shared policy with a receiving-project scope. Registry/profile
and managed-workflow divergence remain explicit rather than being overwritten silently.

The solo-maintainer ruleset is being prepared and is **not yet applied or verified**: required
PRs and stable automation checks, zero human approvals, no force pushes/deletion, no routine
bypass, and an explicit owner recovery path. Settings acceptance requires API/UI readback.

Open gates remain for offline-security execution, independent normalized interpretation and
evidence review (#82), legacy-to-Rust migration semantics, held guideline rights and source
qualification (#95), Track 04 contracts, release/offline reproducibility and provenance,
independent methodology/accessibility and publication. Optional kernel qualification (#94)
has a separate owner. See [the plan](plan.md); this track does not mark those obligations complete.
