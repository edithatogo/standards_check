# E11 advisory graph retrieval — development receipt, 2026-11-26

Track 01; related #158 and specialist pipeline protocol v0.1.0. Separate experiment from E9 (#182), E10 (#186) and the easier classical-placement comparison in #185. Neither equivalence nor canonical promotion is authorized.

## Method

Author-labelled synthetic fixture, 25 targets, five headings, ten queries in five equal-sized synthetic strata, 17 positive relevance associations, complete 250-pair universe. SHA-256: `4aa25eb689a62a7b2758e19d6821f09708563a0d0c627c91b102cd84a3ca066d`. All six explicit cross-reference/dependency edges originate in literal anchored target text; 25 parent edges. No edges use query reference labels. Authored labels, synthetic headings and target wording are not independent source evidence. No related guideline editions or source extracts have been added.

Existing costing_retrieval lexical_rankings, rank and evaluate, existing lexical_text TF-IDF/cosine. Word and character arms preserve the incumbent positive-only ordering and candidate universe. The challenger adds 0.35 times the maximum of parent-heading cosine, 0.8 times explicit cross-reference destination lexical score, or 0.6 times dependency destination lexical score. Heading cosine uses a separate query-heading corpus; existing lexical scores remain unchanged. This is a fixed heuristic, not trained graph inference. One-hop directed links, no closure and no automatic equivalence. The receipt retains complete per-query scores, paired top-five positive gains/losses, family/stratum results and all edges. Zero scores are not artificially promoted to fill ranks.

## Local execution

Python 3.13.5 isolated overlay of the exact relevant incumbent ranking/evaluation functions and lexical helper from main d88f787ffd4647117bca4ca400cbb68d95197d40. Eight tests pass; 98% module branch-inclusive coverage. Initial red import test before implementation. One observed run:

| Method | Macro query recall@5 lexical | Graph | Positive associations gained / lost |
| --- | ---: | ---: | ---: |
| Word | 0.90 | 1.00 | 2 / 0 |
| Character | 0.90 | 0.95 | 1 / 0 |

Equal two queries per stratum means macro-stratum recall equals macro-query recall on this fixture. Word gained Q4/B5 and Q7/D3; character gained Q7/D2. Micro recall was 15/17 for both lexical arms, 17/17 and 16/17 respectively for graph arms. Process wall 0.66 s and peak RSS 96,264 KiB across both methods/arms, not separately isolated. Measured lexical/incremental graph time ~1.28/0.48 ms word, ~2.64/0.89 ms character, single observation; not a meaningful speed benchmark. No model weights or new dependencies downloaded. Hosted workflow pins Python 3.12.16 and retains complete receipts; hosted exact-head status pending at commit.

## Next gate

Do not generalize effect size or tune on this fixture and call it confirmatory. Need independently adjudicated rights-cleared family-component splits, full eligible candidate universe, non-ceiling baselines, and edge-type ablations (parent-only, cross-reference-only, dependency-only and shuffled-edge control). Record losses, uncertainty at family level, precision burden, and separate reader/qualifier error sensitivity. Retain existing source intake holds and human or other independently supported equivalence evidence.


## Hosted replay and edge-type ablation follow-up

Prior exact-head run [45795402697](https://github.com/edithatogo/standards_check/actions/runs/45795402697) passed; checked merge revision 7c48bc6f1c71ddd953808c35ce95d2d314004610. [Artifact 15103968915](https://github.com/edithatogo/standards_check/actions/runs/45795402697/artifacts/15103968915) downloaded and independently checked SHA-256 f3f106a3b8855eaf8d464fe638a15476327ee9d94411c445e52e3768fff05df2. Reproduced word 0.90→1.00, character 0.90→0.95 and exact paired gains, no losses. Assurance failed Ruff formatting; formatted original script and checked exact Python AST equality. No change to original graph scorer or fixture.

Retrospective all 2^3 edge combinations; same original weights, no fit. Twenty fixed seeds (0–19) permute destinations separately by type, preserve source and destination degree counts, forbid self-edges and require a nonidentity permutation per nonempty type. Rewired records explicitly control-only, never source evidence. All ranked candidates, scores, rewired endpoints, positive gains/losses and seven inclusion-exclusion contrasts per method retained. Fixed positive-only ranking, same 250 eligible pairs. Local Python 3.13.5 overlay: RED missing graph_ablation; GREEN 13 tests pass; 98% branch-inclusive coverage across two graph modules; script blob hashes e2f488bb952748746a88a23a9148033cea70e32a and 33d901fc18c734a967f28c550c8bba05ef70aa31. Initial ablation process 0.87 s and peak RSS 101264 KiB, no model weights. Hosted replay and original full suite required.

| Arm | Word macro R@5 | Char macro R@5 |
| --- | ---: | ---: |
| None | .90 | .90 |
| Parent | 1.00 | .95 |
| Cross-reference | .95 | .90 |
| Dependency | .90 | .90 |
| Parent + cross-reference | 1.00 | .95 |
| Parent + dependency | 1.00 | .95 |
| Cross-reference + dependency | .95 | .90 |
| Full graph | 1.00 | .95 |
| Rewired control mean (min–max) | .8342 (.7167–.95) | .85 (.70–1.00) |

Parent-only equals full-graph gain. Word parent×cross-reference inclusion-exclusion contrast -0.05; all other higher-order contrasts zero. This is a conditional descriptive contrast, not a population interaction or a test of independent component effects. Full-graph precision@5 .34/.32 versus .30/.30. Random graph can occasionally equal or exceed observed performance; do not interpret as significance. No independent families or confirmed graph benefits. Preserve original artifact and require real-family and independent source reference qualification.
