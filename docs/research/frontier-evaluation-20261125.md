# Frontier evaluation and test efficiency — 25 November 2026

Owners: [assurance issue 31](https://github.com/edithatogo/standards_check/issues/31),
[publication issue 158](https://github.com/edithatogo/standards_check/issues/158),
[diagnostic issue 116](https://github.com/edithatogo/standards_check/issues/116).
This is a dated operational and exploratory observation, not a new canonical ledger,
approved protocol, rights determination or claim of state-of-the-art performance.
The [publication contract](../../contracts/publication/programme.v1.json) remains the
sole prospective run and claim registry; do not populate it retrospectively.

## Engineering baseline and test value

The final ordinary [main assurance run 45434083296](https://github.com/edithatogo/standards_check/actions/runs/45434083296)
at `ef4fb0dd4c4e01fca4527041e464e816f6f4d73e` passed. The [Python job](https://github.com/edithatogo/standards_check/actions/runs/45434083296/job/138587009492)
recorded 637 passed and three optional skips, with 90.813% combined coverage.
These are measured hosted timings, not a controlled before/after trial.

| Measured scope | Ordinary main | Earlier main with optional reference |
| --- | ---: | ---: |
| Python job wall time | 178 s | 179 s |
| Python and system dependency installation | 54 s | 65 s |
| Regression/validator/coverage/projection step | 87 s | 63 s |
| Local guideline-family comparison step | 13 s | 8 s |
| pytest suite reported time | 47.70 s | Not extracted |
| Locked CLI build reported time | 12.61 s | Not extracted |

Earlier reference run: [45431063021](https://github.com/edithatogo/standards_check/actions/runs/45431063021)
at `019f280d615dcdc8162555e6ab9fea0eaa6fbeb4`; 640 tests passed with 91.647% combined coverage.
Do not pool the optional-reference run and ordinary run as identical workloads.
The final ordinary main had 26 s API coverage, 105 s Rust coverage, 47/75/88 s
Linux/macOS/Windows native jobs respectively, and 38 s workflow policy, all successful.
The independent Scorecard start failed (missing upstream image); offline security stayed
queued. Neither is a passed detector. The latest successful Rust CodeQL job took 253 s.
Wall times include runner and network variation, not just computation.

The next CI change separates pytest and validator steps, retains the slowest 20 case
durations and native JUnit XML alongside the existing checkout-bound coverage logs.
A local synthetic one-test smoke verified the pytest flags and XML duration field;
this is not a local run of the repository. No test is removed and the coverage
configuration and aggregate remain unchanged. Hosted acceptance is pending.

Optimization order (Ponytail): inspect the timings, remove redundant setup or expensive
fixture construction only where outcomes stay identical, then measure a single
candidate. Prefer native pytest tooling and existing dependency mechanisms. A
hash-verified pip wheel cache is a candidate only after transitive closure and a safe
cache trust boundary; do not introduce cross-trust writeable caches. Trial
pytest-xdist with two workers only if isolation, subprocess coverage and deterministic
fixture behavior can be demonstrated; the 47.70 s serial suite is not itself a reason
to add another dependency.

For any timing claim, use the same tested revision, runner class, tool and dependency
pins, input set, optional-model setting, and cache regime. Record at least three
repeats per arm, median and range, total runner time, test identities/outcomes, covered
counts and negative-control/mutation outcomes. Adopt only if median relevant wall time
improves by at least 15% without losing tests, coverage, failure detection or security
and without materially increasing total runner minutes. This proposed engineering
threshold is a decision rule for a future comparison, not a result. Keep the serial
path authoritative until a candidate passes; report regressions and inconclusive trials.

## Observed exploratory experiments

The following are log readbacks and artifact inventory observations on older candidate
revisions, not a newly executed experiment. Retain the original artifacts, immutable
checkout references and previous failures. No scientific gate is changed.

| Observation | Result | Interpretation |
| --- | --- | --- |
| Formal binary equivalence comparison, 24 held-out cases across four families | Exact, lexical, classical, dependency and classical plus dependency each TP 4, FP 0, FN 4, TN 16; bidirectional MiniLM NLI TP 8, FP 0, FN 0, TN 16 | Four additional true equivalences in this bounded designed challenge; no natural-source accuracy or safety claim. |
| Five-class controlled witness reference | 18/30 held-out consensus, all 18 correct; dev accuracies 60% and 100%; correct consensus classes narrower 6, contradictory 6, indeterminate 6 | Scientific gate failed: reference does not cover all five classes and one agent misses the development threshold. |
| Five-class comparison escalation | Baseline 17/30 correct; narrower 4, broader 4, indeterminate 5 errors; zero false-equivalence errors reported | Eligible for the existing conditional challenger experiment; not eligible for production semantic admission. |
| Separate agent benchmark | Consensus 3/10 test pairs in one family; one narrower-class error; qualification false | Sparse, failed reference evidence; no overall five-class qualification. |
| Historical exact-head native pack ingress campaign | 974,312 executed inputs in 61 s; peak RSS 478 MB; workflow successful | Bounded sanitizer campaign on earlier PR 146 head. No proof of vulnerability absence or current-main acceptance. |

Evidence references:
- PR [155](https://github.com/edithatogo/standards_check/pull/155), head
  `0a4c13b197838413c5082dc7d74a09d0db776628`, tested merge
  `e8cdd646db74115e2233b379d76f1d3526ecfd47` as named in artifacts.
  [CPU job](https://github.com/edithatogo/standards_check/actions/runs/45405500543/job/138485002532);
  [artifact 14925311073](https://github.com/edithatogo/standards_check/actions/runs/45405500543/artifacts/14925311073),
  archive digest `sha256:fe3cfa064cde26ba2dd3f8f1be53bb4137c5d071930df588644ae7eb2e805794`.
  [Controlled reference job](https://github.com/edithatogo/standards_check/actions/runs/45405499908/job/138485001341);
  [artifact 14926383953](https://github.com/edithatogo/standards_check/actions/runs/45405499908/artifacts/14926383953),
  archive digest `sha256:579dc3ee33560236175703fcf488df6121e10532f350b7873d50c6d5430022f8`.
  [Separate agent benchmark](https://github.com/edithatogo/standards_check/actions/runs/45405499958/job/138485000926).
  Artifact archive digests are reported by the API, not independently recomputed in this session.
- PR [146](https://github.com/edithatogo/standards_check/pull/146), older head
  `f1354701dfbbaea54940f46b1764faa4b779f63d`;
  [native fuzz job](https://github.com/edithatogo/standards_check/actions/runs/45380390860/job/138397589437).
  The previously recorded 932,153-input and 629,873-input campaigns and initial licence
  failure remain distinct. Reconciled head `55ccfa82ec1adcc78c465531adaff9d721b71526`
  requires a fresh locked campaign and protected checks; do not count queued or historical
  results as new acceptance.

## Continuous model selection: best for each role, not largest or newest

Use existing deterministic extraction and explicit rules as the first pass. The
[architecture shortlist](../architecture/REPORTING_GUIDELINE_INTEROPERABILITY.md) remains
the candidate queue. The following public model cards were inspected on 25 November 2026;
publisher benchmark scores are not our domain results.

| Candidate | Reason to evaluate; next decision |
| --- | --- |
| Existing MiniLM and DeBERTa-v3-xsmall | Preserve exact incumbent results and resource use. Reproduce existing conditional comparison before expanding. |
| [Cross-encoder DeBERTa-v3-large](https://huggingface.co/cross-encoder/nli-deberta-v3-large) | Same-family capacity ablation on the identical predeclared question; supplier reports SNLI/MNLI performance, not reporting obligations. |
| [MoritzLaurer DeBERTa-v3-large](https://huggingface.co/MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli) | Alternate NLI training mixture and adversarial examples; compare error overlap and verify label mapping. |
| [Tasksource ModernBERT-large NLI](https://huggingface.co/tasksource/ModernBERT-large-nli) | Alternative architecture and task mixture; review training-set overlap and actual sequence limits. |
| [Liquid AI d1-2B](https://huggingface.co/LiquidAI/d1-2B) | Typed directional decisions and span extraction rather than free generation. Evaluate incremental supported catches and calibration at fixed review budget. Custom code and licence require separate qualification; no remote model code execution or upload of restricted text. |

Record the actual checkpoint revision, weight/tokenizer/code hashes, model licence,
runtime, hardware, quantization, label order, truncation, prompt/version, source and
family partitions, inference parameters, seeds, cost, latency and failure counts.
For hosted adjudicators record the exact exposed provider/model identifier and date;
if a version or training snapshot is not disclosed, explicitly record that limitation.
Never silently substitute a model alias, update a pinned asset in-place, or infer
cross-model independence from provider names.

Reassess the shortlist at each new protocol freeze, monthly during active work, and
on a material model/runtime/security release. Use public cards, documentation,
release notes and relevant independent evaluations for screening. No automatic model
replacement, retraining, data transfer, new service or indefinite model sweep.
One challenger per decision question; record why it was selected or rejected.
A cheaper model may remain preferred when it meets the risk bound and delivers
more unique supported detections per review minute. A security vulnerability can
require a hold before a scientific comparison.

Use the existing E1–E3 contract, not this dated record, for future confirmatory
experiments. Before freeze specify sampling, effect/uncertainty method, class and
family coverage, maximum false-equivalence risk, allowed review cost and decision
threshold. Report paired incremental catches and harmful changes, shared misses,
abstention and coverage, directional consistency, Brier score/calibration where
probabilities are meaningful, resource costs and unresolved cases. Keep development,
formal controls, natural-source comparisons, and external reference results separate.
Retain negative and inconclusive results with exact commands and artifacts; never
drop failed rows or declare success from a green execution job.

## What would exceed the current frontier

The programme must demonstrate its value against contemporary comparators and real
consumer use, not declare superiority from architecture or coverage. Ordered work:

1. **Reconstruction and exchange:** directory-level denominator conservation, exact
   source spans, qualified edition/rights states, differential readers, and loss-audited
   CEDAR/JSON-ScheeLD round trips. Prioritize actual hard failure families over more
   generated checklist copies.
2. **Selective prediction with verifiable witnesses:** explicit directed implication,
   conditional scope and counterexamples; deterministic inverse/composition checks;
   calibrated abstention and review-budget routing. A witness solver is justified
   only for a bounded formal subset where semantics are explicit and checked.
   Do not pretend arbitrary natural language can be fully formally verified.
3. **Prospective external validity:** untouched guideline families, source formats,
   issuers and editions; independently adjudicated source-grounded cases with
   retained disagreements, clustered uncertainty and leakage review. Model-agent
   references are not independent human truth. Test on material natural discrepancies.
4. **Decision utility:** estimate verified material errors found per reviewer hour at
   equal review budget, plus erroneous equivalences, review delays and compute cost.
   Compare against manual, rules-only, strongest qualified single-model and augmented
   approaches; publish the limits and null findings. An independent consumer and
   actual author/editor workflow are needed for usefulness claims.
5. **Reproducible delivery:** exact release artifacts and SBOM, native sanitizer and
   mutation results, release attestation, independent clean install/restore,
   accessibility and external review; a rights-cleared dataset with a stable
   manifest and retained held states. No data release or upstream approval implied.

Stop at the first demonstrated useful improvement. The study should establish whether
the combined method provides measurable evidence or decision value beyond existing
methods, not prescribe that outcome. See the [publication submission plan](publication-submission-plan.v0.1.0.md)
for planned experiments, outputs and venues.
