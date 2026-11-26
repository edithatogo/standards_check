# Evidence-action verification v3 — 26 November 2026

Development only, T01.063–064 / T05.048, T05.063 / #158. Original PR #184 head
53006835924562b665766b1b99da325d890f6ce0 passed Assurance 45793663091: 860 passed,
three skipped, combined Python coverage 91.95%, replay modules 99.22% and 97.77%,
Codecov patch and CodeQL passed. Offline AI security remains queued. Preserve
the v1 and v2 negative and positive results; no change to scientific holds.

## Protocol fixed before fresh inference

Reuse pinned 36 original synthetic pairs, held-out 24 from four families, no
training or threshold selection. Evaluate each pair at five actual observed
states: initial head; after expansion; after lexical deep reranking; after
neural deep reranking; and the original rule's terminal state. Use the same
fixed initial shortlist for deep reranking; score each candidate independently
with pinned MS MARCO MiniLM-L6-v2 and return at most two fragments, preserving
IDs; the original lexical comparator uses positive scores only. Compare
completeness gains/losses and decisions, not an oracle-selected pool. Synthetic
completeness uses observed head/tail or parent links, not natural source coverage.

For each state score the visible A and B text in both directions using
pinned MiniLM and DeBERTa CPU ONNX, keeping original confidence thresholds
and exact label map. Do not supply gold labels, hidden fragments, later outcomes
or reference data. Report raw scores even on incomplete text, but gate all
incomplete predictions to abstain in the strict agreement and proof arms.
Evaluate raw decisions against the original full-pair reference only as a
diagnostic, not a partial-pair reference. Retain all probabilities, inputs,
durations, call counts, candidate scores and anchored evidence. Compare
raw NLI, original lexical, complete-only strict NLI agreement, lexical plus
proof requirement, strict NLI plus proof requirement and standalone formal
relation. Five paired state assessments per held-out case and four formal
controls: 496 directional NLI calls in total, no training. Each reranker
candidate is scored once; no new candidates. Timing is isolated per
model/view but not an end-to-end or compute-matched policy trial.

## Fail-closed equivalence verifier

Parse only the exact synthetic closed grammar with prefix "A report complies
if and only if", alpha/beta literals with explicit true/false, single
conjunction/disjunction or implication, full sentence boundary. Enumerate
four assignments and classify using the existing witness compiler. Retain
explicit asymmetric truth assignments. Unsupported syntax, missing evidence
or empty compliance sets cannot verify equivalence. This is not a natural
language parser; no proof of source authority. Non-equivalence candidates
remain advisory, not formally validated by this gate. No equivalence
candidate may stop on lexical confidence or neural agreement alone. The
strict proof-only arm will withhold all unsupported natural equivalences;
report the lost utility rather than claim broad safety. Referral outcome
credit remains zero; no independent reviews exist.

## Local evidence

RED missing verification module, then four tests passed; two further tests
cover fixture pinning and held-out future-evidence/model-outcome mutation.
22 focused tests passed (all v1/v2/v3 tests) against extracted pinned
repository functions. Source blob fe2f22a144aa5e97fd052edd4bf44f6f31ec11d1;
test blob a5c783231ea6bc7960a70a7bd65c3c98e8a6165a. Local test scorers are
deterministic doubles, not model evidence. Actual finite evaluation rejected
three of three invalid equivalences with counterexamples and preserved the
one true equivalence; four of four formal relation references matched.
Full checkout and fresh model inference require the explicitly labelled
hosted lane. Record actual receipt and failure, not queued work as success.

## Remaining scientific boundary

Historical synthetic cases and four selected formal controls cannot establish
population risk or independent scientific validity. Real nested source
clauses, independently verified applicability rules, fresh family-disjoint
rights-cleared sources, adjudication and measured review outcomes remain
held. No canonical admission, model promotion, production routing or changes
to acceptance thresholds. Further learned action models remain deferred
until simple routing leaves a material gap. Rollback: revert this focused
research increment; existing v1/v2 reports remain unchanged.


## Exhaustive finite-grammar qualification and hosted dispatch

The follow-up local regression added an independently implemented four-bit
truth-set oracle. It checked 36 supported syntactic expressions and all 1,296
ordered pairs, including empty compliance sets, asymmetric relations, witness
counts and the equivalence-only gate. All 23 focused tests passed. This proves
agreement with the bounded oracle, not correctness of real-language
formalisation. The branch was reconciled with E9 receiving main
`08e86696180936ef6722e539a32d6ebbd2222625` without replacing the concurrent
Conductor records. The labelled fresh-inference experiment is
[run 45797316771](https://github.com/edithatogo/standards_check/actions/runs/45797316771)
on head `421a9b234f12edfac942c18f832a2ee4e5a21950`; its development job was queued at observation. No fresh neural
metrics, model-download success, or hosted qualification are claimed.
