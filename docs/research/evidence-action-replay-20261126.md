# Evidence-action replay — 26 November 2026

Status: synthetic development evidence only; no canonical admission, scientific freeze,
model promotion, rights change or external review. Owner Track 01 / Track 05, issue #158.
Extends the existing E11–E12 development lane; does not add or renumber publication
experiments. Main inspected at d88f787ffd4647117bca4ca400cbb68d95197d40; open PRs #180 and #181 are untouched.

## Design fixed before the first local run

Use the existing 36 analyst-authored pair fixture (exact SHA-256 in the receipt).
Original family partition: 12 training pairs (CHEERS, PRISMA), 24 held-out pairs
(ARRIVE, CONSORT, STARD, TRIPOD). These are historically exposed synthetic controls,
not independent confirmatory evidence. Simulate document layout by deterministic
label-independent ID hash: each candidate has a head and tail; some have a parent
link. Initial view has the source and candidate head. Each family is its own
fragment corpus with distractors; no cross-family indexing or training overlap.

Execute every nonrepeated acquisition action to depth two, recording evidence
IDs/text, query/ranking, new evidence, cost and reference-relative resolution.
Three feasible actions: word/bigram TF-IDF retrieval with missing visible source
terms repeated; probe parent index (including a no-result probe where no link);
character-trigram rerank of initial six-item word shortlist with fixed identity
binding, returning at most two ranked fragments. These are actual lexical
operations over a synthetic layout, not genuine issuer clause/exception recovery
or pretrained reranker inference. All states also have terminal abstain and review
edges, the latter an unadjudicated referral with no correctness credit.

Primary: false equivalences at equal realised acquisition calls and review
workload, with correct resolutions as a guardrail. Initially weak pairs receive
two acquisition calls in each arm even if the first resolves them. This matched
design does not test early stopping. Terminal decision is a common fixed lexical
five-class candidate heuristic (legacy B-relative-to-A orientation), requires
full synthetic target coverage, and uses existing strict-agreement abstention.
It is not a calibrated NLI or proof. Match review count to the minimum unresolved
count across arms, capped at six, based on model dispositions alone; prioritize
incomplete evidence then ID. Remaining unresolved cases abstain. No referral
returns a result, so referral resolutions remain zero.

* Rule: expand first; parent if linked, otherwise rerank.
* Forecast: fit three action-conditioned ridge maps from nine observable features
  to next evidence features; fixed utility two times completeness plus a
  non-abstention indicator. Inspired by V-JEPA's prediction in representation
  space; no V-JEPA weights, learned encoder, or raw-text forecasting.
* Imagined critic: two-horizon linear fitted Q with a greedy actor, learned
  transition rollouts from development observations. Development reference reward
  +1 correct, 0 abstain, -4 false equivalence, -1 other wrong relation. No held-out
  labels in inference. This is Dreamer-inspired, not Dreamer/RSSM or stochastic RL.
* Observed critic: identical critic/actor and reward using executed development
  transitions instead of predicted transitions. All four policies are evaluated
  on held-out **observed** replay, never on imagined rewards.

The predictor consumes only visible source/target evidence features and public
parent-link metadata; action choices use available actions and remaining horizon.
No family ID, reference, unobserved text or outcome is a feature. Model weights
are fit only to development families. Mutation of held-out labels preserves
action choice and disposition in the focused test. Future outcomes are read
by the evaluator only after an action has been selected.

## Executed development results

| Arm | Correct/24 | False equivalences | Missed equivalent | Referrals | Other abstentions | Calls | Reranks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Rule | 18 | 0 | 4 | 6 | 0 | 48 | 5 |
| Forecast | 16 | 0 | 4 | 6 | 2 | 48 | 5 |
| Imagined critic | 18 | 0 | 4 | 6 | 0 | 48 | 19 |
| Observed critic | 15 | 0 | 4 | 6 | 3 | 48 | 18 |

No gains versus the rule; forecast lost consort-6 and stard-5; observed critic
also lost stard-6. Imagined critic ties with more reranks. Zero false equivalences
in every arm is a floor effect, not evidence of risk reduction or equivalence
safety. Four missed equivalent pairs are common to all arms. Completeness
forecast accuracy 191/216 (88.43%); completeness MAE .2084 vs persistence .3426
and action mean .3272. Across nine features learned MAE .1326 vs persistence .0899
and action mean .3231; persistence is stronger overall. No policy promotion.

There are 360 states, 324 acquisition transitions (108 development, 216 held out),
and 720 terminal edges. Initial run took 0.051 s replay / 0.040 s report;
instrumented repeat 0.051 s replay / 0.041 s report; policy runtimes and summed
observed acquisition times are retained in the compact receipt. These are
in-memory lexical/replay timings, not model hosting or production latency.
Initial RED failed with missing experiment module; initial GREEN 3 focused
tests passed; timing instrumentation and leakage/conservation tests yielded
6 focused passes. The repeat conserved all primary outcomes and counts.

## Reproduction and limitations

Run from checkout with its regression environment:

    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 \
      python -m pytest --import-mode=importlib tests/test_evidence_action_replay.py
    python -m scripts.evidence_action_replay --output /tmp/evidence-action-replay-v1.json

Local Python 3.13.5 / NumPy 2.3.5; no model downloads, inference services, private
data or secrets. NumPy is already present transitively in the regression
environment. Local checkout was unavailable (GitHub DNS blocked); exact fixture
bytes reconstructed and verified by SHA-256 and Git blob; the required existing
function bodies were extracted from pinned main into local modules. The new
source and test blob SHAs in the receipt match the local files. Full regression
suite, repository lint/format, typing, make quick and protected hosted checks
were not run locally; Ruff was unavailable. Do not merge or qualify from these
six tests alone. No changes to required workflow, acceptance thresholds,
contracts, release settings or other experiments. Revert this focused commit to
roll back; no canonical data or production state is touched.

The [compact replay receipt](../../conductor/tracks/01-canonical-standard-pack/evidence-action-replay-v1.json)
retains all 324 acquisition observations, initial pools, synthetic layout splits,
timings rounded to microseconds, synthetic decisions/resolution flags, matched
policy traces, and full-output digests. Reconstitute text from the pinned fixture
and state histories; the executable emits full evidence, rankings and query
strings. Measured times vary across reruns; compare deterministic replay digest
with acquisition_seconds removed from every transition and canonical JSON sorted
keys, compact separators, UTF-8. The first and repeat raw output hashes are
separately retained. No review outcome was invented.

The experiment is deliberately small and not a test of full JEPA/Dreamer
architectures or pretrained rerankers. Synthetic completeness is artificially
observable; parent retrieval is simplified; fixed-budget acquisition does not
optimize stop/review decisions. Rule already had zero false equivalences;
there are only four test families and two development families, and familiar
synthetic templates. No independent adjudication or inferential interval.
The next scientifically useful experiment needs rights-cleared independent
families, harder qualifier/exception disagreements with nonzero incumbent
harm, real source retrieval, independent reference adjudication and actual
review outcomes/workload; retain this negative result. Existing T01.028–030,
T01.043, T01.052, T01.060–064 and Track 05 scientific gates remain open.
