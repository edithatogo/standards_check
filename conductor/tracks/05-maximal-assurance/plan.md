# Plan: Maximal assurance, release and external validation

Status: **in progress**. Implementation: **source implemented** for the bounded assurance
work accepted on main `dd3f995c473db0cc1cd6dad9d392b3744166958b`. Its native measurements,
dependency inventories, observed privacy/CodeQL controls and applied protection are verified.
The [portable verification receipt](verification-receipt-20261123.json) reports **partial**
because the existing operational, release and independent programme gates remain open.
The [revision record](hosted-status-20261123.json) preserves earlier failures and observations.

## Completed software and settings work

- [x] **T05.001** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Record applicability and limits for properties, metamorphic relations, contracts and simulation.
- [x] **T05.002** ([#29](https://github.com/edithatogo/standards_check/issues/29)) Qualify eight Rust properties with recorded bounds, three seeds and failure replay.
- [x] **T05.003** ([#29](https://github.com/edithatogo/standards_check/issues/29)) Run the bounded native Rust campaign; retain the initial misses and one unviable mutant.
- [x] **T05.004** ([#29](https://github.com/edithatogo/standards_check/issues/29)) Verify ten schema/API assertion kills after two clean baselines on actual main.
- [x] **T05.005** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Enforce unchanged component coverage floors and verify native report/checkout bindings.
- [x] **T05.006** ([#29](https://github.com/edithatogo/standards_check/issues/29)) Run all six validators and the real two-pair legacy/Rust PRISMA comparison in Python coverage.
- [x] **T05.007** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Verify nine maintained dependency inventories and all 48 retained-file checksums on actual main.
- [x] **T05.008** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Verify three main OIDC uploads and the successful legacy patch status; distinguish absent App/project checks.
- [x] **T05.009** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Repair rate-limit and logging findings; observe alerts #1/#2 Fixed via PR #100.
- [x] **T05.010** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Repair both corpus-path boundaries, retain failure-first and native filesystem regressions,
  and observe alerts #5/#6 Fixed via PR #107. Main shows zero open and four closed alerts.
- [x] **T05.011** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Preserve the initial checksum-format privacy failure, its clean correction and unchanged scanner policy.
- [x] **T05.012** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Correct the valid historical-API review finding, prove old/current receipt separation,
  publish the fix and resolve the addressed thread before normal protected merge.
- [x] **T05.013** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Verify actual main privacy: no detected Gitleaks findings or reviewed exceptions;
  no Presidio blocking findings, with seven advisory checksum matches retained.
- [x] **T05.014** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Bind Pages probe/deployment to the exact attempt artifact and observe native main8029 recovery.
- [x] **T05.015** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Activate ruleset 27871801, verify seven strict app-bound checks with zero human approvals
  and no bypass, and observe normal merges under unchanged protections.
- [x] **T05.016** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Document the authenticated owner recovery path; no recovery change was rehearsed.
- [x] **T05.017** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Reconcile local multi-language `ci.yml` through the existing managed-policy conflict route
  in [#30](https://github.com/edithatogo/standards_check/issues/30), preserving stronger local
  controls without claiming exact reusable-call or template-byte conformance.
- [x] **T05.018** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Export one schema-conforming partial verification receipt from the accepted implementation.

## Remaining operational and programme work

- [ ] **T05.019** ([#30](https://github.com/edithatogo/standards_check/issues/30), [#76](https://github.com/edithatogo/standards_check/issues/76)) Qualify legitimate updater work under current protection, including ecosystem checks,
  normal merge and receiving results; retain Dependabot until handover is demonstrated.
- [ ] **T05.020** ([#30](https://github.com/edithatogo/standards_check/issues/30)) Complete the existing [#30 offline-security prerequisites](https://github.com/edithatogo/standards_check/issues/30)
  and obtain an executed receipt from the qualified image/assets and matching isolated runner.
- [ ] **T05.021** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Complete independent interpretation/evidence review and broader migration semantics
  in [#82](https://github.com/edithatogo/standards_check/issues/82).
- [ ] **T05.022** ([#95](https://github.com/edithatogo/standards_check/issues/95)) Reconcile held guideline identities, item-level rights/provenance and independent fixtures
  before admission in [#95](https://github.com/edithatogo/standards_check/issues/95).
- [ ] **T05.023** ([#161](https://github.com/edithatogo/standards_check/issues/161)) Complete applicable Track 04 ecosystem contracts and downstream canaries.
- [ ] **T05.024** ([#30](https://github.com/edithatogo/standards_check/issues/30)) Produce release/offline reproducibility, release-artifact SBOM, provenance, signing
  and downstream cutover/restore/rollback evidence.
- [ ] **T05.025** ([#158](https://github.com/edithatogo/standards_check/issues/158)) Obtain independent methodological, usability/accessibility and publication acceptance.

Optional kernel qualification merged through #101 and closed #94. Held-source identity
rejection (#102) and bounded PRISMA parity (#103) retain their wider Track 03 limits.
One-command quick-profile integration is an optional improvement under the current policy's
"should" wording, not a new acceptance gate for this work. Scorecard, Security Insights and
SLSA are not selected by the registered baseline; future release applicability remains separate.

The implementation receipt names main `dd3f995`. A later documentation-only commit records
that accepted result and does not create a recursive requirement to qualify another
implementation revision. See [verification](verification.md) and [metadata](metadata.json).


## 24 November: Ponytail solo-maintainer refinement

- [x] **T05.026** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Existing required ALint, workflow syntax/Zizmor, CodeQL, privacy/secrets,
  coverage, mutation, dependency inventories and protected-main checks are present.
  RepoHealth and OpenSSF remain diagnostic workflows, not substitutes for the required gates.
- [ ] **T05.027** ([#30](https://github.com/edithatogo/standards_check/issues/30), [#76](https://github.com/edithatogo/standards_check/issues/76)) Qualify the grouped routine Renovate proposal across maintained managers and lockfiles;
  keep security fixes and breaking upgrades separately reviewable. Dependabot remains
  grouped and available until a protected Renovate handover is observed. Do not assert
  that the newest versions are installed merely because the bot proposes them.
- [x] **T05.028** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Verify focused pre-commit lint configuration and the offline quick profile in the
  receiving checkout. Reuse existing CI instead of adding another full duplicate matrix.
- [ ] **T05.029** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Qualify the shared Rust dependency policy (#131), and the source-XML boundary
  mutation regression and resumed acquisition (#142), on their exact receiving revisions.
  Distinguish seeded parser mutation tests from native coverage-guided fuzz campaigns.
- [ ] **T05.030** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Retain the independent offline security/runner, reproducibility and publication
  gates. Required ruleset, zero-human-approval protection, review resolution and no
  bypass remain unchanged. See #30, #31 and #116.


## Representation/publication assurance increment — 24 November 2026

- [x] **T05.031** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Close the required-lint gap: existing ESLint pre-commit configuration feeds the
  required workflow-policy job; Rust fmt/strict Clippy feed required Rust coverage.
- [x] **T05.032** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Add version-registry and publication-contract checks to the existing Python
  assurance lane and local hooks. Preserve all branch rules and coverage thresholds.
- [x] **T05.033** ([#158](https://github.com/edithatogo/standards_check/issues/158)) Define the publication protocol, three planned experiments, blinded agent roles,
  claim ledger and repository-local publication-evidence skill; fifteen contract regressions
  include negative paths. No model run or scientific acceptance is claimed.
- [x] **T05.034** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Observe exact-head and receiving-main CI for #160 at 82e4a1ef: seven protected contexts passed and native Pages deployment succeeded.
- [ ] **T05.035** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Resolve protocol freeze blockers; execute E1 directory census, E2 independent
  five-class reference and E3 incremental decision-model utility in dependency order.
- [ ] **T05.036** ([#30](https://github.com/edithatogo/standards_check/issues/30), [#116](https://github.com/edithatogo/standards_check/issues/116)) Complete native fuzzing, offline runner, updater handover and release provenance
  using their existing issues. Configuration is not an execution receipt.

See [current programme receipt](../01-canonical-standard-pack/representation-programme-20261124.md)
and [publication protocol](../../../docs/research/publication-protocol.v0.1.0.md).

## 25 November: repository maturity programme

- [x] **T05.037** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Enforce qualified formatting, static lint, typing, security lint and author-prose checks through required CI and local hooks; evaluate dead-code analysis and record its findings and gate decision.
- [x] **T05.038** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Raise Python and Rust coverage above 90 percent through meaningful failure-path and invariant tests without excluding production code; retain strict API coverage.
- [x] **T05.039** ([#163](https://github.com/edithatogo/standards_check/issues/163)) Map every registered plan item and repository issue, validate reverse links and run live read-only reconciliation in required and event-driven CI.
- [ ] **T05.040** ([#163](https://github.com/edithatogo/standards_check/issues/163)) Provide a GitHub Project view over the owning issues, preserving one issue per work scope and explicit completed/held outcomes.
- [ ] **T05.041** ([#162](https://github.com/edithatogo/standards_check/issues/162)) Qualify the reviewed dataset release manifest before any Hugging Face upload, including hashes, export permission, privacy and benchmark exposure.
- [ ] **T05.042** ([#30](https://github.com/edithatogo/standards_check/issues/30), [#116](https://github.com/edithatogo/standards_check/issues/116)) Complete native fuzz execution and targeted mutation evidence using existing lanes, retaining every failure and declared budget.
- [ ] **T05.043** ([#30](https://github.com/edithatogo/standards_check/issues/30), [#116](https://github.com/edithatogo/standards_check/issues/116)) Qualify maintained dependency hash closure, actual offline scanning and protected updater handover; preserve the security-fixed Scorecard pin during upstream failure.
- [ ] **T05.044** ([#30](https://github.com/edithatogo/standards_check/issues/30)) Prepare versioned technical-preview release assets with reproducibility, artifact SBOM, provenance/signatures and actual consumer evidence before public release.
- [ ] **T05.045** ([#123](https://github.com/edithatogo/standards_check/issues/123)) Qualify live website state/import/export/accessibility; adopt a new site framework only for a measured unmet documentation requirement.
- [ ] **T05.046** ([#158](https://github.com/edithatogo/standards_check/issues/158)) Complete the prospective publication evidence bundle and venue-policy checks before preprint or manuscript submission.

The detailed tool decisions and ordered gates are in [the maturity plan](maturity-plan-20261125.md).

## Hardening acceptance — 25 November 2026

[PR 165](https://github.com/edithatogo/standards_check/pull/165) merged normally at
`019f280d615dcdc8162555e6ab9fea0eaa6fbeb4`. All seven required checks passed on
both the corrected PR head and receiving main. The [hosted acceptance record](hosted-hardening-20261125.json)
binds the exact trees, downloaded native reports and live issue-event reconciliation.
T05.037–039 are complete within that software and ownership scope. The remaining
operational, dataset, consumer and publication tasks above retain their own gates.

## Next increment: measurable efficiency and model value

- [ ] **T05.047** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Retain native test timing and case outcomes; qualify a same-revision efficiency improvement against unchanged required tests, coverage and failure detection. Compare at least three repeated runs per configuration before adopting parallelism or a cache.
- [ ] **T05.048** ([#158](https://github.com/edithatogo/standards_check/issues/158)) Maintain dated model evidence and value decisions using the existing experiment contract; qualify the next challenger on the frozen question, budget and reference, retain failed runs, and reassess on relevant releases without changing a frozen experiment.

See [frontier evaluation and efficiency evidence](../../../docs/research/frontier-evaluation-20261125.md). Source changes and historical observations do not close these tasks; receiving checks and actual comparative evidence remain required.

The independently verified controlled trial in [PR 168](https://github.com/edithatogo/standards_check/pull/168) achieved 34.2338% median regression-suite improvement, conserved exact coverage and test outcomes, and passed both failure probes. The production adoption and scoped clean-install qualification are in [PR 169](https://github.com/edithatogo/standards_check/pull/169), with [hash closure evidence](python-ci-hash-closure-20261125.md). T05.047 remains open until fresh protected and receiving acceptance; T05.043 remains open beyond the bounded ordinary Ubuntu Python CI profile. No scientific gate or release hold is closed.

## Prospective composition and graph qualification

- [ ] **T05.049** ([#158](https://github.com/edithatogo/standards_check/issues/158)) Freeze the follow-up E4-E8 publication contract after independent references, sample precision, ontology/citation snapshots, methods and decision rules are approved; retain all empirical results and failed runs.
- [ ] **T05.050** ([#31](https://github.com/edithatogo/standards_check/issues/31), [#162](https://github.com/edithatogo/standards_check/issues/162)) Qualify the contract-only static preview package, analytical contract and receiving CI; bind exact revision and artifact hashes. Keep real data and external release separate.

The [publication contract](../../../contracts/publication/composition-graph.v0.1.0.json) extends the existing validator without replacing E1-E3. The [analysis contract](../../../contracts/analysis/requirement-graph.v0.1.0.json) maps each gate to its existing workflow or explicitly planned extension. No confirmed outcomes or real-data export.

## Optional human review and unattended workflow operation

- [ ] **T05.051** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Qualify automatic and optional dispatch access for all maintained workflows, with no mandatory human approval and actual review objections retained.
- [ ] **T05.052** ([#30](https://github.com/edithatogo/standards_check/issues/30), [#116](https://github.com/edithatogo/standards_check/issues/116)) Observe a protected updater proposal without dashboard approval and qualify the unattended routine merge handover; keep separate breaking/security work and verified receiving receipts.

See [optional human review](../../../docs/development/optional-human-review.md). Model-relative development and candidate reference work can proceed without waiting for human review; T05.049 retains the actual external/scientific evidence gates. No automatic approval, false human review or release permission.

Specialist evaluation extends T05.046, T05.048 and T05.049 under #158. See
[specialist pipeline protocol](../../../docs/research/specialist-pipeline-protocol.v0.1.0.md)
for E9-E14 endpoints, constrained-decoding and symbolic validation boundaries,
resource/rights pins and independent scientific freeze criteria. Grammar acceptance
or green tests never establish semantic or scientific correctness. Preserve the full
negative LFM ablations and source acquisition holds; no model promotion.

T05.048 and T05.049: preserve the [requested model challenger record](../../../docs/research/model-challengers-20261126.md), exact candidate pool, source hashes, local/hosted boundaries and all negative retrieval receipts. The public-data service comparator is explicit local opt-in only; no secret-dependent PR CI or automatic scientific acceptance.
