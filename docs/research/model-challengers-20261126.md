# Model challenger expansion — 26 November 2026

Track 01 and Track 05; issues #111 and #158; PR #155.
Owner requested K2-Horizon-3.7B, MiniCPM5-2B, d1.2-ultra, Jev 1.13 and a
broader reranker panel. This is a dated development amendment to the existing
[specialist protocol](specialist-pipeline-protocol.v0.1.0.md), not a new frozen
study or revision of its hash-bound E9–E14 contract. Preserve all earlier failures.

## Observed retrieval baseline

[Run 45757790945, artifact 15088716936](https://github.com/edithatogo/standards_check/actions/runs/45757790945/artifacts/15088716936)
completed at tested merge e74554fa4ba8ae0c7d5335626da1e0902c7bcb03.
Downloaded ZIP SHA-256
3df9b23127cf07cc67c55ccd18ce942895d70a62769015699cd2af1c95cdb20e;
paired.json SHA-256
09ba04a03e5942f71b3d18e6c6c2f0f3050298ad120d0b6d56ea209b29660bad.
Ten focused regressions passed. All 106 queries, 31 domain definitions, 125 positive
editorial associations, 3,286 pairs. No independent relevance or equivalence claim.

| Method | Macro query R@1 | R@3 | R@5 | R@10 | MRR | nDCG@5 | Scoring seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Word/bigram TF-IDF | 25.47% | 37.74% | 38.21% | 39.62% | .3425 | .3354 | .0093 |
| Char trigram TF-IDF | 28.77% | 46.70% | 52.36% | 68.40% | .4492 | .4295 | .0149 |
| BGE-small | 34.43% | 58.96% | 72.01% | 80.03% | .5501 | .5597 | .5113 |
| BGE then MiniLM top 10 | 40.09% | 62.74% | 68.24% | 80.03% | .5770 | .5714 | 1.5545 |

Timing is single-run CPU observation, not controlled efficiency evidence.
Full paired process 2.73 s; peak RSS 257152 KiB. BGE and MiniLM graph, tokenizer,
config and model-card hashes retained in assets.json. Earlier checkout failures
45757312821 and 45757693829 remain infrastructure failures, not model results.
Assurance 45757763656 passed Python at 92.56% combined coverage; Ruff identified
two exact changes in the research artifact's format.diff. Apply that diff, not a waiver.

## Local reproducible challengers and stage mapping

| Candidate | Licence / access | Stage and action |
| --- | --- | --- |
| [IFM/K2-Horizon-3.7B-GGUF](https://huggingface.co/IFM/K2-Horizon-3.7B-GGUF) | Apache-2.0; publisher GGUF | E12 generative adjudicator and long-context evidence escalation. Official Q4_K_M about 3.16 GB; model name describes core size, total GGUF parameter count differs. Requires llama.cpp b11454 or later; existing pinned b11960 is a candidate. Preserve high-effort/large-budget provider configuration as a separate resource arm; the bounded 256/512-token development arm is not the publisher benchmark. Acquire immutable source/model/weight metadata first. |
| [openbmb/MiniCPM5-2B-GGUF](https://huggingface.co/openbmb/MiniCPM5-2B-GGUF) | Apache-2.0; publisher GGUF | E12 compact generative challenger. Actual model card reports 2.52B total, 1.98B nonembedding parameters, standard Llama architecture. Q4_K_M publisher artifact ~1.56 GB. Verify exact revision and SHA-256 before inference; no remote code. |
| [BAAI/bge-reranker-base](https://huggingface.co/BAAI/bge-reranker-base/blob/711afb1eff814a80f5363996cd76e1b5f39cc7d7/onnx/model.onnx) | MIT, publisher ONNX | E11 pointwise cross-encoder; full precision 1.11 GB, scalar logit; compare exact 1,060 query-candidate pairs. |
| [mixedbread-ai/mxbai-rerank-xsmall-v1](https://huggingface.co/mixedbread-ai/mxbai-rerank-xsmall-v1) | Apache-2.0, publisher-hosted ONNX | E11 xsmall quantized model (~87 MB); official ONNX PR SHA verified, resolve immutable prefix d8e18fd before acquisition. |
| [jinaai/jina-reranker-v1-tiny-en](https://huggingface.co/jinaai/jina-reranker-v1-tiny-en) | Apache-2.0, 33M, publisher ONNX | E11 tiny pointwise alternative; use ONNX graph without remote model code. |
| [Qwen/Qwen3-Reranker-0.6B](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B) | Apache-2.0; publisher safetensors | E11 instruction-aware relevance; use official template and softmax of final yes/no token logits, not scalar classifier graph. Freeze exact weights, tokenizer, library runtime and parity test before execution. |
| BAAI bge-reranker-v2-m3; Mixedbread rerank-v2 | Open-weight candidates | Subsequent scale/architecture ablation, only after first panel; verify checkpoint licence and native format. Do not assume v2-m3 external-data ONNX graph has the same boundary as base. |

Local panel reuses LocalRanker and the existing lexical, BGE and scoring
implementations. The exact ordered top-ten BGE pool is hashed
a86fcf8063efc642eb1295ca0a40e82791a739ca144c0d71904324c7c94e29f1
(canonical UTF-8 JSON list [instrument_id, item_id, ordered_candidate_ids],
sorted by query ID, compact separators). Pin source input digests as well
(costing registry dba42197db8a317e07e18b32f718e38ccdc648a40370240d804423e3940f5378,
mappings 757606b5f703f18eca0474a3a4f6ebf1ed5270e5b867a305c6df67869c2819f1).
Recompute the same pool and abort on drift. Do not change top-ten candidate
budget or label assignments after results. Paired changes in hits, query-level
benefit/harm, recall@1/3/5/10, MRR, nDCG, CPU/RSS and latency. Reranking cannot
recover targets missing from the BGE candidate set.

## Hosted decision and reranking comparisons

| Provider and pinned requested model | Stage | Access boundary |
| --- | --- | --- |
| [Liquid AI d1.2-ultra](https://www.liquid.ai/blog/d1-2), d1.2 | E10/E12 typed decisions and source-offset extraction | Liquid API only in current release; no verified public weights for these exact models. The observed open d1-2B is a different checkpoint. Same historical text-only choice rubric and probability diagnostics first, then separate spans/value and multimodal challenge. |
| [TypeSafe Jev 1.13](https://docs.typesafe.ai/), model jev-1.13.0 | E12 System One typed decision comparator | Hosted; preserve explicit requested version and response identity, never use jev-latest. No public weight verified. |
| [Voyage/MongoDB](https://docs.voyageai.com/docs/reranker) rerank-2.5, rerank-2.5-lite, rerank-3, rerank-3-lite | E11 pointwise ranking | Hosted API; retain requested 2.5 rather than silently replacing it, compare newer 3 family separately. Same text candidates, truncation disabled. |
| [Cohere](https://docs.cohere.com/docs/rerank) rerank-v5.0-pro, rerank-v5.0-fast | E11 hosted ranking | Current named v5 tiers; record response version when available, no comparison with provider leaderboard as domain evidence. |
| [Jina/Elastic](https://jina.ai/reranker) jina-reranker-v3.5, jina-reranker-v2-base-multilingual | E11 listwise versus pointwise | Hosted service comparison, or separately qualified noncommercial local weights. Current v2/v3/v3.5 weight licences are CC-BY-NC-4.0; legacy v1 tiny is Apache-2.0. |
| [Mixedbread](https://www.mixedbread.com/docs/legacy-models) | E11 | Prefer open v1/v2 artifacts; legacy direct reranking API no longer documented; managed stores change retrieval and are not equal-budget reranking. |

Hosted models need separately authorised accounts, costs, data processing terms,
retention/region and confidentiality controls. Do not send unpublished manuscripts,
third-party source wording, patient or institutional data. Only public synthetic
controls and original short costing metadata are eligible for the exploratory
provider arm. No credential access, purchases, secret-dependent PR runs, or
live remote model execution in this increment. Use explicit model IDs, capture
service response identity if supplied, usage, latency, date, input/output hashes,
complete index mapping, failure counts and cost. Hosted model ID is not an
immutable weight revision. Never claim a provider test completed without a receipt.

## Next gate

Run the local BAAI, Mixedbread and Jina panel on identical BGE inputs; check
provider file metadata before acquiring K2, MiniCPM and Qwen. Keep the larger
generative and hosted decision tasks on the original synthetic controls only,
without reclassifying the original holdout as new evidence. d1.2-ultra and Jev
are suitable orthogonal typed-decision challengers, not independent reference
oracles. Provider choice probabilities must be complete, finite, normalized,
and matched to the original question; returned spans must equal the original
source substring. No automatic majority vote, threshold tuning on evaluation
data, canonical admission, scientific freeze, or merge waiver. Extend the
preprint evidence table with all negative and access/transport failures.
