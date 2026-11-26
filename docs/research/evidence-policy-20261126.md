# Offline policy comparison and harness review — 26 November 2026

T01.064 / T05.048/063, #158. Extend existing evidence-action replay, not a
new RL framework, action simulator or production orchestration layer.
Apply Ponytail to reuse observed replay, ridge, lexical rule, existing
formal gate and fixed fixture. No new runtime dependency. Preserve the
full 64-cell design, source intake #188 and receiving #183 locked join.

## Executed comparison

Train on the original 12 development cases in CHEERS/PRISMA; evaluate the
24 historical ARRIVE/CONSORT/STARD/TRIPOD test cases. All cases exposed
by previous development, not confirmatory. Use only observed transitions.
Mask unavailable parent links and repeated actions; fixed one- and two-call
arms receive exact budgets, adaptive arms may stop before two. Compare
deterministic expansion-first, best fixed permutation chosen on development,
one-step contextual value/bandit and backward two-step fitted Q. The learner
sees only existing visible observation features and action history; train
only on development outcomes. No IDs, hidden text, test labels or future
test outcomes are used for action selection. The same terminal gate blocks
unverified equivalences for every arm; non-equivalence labels also remain
advisory. No real review outcome is available.

Illustrative utility: correct gated label +1, abstain 0, wrong -1, false
equivalence -4, complete +0.25, acquisition call -0.1. A reward model
is not a clinical or publication acceptance criterion. Report individual
outcomes, calls, reranks, acquired words and recorded time, not just the
scalar reward. The fixed cost is not measured compute or review cost.

| Budget | Rule complete/correct gated | Bandit | Fitted Q | Rule/learned calls |
| --- | --- | --- | --- | --- |
| Exact one | 19/11 | 20/12 | 20/12 | 24/24 |
| Exact two | 23/14 | 20/12 | 20/12 | 48/48 |
| Adaptive two | 23/14 | 20/12 | 20/12 | 29/24 |

Best fixed development sequence equals rule in every comparison. All arms
have zero raw and gated false equivalences on this fixture; eight true
equivalences withheld, six referrals per arm, zero credited resolutions.
Formal controls explicitly reject three invalid equivalences and preserve
one true equivalence under the same gate. No population safety claim from
zero observed harm.

The separate hindsight oracle has access to held-out labels, so it is an
upper bound under this particular utility, never an eligible policy.
At exact one call its completeness/correctness is 23/14; at two calls
23/14, tying rule at reward 14.95. Adaptive oracle achieves 23/14 with
23 calls and reward 17.45 versus rule 29 calls/reward 16.85. No additional
decision-quality headroom under the existing exact-two utility. Learned
policies have no advantage over the simple rule at two calls; the one-call
gain is one case and increases reranking. Preserve these negative outcomes.

## Ponytail and next steps

- Reuse the full factorial and locked stage join; don't implement an RL
  simulator, Gym environment, replay database, distributed training,
  deep actor-critic or world model while the observed action-space oracle
  leaves little headroom. Do not remove prior negative results.
- Expand real, feasible observed actions first (targeted region recovery,
  verified structure, tag-conditioned queries, novel evidence retrieval,
  independently supported semantic/counterexample operations). Reuse
  actual stage receipts on the same lock, not imagined transitions.
- Measure the hindsight ceiling and a deterministic deficit router on
  eligible common inputs before a learned policy; compare contextual
  bandit and bounded fitted Q at matched compute, candidate, evidence,
  review and safety constraints. Only then test model-based forecasts or
  constrained offline RL if they improve the held-out utility frontier.
  No online exploration, unsafe action or admission decisions.
- Full factorial measures fixed pipelines; policy work uses the actual
  observed transitions between decisions, not independent cell outcomes
  as if they were transitions. Keep family-disjoint calibration/evaluation
  and independent reference, source rights and publication holds.

## Harness, CI and safety

Prior hosted fairness and required workflow-policy both failed I001
import ordering; coverage, Codecov patch, privacy and CodeQL passed.
Apply the exact observed import repair (tested blob in receipt).
The existing fairness opt-in job now also handles the policy replay:
retain both lint and formatting diagnostics even if lint fails, pin executed
Git blobs, run pip check, capture environment, run both focused suites,
and compare deterministic policy output against the pinned digest.
Optional diagnostic replay may run an unformatted but lint-clean branch;
the required formatter gate remains unchanged. No suppressions, credential
changes, broad workflow rewrite or new framework. Exact-head required
checks and hosted reproduction remain outstanding.

Offline AI security continues to be queued; the reusable policy invokes
the shared workflow with enforce_ai false. Treat execution unavailable
as a separate blocker, never as passed. Check registered runner availability
and queue contention via existing shared standards, not parallel ad hoc
runners or a weaker gate. Keep immutable action pins and read-only
permissions. Research-only hosted labels and timeout bounds are retained.
For future resource work, use stage input hashes and actual cached
receipts, avoid rerunning unchanged expensive inference, and predeclare
stop criteria for failed acquisition batches. No change to required CI,
branch protection, source rights, formal gate or scientific admission.

## Reproduce

```sh
python -m pytest --import-mode=importlib -q tests/test_evidence_policy.py
python -m scripts.evidence_policy --output evidence-policy-v1.json
```

Five focused tests pass (initial RED, leakage and invalid-path controls,
formal gate and oracle checks); 60 local extracted-module tests pass.
Local source/test blob IDs match committed files. The local environment
cannot run the pinned Ruff or a full repository checkout; use actual
protected CI. See [receipt](../../conductor/tracks/01-canonical-standard-pack/evidence-policy-v1-receipt.json).

## Observed hosted replay and formatter repair

[Run 45809762393](https://github.com/edithatogo/standards_check/actions/runs/45809762393) completed successfully: 12 focused tests, exact policy deterministic digest match, fairness summary and matched-ranking/coverage results reproduced. Downloaded [artifact 15113035196](https://github.com/edithatogo/standards_check/actions/runs/45809762393/artifacts/15113035196) verified against its archive SHA-256. Both scripts required formatting; apply the exact retained diff to their original blobs, verify Python AST equality and all 60 local overlay tests. The resulting exact formatted Git blob IDs and hosted report hashes are in the versioned receipt. The prior required policy check failed formatting; current-head protected checks remain required. No promotion or automatic merge from an optional replay.

## Parent-first diagnostic follow-up (post-hoc)

A simpler fixed ordering is `parent → expand → deep_rerank`, subject to
the existing action mask. No model or new acquisition backend. Compare
using the original terminal proof gate, referral workload and actual
observed transitions; preserve the original report by making this extra
arm opt-in (`--compare-parent-first`). The additional ordering was
examined after exposure to held-out results, not an independent selection.
The two fixed orders tied on development (10 complete, five gated correct,
12 calls, reward 6.3); no independent generalisation claim.

| Parent-first budget | Complete | Gated correct | Calls | Reranks | Acquired words | Utility |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Exact one | 23 | 14 | 24 | 0 | 159 | 17.35 |
| Exact two | 23 | 14 | 48 | 5 | 279 | 14.95 |
| Adaptive two | 23 | 14 | 25 | 1 | 159 | 17.25 |

At one call the ordering ties its hindsight ceiling and the previous
two-call decision-quality ceiling. Adaptive parent-first wastes one further
call relative to fixed one-call on these cases. Six referrals, no review
resolutions, no gated false equivalence, eight genuine natural-language
equivalences held in every arm. Source structure is artificially easy:
synthetic parent links always recover the full target; real parent/qualifier
links need independent completeness and cost measurements. Do not promote.
The regression test verifies identical original arms/results, legal first
actions, proof and referral conservation. Six focused and 61 overlay tests
pass, hosted checks remain required. No additional dependency or workflow.
See the [receipt](../../conductor/tracks/01-canonical-standard-pack/evidence-policy-parent-first-v1-receipt.json).

```sh
python -m scripts.evidence_policy --compare-parent-first --output evidence-policy-parent-first-v1.json
```

Keep the upstream PR head stable while it qualifies; this small follow-up
must be reconciled to receiving main after #184. Rollback removes only the
opt-in comparator and receipt. The historical default output stays intact.

Protected follow-up: #184 receiving Assurance 45811145369 passed. Parent-first required workflow-policy job 139880152117 failed B008 on a closure default function call; bind `order` before the closure, preserving capture semantics. Six focused tests passed and the full timing-free parent-first report matched exactly. Reconcile disjoint #186 receiving changes at d8384d5a. Fresh exact-head checks required; no scientific promotion.
