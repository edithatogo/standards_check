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
