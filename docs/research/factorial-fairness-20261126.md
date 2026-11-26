# Fair factorial redesign and full-corpus coverage — 26 November 2026

T01.063–064, T05.048/063, #158. Supersedes the prospective half-fraction
preference, not historical results or the immutable specialist protocol.
The hosted [factorial replay 45805221446](https://github.com/edithatogo/standards_check/actions/runs/45805221446)
completed successfully; downloaded artifact 15109861524 matched its API
archive digest, and removing only acquisition edge times gives the exact
previous deterministic result. Apply its exact Ruff diff to the original
runner (blob 4a38c12a1185aeb164663992e896812f8da880d0); no algorithm change.
Reconcile #183 receiving main 413626c4, preserving shared recall audit,
locked join and source-owner boundaries.

## Interpret the earlier factorial as a resource-addition experiment

Factors included different numbers and kinds of calls; a synthetic parent
link yields the complete text, while a reranker cannot recover out-of-pool
evidence. Negative additive interactions can arise from saturation and
overlapping coverage rather than intrinsic substitutability. Do not infer
equal compute, causal mechanism or population effect from those contrasts.
Separate method replacement at common budgets from extra-work interventions,
and compare ordering within matched active component sets. For layout use
the same source regions and reference; for tagging compare equally scoped
rules and model variants on identical offsets; for graph compare equally
sized candidate pools, heading-only and rewired controls; for decision use
identical complete evidence and explicit relation tasks; for formal
verification preserve the actual gate and compare advisory selective
coverage and counterexample utility.

## Executed controlled retrieval factorial

Three binary method factors: original versus deficit-directed query,
word-only versus reciprocal-rank word/character fusion, word versus
character rank on exactly the same selected pool. All arms compute both
channels across 11 unseen same-family fragments per case; six candidates,
two previously unseen fragments (264 scores per channel, 144 shortlist
slots and 48 acquisitions per held-out cell). Selected words range 150–158;
not equal wall time, compute or token budget. No gold enters scoring or
selection. All 36 exposed synthetic cases executed; 24 original held-out
cases, 8 cells, complete outcomes 18/18/18/18/19/20/19/20, correct
14/14/14/14/15/16/15/16, zero false equivalences. All cells recover the
target in the pool for 20/24, so rank-only opportunity remains bounded.
The matched unseen-pool comparison on actual retained MiniLM scores
again yields lexical 20/24 and neural 20/24 complete. No new model scores
or imputed semantic decisions.

On original terminal observed predictions, compare proof routing to a
fixed confidence ordering of the strict NLI advisory labels at the same
accepted count. Unrestricted 20/22 correct; confidence 14/14; proof
12/14. Zero false equivalences in all three; cannot infer safety advantage.
No final equivalence admission or referral resolution. Separate adversarial
controls are still required.

## Statistical methods

Use paired within-case factorial contrasts and family/document blocks;
a family Bayesian bootstrap (10,000 Dirichlet reweights, seed 17) reports
conditional variability over the four observed test families. Average
completeness effects: deficit query +6.25 pp (90% interval 1.57–11.70),
character rank +2.08 pp (0.14–5.25), their interaction +4.17 pp
(0.29–10.51), hybrid 0. These intervals are conditional on observed
support: zero variation is not evidence of zero population uncertainty.
For scientific inference use a predeclared hierarchical model with
family/document/case effects and treatment random slopes where supported,
prior sensitivity, posterior predictive checking and independent reference
freeze; do not treat 288 case-configurations as independent observations.

Actual predictive comparison: leave one whole family out across six
exposed families, 36 cases, 288 case-configurations. Fixed prior-smoothed
arm mean, regularised logistic, fixed-prior hierarchical logistic (normal
family and case random intercepts, Laplace mode/covariance and
Gauss-Hermite prediction for unseen effects), shallow XGBoost (64 trees,
depth 2, learning rate .05, lambda 5, single thread, seed 17). Inputs are
only observable initial feature values and assigned factors. No tuning
on held-out predictions. Brier/log loss: beta .17296/.52956, logistic
.18422/.52207, hierarchical .17675/.51820, XGBoost .18084/.55011.
No consistent XGBoost advantage. Predictive models are not substitutes
for causal contrasts. Use larger independent family datasets to evaluate
conditional pipeline utility, calibration and matched-budget routing
regret. Versions recorded (NumPy 2.3.5, sklearn 1.8.0, XGBoost 3.1.3);
optional analysis only, no maintained dependency change.

## Default full factorial

The [v2 full matrix](../../conductor/tracks/01-canonical-standard-pack/pipeline-factorial-full-v2.json)
contains all 64 configurations, verified rank 64 and exact orthogonality
including all interactions. Preserve the old half fraction solely as an
explicit resource fallback. Apply all valid configurations on the same
eligible source/reference units by format. 720 directory entries x 64 =
46,080 directory/configuration *planning slots*. The executed ledger
marks all full specialist cells held; these are not 46,080 observations.
The underlying census is historical. PR #188 has subsequently attempted
two further acquisitions (both held), observed 42 and 53 literal CONSORT
and SPIRIT IDs as source candidates, and is qualifying structural
evidence; neither those observations nor the one admitted PRISMA pack
establish the full specialist grid. Do not relabel partial observations
or fabricate missing outputs. Use #188's existing source join and #183's
locked same-unit downstream receipts; no new source registry.
Use full eligible cohort for operational development, independent
family-disjoint frozen references for confirmation, with separate
format-appropriate designs for inapplicable cells. Cache exact source,
stage, input, model and configuration hashes; measure per-stage time,
memory, words/tokens, bytes, failed attempts and actual review effort.
Freeze eligible universe, matched resource constraints, multiplicity and
harm tolerances; no confirmatory effect or rights claims.

## Reproduction

```sh
python -m pytest --import-mode=importlib -q tests/test_factorial_fairness.py
python -m scripts.factorial_fairness --neural-report /path/report.json \
  --ledger /path/equator-pipeline-coverage-v1.json --predictive \
  --output factorial-fairness-v2.json
```

Use exact previously retained ledger and neural report hashes; the optional
predictive branch needs the versions in the receipt. The hosted replay
uses the existing neural artifact and deterministic runner without new
model inference or predictive dependencies. RED missing module and
missing new functions; seven focused tests and 55 extracted-module tests
passed locally; exact blobs verified. Full checkout and pinned Ruff
unavailable locally; hosted verification outstanding. Retain complete
local report, summary and input/output digest in the
[receipt](../../conductor/tracks/01-canonical-standard-pack/factorial-fairness-v2-receipt.json).
No changes to final admission, production, scientific freeze, rights or
protected integration policy.
