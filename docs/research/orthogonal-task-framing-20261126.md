# Orthogonal task formulation and model triangulation — 26 November 2026

Status: prospective development amendment; no freeze, no independent scientific
qualification, no normative representation change, no new pack admission.
Owners: Track 01 and Track 05, existing issue #158. Related source work #111,
representation/semantics #82/#149. Reuse the
[specialist E9–E14 protocol](specialist-pipeline-protocol.v0.1.0.md),
[orthogonal assurance design](orthogonal-assurance-20261126.md), and E1–E8
without altering their historical hash-bound designs. No new executor or
runtime dependency: reuse the native loopback, System One, retrieval evaluator,
provenance and deterministic validation contracts.

## Question and design

Do independently framed, logically complementary tasks improve reference-relative
error detection at a fixed review and compute budget, compared with repeating one
prompt or scaling the model? Separate architecture, task representation, candidate
set, answer order, generation cap, quantization and runtime. Agreement across views
of one model is correlated evidence, not multiple independent adjudicators.
Option order is a robustness perturbation, not a new source of semantic truth.
Cross-model and cross-frame ablations use paired inputs, fixed task definitions and
candidate budgets. Report abstentions, false equivalence/discharge, direction errors,
unique catches, introduced errors, shared misses, spurious flags, per-family
uncertainty, inference counts, wall time and memory; never pick the best prompt on
evaluation labels and call it confirmed. Separate calibration and evaluation by
family component; use existing conformal rank oracle only with independent calibration,
exchangeability assumptions and sufficient strata. No new risk guarantees from the
historical synthetic/editorial controls.

| Stage | First view | Orthogonal task and deterministic boundary |
| --- | --- | --- |
| E9 ingestion | Source-native structural parse | Layout/region inventory and independent ID/subitem reader; compare exact source anchors, no invented text |
| E10 extraction | Entity/span candidate | Extract predicate, modality, scope, exception and quantifier; exact source-substring validation, independently detect omissions |
| E11 retrieval | Topic-to-domain relevance | Task-specific index assignment; raw vs instructed embeddings, same domain universe; fixed top-ten reranking with candidate conservation |
| E12 decisions | Five-class relation | Reverse A/B, invert directional labels; reverse option serialization; existential counterexample questions; distinguish incompatible, incomparable and unknown |
| E12 manuscript evidence | Whole-requirement sufficiency | Retrieve supporting spans, atomize obligation, assess entailment and counterevidence separately; unknown passage coverage is not absence |
| E13 structured generation | Direct constrained schema response | Source-span/typed fact extraction then deterministic construction; full semantic/schema checks after grammar |
| E14 formal | Proposed applicability classification | Extract facts and conditions separately, execute approved three-valued rules; finite truth table and solver countermodels, not LLM proofs |

Existing generative PROMPT describes indeterminate as both incomparability and
insufficient context, whereas the native d1 rubric and formal reference distinguish
these. Preserve historical rubric/results; prospectively test a corrected generative
rubric with explicit incomparability only and abstention for insufficient context,
with unchanged grammar/decoding budget. For MiniCPM compare a documented no-thinking
mode only after confirming exact template support, or use separate budget arms;
do not present length-exhausted responses as semantic inability.

## Executable development arms, locked before new inference

Use exact historical fixture SHA-256
55d1dd465c413a4d64890974de42a9719c63b7a711f8172eb70b35160b28c3d0, all 36 original
synthetic cases as development. Each arm supplies only A/B source text and question
criteria. Reuse the same d1-2B GGUF and native llama.cpp b11960, original direct
confidence floor .50 and equivalence .95; directional and witness choice floor .80.
Keep answers/probabilities and exact ordered payload hashes; retain no source text
in receipts and send no reference labels in requests. Each pair receives four requests (144 total):

1. Original direct plus directional questions (within-run comparator).
2. Exact same wording with reverse insertion order of choice criteria; verify sent
   bytes, do not infer actual model-side order if native renderer canonicalizes it.
3. Swap A and B, same original rubric, invert narrower/broader back to legacy
   B-relative-to-A orientation. Other labels unchanged; abstention stays abstention.
4. Ask separately whether A-only, B-only or both can be satisfied. Compile the
   answers using the exact truth table below. These are predicted possibilities,
   not constructed and verified witnesses. Unknown, low confidence, empty scope
   and unsupported combinations abstain.

| A-only possible | B-only possible | Both possible | B relative to A |
| --- | --- | --- | --- |
| no | no | yes | equivalent |
| yes | no | yes | narrower |
| no | yes | yes | broader |
| yes | yes | no | contradictory |
| yes | yes | yes | indeterminate |

Strict four-view agreement is an exploratory selective triage rule; disagreement
or any abstention holds. It is not a calibrated ensemble and cannot admit a semantic
relation. Report all arms and abstention denominators; no oracle cherry-picking.
Model-derived probabilities must not be interpreted as calibrated probabilities of
scientific truth. Measure compute/time per arm in later controlled repeats, not
claim equal resource cost for a four-request ensemble versus a single request.

`run-decision-framing` reuses the existing LFM job and existing native post boundary.
The same framing can be extended to d1.2-ultra and Jev after provider authorization,
with matched model identities, budget and sanitized receipts. Hosted requests are
not run automatically, and no paid service or private manuscript is used here.

For E11, run the same Qwen3-Reranker-0.6B Q8 local runtime with the existing exact
1,060 BGE top-ten query-candidate pairs and a single new query frame:
"Identify the economic domain whose definition substantively covers this reporting
topic. Topic: [original short topic]". This is a query-text intervention, not a claim
that llama.cpp's GGUF-native rerank instruction was replaced; that endpoint
exposes query/documents and top_n, not a separate instruction field in b11960.
The raw-query comparator is the retained Qwen0.6B receipt, so runner/time variation
is a limitation. Label `run-qwen-query-framing`. Distinguish this from a future
verified native instruction/template ablation and listwise reranking (Jina v3.5).
Keep label-free input, exact candidate order and returned index validation; hash
each request, record all scores. Same pool, no new candidates.

First-stage retrieval is separate: evaluate equal-weight reciprocal-rank fusion
(RRF k=60, ties by stable domain ID) of original BGE and char TF-IDF, including
all 106 queries/31 domains/125 editorial associations. Missing lexical rank
contributes zero. No tuning. Compare at equal k, preserve the full universe.
Observed retrospective calculation from hash-verified baseline 15088716936:
R@1 36.32%, R@3 61.32%, R@5 69.34%, R@10 79.72%, MRR .554208; R@5
+6/-11 known associations relative to BGE 72.01%. R@10 +6/-6. This is an
exploratory negative result for recall at five; no production preference.
Use actual Qwen3-Embedding-0.6B official GGUF Q8 at immutable upload prefix
d20cf9c (resolve to full SHA before acquisition; weight SHA-256
06507c7b42688469c4e7298b0a1e16deff06caf291cf0a5b278c308249c3e439).
Apache-2.0 publisher card; same b11960, last-token pooling, normalized finite
1024-dimensional vectors, 31 targets once and 106 queries in each of two views
(243 requests): raw and publisher Instruct/Query format with a domain-specific
instruction, then fixed RRF of instructed Qwen and retained BGE. Full universe,
not original top-ten; compare exactly the same reference and k. Report raw and
instructed arms and the fixed fusion; no threshold or weight selection.
Label `run-qwen-embedding-framing`.

Prioritize Mixedbread large v2 after this, with explicit decoder scoring parity
against publisher yes/no/rank implementation. The available third-party GGUF
conversion is not proven to have the correct ranking head; hold until qualified.
Jina v3.5 (listwise) is a CC-BY-NC-4.0 research comparator only; publisher's
custom-code model path needs review, or separately authorized hosted API. Test
candidate-order sensitivity for listwise rerankers using identical candidates
and de-permuted indices. Keep Qwen4B result and 8B reservation separate; no
scale expansion solely because it is larger. No hosted spend or credentials.

## Reconcile actual receiving and source receipts

PR #155 was merged by repository state, not by this follow-up, receiving main
36556203d952fb07406aaa2a383eea9edca5e991. Prior exact-head
[Assurance 45763257324](https://github.com/edithatogo/standards_check/actions/runs/45763257324)
passed all 13 jobs, 797 Python tests, 92.39% combined coverage. The merge does
not establish independent scientific qualification. This focused branch preserves
the merged history and original experimental holds.

[MiniCPM5 45761889329/artifact 15091536717](https://github.com/edithatogo/standards_check/actions/runs/45761889329/artifacts/15091536717):
downloaded ZIP SHA-256 b8e7b7372579bd63b32b3de290eb9c719eab2a890dea69f29cadd66a26a21817;
report aa83ad1ebe0b2048225fcaa5de11c415689e8595f9995acc6345ffc0ed9ff36d.
7/36 correct, 29 abstained, zero false equivalences, zero unique correct versus
either NLI incumbent. Finish reasons 29 length/7 stop, 1369.10 s, 3832000 KiB
peak. Budget/decoding failure, not a decisive negative semantic comparison.
Qwen4B still running at inspection; do not assume success.

[Issuer geometry 45763270695/artifact 15090403325](https://github.com/edithatogo/standards_check/actions/runs/45763270695/artifacts/15090403325):
downloaded ZIP SHA-256 2f65f149775e276ac5a5d1f823bb6a91f4ca4ef8e321aaa9dac91570f6f1f17c;
ARRIVE 21/21 and STROBE 22/22 printed main IDs/stars matched by both pdfplumber
and Poppler in order. ARRIVE primary PLOS JATS acquired exact 120464 bytes SHA-256
eace6d0c1894a0dd2ca5092325bc3e52fa6eeb3cdbd722b5074d2cdf91b91d8d,
CC0-1.0 article, 21/21 main rows across t001 and t002, both tables held for
block_boundary_difference. Table/item reuse unassessed. STARD alternate EQUATOR
PDF HTTP 404. Next qualify ARRIVE explicit XML break/list subitems, row anchors
and fidelity from independent source-only review; independently match STROBE
nested/variant and footnote obligations, rights and alternate STARD official source.
These are structural observations, zero qualified independent families, no
scientific freeze or source/pack admission.

## Preprint and acceptance

Predeclare development and confirmatory questions separately. Include a crossed
model-by-task design with frozen family/reference, resource-matched single versus
multi-view and fixed-review-budget triage, candidate-pool recall versus rank-only
effects, calibration and false-equivalence risk; paired estimates and clustered
uncertainty. Do not imply same-model views are independent or use consensus as
truth. No human review requirement for routine engineering; model-relative
labels are not expert validation. Preserve original E2/E3 and E4–E14 scientific
gates and planned contracts. Record failed, null, truncated and unsupported runs.
Initial eight pure helper tests RED/GREEN passed in isolation; full hosted
checks and actual new inference receipts are required before engineering acceptance.

Sources:
- Qwen instruction-aware model and evaluation: https://github.com/QwenLM/Qwen3-Embedding
- Official GGUF: https://huggingface.co/Qwen/Qwen3-Embedding-0.6B-GGUF
- Pinned native API: https://github.com/ggml-org/llama.cpp/blob/b11960/tools/server/README.md
- Pezeshkpour and Hruschka, NAACL 2024, doi:10.18653/v1/2024.findings-naacl.130.
- Zheng et al., ICLR 2024, https://proceedings.iclr.cc/paper_files/paper/2024/hash/54dd9e0cff6d9214e20d97eb2a3bae49-Abstract-Conference.html
- Mixedbread v2: https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v2
- Jina listwise: https://huggingface.co/jinaai/jina-reranker-v3.5

Initial [Assurance 45765184474](https://github.com/edithatogo/standards_check/actions/runs/45765184474)
workflow-policy reported a formatting-only failure at task_framing.py line 81.
Lint passed. The new decision, reranker and embedding runs passed the focused test
step and reached native acquisition/inference. Correct the formatting without
changing the frozen experimental questions; retain all old run IDs.

## Completed raw/instructed Qwen embedding and rank-fusion development

[Run 45765210583](https://github.com/edithatogo/standards_check/actions/runs/45765210583/artifacts/15090704998)
completed successfully. Downloaded ZIP independently matches
194ed70304518cea956e60970ff337ac5d4cd486ba64de0a4753574a66aed77f.
Tested merge d988efbf15356dc29e2c73edf578acf55bb3138b;
report.json SHA-256 28dd0f5f343e703f6bd247501c97288443b044022197bcc1f6255153a3b7deba;
fusion.json SHA-256 8b2d7521a7d284316d7194905213142f8619b2cfaaa71ce0018ffb9bc6ca25ca.
Resolved exact official weight revision d20cf9c16f82914a21dbd9c645f56895fb1d7750;
Q8_0 checksum passed (the previously pinned SHA-256). Apache-2.0 publisher
metadata, unchanged full source/query universe, 243 requests, native CPU
scoring 14.1424 s, peak server RSS 1433672 KiB. Timings are single-run only.

| Arm | Macro R@1 | R@3 | R@5 | R@10 | MRR | nDCG@5 | Gains/losses @5 vs BGE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| BGE-small | 34.43% | 58.96% | 72.01% | 80.03% | .55015 | .55966 | baseline |
| BGE + character RRF60 | 36.32% | 61.32% | 69.34% | 79.72% | .55421 | .55630 | 6/11 |
| Qwen raw | 36.32% | 58.33% | 70.13% | 81.92% | .55833 | .55897 | 13/17 |
| Qwen instructed | 39.47% | 67.30% | 73.43% | 85.22% | .60590 | .59848 | 14/14 |
| BGE + instructed Qwen RRF60 | 39.62% | 66.51% | 76.26% | 85.69% | .60123 | .60961 | 8/2 |

The instruction improved same-model macro R@5 by 3.30 percentage points,
and MRR by .04757. Against BGE, Qwen instructed improves macro query R@5
but ties association-level recall at .696 (14 gained and 14 lost). The
predeclared equal-weight fusion improves macro R@5 by 4.25 points and
micro recall from .696 to .744 (93/125 versus 87/125), eight gains and
two losses. BGE plus character fusion remains a negative R@5 result.
This is descriptive evidence of task and architectural complementarity,
not a statistically independent confirmation or claim of a universally
better model. Keep the same budget and all query IDs, distinguish macro
query weighting from association weighting, retain all arms. Next evaluate
a separately frozen full-candidate retrieval reference and use the
fused pool for a separately declared downstream reranking ablation; do
not overwrite the historical BGE-only pool. No calibration or model
promotion. The original four-view decision and Qwen rank-query experiments
and earlier Qwen4B remain active at inspection.
