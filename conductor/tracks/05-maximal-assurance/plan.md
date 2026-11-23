# Plan: Maximal assurance, release and external validation

Status: **in progress**. Implementation: **source implemented** for the bounded local assurance
slice. Evidence: **local qualification; published-head and receiving-main acceptance pending**.

## Current software and policy qualification

- [x] Record technique applicability and the scoped deterministic-simulation exclusion.
- [x] Qualify property bounds, three seeds, lock/arithmetic/renderer invariants and failure replay.
- [x] Run native Rust mutations, retain the two initial misses and verify strengthened assertions.
- [x] Run ten hand-selected schema/API mutations with clean baselines and distinct failure classes.
- [x] Add component coverage reporting and enforcement, workflow lint and PR dependency review.
- [x] Add a separate trusted OIDC upload job with explicit component reports and no token secret.
- [x] Restore the shared security policy with local scope and pin the managed-file comparison.
- [x] Triage Unicode findings without changing preserved source bodies or suppressing the detector.
- [x] Record the final combined Python coverage measurement after configuration reconciliation.
- [ ] Obtain exact published-head and receiving-main receipts for the new assurance jobs.
- [ ] Observe Codecov OIDC uploads and actual component/patch commit statuses.
- [ ] Apply and read back the solo-maintainer ruleset after confirming stable check names.
- [ ] Qualify remaining managed-policy/profile divergence and the updater lifecycle; retain
  Dependabot until the receiving handover is demonstrated.
- [ ] Obtain an executed offline-security receipt from its qualified runner.

## Later acceptance

- [ ] Complete independent interpretation/evidence review and migration semantic parity (#82).
- [ ] Reconcile held guideline sources, item-level rights and independent fixtures before admission (#95).
- [ ] Complete applicable ecosystem contracts and downstream canaries in Track 04.
- [ ] Produce release/offline reproducibility, SBOM, provenance, signing and restore/rollback evidence.
- [ ] Obtain independent methodological, usability/accessibility and publication acceptance.

Optional interactive-kernel qualification remains with the separate owner of #94. The imported
runtime's 52-test compatibility and notebook/output parity receipts remain in Track 03; they do
not substitute for Rust equivalence or the source/content gates above. See [verification](verification.md)
for current evidence and [metadata](metadata.json) for machine-readable state.
