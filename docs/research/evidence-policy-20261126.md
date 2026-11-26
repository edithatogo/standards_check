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
