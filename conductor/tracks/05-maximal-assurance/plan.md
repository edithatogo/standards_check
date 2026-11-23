# Plan: Maximal assurance, release and external validation

Status: **in progress**. Implementation: **source implemented** for the bounded local assurance
slice. Evidence: **local qualification; published-head and receiving-main acceptance pending**.

## Current software and policy qualification

- [x] Record technique applicability and scoped exclusions; test API rate-counter expiry with a mocked clock.
- [x] Qualify property bounds, three seeds, lock/arithmetic/renderer invariants and failure replay.
- [x] Run native Rust mutations, retain the two initial misses and verify strengthened assertions.
- [x] Run ten hand-selected schema/API mutations with clean baselines and distinct failure classes.
- [x] Add component coverage reporting and enforcement, workflow lint and PR dependency review.
- [x] Add a separate trusted OIDC upload job with explicit component reports and no token secret.
- [x] Restore the shared security policy with local scope and pin the managed-file comparison.
- [x] Triage Unicode findings without changing preserved source bodies or suppressing the detector.
- [x] Record the final combined Python coverage measurement after configuration reconciliation.
- [x] Repair both observed High API CodeQL findings with bounded middleware and constant-format logging; retain failure-first regressions.
- [ ] Observe fixed alert state on the published receiving revision.
- [x] Produce nine baseline dependency SBOMs for maintained Python, Rust and Node graphs, bound to local inputs; hosted acceptance remains separately pending.
- [ ] Obtain exact published-head and receiving-main receipts for the new assurance jobs.
- [x] Bind Pages upload/deployment to the current attempt and exact uploaded artifact; retain bounded visibility and rejection regressions.
- [ ] Observe successful native Pages deployment on receiving main after the artifact-readiness repair.
- [x] Observe all three Codecov OIDC uploads and actual patch-provider acceptance at first head `12b7b007`; later revisions need their own observations.
- [ ] Apply and read back the solo-maintainer ruleset after confirming stable check names.
- [ ] Qualify remaining managed-policy/profile divergence and the updater lifecycle; retain
  Dependabot until the receiving handover is demonstrated.
- [ ] Obtain an executed offline-security receipt from its qualified runner.

## Later acceptance

- [ ] Complete independent interpretation/evidence review and migration semantic parity (#82).
- [ ] Reconcile held guideline sources, item-level rights and independent fixtures before admission (#95).
- [ ] Complete applicable ecosystem contracts and downstream canaries in Track 04.
- [ ] Produce release/offline reproducibility, release-artifact SBOM, provenance, signing and restore/rollback evidence.
- [ ] Obtain independent methodological, usability/accessibility and publication acceptance.

Optional interactive-kernel qualification merged through #101 and closed #94. Held-source
identity rejection and bounded legacy PRISMA parity merged through #102/#103 and are included
in the integrated candidate. Their Track 03 receipts retain the wider content, migration and
independent acceptance limits. See [verification](verification.md)
for current evidence and [metadata](metadata.json) for machine-readable state.
