# Quality-frontier and Conductor reconciliation (19 November 2026)

## Revision-scoped evidence

- Baseline prior to acceptance: `944ce78161c25a64803909625bdddb1dab25aa91`.
- Track 00 PR [#79](https://github.com/edithatogo/standards_check/pull/79), reviewed head `baab246e62f3585237b987f87647eba743f2818e`: **11 successful check runs**, one deployment check skipped. Exact-head jobs included foundation contracts, Rust, offline Python, document build, privacy/secrets and CodeQL for Rust/Python/JS/Actions.
- [Foundation contracts job](https://github.com/edithatogo/standards_check/actions/runs/44498580063/job/135472024917): foundation validator, `tests.test_foundation_audit`, and `scripts/audit_foundation.py` succeeded. Its JSON reports 1,316 tracked files, 292 source files, 11 paths with explicit placeholder markers, zero unreadable text files and zero Conductor context errors.
- PR #79 merged (squash) to `main` as `840b8431403035be7e5dec5f22b64ad3ddb20d2b`.
- Receiving-main check runs were **separately observed complete** at `840b8431403035be7e5dec5f22b64ad3ddb20d2b`: **11 of 11 successful** (including deployment, document build, schema validation, Rust, Python, privacy/secrets and four CodeQL analyses). See [commit check runs](https://github.com/edithatogo/standards_check/commit/840b8431403035be7e5dec5f22b64ad3ddb20d2b/checks). This is a receiving-main receipt, distinct from the PR head.

## Snapshot versus obsolete audit claims

| Property | Verified present | Unverified or outstanding |
| --- | --- | --- |
| Workflows | Seven YAML workflows in `.github/workflows/`; Rust foundation, pack, diagrams, docs, Python, dependency security, privacy | All checks are not universally required; no rule set currently exists |
| Automated security | CodeQL analyses on reviewed PR head; privacy/secrets workflow; lockfile npm audit for both graphs when dependency workflow runs | Dependency review gate, workflow lint gate, Scorecard, SBOM/provenance and release-level threat assurance not independently confirmed |
| Testing | Rust unit/property and CLI tests, schema contracts, Python regressions, Node dependency/security tests, deterministic 12-output PRISMA generation and cross-platform matrix | Recorded mutation score, deterministic simulation applicability, metamorphic-test coverage, code coverage and independent methodology/accessibility acceptance |
| Conductor | Exact `f06add33...` gitlink and local context-link audit in CI; 00 foundation merged; 01 and 02 fixture-proven on recorded revisions | 03 migration, 04 ecosystem contracts, 05 deep assurance; rights/source reconciliation |
| Maintainer settings | Public repository; Renovate configured and [dependency dashboard #76](https://github.com/edithatogo/standards_check/issues/76) exists; `AGENTS.md` and `CONTRIBUTING.md` local | Repository has zero rulesets; root `SECURITY.md` missing; Codecov status, OIDC coverage and protection settings unverified |

The previous issue statement of **one workflow** was obsolete. Counts of five tests or 38 code files are not a reproducible current quality measure. The inventory is a Git-index count rather than evidence of rights or publication validation.

## Required decisions and closure gates

### #29 testing and CI/CD

- [x] Reconcile the recorded baseline to current code, tests and workflows.
- [ ] Establish applicability matrix and explicit evidence-backed exclusions for property, mutation, deterministic simulation, metamorphic and contract tests.
- [ ] Add bounded mutation/coverage thresholds for high-value Rust and parsing logic, with published exact-head receipts.
- [ ] Qualify workflow lint, dependency review, supply-chain assurance and immutable pin exceptions where warranted.
- [x] Record PR #79 exact-head and receiving-main CI distinctly (11/11 receiving-main success); later heads require new checks.

### #30 security, maintainer and dependencies

- [x] Verify the root `SECURITY.md` is absent, the default-branch ruleset collection is empty, Renovate is configured, and dashboard #76 exists.
- [ ] Adopt a single-operator ruleset preventing force-push/deletion and requiring proven stable automated checks, without mandatory human approvals and with owner recovery.
- [ ] Add/reconcile `SECURITY.md` using canonical community policy, while retaining local extensions.
- [ ] Validate managed-file drift and community context against `edithatogo/repository-standards`.
- [ ] Confirm Codecov OIDC and coverage reports from an observed run; do not claim it exists from a missing `codecov.yml`.
- [ ] Keep Dependabot update coverage until Renovate's relevant ecosystems are working and the transition is proven.
- [ ] Triage Renovate's hidden-Unicode warning and proposed major upgrades individually.

### #31 umbrella acceptance

- [x] Replace obsolete baseline with current verifiable evidence.
- [ ] Close #29 and #30 only when their distinct gates are satisfied or independently justified exclusions are recorded.
- [ ] Keep unverified settings, method-level testing and external source/rights acceptance explicitly open.

## Upstream repository-standards contract

The upstream [archetype-profiles.json](https://github.com/edithatogo/repository-standards/blob/main/profiles/archetype-profiles.json) defines the solo-maintainer requirements, including explicit permissions, timeouts, immutable pins, automated checks, no mandatory human approvals, and required AGENTS/SECURITY/CONTRIBUTING context. Local implementation is only **partially aligned**, not fully reconciled. In particular, rulesets and SECURITY.md are absent. The upstream managed-files manifest prescribes source-aware drift and controlled pull-request adoption, not unilateral overwrite.

## Evidence limitations

An audit script's output is **inventory-only**. The PR and main SHA differ; acceptances are immutable revision-scoped claims. A hosted check being configured is not the same as its observed success. Source rights, migration parity and scientific external validation remain separate from repository quality controls.
