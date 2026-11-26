# E10 task formulation and supervised controls — 26 November 2026

Existing #158 / T01.027, T01.029, T05.048 and T05.049. Stacked on #186
(`bc9f70057f52aa95b2f6346d9893d4b5548eefbd`); no production or canonical changes. Preserve original
negative result from run 45794639014, verified artifact 15104920210.
Do not relabel this follow-up as confirmation on the already observed
synthetic fixture.

Two fixed neural alternatives: explicit whole-clause definitions
(including governing conjunction/preposition) with joint extraction,
and the same three definitions evaluated one type at a time (three
calls per case). Same pinned checkpoint, offsets, overlap setting,
threshold 0.5 and fixture; only task framing/call grouping changes.
Exact prior wheel closure and all five model asset hashes recovered
from the independently verified artifact; no floating dependencies or
remote model code. New actual neural runs pending hosted execution;
previous actual negative result retained. No supervision on held cases.

Two small supervised models with no external weights: per-type
token-context BIO multinomial naive Bayes, and contiguous candidate-span
boundary-pair multinomial naive Bayes (maximum 12 tokens, fixed 0.5
positive cutoff, deterministic same-type non-overlap). Distinct
span formulations allow overlapping different entity types. Train on
two author-labelled synthetic strata, predict the third; rotate all
three strata with exact IDs retained, no tuning or reference-derived
test features. This is not real guideline-family independence.

## Actual local results

16 cases, 17 reference spans. Python 3.13.5 isolated overlay, no model
downloads. RED missing module, GREEN 13 focused tests (including seven
original tests), 99% branch-inclusive coverage across both modules
(tagger_followup 98%). All results and training/test case IDs generated
by actual runner. Local process wall 0.0778 s, peak RSS 96652 KiB,
token fit/predict 0.0147 s, span fit/predict 0.0620 s; not comparable
to separately executed pretrained runtime. Exact local blobs:
tagger_followup 661f14bb91704ba1f44f13117fdb258b8403955a,
extractive_development 266c682ac5e0f6f86a80b42466d0fd6cc72187c8.

| Arm | TP | FP | FN | Exact F1 |
| --- | ---: | ---: | ---: | ---: |
| Retained rules | 14 | 2 | 3 | .848485 |
| Prior GLiNER joint | 1 | 6 | 16 | .083333 |
| Fitted token BIO | 0 | 1 | 17 | 0 |
| Fitted span pair | 0 | 0 | 17 | 0 |

Supervised models are too data-limited to infer general inferiority.
The span classifier predicts no positive spans; precision undefined,
recall zero. The token classifier emits one incorrect span. Retain
negative results without modifying the reference or tuning on these
held-out outputs. Previous GLiNER errors include marker omission
(clustered trials, studies with linked records, no sample remains)
and unrelated spans. Alternative formulations test those failure modes
without accepting unanchored text or claiming relaxed fidelity.

Ordinary CI and hosted inference required. Scientific confirmation,
independent source rights and family-qualified labels remain held.
Rollback removes follow-up runner, fixture-independent tests and
workflow, restores loader wrapper. No admission or equivalence inference.


## Actual hosted follow-up and Ponytail reconciliation

[Run 45798338941](https://github.com/edithatogo/standards_check/actions/runs/45798338941)
completed both learned framings and supervised controls using the exact
prior wheel closure and model assets. Downloaded
[artifact 15107111276](https://github.com/edithatogo/standards_check/actions/runs/45798338941/artifacts/15107111276)
SHA-256 `cf41d449aca1231ae24f544b6b36834b57de0b1c604ccb91ab34628a313878b8`;
tested merge `b2c62207effb72107f70e5ba775422c4c57f4b9f`.

| Arm | TP/FP/FN | Exact F1 |
| --- | --- | ---: |
| Rules | 14/2/3 | .848485 |
| Whole-clause joint | 1/2/16 | .10 |
| Per-type | 2/19/15 | .105263 |
| Fitted BIO | 0/1/17 | 0 |
| Fitted span boundary | 0/0/17 | 0 |

Joint model recovers q02 exception [9,22); per-type also recovers q10
exception [67,95). Both already recovered by the rules. Joint 16 calls,
per-type 48 calls: report as different acquisition costs, not equal compute.
Retain all raw offsets and negatives. No further synthetic prompt sweep.
Use the exact pinned closure for future independent qualification.

Reconciled stacked #189 onto #186 `38fbcb66976e6a1686b7dbaea96dbadeedc2ed5f`: retain one model
initialization path (load_extractor) and the existing load_model wrapper
with optional predictor_factory for both original label frames and the
follow-up. Fix observed Ruff F821 and B023 in the follow-up (initialize
end; bind predictions for the fold). New RED: missing predictor_factory
argument, GREEN: 14 focused local tests passed; supervised per-case
predictions and all metrics exactly equal the previous local receipt.
Only tested the isolated overlay, not full checkout or fresh neural inference.
Keep original source blobs and prior hosted results intact; exact-head
required CI remains necessary. Defer any larger model until independent
references and residual gaps justify it. No scientific promotion.

Use the coordinator's existing exchange convention in #183
[replay.md](https://github.com/edithatogo/standards_check/blob/dd0eff304c0b1aa42e8b863514bd2b33b4ac95c1/research/model-placement/replay.md)
and retain separate E9/E10/E11 identifiers; no cross-dataset join.


## Review and formatting follow-up

Reconciled with #186's raw-response retention repair `aecbb1fc09d9c3a521b1e9a7ba03529de93ccf83`.
Multi-call framing preserves every response received before invalid span or
label validation, including the offending response, using the same
InvalidPrediction boundary; no partial credit. RED reproduced lost raw
response, GREEN 16 focused local tests passed across evaluator and follow-up.
Supervised per-case predictions and score dictionaries exactly match the
prior local receipt for all three arms. Addressed hosted Ruff-format finding
in run 45803120923, job 139853520573 by wrapping the reported call. No changed
labels, weights, scoring, or independent scientific evidence. Full hosted
exact-head qualification still required.
