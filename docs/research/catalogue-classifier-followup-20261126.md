# Catalogue classifier and role follow-up

Exploratory extension of #194 and #193, under T01.052/053/064 and #158.
Reuse the exact retained 720-entry catalogue, selected MeSH inventory and five
proxy grouped folds. Do not claim independent family/reference qualification.
No source rights, applicability, equivalence or deployment admission.

## Observed local comparison

Cross two TF-IDF representations with three classifiers, using the same
training-fold vocabulary, known-label training pool per facet and top-1/3/5
label budgets. Unknown-only facet rows are excluded from classifier fitting
and from voting; other recorded labels are weak negatives for one-vs-rest
logistic, not independently verified absent. This pool differs from the old
neighbour experiment, so use the matched new control. Word (1,2), char (3,5)
grams. Ordinary vs balanced logistic C=1, liblinear, no hyperparameter search.
Preserve the original 617 proxy groups and all 720 output IDs, including the
one without a title. Independently recompute and verify the exact prior
fold manifest digest before training. Evaluation is case-relative macro
recall, precision at fixed K and per-label recall; no post-hoc threshold
tuning. Results repeated with identical complete per-case rankings.

| Representation/classifier | Macro R@3 study | Clinical | Section |
| --- | ---: | ---: | ---: |
| Word / kNN | .7503 | .4612 | .6136 |
| Word / logistic | .6561 | .3464 | .6597 |
| Word / balanced | .8134 | .5132 | .6644 |
| Character / kNN | .7663 | .5836 | .6366 |
| Character / logistic | .6714 | .4115 | .6693 |
| Character / balanced | .8124 | .5875 | .6761 |

Matched char balanced versus char kNN: study +117/-52, clinical +63/-56,
section +227/-119 at K=3. Count shared misses 176, 236 and 480 respectively.
The added computation is real: repeated local revised report representation
and all-facet classifier timings are retained separately. No hardware-matched
population inference or calibrated probabilities. Class balancing can alter
rankings materially, so cross classifier and model rather than confounding them.
The new balanced word arm improves study-type macro recall most; balanced
character improves clinical and section macro recall in this exposed panel.
Recompute context-specific Pareto frontiers after measured neural outcomes,
including equal-label recall, precision and resource cost. Do not treat
prediction on historical labelled data as valid admission.

## Role-aware extraction audit

Reuse the exact longest-match dictionary extractor and span hashes. Add
a deliberately conservative cue rule for an explicit preceding reporting or
guideline-for phrase, and separate explicit developed-using/derived-from cues.
Negation/exclusion and unresolved context remain unknown. These are
role candidates, not independently adjudicated NER. Among 259 actual title
mentions, 52 target cues, one development cue, 206 unresolved. Of 40 direct
novel category pairs, one has a target cue. The other 39 are not proved
incorrect; retain them for blinded role adjudication. No mapping is promoted.
This reduces the review shortlist without interpreting silence as exclusion.
It is not a measured precision gain. Next compare contextual span/role models
on independently anchored sentences and distinguish development, examples,
background, target population, study design, obligation and condition.
Cite and reuse #191 bibliographic evidence and #188 source qualification,
not a second provider sweep or separate incompatible reference registry.

## Hosted representation comparison

Explicit opt-in catalogue embedding job uses the historical exact catalogue
member, verified split and same sparse controls within each runner.
BGE-small raw 384 dimensions, exact observed ONNX model, config, tokenizer
and card hashes from artifact 15088716936; Qwen3-Embedding 0.6B raw 1024
dimensions, exact official Q8 GGUF, llama.cpp b11960, model-card hash from
15090704998. 719 local embedding requests per backend, no label or future
outcome used in extraction. For each model cross kNN, ordinary logistic,
balanced logistic on identical folds, 9 arms per runner including sparse
controls. Across both jobs this gives 12 distinct representation/classifier
cells; do not count repeated sparse controls as independent evidence.
The neural runs measure model plus numerical/runtime representation; they
are not an isolated architecture comparison. Capture actual dimensions,
matrix digests, request counts, execution/fit times, process resource
measurement, model card and environment; no raw titles or vectors exported.
Do not start a hosted neural run unless exact prior artifact, assets, pins
and runtime are available. Stop on hash or fold mismatch. Record transport
or runtime failures explicitly. No new maintained application dependency.
The explicit research runtime test is opt-in because scikit-learn is
not part of the maintained ordinary test dependencies.

## Retention and acceptance

See [versioned receipt](../../research/catalogue/classifier-followup-v2-receipt.json).
Both actual local reports, exact folds and original source graph retained in
the personal Library under content-addressed paths. Do not replace the
older publication snapshot or other receipts. Supply safe metrics and
exact provenance to #192 for its next additive supplement. Five new
focused tests passed, 15 total in extracted local module suite; full checkout
unavailable locally. Actual hosted inference results and protected
qualification remain to be observed separately. Scientific and source
holds remain. Ponytail: reuse existing dictionary, observed folds,
classifier metrics, ONNX and llama.cpp runtime; no vector database, new
neural training framework or broad bibliographic pipeline.

## Hosted attempt and split portability repair

Run 45836556902 failed before inference in both jobs, after exact catalogue
and all pinned model assets passed their hashes. Original scikit-learn
split reconstruction did not reproduce the retained fold digest across
runtimes. Do not relax the gate: encode the exact 719 original assignments
in sorted-ID order, bind them to the exact catalogue digest, reconstruct
and verify the original manifest and test group isolation before acquisition.
Both original artifacts are digest-verified and retained privately. RED
missing assignment decoder, GREEN six focused and 16 extracted-module tests.
All local case-level metrics, rankings and roles exactly equal v2. No neural
inference result from either failed job; new hosted replay required.
