# Synthetic compact-model placement — 26 November 2026

Development-only author-labelled controls; issue #158, T01.025/063–064 and T05.063; complementary to PR #182 (Poppler, existing grid fixture) and PR #183 (retained inference replay). Exact starting main d88f787ffd4647117bca4ca400cbb68d95197d40. No source rights, pack, equivalence, independent calibration or release gate changes.

## Reproduce

In a separate research environment, not production dependency installation: Python 3.13.5, Linux x86_64, scikit-learn 1.8.0, numpy 2.3.5, PyMuPDF 1.26.7, pdfplumber 0.11.9, reportlab 4.4.9, pytest 9.0.2. Record full dependency lock and licences before hosted promotion. PyMuPDF licensing requires separate review before any deployment. No downloaded model weights or external inference. This is not the maintained repository pdfplumber version 0.11.11.

```sh
cd research/model-placement
python -m pytest -q test_synthetic.py
python synthetic.py --output /path/to/run
```

Local RED (missing module), GREEN 2 focused tests passed; full executed synthetic receipt and rendered first page generated. Exact script blob fadc890b21125909caa8f48019e3f159ce7140b9, script SHA256 daf852956be1fbef1d62549e260eb7f4b7c4eda41f2ccd38a5e989cf3d35cbfd; generated PDF SHA256 02ff1c437ab1b0cd034cae94b71463a5f49bdf664e12777cd56969765e69fcca; receipt SHA256 4e91d4648d50b843000c23838494479a4b176f6898c94b86ace0e72c41743bf5 (includes variable resource observations). Linux process wall 0.755539 s, peak RSS 207516 KiB, model download 0 B. Not per-arm resource isolation. All predictions, region boxes, span offsets, family partitions, reference and candidate identities retained by the executable receipt. No third-party guideline wording.

## Design and results

Six family-labelled synthetic controls, not independent guideline families. PRISMA/CHEERS development, CONSORT/STARD/ARRIVE/TRIPOD held out; exact actor/condition/exception offsets and source row/footnote references authored before the run. Small templates share structure; no claim of natural generalization. Linear classifiers and eight-dimensional LSA fit only on development families. Graph is section membership and adjacent synthetic dependencies, not validated guideline graph. Lexical comparator in this new fixture is development-fitted char TF-IDF, not live BGE. Historical five-class and BGE comparisons are in #183.

| Layout reader/placement | Exact nested-ID rows | Footnotes | linked row/qualifier |
| --- | ---: | ---: | ---: |
| pdfplumber whole-page text | 0/36 | 36/36 | 0/36 |
| PyMuPDF whole-page sorted | 0/36 | 36/36 | 0/36 |
| PyMuPDF detected rectangle crops | 36/36 | 36/36 | 36/36 |

Known drawn boxes, both columns and explicit synthetic footnote identifiers. This is a bounded geometry control, not scan/OCR, parent hierarchy reconstruction, TEDS, or real issuer qualification. Cross-replay #182 grids and real rights-cleared independent region references before adoption.

| Exact held-out span | Rules TP/FP/FN | Linear tagger TP/FP/FN |
| --- | --- | --- |
| actor | 48/0/0 | 42/0/6 |
| condition | 24/0/24 | 25/9/23 |
| exception | 40/0/8 | 48/0/0 |

Rule F1 100.0/66.7/90.9%; model 93.3/61.0/100.0%. No wholesale replacement; exceptions are a candidate supplemental signal. Tagging enriches retrieval and supplies typed evidence verification. Separate tag-free vs tagged pair classifier ablation and independently annotated natural spans still outstanding.

| Held-out retrieval | Hit@1 /24 | Hit@3 /24 | Candidates |
| --- | ---: | ---: | ---: |
| lexical | 24 | 24 | 72 |
| tag enrichment | 24 | 24 | 72 |
| graph simple | 23 | 24 | 72 |
| graph diffusion | 24 | 24 | 72 |
| graph simple rerank | 23 | 24 | 72 |
| graph-feature rerank | 24 | 24 | 72 |
| dense LSA | 23 | 24 | 72 |
| lexical+dense RRF | 23 | 24 | 72 |
| learned reranker lexical pool | 24 | 24 | 72 |
| learned reranker fused pool | 24 | 24 | 72 |
| combination tag+graph | 24 | 24 | 72 |

The perfect baseline creates a ceiling; no demonstrated incremental retrieval benefit. Fixed pool checks for reranking. The learned ranker and atom classifiers are binary synthetic feasibility controls, not substitutes for five-class NLI. Direct equivalent decision: 21/24 TP, 0/120 FP, 3 FN; separate actor/condition/exception/action judgments compiled by conjunction: 7 TP, 0 FP, 17 FN. No evidence for hard atom agreement. Second retrieval: first one 24/24 correct; both fixed and score-triggered extra candidate allocations 24/24 at 48 candidates, no gain. Score abstention 21/24, 3 withheld, no unsupported top-one accepted on this easy fixture.

| Verifier placement | Valid accepted | Invalid accepted | Valid withheld |
| --- | ---: | ---: | ---: |
| exact claim anchor | 144/144 | 144/288 | 0 |
| exact+typed span role | 115/144 | 0/288 | 29 |
| relationship+exact cited anchor | 21/24 | 21/264 | 3 |
| relationship+typed cited role | 7/24 | 0/264 | 17 |

Unsupported citation acceptance (correct substring, wrong role) is distinct from false equivalence. Exact-anchor checks are necessary and not semantic validation. Typed checks improve rejection with major coverage loss; only review/escalation candidate. This is no proof of semantic sufficiency.

## Remaining

The local git transport failed DNS; no GLiNER, Granite-Docling, pretrained GNN or new neural reranking weights acquired. The classical alternatives actually ran. Keep independent source rights/annotation, harder family-disjoint retrieval, first-pass frozen budgets, genuine cross-reference graph, full relation classes, separate learned evidence sufficiency, exact per-arm CPU/RSS/model byte receipts and hosted exact-head qualification outstanding. Add only opt-in runners, after maintained checks; no routine network, new dependency or acceptance bypass. Retain original negative results, not just the favorable cells.


## Exception-specific stress and verifier-placement follow-up (26 November)

Executed fresh local fit using original development partition, plus 32 newly
authored synthetic cases (24 exception present, eight absent, four family-labelled
groups). Same original model, no evaluation cases supplied for training.
An exploratory expanded regex adds explicit surface cues excluding, other than,
but not, outside and semicolon boundaries. Its design shares the vocabulary
of the authored challenge: not an independent reference or evidence of
generalisation. Missing-only learned fallback does not overwrite any rule span.
No automatic acceptance or release changes.

```sh
cd research/model-placement
python -m pytest -q test_tagging_followup.py
python tagging_followup.py --output tagging-receipt.json
```

RED missing module; GREEN two tests passed. Actual run wall 0.181836 s, peak
161300 KiB RSS, no model download. Same local research environment as above.
Receipt SHA-256 3edbf13d6b98165f131a7be4bf06d3ccdf232ae244f66ae06a6f22b60f839387
(includes non-deterministic timing/resource observations). Exact per-case
spans, review flags, family summaries, paired gains and losses regenerable.

| Method | Original exceptions TP/48 | Stress TP/24 | Stress FP | Stress FN | Stress F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original rules | 40 | 4 | 4 | 20 | 25.0% |
| Compact learned | 48 | 0 | 23 | 24 | 0.0% |
| Missing-only learned fallback | 48 | 4 | 26 | 20 | 14.8% |
| Expanded rules | 48 | 24 | 0 | 0 | 100% |
| Expanded rules + fallback | 48 | 24 | 8 | 0 | 85.7% |

Original rule omissions recovered by expanded surface rules; learned tagger
fails on all new exact exception boundaries. Expanded+learned introduces
eight spurious exception claims on absence controls. The 100% regex result
is a cue-matched ceiling on these authored examples, not external validity.
No adoption of a learned exception fallback. Further challenge implicit
exceptions, cue polysemy, nested and cross-sentence scopes, independent span
references before promoting any rule expansion.

Typed verifier follow-up on original 432 claims (144 valid, 288 invalid):

| Review flag method | Invalid flagged | Valid flagged |
| --- | ---: | ---: |
| Exact anchor only | 144 | 0 |
| Rule-typed | 288 | 32 |
| Learned typed | 288 | 29 |
| Rule-typed + missing-only learned exception fallback | 288 | 24 |

The hybrid reduces unnecessary flags by five vs the learned verifier and
eight vs rule-typed on the original controls; all 288 invalid claims flagged.
This does not override the new negative stress result. Keep hybrid as an
experimental review-prioritisation signal only, not an automatic rejection
or authorisation rule. Need harder mixed-validity and natural citation
judgments and fresh pretrained tagging before scientific qualification.
