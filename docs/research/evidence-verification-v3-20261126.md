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

## Executed hosted fresh inference

[Run 45797316771](https://github.com/edithatogo/standards_check/actions/runs/45797316771)
succeeded on merge `5dc29e64ad6ea05fd096cc72090603d2f759e209`. The downloaded
[artifact 15106112148](https://github.com/edithatogo/standards_check/actions/runs/45797316771/artifacts/15106112148)
matches SHA-256 `e5f3d8a17ce8b57169aa19f7730b1d2f272c04d23282e8240822539d3b55f09f`; report.json
`7a79c7734a6d202332fa1a65178a1fb4a9b14e83762041418574dd3a7eea2f7d`. Retain the [versioned summary](../../conductor/tracks/01-canonical-standard-pack/evidence-verification-v3-receipt.json);
the complete artifact contains probabilities, evidence, pool identities and timings.
The exact formatted script blob `5ffcbb4b993d32a409087f33d64123c4fdbe1bcd` was applied
without changing the executed logic. Hosted focused tests 21 passed (the
exhaustive follow-up test was added on a later head). All current-head
protected checks remain separate.

| State | Complete /24 | Lexical correct | MiniLM correct | DeBERTa correct | Strict agreement correct | Proof-required correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Head | 0 | 0 | 7 | 7 | 0 | 0 |
| Expansion | 19 | 15 | 19 | 19 | 19 | 11 |
| Lexical deep | 19 | 15 | 19 | 19 | 19 | 11 |
| Neural deep | 19 | 15 | 19 | 19 | 19 | 11 |
| Rule terminal | 23 | 18 | 20 | 20 | 20 | 12 |

496 directional NLI and 141 neural reranker calls; runtime 4.2017 s after
1.3252 s initialization; peak RSS 589704 KiB. Model and artifact hashes
retained in original report. Incomplete head-only judgments are diagnostic:
both NLI models correctly resolved seven full-pair references without complete
evidence, not a basis for acceptance. Deep reranking added no complete pairs
or correct decisions. Strict NLI at terminal state had zero false equivalences,
two abstentions and two wrong relations. Requiring formal verification reduced
correct decisions from 20 to 12, withholding all eight true natural-language
equivalences; ten abstentions, zero false equivalences. On four separate
formal controls, lexical 1/4 correct and three false equivalences; lexical
plus proof 1/4 correct and three abstentions; MiniLM 0/4, DeBERTa 1/4,
finite oracle 4/4. Neither neural model correctly resolved the true formal
equivalence. Preserve these negative findings and avoid claiming population
risk or equal-compute utility. No independent review outcome.

Source-anchored conditional scope and identity audit is coordinated with the
source rule candidate on PR #180; independent family acquisition remains
with PR #188. Neither is qualified by this run.

## Evidence completeness: diagnostic and scaling follow-up

Reanalyse the verified fresh-inference report (15106112148, report SHA-256
`7a79c7734a6d202332fa1a65178a1fb4a9b14e83762041418574dd3a7eea2f7d`) without new neural scoring. Three focused
tests passed locally; initial missing-module failure and a test-fixture
aliasing failure were repaired. Reproduction:

    python -m scripts.evidence_replay_diagnostics --report /path/to/report.json --output /tmp/diagnostics.json

The [compact receipt](../../conductor/tracks/01-canonical-standard-pack/evidence-replay-diagnostics-v1.json)
pins the input, tested Git blobs and full regenerated JSON hash. Four of five
missing tail fragments are absent from the fixed shortlist. STARD-6 is at
lexical rank 4, neural rank 5. Of 48 second-pass slots, lexical repeats all
48, neural repeats 46 and adds two irrelevant fragments. Novelty-aware
selection of the top two unseen stable IDs recovers STARD-6 for both arms,
20/24 complete rather than 19/24. At four and six unseen fragments both
remain 20/24. No semantic decisions are imputed for the new state.
Earlier rank placement at initial head, top two novel: 18/24 for each
ranker, different paired cases; top four or six: 20/24 for both. These are
retrospective applications of the same full-source query and fixed ranking,
not a fresh policy evaluation.

Raw neural predictions agree 17, 22 and 23 times at head, expansion and
terminal stages; wrong shared non-abstained labels 9, 3 and 3, respectively.
Two terminal shared errors have complete evidence (stard-5, tripod-5).
Both classify the synthetic incomparable obligations as contradictory.
Keep genuine directional disagreement, incomparability, unknown evidence
and incompatibility separate. Formal verification of a representation is
not verification of that representation's source fidelity.

Next measured stages: (1) build declared/observed evidence-unit inventory
with parent, continuation, table-cell and footnote closure, exact IDs and
explicit qualifier and exception links; (2) use stable-ID novelty filtering
and document-local structural expansion before semantic reranking; (3)
measure candidate-generation recall independently from conditional rank
utility, with matched pool sizes, top-new evidence budgets and per-stage
cost; (4) compare direct NLI, bidirectional and witnessed compliance-set
tasks, candidate structured rules, and verifier-gated equivalence with
matched review workload and selective coverage, reporting correlation of
errors. Only evaluate new neural outcomes on actual acquired evidence.
Use #187 graph retrieval, #186/#189 tagging, #180 candidate applicability
and #188 independent-family/corpus intake; no new duplicate registry.
Scale deterministic coverage census first, then eligibility-filtered
development, and finally held-out family-disjoint reference evaluation.
Preserve historical E1-E21 gates and all null outcomes. No production,
source rights, admission or scientific promotion. Current-head checks pending.
