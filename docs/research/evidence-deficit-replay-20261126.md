# Evidence versus decision deficit replay — 26 November 2026

Development follow-up to the first evidence-action replay (PR #184, #158). No
change to E1–E14, source rights, canonical admission, scientific thresholds or
independent-family holds. Main inspected at d88f787ffd4647117bca4ca400cbb68d95197d40.
PRs #180–183 and #185 remain separate; #183's model-placement replay is a
related but different experiment.

## Repair and qualification

Original head 8b83a7580361b7f5899be226fe4281ecdfb8688f: Assurance run
[45787051622](https://github.com/edithatogo/standards_check/actions/runs/45787051622)
completed 851 Python tests, three skips, 91.57% combined coverage (replay
module 84.77%). Rust/API coverage and cross-platform jobs passed. Workflow
policy failed on 12 B023 loop-capture diagnostics, and Codecov patch failed.
Bind loop variables in the recursive replay builder; add regression tests for
previously uncovered lexical decision, reward, input and CLI paths. Preserve
all original outcome counts and receipts. Focused local suite: 15 passed,
combined module branch coverage 99% rounded (333 statements, three missed,
102 branches, three partial). Local checkout and pinned Ruff installation
remain unavailable. Use the existing hosted qualification gates; temporary
read-only pinned-format diagnostic is removed before integration. No policy
or threshold changes.

## Design

Keep the 12 original training and 24 test pairs grouped by guideline family.
Each pair starts with the same actual lexical expansion. The second action
is either a parent lookup or deeper lexical reranking (incumbent), or a
cached full-pair MiniLM/DeBERTa decision. Historical artifact 15087556116
from run 45754736904, original run overall failed but its retained decision
artifact is hash-verified and independently reused in #183. Exact fixture,
opaque pair identity, both text hashes, relation orientation, split and
family are verified. A semantic outcome is available only if the currently
observed target text exactly matches the model-input hash; incomplete evidence
does not receive an invented model output. Ten dev and 19 test pairs eligible
after expansion. These are exposed synthetic controls, not a new confirmatory
cohort or new neural inference.

For each model independently, allocate exactly four semantic actions in the
fixed, deficit and learned arms, with remaining pairs receiving incumbent
second acquisition. Fixed ranks opaque ID hashes; deficit prioritizes
complete-but-abstained cases, then the same hash tie break; learned uses
ridge regression trained on eligible dev pairs to predict semantic minus
acquisition reward (+1 correct, 0 abstain, -4 false equivalence, -1 other wrong).
All priorities use current observable features only. Inference uses no
held-out labels, future evidence or cached model prediction before action
selection. Early-stop diagnostic uses the same deficit rule but stops when
the initial lexical decision is decisive; not a safety gate. Matched referral
workload uses the label-free minimum abstention count, capped at six; actual
review outcomes are absent, so no referral resolution is credited.

Primary comparison within the three equal allocation arms: false equivalences
and correct resolutions at 44 retrieval plus four semantic calls and matched
referrals. Compare also all-retrieval and early-stop arms at explicit
resource counts; unlike calls are not equal measured compute. Do not compare
historical model wall time to current replay time.

## Executed results

| Arm (same outcome for each retained NLI model) | Correct /24 | False eq | Missed eq | Abstain | Retrieval | Semantic | Stop | Referrals |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Search again | 18 | 0 | 4 | 6 | 48 | 0 | 0 | 2 |
| Fixed | 18 | 0 | 4 | 6 | 44 | 4 | 0 | 2 |
| Deficit | 22 | 0 | 0 | 2 | 44 | 4 | 0 | 2 |
| Learned | 19 | 0 | 3 | 5 | 44 | 4 | 0 | 2 |
| Early stop | 22 | 0 | 0 | 2 | 29 | 4 | 15 | 2 |

Both models agree on every selected cached outcome in these arms, not
independent evidence. Deficit gains all four previously missed equivalent
pairs (arrive-1, consort-1, stard-1, tripod-1), no losses. Learned gains only
arrive-1; fixed gains none. Two unresolved cases common to deficit arms:
arrive-6 and tripod-5. No independent review outcomes. Full output digest
and every case/action/disposition in [receipt](../../conductor/tracks/01-canonical-standard-pack/evidence-deficit-replay-v2.json).
Run wall time 0.0563 s in local Python 3.13.5 / NumPy 2.3.5; replay cost only.

## Separate formal safety diagnostic

Four newly constructed two-atom controls have reference relations computed
by exhaustively enumerating all four assignments using the existing witness
compiler. The common lexical decision rule calls all four equivalent; three
are false equivalences (implication vs converse, opposing conjunctions and
opposing disjunctions); the commutative conjunction is correctly equivalent.
These intentionally adversarial controls are not part of the historical
matched-budget cohort; no cached NLI results exist for them. This establishes
an actual failure mechanism, not the prevalence of false equivalence.
In particular, lexical confidence or complete evidence cannot be a safe
early stopping criterion for equivalence. Preserve the negative result;
do not promote any policy on these data.

## Reproduction and remaining gates

```sh
python -m pytest --import-mode=importlib tests/test_evidence_action_replay.py tests/test_evidence_deficit_replay.py
python -m scripts.evidence_deficit_replay --artifact /path/to/github-actions-artifact-15087556116.zip --output evidence-deficit-replay-v2.json
```

Run held-out source families only after rights/structure/independent reference
qualification. Extend the existing opt-in native inference lane to fresh
partial and complete evidence, including formal controls, record actual
retrieval/reranking and decision compute separately and compare against
symbolic witnesses and independent adjudication. Review referrals remain
workload until actual review outcomes. Keep T01.063–064, T05.048/063 and
scientific gates open. No automatic canonical admission or production changes.
