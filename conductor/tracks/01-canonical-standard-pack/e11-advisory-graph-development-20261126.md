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
