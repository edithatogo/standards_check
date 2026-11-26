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

## Completed three-arm local reranking panel

[45761224407](https://github.com/edithatogo/standards_check/actions/runs/45761224407), tested merge
cb27e1fd5a466df8f03976cefa014a2b21f5cc44. Downloaded all three ZIPs and independently
matched their SHA-256 against the artifact API. Every arm recovered exactly the original
ordered BGE top-ten pool (hash above); all 106 queries and 125 editorial associations
retained. No model selected for production.

| Arm | R@1 | R@3 | R@5 | R@10 | MRR | nDCG@5 | Rerank seconds | Peak RSS KiB | Gains/losses at 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Mixedbread xsmall | 29.25% | 58.96% | 68.71% | 80.03% | .5019 | .5215 | 8.41 | 573924 | 5/11 |
| Jina v1 tiny | 27.83% | 51.42% | 63.21% | 80.03% | .4755 | .4776 | 2.24 | 453816 | 3/15 |
| BAAI base | 24.53% | 53.30% | 67.77% | 80.03% | .4505 | .4810 | 26.14 | 2336664 | 6/11 |

- [Mixedbread artifact 15089023958](https://github.com/edithatogo/standards_check/actions/runs/45761224407/artifacts/15089023958),
  ZIP 01216758bd60eb11e307120e6e36ae13995c4a5cf3c1ff7190bf9117f60f8f99,
  paired JSON b6dfc88232b3135f36b61a27ab4185fcb71513e46e5267e7e2d368a628c5033c.
  Exact resolved revision d8e18fdfcfc8b37c036c5c23e9fa9bda8d738cc9.
- [Jina artifact 15089918476](https://github.com/edithatogo/standards_check/actions/runs/45761224407/artifacts/15089918476),
  ZIP e50244529acd5cd8b177f4d78733c5a00d87812d9ce930a2dd5150f408907659,
  paired JSON d643b8ea906131b34c9e09d4184b6e19078f6a620222cdf5b9c73f40fd0b5d42.
- [BAAI artifact 15090166662](https://github.com/edithatogo/standards_check/actions/runs/45761224407/artifacts/15090166662),
  ZIP f334ca3f2683c347855e58b5f8401f69bf0349832b135fff768b54b7e1fdbbf0,
  paired JSON 4414ce34fed30d972e913602f49f267e958483eba34f7fd76df32bedc801febd.

BGE-only retains the best observed R@5. The new rerankers all lose more known
associations than they gain at five, although each makes unique catches. Prefer
the original BGE candidate pool and compare incremental evidence at fixed budget;
do not choose a ranking by historical outcomes and declare it confirmed.
No claims about unlisted relevant domains, family independence or broad generalization.

## Execution boundary and next pinned candidates

Native Qwen reranking can reuse the same already pinned llama.cpp b11960 runtime:
[ggml-org Qwen3-Reranker-0.6B-Q8_0-GGUF](https://huggingface.co/ggml-org/Qwen3-Reranker-0.6B-Q8_0-GGUF)
contains the explicit classification projection required by the native rank endpoint
(see [llama.cpp server reference](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)).
Do not treat an arbitrary causal-LM GGUF as a reranker. Run a positive/negative
relevance smoke and exact candidate-index validation before scoring the panel.

The opt-in `run-specialist-model-pins` job records fixed publisher metadata for
K2, MiniCPM5, and the ggml-org Qwen reranker. The K2 mutable ref is discovery
only, never used for inference; freeze complete revision and LFS digest after
inspection. Pin MiniCPM and Qwen to their known publisher revisions.
The job cannot download weights or promote a model.

Manual hosted comparator script reuses existing direct/directional decision
rubric and exact BGE ranking receipt. Run only on the exact public 36-case
synthetic fixture or verified 106-query editorial source bytes. No external
requests from GitHub Actions. Example (credentials supplied locally, not committed):

```sh
python -m scripts.hosted_specialist_development --model d1.2-ultra \
  --allow-hosted-public-development --max-requests 36 --output /tmp/d1-ultra.json

python -m scripts.hosted_specialist_development --model jev-1.13.0 \
  --allow-hosted-public-development --max-requests 36 --output /tmp/jev.json

python -m scripts.hosted_specialist_development --model rerank-2.5 \
  --baseline /path/to/verified/paired.json --allow-hosted-public-development \
  --max-requests 106 --output /tmp/voyage.json
```

Use LIQUID_API_KEY, TYPESAFE_API_KEY, VOYAGE_API_KEY, CO_API_KEY or JINA_API_KEY
in the local environment as appropriate. Verify service terms, allowed data and
actual costs before running. Explicit full-cohort request budgets, bounded response
size, no redirects, no retries, no proxy credential forwarding, no source labels
or private content in request. Preserve the provider-model identity and returned
numeric usage where available; model version may be unavailable for hosted rerank.
The implementation is not a provider service qualification. No live calls,
account purchases or credential access occurred here. Mixedbread legacy API is
held; open-weight experiment above is complete.

## Verified metadata and native follow-up

[Pin survey 45761669794](https://github.com/edithatogo/standards_check/actions/runs/45761669794),
[artifact 15089154238](https://github.com/edithatogo/standards_check/actions/runs/45761669794/artifacts/15089154238)
was downloaded and matched ZIP SHA-256
3fdb902a05c0a1736f2029088a37d5032866118898898d0ac08285c9995ed37d.
Publisher metadata confirms Apache-2.0 model cards and these exact assets:

- MiniCPM5 Q4_K_M, revision `2079a22f3beaa4e306449978533478fe0522f4b3`,
  weight SHA-256 `ec2d5801640099e97d8d7e8003ad4d81f336e757811f03a26173dddf386602fd`,
  1,561,318,368 bytes. Native compact arm uses 512 output tokens, the unchanged
  blinded 36-case synthetic controls and existing NLI comparators.
- ggml-org Qwen3-Reranker-0.6B Q8_0, revision `a02f48bb4f057028298c21fa033da2b30d7742d5`,
  weight SHA-256 `22c9979ce4fbcdc5acdc310c6641c32797eff1aa980b8f7a2db8a8ea23429a48`,
  639,153,184 bytes. Native rank endpoint must pass fixed relevance smoke before
  using the exact retained BGE receipt, 106 queries and 1,060 candidates.
- K2 held: initial publisher filename did not match uniquely. Retry publisher
  metadata for the 3.7B/4B naming variants; retain observed filenames and exact
  metadata bytes even on hold. Never infer against mutable main or silently
  substitute a third-party quantization.

Trigger labels `run-compact-model-panel`, `run-native-qwen-reranker`,
`run-k2-pin-review` are isolated explicit development/metadata lanes. No hosted
credentials, no inference on private data, no scientific qualification. The
bounded 512-token MiniCPM arm is not a reproduction of publisher benchmark settings.

### K2 publisher naming resolved

[Metadata retry 45761900423](https://github.com/edithatogo/standards_check/actions/runs/45761900423/artifacts/15089119538),
ZIP SHA-256 d4e378da09d9e18d80a14d43d39887ccd4f78386b4e7966fac683607270723c2,
confirms the unique official Q4_K_M artifact is named
`K2-Horizon-4B-Q4_K_M.gguf` in IFM/K2-Horizon-3.7B-GGUF. Pin revision
`839b82cdd4e8b7c824b509172ae0cd1fab56576e`, weights SHA-256
`07773aed93890d4f5d08b421430000d5c8d73cefc74fbdc32e67d820f23207b2`,
3,156,598,144 bytes, Apache-2.0 model card. This supersedes only the filename
hold, not any scientific gate. The `run-k2-development` arm uses the same
36 historical synthetic controls, native b11960 CPU runtime, seed 724,
1024 output tokens and low reasoning effort. The publisher recommends high
reasoning effort and a much larger generation budget, so this is explicitly a
bounded CPU feasibility diagnostic, not a replication of publisher scores;
length exhaustion stays an abstention. No mutable revision, remote code or
third-party quantization. Weight acquisition and inference must succeed before
reporting metrics.

## Scale, orthogonal alternatives and receiving-base reconciliation

The receiving main 6632782f51f126c82bbbddc2fe66d931e6d42382 introduces
the [orthogonal assurance design](orthogonal-assurance-20261126.md) and the
existing conformal rank oracle. Reconcile both Conductor histories, retain
T01.060–062 and T05.060–062, and do not fit thresholds on historical evaluation
controls. Confirmatory reference and source-family gates remain open.

[Assurance 45762031866](https://github.com/edithatogo/standards_check/actions/runs/45762031866)
on the previous head d2f609d passed all 13 jobs, including policy, Python,
API and Rust, cross-platform and Codecov. Python: 786 passed, 92.21% combined
coverage, above 90.50%. The reconciled head requires a new pass.

### Completed K2 and Qwen 0.6B observations

[ K2 artifact 15089979448 ](https://github.com/edithatogo/standards_check/actions/runs/45762032725/artifacts/15089979448)
ZIP SHA-256 61d302283af1d62951323cfe7b153e45b0466d3f7e732f99250da5b778d4b817,
report b35ff0185eb794147f4c4f3a559d04b140967855967fcc55d3271d4064f9155a.
K2 native low-effort 1024-token Q4_K_M: 29/36, zero abstentions, five false
equivalences. Versus each NLI incumbent: 22 both correct, 6 incumbent-only,
7 challenger-only, 1 both wrong, 14 disagreements; all 36 finish normally,
69.451 s, peak 6184240 KiB. Never promote as replacement or infer publisher
high-effort benchmark parity.

[Qwen 0.6B artifact 15090675906](https://github.com/edithatogo/standards_check/actions/runs/45761895728/artifacts/15090675906)
ZIP SHA-256 87e6a5262fa06f54a9efb45af0d8b00c09193d48e8f8f74867daf344b22ae45b,
report caef03d6b61e71b125d349cefae8c728fe40b19b3eb63dcc375018886b809668.
Native Q8_0 rank smoke relevant .993536 vs irrelevant .000049469. All 106
requests and exact original top-ten pool retained. R@1 38.68%, R@3 61.32%,
R@5 68.40%, R@10 80.03%, MRR .56703, nDCG@5 .56524. At five +5/-11
associations relative to BGE, no improvement over its 72.01% macro query recall.
232.677 s loopback scoring, peak 1437492 KiB; not controlled repeated timing.
Both ZIPs downloaded and independently checksum-verified. Development only.

### Predeclared next arms

Use Qwen3-Reranker-4B Q8_0 first, matching the prior quantization class;
reserve 8B rather than assume scale monotonicity. Qwen's own top-100 MTEB-R
English evaluation: 0.6B 65.80, 4B 69.76, 8B 69.02; FollowIR 5.41/14.84/8.05.
See https://huggingface.co/Qwen/Qwen3-Reranker-4B and
https://huggingface.co/Qwen/Qwen3-Reranker-8B .
No claim about the costing domain from that external benchmark.

A documented candidate is https://huggingface.co/gorse-io/Qwen3-Reranker-4B-GGUF
(Apache-2.0 metadata, upstream Qwen3-Reranker-4B, rank pooling and cls.output.weight
described in conversion notes). This is a third-party GGUF conversion, not a
publisher checkpoint. Inspect fixed LFS metadata and freeze SHA/revision before
executing; verify original upstream identity and licence, native rank smoke and
exact candidate pool. Full upstream numerical parity remains unqualified.
Do not execute an arbitrary causal model or mutable main. The metadata-only
label `run-qwen-scale-pins` performs no model execution.

GTE ModernBERT base 149M, Apache-2.0, is a compact encoder contrast. Pin
publisher ONNX file at immutable upload commit prefix 1299fb8, SHA-256
ecc6a0ae67cee3d898167802383112d9185ca9250e07bd5d1fa65019b050179d.
See https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base/blob/main/onnx/model_quantized.onnx .
Use the existing scalar ONNX adapter and equal frozen pool; fail closed if
the input/output signature differs. Label `run-modernbert-reranker`.

In Jina's published unified top-100 comparison (model card at
https://huggingface.co/jinaai/jina-reranker-v3.5), Qwen3 4B leads their RTEB
and Struct-IR arms at 77.68/55.6, while Jina v3.5 (0.6B) leads BEIR at 63.20.
Mixedbread large v2 (1.5B, Apache-2.0) is a worthwhile additional distinct
architecture (BEIR 62.45 vs Qwen4B 62.28, RTEB 70.81); its native decoder
scoring differs from xsmall v1 and needs a pinned parity check. Jina v3.5
is noncommercial weights or authorized hosted service. No universal performance
ordering, no remote credentials or charges, no unverified model promotion.
If reranking alone cannot recover missed relevant domains, test an independent
dense first-stage retrieval model (Qwen3-Embedding-0.6B or gte-modernbert-base)
and lexical+dense fusion on separately declared development pools; keep the
original 1,060-pair comparison unchanged. This is a separate retrieval ablation,
not a retuning of prior controls.

### Exact Qwen4B and source-layout gate

[Model pin survey 45762792595](https://github.com/edithatogo/standards_check/actions/runs/45762792595/artifacts/15090706355)
ZIP SHA-256 d942f79d8337f537152a3d938484e42c63b3bf11860aabe8c9eebfb37888455b
downloaded and verified. Qwen4B third-party rank conversion metadata: repo
gorse-io/Qwen3-Reranker-4B-GGUF, revision b22e6e5e27598ecc2a9b38439357034f3815d8cb,
Qwen3-Reranker-4B-Q8_0.gguf, SHA-256
2cf26934b45414d51cb1e1fc68378da02f8a1ae2893b70ccb13c381ec1ec9398,
4,279,678,944 bytes, Apache-2.0, Qwen3 architecture, rank pooling metadata.
Require exact model card names original reranker; conversion parity remains
unqualified. Native existing b11960 rank endpoint, same Q8 class and original
1,060 candidate pool, same positive/negative smoke plus exact alias. Separate
label `run-qwen4b-reranker`, no effect on routine inference or hosted services.
The GTE publisher upload resolves to 1299fb80afdf8c1ef9957056add3bc1db3b70a4e;
weight digest unchanged. 8B held pending marginal utility.

Source-side: inspected both rendered pages of the official
[ARRIVE author checklist](https://arriveguidelines.org/sites/arrive/files/documents/Author%20Checklist%20-%20Full.pdf)
and [STROBE combined checklist](https://www.strobe-statement.org/download/strobe-checklist-cohort-case-control-and-cross-sectional-studies-combined).
The generic ruled-grid reader cannot bind the missing interior vertical rules.
Freeze the visual main-ID denominators (ARRIVE 1–10 then 11–21, STROBE 1–12
then 13–22, with printed stars on 8, 13–15) and edition-specific page-relative
ID-column bounds before extraction. These are source-bound structural observations,
not an independent semantic reference or validated full-row transcription.
Use the existing native and Poppler geometry word helpers and retain only
main identifier anchors and discrepancy counts. Exact bytes required; no
unverified OCR or guessed items. Lettered subitems, study-design branches,
footnote meanings, exact requirement spans and source rights remain separate
holds. The ARRIVE primary PLOS article declares CC0 (DOI 10.1371/journal.pbio.3000410);
do not propagate article rights to the issuer form. STARD alternate
EQUATOR article PDF has CC-BY-NC-4.0 notice, not unrestricted redistribution.
The `run-issuer-column-probe` job also attempts fixed primary ARRIVE XML
and the EQUATOR-hosted STARD manifestation; retain metadata and fingerprint
receipts only. Two pure source-identifier RED/GREEN regressions passed in
isolation; full hosted verification and actual source receipts remain required.
