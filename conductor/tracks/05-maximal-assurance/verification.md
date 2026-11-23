# Track 05 verification

## Evidence boundary, 23 November 2026

The local assurance candidate began at `ba6b0888806e84276e5f54afc07e4e555220c4ea`;
the individual receipts bind changed inputs by hash. Its first published head was
`12b7b00737124aa7c0feaead893c930124332489` in PR #100. The follow-up fixes and receiving-main
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
| Deterministic simulation | The API request-budget test advances a mocked clock to verify exhaustion, rejection before parsing/I/O and recovery after expiry. | No distributed scheduler, retry queue or replica exists in this slice. The rate counter is process-local; shared-store/deployment semantics need their own qualification before adding workers. Synchronous Rust filesystem failure/race tests remain required. |

The [Rust receipt](rust-qualification-20261123.json) retains native outcomes, initial misses and
input hashes. The [boundary receipt](boundary-mutation-20261123.md) explains the standard-library
driver and its assertion-only classification. Rust mutation runs are scheduled/manual in the
existing canonical-property workflow; bounded property checks remain available on relevant PRs.
The [actual manual hosted run](rust-hosted-first-head-20261123.md) at first head `12b7b007`
also passed: 72 workspace tests and the exact 25-caught/one-unviable native campaign, with
downloaded artifacts verified. cargo-mutants' own selected-package baseline had 61 passing
tests; it is distinct from the full-workspace gate. Those Rust inputs remain unchanged in
the subsequent Python/API integration.

## Coverage and CI

| Component | Local observation | Enforced floor |
| --- | --- | --- |
| Rust workspace | 2,742/3,430 lines, 79.94169096209912% | 79% lines |
| Maintained API | 100% lines, 94.74% branches; 40 tests passed | 98% lines, 90% branches |
| Maintained Python | 1,700/2,151 lines and 520/744 branches; 76.68% combined; 265 tests passed | 75% combined |

The [coverage receipt](coverage-20261123.json) retains per-file counts, source/report hashes and
the full denominator. Python keeps all 28 maintained modules, including `simple_extract.py` at zero coverage.
The Rust source-file report includes embedded unit-test code and has no stable-toolchain branch
measurement. Static API generation and browser JavaScript remain outside the API component.

`ci.yml` emits separate Python XML and Rust/API LCOV artifacts, hashes each report and
binds it to the checked-out commit. The separate trusted Codecov job verifies that identity and
requests OIDC only there; fork PRs do not receive that upload permission. Codecov action 7.1.1
and CLI 11.3.2 are pinned. At first head `12b7b007`, all three OIDC uploads succeeded and the
[Codecov App patch check](https://github.com/edithatogo/standards_check/runs/137437302663)
passed with 94.59% diff coverage against the 80% target. No project check was observed at that
head; legacy commit statuses were empty. Local component floors apply independently of the
external service. Later revisions require their own upload/provider observations.

The integrated Python measurement adds the existing real legacy/Rust PRISMA comparison after
its six validators. The new production modules initially reduced coverage to 71.47%; exercising
the qualified CLI contract raised it to 76.66% without exclusions or a lower floor. Its full-history
checkout, maintained legacy profile and exact Rust CLI build are explicit in CI.

The later runtime integration retains PR #104/#105's fixes and requests the repository-declared
`rustfmt,clippy` components explicitly at all eleven pinned Rust setup sites. The Rust coverage
job also retains `llvm-tools-preview`. This removes the deferred component-installation phase
that failed before PRISMA execution on both receiving main and the first integrated candidate;
the original `not_run` observations remain distinct from successful contract receipts. The
foundation profile's conditional dependency is evaluated by the SBOM guard for its selected
interpreter, with unsupported marker forms rejected before installation.

PR #106 repairs two observed Pages deployment failures in
[run 45097737175](https://github.com/edithatogo/standards_check/actions/runs/45097737175):
metadata was initially unavailable, and a retry then found two artifacts with the old shared
name. Upload and native deployment now share an attempt-specific name. A bounded REST guard
requires the exact uploaded ID, name, workflow run and unexpired state; ambiguous or incomplete
metadata fails. Eleven runnable regressions exercise the actual inline probe with controlled responses
and clock, while the native deployment remains authoritative for its separate Actions Results
lookup. Successful receiving-main Pages deployment is still required before claiming recovery.

Workflow lint uses actionlint 1.7.12 and offline zizmor 1.33.1. PR dependency review uses the
pinned 5.0.1 action with a low-severity threshold. Those jobs, all three component coverage
jobs and the upgraded privacy action passed at the first head. Its mutation job failed before
mutation because the five-package foundation profile was installed under Python 3.12. The
[setup correction](boundary-mutation-20261123.md) uses the existing profile's qualified Python
3.14 runtime and retains the failed observation. The stable aggregate correctly failed then.
Existing CodeQL, privacy and offline-security evidence remain distinct; a queued offline job
is not a completed security assessment. The authenticated runner settings page explicitly
reported **no runners configured**. The pinned caller requires a self-hosted Linux/x64
`ai-security-offline` runner with a preloaded digest-bound security image and isolated Docker
execution; neither a hosted substitute nor a disabled check qualifies that requirement.

Live security inspection found two High CodeQL alerts in the maintained API: missing rate
limiting and request-derived log formatting. The follow-up adds the shared 100-request/minute
budget and constant-format logging, with failure-first HTTP/clock regressions and unchanged
coverage floors. Hosted alert resolution is still a separate observation; passing Analyze
jobs alone does not establish an empty alert inventory.

## Policy and remaining gates

The [managed-file receipt](managed-file-drift-20261123.json) compares exact upstream
`repository-standards@a3cc8dccdb67e6f122c71cec713194cdec792d07`, records local extensions and
Unicode findings, and separates live dependency discovery from update/merge qualification.
Root `SECURITY.md` preserves the shared policy with a receiving-project scope. The registered
public/baseline controls require dependency review and a current dependency SBOM. Scorecard,
Security Insights and SLSA are not selected by that profile; future publication may change
their applicability. The [nine dependency inventories](sbom-20261123.md) cover current
Cargo/npm locks and maintained Python profiles, including both optional kernel environments.
Their standalone `Maintained dependency inventories` job is a separate required check; these
are dependency inventories, not release binary/container provenance. Local multi-language assurance occupies the managed `ci.yml` path while
preserving its specialized jobs; this is not byte equality with the central Node-only template.
Registry/profile and managed-workflow divergence remain explicit.

The authenticated security overview showed private vulnerability reporting, Dependabot alerts,
CodeQL/code-scanning alerts and secret scanning enabled. The repository's installed-apps page
showed Renovate. These are observed settings, not qualification of every updater's protected
update/merge lifecycle. Dependabot's Actions configuration remains in place.

The solo-maintainer ruleset is being prepared and is **not yet applied or verified**: required
PRs and stable automation checks, zero human approvals, no force pushes/deletion, no routine
bypass, conversation resolution and an explicit owner recovery path. It also requires CodeQL
results with High-or-higher security alerts and error-level alerts blocked in the PR diff.
That native rule does not independently clear pre-existing alerts; actual alert resolution
still needs observation. Settings acceptance requires API/UI readback.

The 23 November submission reached GitHub's **Confirm access / Passkey** prompt before saving.
The complete form has Active selected, seven checks bound to GitHub Actions, no bypass actors
and zero required approvals, but the API still returned an empty ruleset inventory. Activation
requires the owner's GitHub reauthentication; the prepared form is not an enforced rule.

Open gates remain for offline-security execution, independent normalized interpretation and
evidence review (#82), legacy-to-Rust migration semantics, held guideline rights and source
qualification (#95), Track 04 contracts, release/offline reproducibility and provenance,
independent methodology/accessibility and publication. The optional kernel comparison (#94)
is now qualified through #101. PRs #102/#103 add held-source identity rejection and bounded
legacy PRISMA count parity; their broader source/content and consumer gates remain open.
See [the plan](plan.md); this track does not mark those obligations complete.
