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
