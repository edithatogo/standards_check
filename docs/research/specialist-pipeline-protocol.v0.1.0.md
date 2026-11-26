# Specialist neural and deterministic reporting assurance

Version 0.1.0 | 26 November 2026 | Prospective design, not frozen.
Owner: Track 01, with Track 02 artefacts, Track 04 interoperability and Track 05 assurance.
Issues #82, #95, #111, #149, #158 and PR #155. This extension reuses the existing
publication programme E1-E8, source evidence, composition contracts and canonical
Standard Pack validators. It does not change the approved representation or historical
scientific gates. No study registration, scientific acceptance or preprint submission.

## Research question

Can a heterogeneous pipeline of small task-specialised neural models and deterministic
verification outperform general-purpose generation at source-faithful conversion,
anchored extraction, retrieval, applicability-aware evidence assessment and trustworthy
structured output, at lower resource and review cost?

The contribution to test is the stage-specific allocation of work and measured
incremental benefit, not invention of OCR, embeddings, NLI, constrained generation,
ontology linking or formal verification. Compare against source-native parsers,
existing lexical/classical NLP, current NLI and LFM comparators, and a matched-budget
general-purpose generative comparator. Keep the existing E1 directory census, E2/E3
semantic/reference and triage work, and E4-E8 composition, ontology and editorial
utility designs distinct. The new E9-E14 specialist feasibility endpoints extend
these designs; do not split the same findings into multiple publications.

## Architecture and candidate selection

Prefer existing readers, runtime libraries, native validators and exact source pins.
Only add model or solver dependencies in opt-in research lanes after measuring a
specific gap. Models never become the canonical authority.

| Stage | Incumbent and first challenger | Further bounded ablation | Authority boundary |
| --- | --- | --- | --- |
| E9 ingestion/layout | Existing JATS/HTML, python-docx, pdfplumber/Poppler and structured readers; IBM Granite-Docling-258M (Apache-2.0) for tiny region/DocTags feasibility | PaddleOCR-VL-1.6 0.9B (Apache-2.0), GLM-OCR 0.9B (MIT), Xiaomi-OCR-0 0.8B (Apache-2.0); TeleOCR 1.2B and OvisOCR3 0.8B benchmark leads, licence and runtime qualification pending | Exact source bytes, printed IDs, text spans, page/box/row/column/order, subitems, footnotes and diagram edges checked independently; no OCR-only admission |
| E10 tagging | Regex, source identifiers, existing classical linguistic analysis; GLiNER2.5-small 74M (Apache-2.0) | GLiNER2.5-base 194M, GLiNER2-base 205M (Apache-2.0); fine-tuned ModernBERT token head only with independent labels; tasksource ModernBERT-base-NLI for separate zero-shot document classification | Extractive offsets and candidate tags, not minted provenance or semantic equivalence |
| E11 retrieval | Existing word/bigram and char-trigram TF-IDF; BGE-small-en-v1.5 33M (MIT) with official ONNX; MS MARCO MiniLM-L6-v2 22.7M reranker (Apache-2.0) | gte-modernbert-base and gte-reranker-modernbert-base 149M (Apache-2.0); Qwen3-Embedding-0.6B and Qwen3-Reranker-0.6B (Apache-2.0) | All stable item identities conserved. Ranking/topic match is not directional relation, equivalence, scope or methodological quality |
| E12 evidence/NLI | Existing bidirectional MiniLM and DeBERTa-v3-xsmall, source-grounded span validation; manuscript passage as premise and a concrete evidence hypothesis | cross-encoder/nli-deberta-v3-large, tasksource/ModernBERT-base-nli or large (Apache-2.0); LFM/d1 complementary development diagnostics | Explicit model label maps, source anchors and applicable obligation scope; unknown, absent, contradiction and nonapplicability distinct |
| E13 structured decoding | Existing llama.cpp GBNF/schema subset, strict JSON parsing, full schemas and Rust validation | XGrammar or Outlines (Apache-2.0) or Guidance (MIT) only if coverage or throughput merits one alternative | Grammar acceptance is syntactic, not evidence, cross-record integrity, rights, correctness or full JSON Schema conformance |
| E14 symbolic verification | Existing Rust typed validators, exact arithmetic, finite truth tables, PNML/PM4Py generator | Z3 SMT (MIT) for bounded implication/witness and numerical constraints; Datalog for monotone closure; PM4Py soundness checks where their scope/licence fits | No ML in arithmetic, identity, policy evaluation, canonical lock, graph soundness or acceptance-state transitions |

### Current external model evidence

The dated shortlist is a set of Pareto candidates, not a universal model ranking.
The OmniDocBench v1.6 full leaderboard observed on 26 November reports TeleOCR
96.91 overall and table TEDS 96.82, OvisOCR3 96.69 overall, PaddleOCR-VL-1.6
96.34 overall and GLM-OCR 95.22 overall. OXR-1.0 reports 97.03 with a bespoke
licence. Verify the selected TeleOCR/Ovis checkpoint licences before selecting them.
Xiaomi-OCR-0's author report gives 96.83 overall on its selected comparison, but
the reproduction configuration reports 96.47 for the two-stage pipeline and
94.63 end-to-end; do not mix these with independently run leaderboard rows.
Granite-Docling has a much smaller footprint and structured document output;
its architectural fit is a reason to benchmark, not evidence of superior accuracy.
Keep layout detection, table cell recognition and diagram node/edge reconstruction
distinct. Prefer native DOCX XML and source tables over rendering to images.

GLiNER2.5's sparse boundary architecture and span/record heads are a better fit than
generation for offsets and entity candidates. Check both size variants, exact span
precision/recall/F1, nested spans, chunk boundaries, false negatives and actual CPU cost.
A pretrained ModernBERT base encoder alone has no token-classification head;
do not claim a zero-shot NER capability without the task-specific checkpoint.
Every accepted span must reproduce source characters and anchor offsets; provenance
identities/hashes are derived by software, never inferred by models.

BGE-small reports 62.17 MTEB English average and 51.68 retrieval in its model-card
evaluation; gte-modernbert-base reports 64.38 MTEB-en and 55.33 BEIR in its
provider evaluation. The Qwen3 provider's own retrieval/reranking comparison
reports Qwen3-Embedding-0.6B 61.82 and Qwen3-Reranker-0.6B 65.80 on its MTEB-R
protocol. These are distinct evaluation settings, not a combined leaderboard or
costing-specific qualification. Start with the smaller CPU ONNX pair, then test one
additional architecture on a frozen reference. Use in-memory complete bounded
candidate pools before considering any ANN index or vector database.

### Scientific and software constraints

A manuscript hypothesis must be operationalised (e.g. a specific outcome definition
is reported), not the literal prescriptive sentence "authors should report X".
Use one or several anchored passages; neutral from a retrieved passage means
insufficient evidence in that passage, not absence throughout the manuscript.
Assess full eligible scope and retrieval completeness before "not reported".
Do not infer methodological appropriateness from reporting completeness. Reverse
requirement comparisons and manuscript-evidence NLI are separate tasks. Preserve
RGI-06 orientation, explicit label maps, calibrated abstention and independent review.
Do not combine correlated votes as if independent. Calibrate d1 probabilities on
development families only; compare raw probabilities, temperature calibration or
one predeclared alternative with reliability plots, Brier/log loss and risk-coverage.
Lock thresholds, family split and review budget before evaluation; retain original
failed decisions and all negative ablations.

Constrained decoding only guarantees membership of the implemented grammar for
completed accepted strings under correct engine behaviour. It does not guarantee
all JSON Schema keywords (including cross-field dependencies or uniqueness),
semantic validity, correct source spans, or non-truncation. Verify the actual
schema dialect and supported subset using valid and invalid cases; reject duplicate
keys, incomplete output, nonfinite values, unknown fields and unsupported constraints.
Always run the existing full JSON Schema, Rust semantic and lock validators.
Generate deterministic data directly where possible rather than invoke a model.

For applicability, use typed values with explicit unknown rather than closed-world
false. Compile approved rules, not free-form generated code. Evaluate eligibility,
requiredness, evidence and exceptions separately. A model may suggest a candidate
fact with an exact source span. Deterministic code verifies it and preserves holds.
For a finite known shared scope, prove equivalence by both implication checks, and
contradiction by joint unsatisfiability; handle empty/unknown applicability explicitly.
For real-valued costs, use exact decimal/rational arithmetic, currency/price-year,
quantity/unit/denominator and allocation conservation tests. SMT witnesses establish
properties only of the encoded formal model. Datalog can provide finite rule closure,
not unknown-as-false or automatic authority. Use existing Rust first; add a solver
only for a demonstrable expressivity need. Existing PNML generation is a visual
checklist projection, not evidence of a sound workflow. Verify initial/final markings,
reachability, dead transitions, proper completion, deadlocks and boundedness with a
bounded analysis; timeout/unbounded/unsupported is unknown, never passed.

## Study design and outcomes

Freeze the complete source rights and structural evidence, exact model/runtime/code,
tokenizer/grammar/solver versions and hashes, input IDs, family-component partitions,
annotation rules, reference scope, metrics, candidate budgets, decision limits and
resource environment before confirmatory evaluation. Family independence groups
include derivatives, extensions, translations, editions and related source variants.
Record training overlap uncertainty. Use separate source-only blinded reference agents
with initial decisions locked and a separate resolver. Distinguish formal truth-table
controls, author-labelled synthetic data, editorial mappings, natural model-relative
references and human/external reference evidence. Existing optional-human-review
policy applies; no false expert-reference or ethics/approval claim.

| Experiment | Primary measure | Complementary measures and falsification |
| --- | --- | --- |
| E9 | Exact source requirement and anchor conservation | Row/subitem precision/recall, exact text fidelity, reading order error, TEDS/TEDS-S, box/edge F1, omitted/duplicated items, footnote and continuation retention, scan/multi-column stress, CPU/RSS |
| E10 | Exact typed source-span F1 | Boundary errors, nested/overlapping spans, entity type confusion, false negatives, abstention, chunk leakage, runtime |
| E11 | Macro-family recall@5 against independent relevance | Recall@1/3/10, MRR, nDCG, precision, full target pool denominator, candidate reduction, paired misses, CPU/RSS |
| E12 | Reference-relative false discharge among usable assessed obligations | Separate evidence retrieval failures, false entailment/equivalence, contradiction, direction errors, missing evidence, Brier/log loss, risk-coverage, paired incremental detections per review budget |
| E13 | Invalid output accepted by the full validation boundary | Valid completion, length stops, unsupported keywords, hostile duplicate/nonfinite data, schema coverage, grammar compile/mask cost and latency |
| E14 | Unsupported formal or arithmetic decisions accepted | Exact truth-table/witness tests, property/metamorphic/mutation tests, unknown/timeout propagation, reachability and conservation, solver/CPU cost |

For each stage compare an incumbent, one qualified compact specialist, optional
orthogonal specialist and matched-cost general-purpose baseline where relevant.
Keep failure/abstention in denominators. Report paired differences and family-clustered
uncertainty; with few independent families report counts and descriptive estimates.
Do not select thresholds or methods on evaluation labels. Retain source/identity
conservation and zero automatic admission as hard constraints. Predeclare minimum
useful gain, acceptable review burden, resource limits and harm limits on independent
development data; no unqualified numerical adoption rule is implied by the draft.
Evaluate each stage and the integrated pipeline separately; avoid masking common-mode
failures with an oracle ensemble. Time, peak RSS, model/index bytes, hardware, seeds,
inference precision and licence constraints accompany every result.

### Immediate bounded development slice (not E11 confirmation)

The existing costing registry contains 26 instrument/publication records, 31 domains
and 106 item/principle mappings across five mapped instruments. The verified fact is
the source identifier, not the correctness of the editorial covers_topic mapping.
Use all 106 short original topic labels as queries and all 31 domain definitions as
targets (3,286 possible pairs; 125 existing positive associations). Do not add source
wording, pass the reference domain IDs to a model or infer negative truth from an
unlisted association. Preserve 21 unmapped instruments as outside the query cohort.
No training, no split claim, no deduplication. Compare shared word and char TF-IDF,
BGE-small CLS cosine and top-10 BGE candidates reranked by MS MARCO MiniLM-L6-v2;
ties by domain ID. Use BGE's documented query prefix and unprefixed target definitions,
no truncation. Report query-level and association-level recall, precision@k (missing
slots count as nonhits), reciprocal rank, nDCG@5, empty queries and per-instrument
counts, with all query IDs and candidate lists retained. Reranking cannot recover
targets missing from the retrieval top ten. This measures agreement with editorial
seed mappings, not independent relevance or scope.

Use publisher ONNX artifacts only; BGE revision
5c38ec7c405ec4b44b94cc5a9bb96e735b38267a (weight SHA-256
828e1496d7fabb79cfa4dcd84fa38625c0d3d21da474a00f08db0f559940cf35),
MiniLM reranker revision 739bce82df32cacea8ff0edf73ab49ae315e5a5f
(weight SHA-256 c80a8b34256ea453093d612e3ac48d3d965a0c0a48c7906709af8b8e28461bf9).
Retain tokenizer/config hashes, runtime, source bytes hashes, complete ranking IDs
and exact tested commit. Use the already qualified CPU ONNX/tokenizers dependencies
in an explicit development workflow. Fail on unqualified assets, output or context.
No model downloads in routine tests, no external inference, no raw manuscript text.
The preceding LFM receipts and source holds remain historical evidence in
the [semantic qualification receipt](../../conductor/tracks/01-canonical-standard-pack/semantic-reconciliation-qualification.md).

## Preprint plan and reproducibility

Working title: "From generative AI to verified reporting infrastructure: evaluating
small specialist neural models and deterministic engines for machine-actionable
research reporting standards." Structure the preprint around the source and semantic
failure taxonomy, a task-specialist architecture, paired development observations,
prospective independent-family evaluation, stage and system ablations, safety and
licensing limits, and the reproducibility bundle. Include failed runs, not only
best-performing cells. Present model/runtime changes and retrospective probability
analyses as exploratory; only claims bound to a frozen design, actual run and review
can enter the existing observed-claim ledger. Report independent source acquisition
holds and incomplete denominators. No pooled accuracy across incompatible tasks or
datasets. Use rights-qualified artifacts/metadata, model/revision hashes and retained
receipts; no unrestricted source redistribution or submission without authorization.

## Primary sources (checked 26 November 2026)

- OmniDocBench, CVPR 2025: https://github.com/opendatalab/OmniDocBench
- Granite-Docling: https://huggingface.co/ibm-granite/granite-docling-258M
- PaddleOCR-VL-1.6: https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6
- GLM-OCR: https://huggingface.co/zai-org/GLM-OCR
- Xiaomi-OCR-0: https://github.com/xiaomi-research/Xiaomi-OCR-0 and https://arxiv.org/abs/2609.36136
- GLiNER2/2.5: https://github.com/fastino-ai/GLiNER2 ; https://arxiv.org/abs/2507.18546
- https://huggingface.co/fastino/gliner2.5-small-v1 ; https://huggingface.co/fastino/gliner2.5-base-v1
- https://huggingface.co/BAAI/bge-small-en-v1.5 ; https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2
- https://huggingface.co/Alibaba-NLP/gte-modernbert-base ; https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base
- https://github.com/QwenLM/Qwen3-Embedding ; https://arxiv.org/abs/2506.05176
- https://huggingface.co/tasksource/ModernBERT-base-nli ; https://huggingface.co/tasksource/ModernBERT-large-nli
- https://huggingface.co/cross-encoder/nli-deberta-v3-large
- https://github.com/ggml-org/llama.cpp/tree/master/grammars
- https://github.com/mlc-ai/xgrammar ; https://github.com/dottxt-ai/outlines-core ; https://github.com/guidance-ai/guidance
- https://github.com/Z3Prover/z3 ; https://github.com/souffle-lang/souffle ; https://github.com/process-intelligence-solutions/pm4py

Model-card licence metadata is a shortlist observation; exact checkpoint licence,
dependency/transitive licences, redistribution, source reuse and deployment rights
must be independently recorded before promotion. Keep the verified LFM custom licence
separate from Apache-2.0 and MIT candidates.
