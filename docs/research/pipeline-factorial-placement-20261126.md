# Factorial pipeline placement and ordering — development, 26 November 2026

Tracks T01.063–064, T05.048/063, issue #158. Extend the existing immutable
E9–E14 specialist protocol with a separate development increment and proposed
screening matrix; do not change claim C7 or any scientific freeze. Reconcile
E11 receiving main `776ed1dbfbe19d16365310ef0fa07d29a793611a`. Coordinate E9 #182, E10 #186/#189, graph #187,
source inventory #188, model placement #183/#185 and applicability #180.
No new dependencies or model promotion.

## Executed acquisition design

Use exact pinned fixture, existing acquisition, lexical retrieval/reranking,
observation and decision functions. Three binary factors: query expansion,
parent lookup, deep lexical rerank. Full 2^3 design; for each subset execute
every nonrepeated permutation (16 configurations total). Reexecute the
original 240 held-out states, confirm evidence IDs and decisions against
historical replay, and execute all 144 previously unobserved third-action
transitions on current visible states. 24 case units from four historical
test families; permutations are repeated measures, not independent samples.
Average orders within each cell per case, then aggregate; retain all orders.

| Expansion | Parent | Rerank | Mean complete /24 | Mean correct /24 | Calls |
| --- | --- | --- | ---: | ---: | ---: |
| 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 19 | 15 | 24 |
| 0 | 1 | 0 | 19 | 15 | 24 |
| 0 | 0 | 1 | 17 | 14 | 24 |
| 1 | 1 | 0 | 23 | 18 | 48 |
| 1 | 0 | 1 | 19.5 | 15.5 | 48 |
| 0 | 1 | 1 | 22 | 18 | 48 |
| 1 | 1 | 1 | 23 | 18 | 72 |

All six three-action orders yield 23 complete and 18 correct, no additional
benefit beyond expansion plus parent. All false equivalences zero, so no
safety contrast identifiable in these synthetic cases. Mean completeness
main effects +27.60, +32.81, +21.35 percentage points. Two-way average
differences of differences -34.38, -40.63, -30.21 points respectively
(expand:parent, expand:rerank, parent:rerank); three-way +56.25 points.
Correct-decision main effects +20.31, +25.52, +18.23 points; two-way
-28.13, -34.38, -23.96, three-way +43.75. These are bounded additive
contrasts with overlap and ceiling effects, not estimates of independent
causal mechanisms or population interactions. Across subsets, acquisition
budgets differ by construction; report marginal gains/calls and same-set
order comparisons separately. No independent compute-matched claim.

## Executed semantic factorial on retained inference

Cross original head vs rule-terminal acquisition bundle, lexical vs strict
MiniLM/DeBERTa agreement, advisory label vs formal proof required for
equivalence. Exact hash-verified v3 report 15106112148; reuse only actual
predictions at those states, no fresh inference or imputed new outcomes.
All four head cells abstain by design; rule terminal 23/24 complete.
Terminal lexical/no proof 18 correct, lexical/proof 14, NLI/no proof 20,
NLI/proof 12. Conditional NLI effect +2 vs -2 (interaction -4/24 or
-16.67 percentage points at terminal). Averaged over both acquisition
states, NLI main effect zero, NLI:proof -8.33 points, three-way -16.67.
Proof gate withholds unsupported real-language equivalences; this is a
coverage cost, not a change in actual final admission. Do not credit
referral as resolution; no independent review outcomes. Counts are
counterfactual call budgets from observed action/model calls, not a
fresh measured timing comparison. No safety estimate from a zero-harm
floor; retain separate formal counterexamples from v3.

## Prospective corpus-scale design

See [machine-readable screening design](../../conductor/tracks/01-canonical-standard-pack/pipeline-factorial-screening-v1.json).
Prefer full factorial for three or four factors, or all 64 six-factor
configurations if feasible. For a bounded screen use the regular 32-run
half fraction F=ABCDE, resolution VI. Independent NumPy rank and
orthogonality check: 32 rows, 22 columns for intercept, six main and
15 two-factor effects, rank 22; complementary three-way effects aliased.
No actual 32-cell model execution claimed. Add complementary fraction
or targeted confirmation where higher-order interactions matter.

The six factors are layout challenger, structural closure, tagger,
candidate fusion, neural rerank and advisory specialist decision.
Low levels still retain deterministic source and final acceptance controls.
Freeze exact levels, model assets and legal permutations by eligible format.
Invalid precedence/format cells are not missing at random: choose a
constrained design with rank and alias checks rather than inventing outcomes.
Measure component inclusion, ordered contrasts within equal sets, and
separate parallel/sequential fusion. Use the placement experiment inventory
in the plan (including provisional scope and early witness search), with
matched candidate and review budgets. Compare actual resource measurements;
keep no-source and held records in the corpus ledger but exclude from the
scientific endpoint only by frozen eligibility and report denominators.

Family-component blocked paired repeated-measures analysis; document-level
reader effects, complete independent reference denominator, clustered
uncertainty, sample precision and prespecified primary interactions/harm
margin; multiplicity plan before confirmation. The original 24 exposed
cases cannot establish sample size or independent effects. Keep every
null/adverse finding; compare cost/risk frontier. Adaptive deterministic
routing first; revisit learned action consequence prediction only when
there is an empirically demonstrated residual gap. No requirement to
promote a model or remove safety verification.

## Reproduction and verification

```sh
python -m pytest --import-mode=importlib -q tests/test_evidence_factorial.py
python -m scripts.evidence_factorial --neural-report /path/to/report.json --output evidence-factorial-v1.json
```

RED missing module, six focused tests pass; 48 local extracted-module
tests pass, 99% branch-inclusive coverage on the new module (rounded).
Exact source/test blob hashes and compact case-level predictions in the
[receipt](../../conductor/tracks/01-canonical-standard-pack/evidence-factorial-v1.json).
Complete report digest includes measured edge timing; stable digest removes
only acquisition_seconds from each acquisition case outcome. The hosted
label `run-evidence-factorial` reuses the previous artifact, no model
downloads; current exact-head lint, full suite and protected checks
remain separate. Local full checkout and pinned Ruff unavailable.
No new independent reference, rights or production decisions.
