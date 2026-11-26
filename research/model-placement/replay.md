# Model-placement replay — 26 November 2026

Development only; tracks T01.063–064 and T05.063, issue #158. Starting main d88f787ffd4647117bca4ca400cbb68d95197d40. PRs #180/#181 are orthogonal; no conflict resolution or normative changes attempted. Existing E9–E14, E1–E21 and rights/reference gates unchanged.

## Reproduce

Obtain GitHub Actions artifacts 15087556116, 15091873096, 15088716936 and 15091588651 from runs 45754736904, 45765197238, 45757790945 and 45765203487 respectively, named github-actions-artifact-ID.zip. Replay fails closed on exact ZIP hash mismatch. Run:

```sh
cd research/model-placement
python -m pytest -q test_replay.py
python replay.py --artifacts /path/to/artifacts --output replay-receipt.json
```

Uses original 36 analyst-labelled synthetic relation cases (12 dev, 24 test, grouped by family); 106 costing queries, 31 domains, 125 editorial positive associations. No reference labels to models; no new neural inference. Reuses retained per-case predictions, probabilities, scores, rankings and exact input identities. Costing instrument partitions are descriptive, not independently held out. Rules fixed for this replay before computation, not prospective study freeze.

## Executed observations

Python 3.13.5 Linux x86_64; RED missing module then 2 focused tests passed. Local replay wall 0.028796 s; process peak RSS 99,212 KiB; model downloads 0 B. Historical inference cost is not replay cost. Full generated receipt SHA-256 14ec54bfaef3518098346db53e5732248daeea6998e509347089ad717e6d1682 (includes nondeterministic timing/RSS); stable row content regenerated from pinned artifacts. Script Git blob f86126afd6cb2ce8372b826dea380348ff5bdab4.

| Held-out decision arm | Correct /24 | Abstain | False equivalence | Gains/losses vs d1 direct |
| --- | ---: | ---: | ---: | ---: |
| MiniLM | 20 | 0 | 0 | 10/1 |
| DeBERTa | 20 | 1 | 0 | 10/1 |
| d1 direct | 11 | 12 | 0 | 0/0 |
| directional | 8 | 16 | 0 | 5/8 |
| witness | 2 | 22 | 0 | 2/11 |
| four-view strict | 0 | 24 | 0 | 0/11 |
| fixed router | 11 | 12 | 0 | 0/0 |
| difficulty entropy router | 11 | 12 | 0 | 0/0 |
| uncertainty/disagreement router | 11 | 12 | 0 | 0/0 |

Routing comparison: 3 extra swapped-view requests per six-case family; actual replay uses cached model outputs, equal request-count proxy not measured equal FLOPs/time. No gain. d1 four-view historical run 45765197238 completed, peak 1,930,852 KiB; strict all-36 abstention retained. Original run 45754736904 overall failed; verified d1 artifact retained separately.

| Costing arm | Macro R@5 | Positive associations @5 | Gains/losses |
| --- | ---: | ---: | ---: |
| BGE | 72.01% | 87 | — |
| lexical+dense RRF | 69.34% | 82 | 6/11 vs BGE |
| MiniLM on BGE pool | 68.24% | 82 | 4/9 |
| Qwen 0.6B domain-index on BGE pool | 66.51% | 79 | 5/13 |
| lexical reranker on BGE pool | 65.09% | 78 | 5/14 |
| lexical reranker on RRF pool | 56.13% | 67 | 2/17 vs RRF |

Same fixed candidate pool within each comparison, 1,060 candidates. Fresh neural reranking on the fused shortlist is still outstanding; lexical fallback is not a neural comparison. Qwen 4B run 45763122344 cancelled, smoke test only (artifact 15091704770; ZIP SHA-256 082f73fe414927f9517c372daeee49c9c6a541f4c13cb1107dc178b51616745a); no fabricated result. Qwen 0.6B run 45765203487 completed: 304.859 s, peak 1,438,376 KiB; original BGE/MiniLM run 45757790945 passed, 2.73 s process and 257,152 KiB peak, distinct hardware/time not controlled.

| Evidence-evaluator placement | Candidate budget | Associations recovered | Missing |
| --- | ---: | ---: | ---: |
| BGE first five | 530 | 87 | 38 |
| fixed second pass | 790 | 92 | 33 |
| score-triggered BGE continuation | 790 | 92 | 33 |
| score-triggered RRF second pass | 790 | 94 | 31 |
| score abstention (0.05) | 370 | 63 | 62 |

52 second passes at equal per-instrument allocation; low max retained Qwen score on the first five triggers expansion. Abstention withholds 32 queries and loses 24 known associations. No independent negative labels; unsupported decisions cannot be assessed from costing seed. No promotion. Candidate budget excludes prior cached scoring and is not equal fresh inference cost.

## Next

Use existing LocalRanker and pinned BGE/MiniLM assets for both fixed top-ten pools, isolate per-arm time/peak RSS and download bytes, and qualify fresh inference with exact-head tests before opt-in. Evaluate routing against a genuinely orthogonal model at equal measured compute, and evidence sufficiency with an independent reference, not relevance scores. Preserve the observed negative arms. No model downloads in routine CI.


## Fixed-pool neural reranking follow-up (26 November)

Prospective development amendment, before any new inference: equal-weight RRF k=60, same query text, exact 10 candidates per pool, same pinned MiniLM reranker, tie break stable ID. Compare each pool's original ordering against neural reranking of precisely that pool; retain all 1,060 raw finite scores per arm and paired gains/losses, per-instrument results, per-process RSS/time and exact model asset bytes. Reuse the existing hash-pinned BGE/MiniLM workflow and LocalRanker; fail closed on changed input digest, BGE pool digest, lexical order, reference or candidate mismatch. Label run-fixed-pool-rerank only after required exact-head deterministic/security checks pass. Existing ordinary/label workflows otherwise unchanged; no hosted model API.

Local RED import failure followed by GREEN 2 focused tests. Tested pure pool preparation against original archived paired.json (artifact 15088716936): 106 queries, 31 domains, 1,060 candidates in each arm; all 106 pool memberships differ, 347 slots replaced, 713 overlap. Both top-ten pools recover 97/125 known associations; top five 87 vs 82 before reranking. The new scorer was exercised only with injected finite/nonfinite test scores; fresh ONNX inference has NOT run. Local git DNS failed; onnxruntime and tokenizers absent; the hosted opt-in execution is the next gate. Do not reuse cached neural scores for new candidates or claim a comparison of fresh inference until the exact artifact is verified.

The separately hosted E9 run 45787042673 (artifact 15100692740; independently verified ZIP digest f7155c826e7e9e601855f8e54e38220e185c05f622429e029205fb7e7261d7a6) supports native geometry qualification first: exact rows 1/4 vs 4/4, nested 1/1, footnote 1/1, qualifier links 2/2 both; Poppler 24.02.0 vs pdfplumber 0.11.11. Both synthetic, no independent qualification.


## Evidence escalation: stronger equal-budget baseline (26 November)

Replay the same pinned historical artifacts with fixed, low-max relevance,
small-gap and lexical/dense disagreement priority; allocate within each
instrument at 25/50/75/100% (floor), preserving all first-five BGE candidates,
appending five unseen fused candidates. In each cell compare exactly the same
expansion budget against 1,000 deterministic uniform allocation seeds and the
exact expected random gain. No evaluation labels used for selection; no new
model calls. Cached relevance scores not calibrated probabilities. No fresh
compute-cost comparison or independently established negatives.

```sh
cd research/model-placement
python -m pytest -q test_evidence_budget.py
python evidence_budget.py --artifacts /path/to/artifacts --output evidence-budget-receipt.json
```

RED missing module, GREEN two focused tests passed. Actual wall 0.184488 s,
98,700 KiB peak RSS, 0 model bytes downloaded. Receipt SHA-256
c936723751d97784e8210c6caed0de18a31ab7c97dde769f755069eebf093918
(resource observations variable). Initial 87/125 known associations; all
expansions append rather than replace, so losses are zero.

| Budget | Candidates | Fixed gain | Low max gain | Small gap gain | Lexical disagreement gain | Random expected gain | Random 95% empirical range |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 25% | 655 | 3 | 5 | 5 | 2 | 2.82 | 0–6 |
| 50% | 790 | 5 | 7 | 6 | 3 | 5.97 | 3–9 |
| 75% | 920 | 10 | 9 | 8 | 5 | 8.79 | 6–11 |
| 100% | 1060 | 12 | 12 | 12 | 12 | 12 | 12–12 |

At 50%, 359/1000 random draws achieved at least the low-max gain. At 75%,
fixed outperformed low-max; all observed low-max gains lie in the empirical
random range. This is a negative robustness finding, not a statistical
significance test or a calibration study. No score-trigger adoption; keep
random and deterministic policies as comparators and require independent
references and matched fresh inference costs before selection. Retain every
selected ID and instrument-level gain; do not relabel unlisted associations
as unsupported decisions.


## Non-ceiling graph comparison (26 November)

Main's costing registry has domain definitions and ontology modelling rules, not
independently qualified domain edges. Do not invent source hierarchy. Instead use
a label-free co-retrieval graph from the original BGE rankings: top-five
co-occurrence counts on the other instruments only, row-normalized, isolated
vertices self-looped. Leave one instrument out, no reference labels in graph
construction or propagation. Seed reciprocal BGE rank, restart 0.7, transition
0.3. Compare one step and eight steps, both full-universe candidate generation
and fixed original top-ten reranking. Parameters fixed for this exploratory run,
no tuning on held-out labels. These are statistical graph placements, not a GNN
or source ontology; instrument separation does not establish guideline-family
independence.

```sh
cd research/model-placement
python -m pytest -q test_graph_replay.py
python graph_replay.py --artifacts /path/to/artifacts --output graph-receipt.json
```

RED missing module then GREEN two focused tests. Executed actual graph replay
wall 0.137138 s, peak 98,576 KiB, zero model downloads. Receipt SHA-256
08882913613afd30d9f13a7312bc4d4c24304a82cd08849e6c589ef3d45bd151
(variable resource observation); includes graph adjacency, scores, full
per-instrument paired observations. MRR evaluated at ten.

| Method | Macro query R@5 | Known hits @5 | Gain/loss at 5 vs BGE | Known hits @10 |
| --- | ---: | ---: | ---: | ---: |
| BGE top ten | 72.01% | 87 | 0/0 | 97 |
| One-hop generation | 66.35% | 81 | 1/7 | 97 |
| Diffusion generation | 66.82% | 82 | 1/6 | 97 |
| One-hop fixed-pool rerank | 66.35% | 81 | 1/7 | 97 |
| Diffusion fixed-pool rerank | 66.82% | 82 | 1/6 | 97 |

A real non-ceiling negative result for this co-retrieval graph and both
placements. Diffusion does not outperform the original BGE incumbent, although
one known association is newly recovered at five. Not evidence against
source-anchored hierarchy/cross-reference/dependency edges, which remain a
separate qualified-graph prerequisite. No model adoption or semantic admission.


## Fresh fixed-pool neural reranking — observed hosted result

Run [45796791489](https://github.com/edithatogo/standards_check/actions/runs/45796791489)
completed successfully on exact PR head 27b94938ff28ee8012ed768e8285cf708d28d8d7
and checked merge revision 971a59e92dba04c95978cd202f524433fe66c211.
[Artifact 15105542356](https://github.com/edithatogo/standards_check/actions/runs/45796791489/artifacts/15105542356)
ZIP SHA-256 verified:
1d8fefd7f760444e0df99b733d050bc7ecc386a377b060b2cfc136c5613247b3.
Member digests (SHA-256): paired.json
4f2b0c97a95154cb55724988a9f483a1aecdae6621b1d2e8446a4b619d271966;
fixed-bge.json ed860392e19c0fd778eb82d9b61e8bc7a65626e7a994f224e62c229b17151b72;
fixed-fused.json c557b2a38c8de8046384d32cfc2bf936a0914de246fa5f9e65e9dd3ca8e929bc.
Independently recomputed score-to-candidate bindings, stable ordering,
exact reference identity and paired gains/losses at 1/3/5/10 for every query.
Both arms scored 1060 candidates; 713 shared scores match exactly, with
maximum absolute difference zero. All 347 new fused candidates were actually
scored; no cached-value substitution. Input pins and BGE pool pin match.
Fused ordered pool digest:
ce074af0f704d0b91855b61b0394a47bf1badc6a1fb4537a3627ba3cc207a806.
Weights 23,200,716 bytes; reranker assets 23,916,695 bytes including tokenizer,
config and model card. Same pinned MiniLM revision and ONNX Runtime 1.23.2,
two CPU threads; observed load/score seconds 0.1964/1.5506 vs 0.1880/1.5488;
total process wall 1.82/1.81 seconds and peak RSS 114912/114928 KiB.
Both exited zero; GPU discovery warning did not prevent CPU execution.

| Arm | Macro R@1 | R@3 | R@5 | R@10 | MRR@10 | Hits@5 | Gain/loss@5 vs own pool |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BGE top ten | .34434 | .58962 | .72013 | .80031 | .54124 | 87 | — |
| BGE plus MiniLM | .40094 | .62736 | .68239 | .80031 | .57700 | 82 | 4/9 |
| RRF top ten | .36321 | .61321 | .69340 | .79717 | .54565 | 82 | — |
| RRF plus MiniLM | .40094 | .63208 | .67453 | .79717 | .57117 | 81 | 7/8 |

R@1 gain/loss BGE 17/11, RRF 13/8; at three 7/4 and 11/8; at ten
0/0 by construction. Top-five recall fell in both arms. Keep BGE candidate
discovery; reranker may be an advisory review-ordering comparator, not a
completeness gate or reason to truncate. MRR at ten is not full-universe MRR.
Five instrument partitions are descriptive; known associations are editorial
positives, not independently adjudicated relevance. No model promotion.

Receiving main 08e86696180936ef6722e539a32d6ebbd2222625 contains #182.
Merge that main into this branch while preserving all prior experimental files,
both Track 01 plan additions and the actual earlier run identity. New exact-head
checks are required; offline AI security at the original head remained queued.
Independent source/reference/family freeze and scientific gates remain open.


## Shared missed-match coordination and bounded audit — 26 November

This is the single shared attribution receipt for #158, T01.064 and T05.063
on the existing #183/#185 lane. It is an experimental exchange convention,
not a new canonical schema, publication registry or acceptance decision.
Preserve the existing owners: Layout (#182/#186/#187/#188/#189) owns
source extraction, span and structural retrieval, and independent family intake;
Offline (#184) owns evidence acquisition/replay and action outcomes;
Orthogonal owns definition/applicability/directional verification; Complete PR
Work owns existing model/task-framing receipts. The coordinator joins their
immutable outputs and owns recall accounting, not their branches. #185's
heading-context control and #183's MiniLM negative result remain separate
observations, not new executions of their owners' workloads.

### Minimal exchange receipt for independently labelled positives

One row per locked positive reference ID and evaluated arm. Use a stable
opaque ID (bound to the query/item and target ID by the private reference
ledger), never text or model-derived labels as join keys. Receipt metadata:
dataset/version, reference tier (independently adjudicated / model-relative /
editorial / synthetic), exact reference-lock digest, component/split IDs,
eligible candidate universe digest, exact code/model/data/run and artifact
pins, arm, candidate and review budgets, and owner/receipt references.
Per-positive fields: case ID; expected source and target anchor references
or hashes; observed anchor identity and fidelity status; original pool and
review rank or null; stage states; decision outcome/reason (including
abstention, rejection, unsupported, referral and observed resolution);
per-stage evidence receipt identifiers. Do not expose restricted text.
Explicit stage states: pass, fail, unknown (not measured/insufficient
reference), not_reached (upstream exclusion demonstrated). Stages in order:
source_anchor (including missing items, nested block or qualifier loss);
candidate_generation (missing from the allowed pool); rank_cutoff (present
in pool but excluded from the fixed review budget); evidence (insufficient
or incorrect source-bound evidence); decision (wrong relation, unresolved
abstention/referral). Only call a rank-cutoff loss a *reranker-induced loss*
if the same candidate pool and baseline review set contained the positive.
Retain all gains, losses, and abstentions; referral alone is not resolution.

Report first_observed and first_established separately: the earliest
observed failing stage is not a causal/end-to-end attribution when an
earlier stage is unknown. A first_established stage requires all earlier
stages to pass. None_observed is not success; independent end-to-end
success requires all stages to pass. Count both-failed overlap alongside
both-observed denominator for every stage pair; for arm pairs count shared
and arm-specific misses on identical locked IDs and at both pool and review
cutoffs. Do not impute downstream failures or zeros when unobserved.
If independent counterfactual full-pool evidence is available, retain its
separate budget and run IDs. Inference/reference separation: Layout/curators
lock source-only adjudication by separate independent contexts, with all
related editions/derivatives in the same component. Model runners receive
only opaque cases, text and admissible anchors, never positive IDs/labels
or earlier model results for adjudication. Coordinator joins only after
runs are locked. No claim of human adjudication without actual humans.

### Executed editorial diagnostic (not independent or confirmatory)

Three retained ZIPs independently SHA-256 checked: BGE 15088716936,
instructed Qwen fusion 15090704998, two-pool MiniLM 15105542356. Exact pins
in recall_audit.py. Same 106 queries, 31 domains, 125 known editorial
positive covers_topic associations; exact query/target/reference and
MiniLM candidate pool identity checked. No independently adjudicated
positives available; unlisted associations are not known negatives.
Same 10 candidate slots and 5 review opportunities/query (1,060 and 530),
not matched neural compute or observed review workload. Full rankings
are separate from pool recall. No new neural downloads or inference.
Plain lexical challenger: exact contiguous normalized query phrase in
definition, then equal word/char RRF60, stable ID tie break. Parent-topic
proxy uses nearest existing same-instrument dotted ID prefix for 24
queries, prepending its short topic to the lexical query; not an
independently verified source heading or clause. No labels or target
IDs as lexical text. Stable zero-signal fill is explicitly counted
(14 plain, 7 parent-proxy pool slots), not evidence of relevance.
Local text projection copied from current repository's original editorial
topic/definition metadata; exact retained word and char ranks reproduce
for every query. Full checkout mode verifies source-file SHA-256 pins.
No new reference registry or original-source disclosure.

| Arm | Macro R@1 | R@3 | R@5 | Pool R@10 | Hits@5/125 | Pool hits/125 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BGE | .34434 | .58962 | .72013 | .80031 | 87 | 97 |
| Instructed Qwen+BGE | .39623 | .66509 | .76258 | .85692 | 93 | 104 |
| BGE MiniLM | .40094 | .62736 | .68239 | .80031 | 82 | 97 |
| Exact phrase + lexical | .32075 | .47642 | .52830 | .68868 | 63 | 81 |
| Parent-topic proxy + exact/lexical | .37264 | .51887 | .55660 | .65094 | 66 | 77 |

All-31 enumeration: 125/125 known associations, 3,286 candidate inspections;
label-aware ranking oracle at 10/5: 125/125, R@1 .9135, R@3/5 1.0.
The oracle uses known reference IDs only after evaluation, not operational
inference, actual reviewer success or an equal-cost all-31 decision run.

| Arm | Pool miss | In pool, outside review | No observed retrieval failure |
| --- | ---: | ---: | ---: |
| BGE | 28 | 10 | 87 |
| Instructed Qwen+BGE | 21 | 11 | 93 |
| BGE MiniLM | 28 | 15 | 82 |
| Exact phrase + lexical | 44 | 18 | 63 |
| Parent-topic proxy | 48 | 11 | 66 |

Source/anchor, evidence and decision unknown for all 125 in each arm;
first-established end-to-end attribution unresolved for all 125.
Within-arm source/evidence/decision overlap denominators zero; do not
interpret zero observed overlap as no failure. Pool/rank stages are
sequential, so pool misses have rank not_reached. BGE vs instructed-Qwen
fusion pool misses: 18 shared, 10 BGE-only, 3 fusion-only; review misses
30 shared, 8 BGE-only, 2 fusion-only. MiniLM same BGE pool loses nine
review positives and gains four; 34 shared review misses. Exact/lexical
vs Qwen fusion review misses: 27 shared, 35 lexical-only, 5 fusion-only.
Parent proxy vs Qwen fusion: 25 shared, 34 proxy-only, 7 fusion-only.
Full per-positive stage rows, instrument strata, pairwise overlaps,
candidate ranks and all full rankings generated by the audit. Instrument
strata are not independent guideline components. Keep false-equivalence
and decision recall unestimated on this positive-only editorial audit.

Three focused tests: initial RED missing module, GREEN 3 passed. Local
Python 3.13.5; wall .117809 s, peak RSS 101516 KiB. Script/test Git blobs
35155c2a85fa396d045eb9a1606f840e4512ffdb and
3ee57e049b09f1a649b08a40f5246a3d11aeec8d match locally executed sources.
Projection SHA-256 8c35d63b307ffbb152490c912eb69e9a5830a2585dc38882ec4188a5a5468c48;
generated receipt SHA-256 ad370b7cc7966b0beaaef2e7005c4bb155aec1fb2ea56a531132761e17532f23
(includes variable runtime fields). Reproduce from repository root with
the three exact GitHub artifact ZIPs (filenames github-actions-artifact-ID.zip):

```sh
PYTHONPATH=. python -m pytest -q research/model-placement/test_recall_audit.py
PYTHONPATH=. python research/model-placement/recall_audit.py --artifacts /path/to/artifacts --inputs . --output recall-audit.json
```

Full-file checkout path remains to be exercised on hosted checkout; the
local run used --projection-only with the rank-equivalence check.
Do not use --projection-only for confirmation.

### Dependency and disposition

The latest Layout source-intake run 45797664414 completed; verified ZIP
15106576904 SHA-256
4133e229f7b6965e17690e063ebecd745ed96671b1fd8ce8247acedd2455a846.
All five attempted editions held (PLOS OSError, Europe PMC TimeoutError,
PMC OAI unavailable/held); zero newly qualified independent families or
new canonical packs. Layout owns retries and source/anchor/reference
qualification; do not duplicate. Next handoff is a frozen family-component
source/anchor and independently adjudicated positive ledger, with full
candidate references (or prespecified sampling weights). Then join
Offline evidence sufficiency/resolution and Orthogonal applicability/
direction outcomes against the same opaque IDs; Complete PR Work supplies
existing model/framing pins. No cross-dataset pseudo-join, no production
change, no new registry or release. #185's actual heading text synthetic
control is retained (1.00/1.00 word/char R@5, fixed-pool 1.00/.95), not
pooled with costing. Instructed Qwen+BGE is the strongest observed
candidate-generation comparator here, not an adoption claim; focus on
pool misses and common misses before further ranking experiments.


## Shared audit handoffs — imported actual stage evidence

Receiving main 776ed1dbfbe19d16365310ef0fa07d29a793611a includes #187 (source-anchored graph and factorial);
its changed paths do not overlap this lane. Keep the other writers and their
actual execution revisions. The sole shared research receipt convention is
the preceding section and [row/ID constructor](recall_handoff.py) here;
no new production or publication schema or case registry. The full stable
case ID is SHA-256 of compact sorted-key UTF-8 JSON array
[namespace, reference digest, original local identity]; arm is excluded.
Preserve original IDs/anchors and exact receipt references. Reference tier
and namespace must stay attached; stage states not observed remain unknown.
Positive units are separate: editorial associations, layout facts, typed spans,
relevance associations and equivalent pairs. Summaries are per namespace/arm,
not pooled across the 175 distinct IDs.

Executed import of exact original costing audit plus Layout handoff
[#158 comment 7189323646](https://github.com/edithatogo/standards_check/issues/158#issuecomment-7189323646),
Orthogonal [7189300653](https://github.com/edithatogo/standards_check/issues/158#issuecomment-7189300653)
and Offline #184. Artifact pins in recall_handoff.py: E9 15100692740,
E10 15105999587, E11 15105947458, Offline 15106112148 and intake
15106576904; all independently verified. #185's local heading receipt
is consumed without rerunning its benchmark (optional input, exact pin).
No model calls or new labels. Six focused tests passed (three new after
initial missing-module RED, three previous). Actual local import:
1,254 arm-specific rows, 175 distinct reference IDs, nine separate
unexecuted control proposals, five source-acquisition holds, zero
independent positives. Local wall 1.00 s, RSS 108436 KiB; no model
downloads. Receipt SHA-256
6dda611871f462f1c2cf24282769e9185dd2a891304508a6b8c5f839a328be69.
Source and test blob hashes 44ba9f73ee4d2b3f7c22bd567de6b27b0932f00c and
21871181e586cc601e175e64923d8361de3ab520 match locally executed files.

| Namespace (separate denominator) | Observed result |
| --- | --- |
| E9, 8 structural facts including 4 rows | pdfplumber 3 content-corrupted rows, Poppler 0; all 4 other facts preserved; manual region anchors distinct from observed line locators |
| E10, 17 spans | rule / GLiNER / clause-names / operator-first exact misses 3 / 16 / 15 / 17; no learned unique exact hit; invalid-output abstentions zero |
| E11, 17 relevance associations | original word pool misses 0, review misses 2; char pool misses 1, further review miss 1; heading generation 0 misses for both; char fixed pool still misses 1 |
| E12 Offline, 8 equivalent synthetic pairs | head-only: evidence incomplete and strict NLI abstained on all 8 (both-failed overlap 8/8); expanded/terminal: bundle complete, strict NLI 8/8, proof-required abstained on all 8; zero actual review resolutions |

E12 uses complete as *synthetic evidence-bundle* completeness only, not
independent source/evidence sufficiency or proof. Unsupported proof is a
withheld positive relative to these labels, not known rejection or error
in safe policy. No fragment-rank-to-pair-rank substitution. The original
24-case five-class and separate formal controls remain in #184, not pooled
with the positive-only eight-pair subset. Source and pair shortlist/rank
unobserved, so first-established end-to-end attribution remains unresolved.
E9/E10 exact fact/span observations are not end-to-end pair success.
All five source-intake failures remain source-availability holds, not
extraction false negatives. No independent-reference freeze.

### Common misses (costing editorial diagnostic)

For 18 shared BGE/Qwen-fusion top-ten pool misses, use the already
retained full rankings, not a new model run. Ten have best dense rank
11–15; eight remain outside 15 for both. Three recoverable by each of
the plain and parent-topic lexical comparators at ten, four in their
union. Seven AGREE-DT, four CHEERS, two CHEERS-VOI, three GHCC and
two iDSI. Four diagnostic-pathway, three results-disaggregation and
two price-provenance associations; others are dispersed. Retain all
original IDs/full ranks in the handoff result. These are hypothesis
generators, not independently verified errors or a valid oracle-driven
operational allocation. Any deeper or hybrid pool trial must use a
predeclared label-blind policy across all queries at equal budget;
Offline owns evidence acquisition policy. Do not tune on these misses.

### Orthogonal ID allocation (proposals, not observed positives)

Use namespace PRISMA-proposed and source pack Git blob
318b0786e195ee9b6ccb5b0a39ade117ce3c6a2c at prior main 08e86696.
Retain the source parent anchor(s) exactly; proposed subclause/bundle
interpretations remain noncanonical. ID prefixes for orientation only
(full 64-character IDs in receipt):

| Original scenario key | Prefix |
| --- | --- |
| methods-results | 5baad1e93283 |
| automation-scope | f9637eda7595 |
| parent-child | a98c844046ba |
| complete-bundle | 82b3010298fe |
| sought-collected | 7f9cfb7b12c4 |
| registration-protocol | 94e9d9e041b3 |
| analysis-level | 48abd3044269 |
| heterogeneity-sensitivity | a19765da93b7 |
| source-only-evidence | 9291e39f2ad5 |

Proposals are development scenarios, not independently labelled positives.
No automatic conversion of the nine into observed failures, no new
registry or experiment ID. Orthogonal retains actual definition/directional
verification; Offline retains proof/evidence-bundle outcomes. Future
independent label lock must precede model runs; do not share reference IDs
or gold relations with model inference. For one-to-many positives, bind
one reference obligation to its required bundle (all applicable components),
preserve child IDs and separate directional scope; no duplicate credit.

Reproduce with existing three costing ZIPs and five newly joined ZIPs:
```sh
PYTHONPATH=. python -m pytest -q research/model-placement/test_recall_audit.py research/model-placement/test_recall_handoff.py
PYTHONPATH=. python research/model-placement/recall_audit.py --artifacts /path/to/artifacts --inputs . --output recall-audit.json
PYTHONPATH=. python research/model-placement/recall_handoff.py --artifacts /path/to/artifacts --audit recall-audit.json --heading /path/to/graph-context-receipt.json --output handoff.json
```

Added read-only opt-in label run-shared-recall-audit to the existing
five-class workflow: exact receiving checkout, test first, read-only
Actions token downloads fixed public synthetic/editorial ZIPs, all hashes
checked by the existing audit and handoff. Full source-file pins required;
no projection-only hosted path. Optional locally retained #185 heading
receipt is explicitly absent in hosted run rather than rerun or substituted.
No model inference or production dependencies. Actual full-checkout run
and new exact-head checks remain required. Dedicated offline security
runner remains a separate gate; no bypass.
