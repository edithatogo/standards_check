# Orthogonal assurance implementation receipt — 26 November 2026

Scope: [PR #177](https://github.com/edithatogo/standards_check/pull/177) and the
existing eight tasks from [PR #176](https://github.com/edithatogo/standards_check/pull/176),
merged at `6632782f51f126c82bbbddc2fe66d931e6d42382`.
This is a bounded software and exploratory evidence receipt, not scientific,
rights, interoperability or release acceptance. No task or issue is closed by
partial implementation. Preserve the single publication programme in issue #158.

## Historical hosted observation

- PR head `5d94912d936528f4802ca995064595d0717257b8`, tested merge
  `ef50444373dbdd589727d6c84bd8ce218134289a`.
- [Assurance run 45762873878](https://github.com/edithatogo/standards_check/actions/runs/45762873878)
  failed overall. Workflow-policy job
  [139717065867](https://github.com/edithatogo/standards_check/actions/runs/45762873878/job/139717065867)
  passed ESLint and Ruff lint, then rejected formatting in four maintained scripts.
  Subsequent policy hooks did not execute in that job; retain the failure.
- The [Python job 139717065828](https://github.com/edithatogo/standards_check/actions/runs/45762873878/job/139717065828)
  passed 714 tests, three skipped, and combined line/branch coverage 91.47 percent
  (90.50 percent floor). The combined report recorded conformal_triage 100.00,
  orthogonal_checks 93.79, orthogonal_experiments 98.17, check_restricted_overlap
  88.24 and qualify_legacy_prisma 96.54 percent. The workflow reported a clean
  working tree. Retained Python artifact
  [15090996334](https://github.com/edithatogo/standards_check/actions/runs/45762873878/artifacts/15090996334)
  has API-reported SHA-256
  `16721f4f206f8a403fa335e4ccc260aa11759236fd81b2b7b3afd9b78751ea93`;
  this receipt is based on the job log and artifact metadata, not independently
  downloaded archive bytes.
- The actual Python legacy and native Rust renderers executed two authored plus
  six generated valid pairs (three partitions, new and updated reviews).
  Eight intentional invalid cases rendered in legacy and returned validation
  failure with no artifact in Rust. Preserve these as intentional divergence,
  not parity successes. Counts, scene nodes, SVG labels and text relationships
  were compared under the explicit database-only, one-report-per-study contract.
- Rust, API, three cross-platform jobs, dependency review, mutation checks and
  Codecov uploads passed in that run. Offline AI security remained queued.
  No protected integration acceptance is inferred from the partial pass.
- Synthetic conformal stress test: 495 fabricated calibration rows, 50 fabricated
  evaluation rows; 1 percent alpha, zero direct-count versus sorted-rank
  disagreements. Baseline 50 accepted, 20 errors, 16 false equivalences; both
  conformal variants 35 accepted, 15 abstentions, 20 errors and 16 false
  equivalences. Abstention did not remove those errors under the deliberately
  shifted fabricated scores. This is a negative development control, not a
  distribution-free empirical risk guarantee or evidence of independent calibration.

## Reconciled implementation and outstanding gates

| Task | Bounded implementation and evidence | Remaining acceptance |
| --- | --- | --- |
| T01.060 | Merged conformal rank oracle; independent direct-count comparison; synthetic shift and overlap-rejection tests in #177 | Independent family-disjoint source/reference, freeze scores/alpha and selective false-equivalence risk evaluation |
| T01.061 | Conjunctive typed-literal applicability, explicit unknown/conflict; exhaustive small weighted equivalence-subset oracle with incompatible pairs and ties held | Source-anchored rule corpus, recursive inference and precedence; real typed costing/ontology candidates and scalable solver qualification |
| T01.062 | Hash-bound expected reference/output inventories, ordered extracted text, exact normalized n-grams and no-excerpt receipts | Authorized restricted corpus, independently complete extraction and actual artifact coverage |
| T02.060 | Bounded ordinary P/T marking traversal, restricted PNML adapter, stale/overlap-rejecting byte edits; synthetic success, deadlock and limit controls | All applicable maintained PNML nets vs independent PM4Py; actual CST and transducer qualification, citation/unit and projection conservation |
| T03.060 | Six generated valid differential cases and six additional invalid rejection counterexamples; actual Python and Rust renderer tests in prior job | Current-base/receiving evidence; expanded shared domain, property/fuzz, other streams and families and minimized mismatch handling |
| T05.060 | Synthetic comparative protocol/metrics; existing E1–E14 retained (specialist E9–E14 source merged through #155) | Prospective orthogonal ablation amendments and independently frozen scientific run; one integrated manuscript, no historical result relabeling |
| T05.061 | Private overlap CLI with nonzero exit for held/malformed/missing inputs and synthetic positive/negative controls | Real authorized corpus runner, release-pipeline invocation and exact final artifact scan; no legal clearance |
| T05.062 | Existing differential runner extended; finite oracle and negative tests in ordinary CI, no new dependencies | Current-base and receiving receipts, expanded property/fuzz and retained independent counterexamples |

## Receiving reconciliation

Main advanced 38 commits from the PR's original base to
`36556203d952fb07406aaa2a383eea9edca5e991`. The main-only changed paths did
not overlap the seven implementation paths. Merge commit
`b9eacdd55ad94f9322b0e31c4fd7314d4494af00` uses the exact main tree plus the
seven PR blobs and retains both parents. The formatting repair
`0ad4bf9e36b48c7774b4c54aee6f174d245f969d` addresses the four reported files
without changing required controls, adding dependencies or claiming a new
scientific result. GitHub comparison reported zero commits behind main after
the reconciliation. The subsequent documentation changes link this same
receipt from Tracks 01, 02, 03 and 05, without changing stable task IDs or owners.

Full local checkout and the pinned formatter/native Rust toolchain were unavailable
in the current environment; rely on fresh protected hosted checks, not an inferred
local pass. Before merging, verify the exact latest head, required check identities
and conclusions, absence of unresolved review threads, and current base. Then verify
the exact receiving-main execution and prune only the merged feature branch.
Record final integration and receiving results separately when actually observed.
No source or model promotion; all eight wider acceptance tasks remain open.
