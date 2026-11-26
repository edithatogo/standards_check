# Semantic reconciliation qualification (T01.5d–g)

## MoSCoW and evidence boundary

- **Must:** separate guideline families between development and held-out evaluation; preserve source fingerprints, both NLI directions, contradiction and neutrality; calibrate only on development cases; record false acceptance, false holds, coverage, per-family outcomes, runtime and exact model hashes.
- **Must:** candidate-only recommendations, never rights, methodological review, or canonical admission. Missing model/labels/overlong pairs are held, not truncated or interpreted as agreement.
- **Should:** compare lexical, classical marker, dependency-only and combined classical/dependency scores against bidirectional NLI using the same frozen cases. Evaluate paired errors and uncertainty on independently labelled actual guideline families before selecting a production method.
- **Could:** benchmark a decision model or tiny generative model only when held-out evidence identifies a residual error that such a model could plausibly resolve. Verify exact licence, artifact/runtime compatibility, structured output, and source-span accuracy first.
- **Won't:** download models in routine regression CI or execute remote model code; introduce a service, vector store or auto-approve any candidate.

```mermaid
flowchart TD
  A[Frozen pair ledger] --> B[Family-disjoint dev and test]
  B --> C[Lexical and rule baseline]
  B --> D[spaCy dependency arcs]
  B --> E[Pinned local ONNX forward and reverse]
  C --> F[Development-only thresholds]
  D --> F
  E --> F
  F --> G[Held-out metrics and directional errors]
  G --> H[Candidate diagnostics only]
  G --> I[Independent review and model retention decision]
  I -. residual error justifies .-> J[Decision or tiny model trial]
```

## First experiment

Thirty-six original synthetic pairs (12 dev, 24 held-out): PRISMA and CHEERS
dev; CONSORT, STARD, ARRIVE and TRIPOD held-out. Exact, active/passive,
conjunction removal, numerical changes, negation, unrelated and reverse
implication. These are analyst-authored labels frozen before execution,
**not independent clinical/methodological adjudication or real guideline pairs**.
No verbatim guideline text added.

Fixed model: [cross-encoder/nli-MiniLM2-L6-H768](https://huggingface.co/cross-encoder/nli-MiniLM2-L6-H768)
revision c847a3c0e1cad93a5343183ef183f3044e3fc7c2; Apache-2.0; quantised
ONNX AVX2 file SHA-256 44391a5241a62e0083c1a8899a71e69a092b95aea5ba89e14062925468eceac7.
Official config label order contradiction/entailment/neutral. No remote code,
no Hugging Face inference. Hosted CPU runs explicitly when experimental inputs
change or manually dispatched. spaCy en_core_web_sm 3.8.0 is a reference
pipeline; record exact installed versions and CPU. Do not infer training
independence of external model from our family split.

Predeclared threshold grid .5/.6/.7/.8/.9/.95/.99/1.01. Select max dev true
accepts at zero dev false accepts, break ties at higher threshold. 1.01 is
abstain-all. Test metrics are descriptive for this tiny curated benchmark
and not production operating thresholds. NLI scores must have finite
probabilities in both directions, both top labels entailment; report the full
directional confusion. Exact surface agreement remains separately reported.

## Independent actual-source qualification — blinded model subagents

No human labelling or adjudication is required for this benchmark. Use two
stateless model-agent processes with distinct pinned Apache-2.0 GGUF weights
(Qwen2.5-1.5B-Instruct and SmolLM2-1.7B-Instruct), neither the MiniLM comparator.
Freeze the family-disjoint actual-source and candidate pair ledger before
inference. Give each agent only opaque ID and A/B text; hide guideline-family
split, constructed control class, other votes, and algorithmic predictions.
Use independently generated structured five-class judgements and exact unique
supporting spans. Invalid, missing, or conflicting votes abstain. Never
fabricate a third adjudication or equate agreement with ground truth.

Source-derived controls cover equivalent, additional obligation (narrower),
weakened obligation (broader), negation (contradictory), and different
requirements (indeterminate); the agents independently assess the actual
relationship rather than receive those intended classes. Keep real legacy
discrepancies separate from constructed controls. Reuse exact source and
table pins; unavailable or changed sources stay held. No source text, agent
quotes, or private pair files in public artifacts. Record model revisions,
weight hashes, prompts, input digests, span offsets, runtime, coverage and
per-class agreement and errors. PRISMA is development; CHEERS, CONSORT and
TRIPOD are held out when their exact source pins can be replayed.

Escalation gate predeclared: at least ten held-out consensus pairs, at least
two held-out families and 50% agreement coverage; at least two false
equivalences or two errors within a class with at least three consensus
examples. Only then evaluate one targeted additional NLI or decision model.
If insufficient agreement, report an adjudication deficit, not a comparator
accuracy claim. Small models are fallible and may share training biases.
The benchmark is automated candidate evidence, not rights, methodological
authority, or canonical admission. Existing external admission gates remain
distinct.

```mermaid
flowchart TD
  P[Pinned actual source and candidate pairs] --> F[Frozen family split and pair digests]
  F --> B[Opaque A/B input without labels or predictions]
  B --> Q[Qwen adjudicator]
  B --> S[SmolLM adjudicator]
  Q --> V[Validate exact quote spans and input hashes]
  S --> V
  V --> C{Both agree?}
  C -->|No| A[Abstain]
  C -->|Yes| L[Consensus label ledger]
  F --> N[Existing bidirectional MiniLM comparator]
  L --> E[Unblind and compare held-out errors]
  N --> E
  E --> G{Predeclared escalation gate}
  G -->|Yes| T[One targeted additional model]
  G -->|No| H[Hold or retain baseline]
```

Four isolated RED/GREEN tests passed for blinding, span validity,
directionality and escalation gating. Actual model-agent and real-source
execution must be established by its hosted receipt; this plan is not a
claim of completed adjudication.

## Reproduction

```sh
python -m unittest tests.test_semantic_benchmark -v
python -m scripts.semantic_benchmark --cases contracts/examples/semantic-reconciliation-synthetic-v1.json --assets /path/to/pinned-assets --output /tmp/semantic-receipt.json --revision "$(git rev-parse HEAD)"
```

Three isolated RED/GREEN tests of the deterministic scoring/split core passed
locally. Full code and actual model/dep execution require hosted artifacts.
No decision/tiny-model benchmark is justified before seeing residual held-out
errors. The user requested a benchmark, not admission. Track 05 remains the
independent qualification owner. #111/#95/#82; depends on #150.

## Second controlled qualification: five classes and independently blinded agents

First actual receipt 14920298460: 3/22 consensuses, 19 abstentions; invalid/missing quote spans dominated. Qwen1.5B seven non-abstentions, SmolLM1.7B nine; several direction errors. Replace generated quotations with numbered input-line evidence (selection is checked against exact offsets, not claimed proof of reasoning); upgrade to independent Qwen3-4B and Phi-4-mini quantized GGUF processes. No human labelling. Weight provenance: [Open4bits Qwen3](https://huggingface.co/Open4bits/Qwen3-4B-Instruct-2507-GGUF/blob/7ddd64cfdb879bd66e42cdf94c11debd3d596ee7/qwen3-4b-instruct-2507-Q4_K_M.gguf), [Phi-4-mini MIT quantization](https://huggingface.co/GainPublications/Phi-4-mini-instruct-GGUF); check exact published SHA-256, resolve Phi's repository revision before download and record it. Both are third-party quantizations, no remote executable code, no production dependency.

Use PRISMA-P development, CHEERS and SPIRIT held out. SPIRIT's repository DOCX SHA-256 `9159179d53b65f2615135c554e661d40259eedb2d61318c890617f4a49bd1f2d` and exact independent 53-ID sequence must reproduce; candidate document, not refreshed primary authority. Each family supplies four bounded real rows, forming two independent-check pairs; derive five controlled relationship labels per pair by enumerated truth sets. State independence explicitly in the controlled examples. Equal, strict subset/superset, disjoint and overlapping incomparable sets give the five classes. No labels or predictions supplied to judges; natural observed legacy pairs stay unlabelled unless both agents agree. Do not extrapolate formal control results to natural requirements.

**Prespecified gates:** both agents ≥80% accuracy on development controls; ≥10 held-out consensus controls, ≥50% coverage, ≥90% agreement with independent truth-table reference, correct consensus across all five classes and ≥2 held-out families. Report all abstentions. Separate additional-comparator gate on independent formal controls: at least ten held-out pairs across two families and at least two false equivalences or two errors in a class with ≥3 examples. If eligible, compare [DeBERTa-v3-xsmall](https://huggingface.co/cross-encoder/nli-deberta-v3-xsmall/commit/03d06b2f6f06023bd596151a16477e2fcec601fb), Apache-2.0 quantized ONNX (published SHA-256 checked), against MiniLM with identical fixed five-class mapping and .95 equivalence threshold; report paired fixed/introduced errors. No additional model on failed gate, no production promotion. The new held-out cohort is independent of the earlier tiny synthetic threshold experiment, but intentionally constructed controls not external natural ground truth.

Four isolated tests were run RED (missing module) and GREEN (all pass) on the deterministic core. Full source preparation, model inference and exact-head CI require hosted receipts. No ordinary CI model downloads. Workflow artifacts exclude both input text and weights.

## Actual second experiment and witness-protocol correction

[Run 45398138785](https://github.com/edithatogo/standards_check/actions/runs/45398138785), [artifact 14922043306](https://github.com/edithatogo/standards_check/actions/runs/45398138785/artifacts/14922043306), tested merge `795a2b26b01afa63581d969fa19afab3f8acf2ad`; ZIP SHA-256 `8be81cbe6c8c60811fbe793424f7f52fcfbe60eb0ad13d62792ae89dcceb258b`; receipt SHA-256 `ee6f4f73d1e987221816b2c5e8eafd0165bf5728de64060c1dea45b2c1c846db`. 30 formal controls across PRISMA-P, CHEERS and SPIRIT, six observed legacy pairs. Both dev accuracies 60%; held-out agreement 7/20 (35%), all seven correct (three equivalent, four contradictory); three classes absent. Gate failed. All sources obtained; observed natural held-out consensus one of two, neither NLI model agreed with it. The formal-control escalation gate passed: MiniLM 12/20 correct, DeBERTa 18/20, six fixed/zero introduced, zero false equivalences among 16 non-equivalent controls for both, scoring 0.580s and 0.758s. Class correct counts (equivalent/narrower/broader/contradictory/indeterminate): MiniLM 3/2/2/4/1; DeBERTa 4/4/4/4/2. No production replacement or admission. The residual problem is direction-of-implication judgement, not unavailable evidence spans.

Keep all thresholds unchanged. **Witness protocol v2:** each blinded judge evaluates which of four independently specified report scenarios satisfies each formal requirement separately. Do not show reference masks, classes, comparator predictions or other votes; deterministic relation calculation is applied only to model-generated scenario sets, with invalid sets or evidence selections abstaining. Retain both vote arrays and protocol/prompt hashes. Natural pairs still use the original direct five-class judge, and are never assigned formal truth-set labels. Use ranks 4–7 of the previously frozen source-row selection for existing families, disjoint from the previous anchors; additionally attempt pinned repository CONSORT 2025 DOCX (exact 42-ID sequence, Git blob a1bf7fa3b9c019c5360750cd4981db73cccc3add, SHA-256 computed and retained). No publisher-authority promotion. Same prespecified gates on the new control cohort; family effects already observed from the prior experiment limit external generalization. Phi weight repository now fixed to the exact observed revision a8bb35ae595c241309e8186ec19690dd3b6b01e7. Four focused witness tests RED missing module then GREEN; new actual benchmark required. Do not weaken or waive consensus gate.

## Witness-v2 observed failure and bounded condition-extraction follow-up

[Run 45400872869](https://github.com/edithatogo/standards_check/actions/runs/45400872869), [artifact 14924523529](https://github.com/edithatogo/standards_check/actions/runs/45400872869/artifacts/14924523529), tested merge e1a03e4ee0d7925d95d2e36e30f334d7012d002c. ZIP SHA-256 1047f28eba5ab300fbb3419c94f9a39275964d246d79b6a45c7fc2040ecc5c0d; receipt d23c3a52ad1e626cab22997df232a90ed30f6f22e78690bb77b1b1a83ac622b3. Four source families, 40 formal controls (10 development, 30 held out), five natural pairs; no source holds. Both judges development 2/10; consensus 17/30 (56.7%), correct 6/17 (35.3%), only equivalent correct across three test families. No natural consensus. Typical failure: P-only incorrectly selects [2,3] or [3], omitting scenario 4, rather than [3,4]. The scientific gate failed; greater agreement is not sufficient. Repeat NLI escalation triggered: MiniLM 16/30, DeBERTa 29/30; 13 fixed, zero introduced; 2/24 vs 0/24 false equivalences. One DeBERTa indeterminate-to-contradictory error. Wall scoring 4.241s vs 3.746s. Retain DeBERTa experimentally, not production promotion.

Condition-v3 isolates the explicit condition recognition step for formal controls: each model selects P, Q, NOT_P or P_AND_Q separately, with numbered operative line evidence. The existing truth-set evaluator derives the label; no reference labels or comparator results enter the prompts. Invalid/unsupported condition or missing operative line evidence abstains. Do not confuse this narrower compositional diagnostic with independent natural-language adjudication. The existing development and held-out qualification thresholds remain unchanged; use fresh source-row ranks 8–11 for existing families, 4–7 for CONSORT, hold unavailable/insufficient rows. Natural pairs continue direct blinded adjudication and remain separately reported. Two isolated condition-vote tests failed RED (missing function), then passed GREEN together with four existing witness tests. This is the bounded final controlled-protocol correction; if failed, report the failure rather than endlessly tune on test results. No model or pack promotion and no merge before actual scientific gate. Current main includes #154 and #157; preserve their independent NLP runtime pin and source/rights boundaries.


## 26 November integration hold

Current-base required checks first. Model jobs on the experimental branch now require explicit same-repository PR label `run-semantic-benchmark` (apply only after the exact-head deterministic checks and review prerequisites are satisfied), or manual dispatch where the workflow is registered. Do not apply the label on routine updates. Prior experimental receipts and their failed scientific gate are retained. The existing coverage threshold is not waived; prior artifact 15029995445 records combined 85.86% (7987/9302), including the three experimental scripts. Correct the lint and add meaningful deterministic coverage for input, model-pin, receipt and decision boundaries. Before wiring this benchmark into the requirement graph, normalize the legacy direction convention (candidate B relative to source A) to the draft RGI-06 convention (A relative to B), with inversion and contradiction tests. Do not relabel historical raw receipts or treat model agreement as independent truth.

## 26 November repair and scientific disposition

The condition-v3 run [45405499908](https://github.com/edithatogo/standards_check/actions/runs/45405499908)
and rerun artifact 15030976063 remain failed scientific evidence: development accuracy 0.60/1.00,
18/30 formal held-out consensuses, all correct but only narrower, contradictory and indeterminate.
No natural held-out consensus. DeBERTa 25/30 versus MiniLM 17/30; 12 errors fixed and four introduced.
The earlier witness-v2 and direct-judge failures remain intact. Do not reclassify these results as
independent methodological validation or tune repeatedly to achieve a pass.

The head before repair failed [Assurance 45637024692](https://github.com/edithatogo/standards_check/actions/runs/45637024692):
95 Ruff findings and combined Python coverage 86.28% (90.5% required).
Reconcile the branch with main `341f5388`; preserve all source and review holds.
[Ruff 0.17.6 diagnostic 45751013372](https://github.com/edithatogo/standards_check/actions/runs/45751013372)
fixed the final two lint findings, formatted four scripts, and reported all checks passed for those scripts.
Verified patch application by matching the four resulting Git blob prefixes; the temporary read-only
diagnostic is removed. New offline behavioral tests cover actual local source preparation, pinned
model and runtime boundaries, vote integrity, malformed outputs, candidate-only CLI receipts and
gated comparator execution using synthetic inference stubs. These are software tests, not model
qualification. Full current-head hosted assurance is required; no coverage exemption.

The `legacy_to_rgi06` adapter explicitly inverts narrower/broader (legacy B relative to A;
RGI-06 A relative to B), preserves the other three classes, returns no mapping for abstention
and rejects unknown labels. Six isolated RED/GREEN tests against the extracted relation logic
passed; current-head integration is still required. Historical raw labels and receipts are unchanged,
and the adapter does not admit a relation to the graph.

The [independent-family intake](../../source-reconciliation/independent-family-intake-20261126.md)
is the next prerequisite: source rights, independent structure/wording and family-component
eligibility must pass before a fresh frozen confirmatory sample. CONSORT and SPIRIT belong to
one harmonized independence component; PRISMA descendants are also correlated.
The condition-v3 experiment was the bounded final controlled-protocol correction. Preserve its
negative result rather than continuing to tune on familiar controls. The prospective complementary
d1-2B experiment remains subject to #159 and the existing #158 protocol, not a substitute for
qualified reference evidence. Do not authorize further model runs or merge this draft until the
predeclared scientific gate and all current-head protected checks are satisfied.

## 26 November review handoff — engineering passed, scientific hold

### Engineering acceptance on the tested head

[Assurance 45751485991](https://github.com/edithatogo/standards_check/actions/runs/45751485991)
passed on head `2779f19ec45092137fcdc3baaa0617308692723c`, tested merge
`0f3a01d536f5a70e82d3aaaaced9d75b4c41d37c`, receiving base
`341f5388bae99e7a5be9f7a29d04e2ed65b7f6dc`. All seven required workflow groups
passed; optional Offline AI security was still queued at observation.
[Python coverage job](https://github.com/edithatogo/standards_check/actions/runs/45751485991/job/139681007791)
reported **724 passed, 3 skipped, 2 warnings; 91.59% combined branch coverage** versus
the unchanged 90.50% floor. Blind adjudication 90.42%, five-class benchmark 95.31%,
semantic benchmark 99.05%, witness adjudication 100%. Workflow policy, all three
platforms, dependency review, mutation boundary, API and Rust coverage and Codecov
upload jobs passed. This verifies software behavior, not actual model quality.
Codecov patch status is advisory and not inferred from successful upload.

### Fresh-family eligibility and pre-freeze reservation

Downloaded and independently verified [main source census 45740480356, artifact 15080683676](https://github.com/edithatogo/standards_check/actions/runs/45740480356/artifacts/15080683676).
ZIP SHA-256 `2aa6e7abc1564ae0966973a98417c48797257d1ad57cfa7a854f15310a4835ed`;
survey SHA-256 `9bd9f5acc05c68f0e85796b5f7d9a83e8d6885c0ca6be98c8b5801ddd3e6e206`;
EQUATOR revision `388e294f05d4d55cf6fc01ddf56b6ad48577b190`.
All eight priority manifestations are held: ARRIVE, STROBE, STARD, TRIPOD+AI,
CONSORT and SPIRIT BMJ, and CONSORT and SPIRIT PLOS. The PLOS transport attempts
returned OSError, Europe PMC timed out and PMC OAI did not provide usable sources.
The census records 720 directory identities; of 186 bulk records, 183 were deferred,
two held, and one inventory observed but not reconciled. No canonical packs promoted.

Reuse the existing [independent-family intake](../../source-reconciliation/independent-family-intake-20261126.md)
and source retrospective rather than creating another crawler or duplicating acquisition.
Reserve these prospective slots before seeing new inference results. These are **not** an
eligible frozen sample, a source repin, or a publication design freeze.

| Independence component | Prospective slot | Candidate evidence and unresolved gate |
| --- | --- | --- |
| ARRIVE 2.0 | Development | PLOS DOI 10.1371/journal.pbio.3000410; [issuer checklist resources](https://arriveguidelines.org/resources/author-checklists). The existing article receipt held 21 main-row fingerprints for block boundaries; independently compare ordered subitems and wording in the issuer and journal formats and verify exact source rights. |
| STROBE 2007 | Held out 1 | PLOS DOI 10.1371/journal.pmed.0040296; [issuer combined checklist, PDF and Word](https://www.strobe-statement.org/checklists/). Verify the combined edition and conditional design-specific branches, independent anchors and manifestation-specific licence; [issuer](https://www.strobe-statement.org/?id=checklists) requests contact before republication. |
| STARD 2015 | Held out 2 | DOI 10.1136/bmj.h5527; [EQUATOR source and co-publications](https://equator-network.org/reporting-guidelines/stard/). BMJ article footer says CC BY 4.0 but footnote says CC BY-NC 4.0; retain rights hold until the exact manifestation and use are resolved. Check the complete ordered item/subitem sequence against independent representations. |
| TRIPOD+AI and related prediction guidance | Reserve/held | Prior attempted adjudication source was held; avoid allocating any potentially previously exposed component without an explicit leakage audit. |
| PRISMA descendants, CHEERS, CONSORT/SPIRIT | Historical only | Exclude from the new confirmatory components; related editions, extensions, translations and co-publications do not count as separate independent families. |

Local exact-byte transport for issuer ARRIVE and STROBE downloads and PLOS ARRIVE
article failed DNS resolution. A separate ARRIVE download attempt also failed. Web source
discovery establishes the alternate source routes, not receipt-level source qualification.
No new source wording was acquired, recorded or redistributed by this increment.
Current eligible fresh family count: zero; no actual frozen pair ledger or confirmatory run.
Do not change the candidate splits after outcomes are seen. If a component fails eligibility
or independence, make and document a prospective amendment before any predictions.

On source qualification, freeze exact bytes, source-local rights, independent ordered structure
and wording/anchors, connected family components, eligible complete-pool denominators and
selection algorithm in the existing versioned publication contract. For the bounded formal
control diagnostic retain the same five classes, original development and held-out thresholds
(at least 10 consensus, 50% coverage, 90% accuracy, all five classes and two independent held-out
families; both dev agents at least 80%). Use the existing condition-v3 judge protocol unchanged,
with genuinely fresh sources, and retain every failure. For natural-source E2 use the separate
prospective three-agent source-only protocol in the publication plan, not truth-table labels
or a two-model vote as ground truth. Freeze the actual eligible sample and numerical analysis
limits before either confirmatory execution. No run label or model acquisition now.

### Paired historical complementary-model assessment (descriptive only)

Downloaded the three original artifacts and verified each ZIP hash against the GitHub artifact
metadata. Joined MiniLM and DeBERTa records by unique pair ID; checked matching reference labels
and family on both sides. Retain constructed held-out controls only for this table. These are
adaptively investigated historical datasets, not an independent confirmatory sample.

| Receipt | N | Both correct | MiniLM only | DeBERTa only | Both wrong | Disagreements | Shared same wrong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [14922043306](https://github.com/edithatogo/standards_check/actions/runs/45398138785/artifacts/14922043306) | 20 | 12 | 0 | 6 | 2 | 7 | 1 |
| [14924523529](https://github.com/edithatogo/standards_check/actions/runs/45400872869/artifacts/14924523529) | 30 | 16 | 0 | 13 | 1 | 13 | 1 |
| [14926383953](https://github.com/edithatogo/standards_check/actions/runs/45405499908/artifacts/14926383953) | 30 | 13 | 4 | 12 | 1 | 16 | 1 |

Condition-v3 receipt SHA-256 `e7768d40f843a1743a9bbdb1bed6090c454924f5637983dfcff776f833392a4c`.
The last row's disagreement flags 12 of 13 MiniLM errors and four of 17 correct MiniLM
decisions (16 flagged, one shared error remains unflagged). Those four baseline-only
correct pairs comprise three equivalent and one indeterminate case. Thus disagreement
may enrich triage, but agreement cannot certify correctness and replacing the baseline
would lose valid decisions. Historical natural held-out consensus counts: 1/2, 0/3,
0/2; both comparators disagree with the single usable natural reference. No pooled
accuracy, confirmatory inference, fixed-budget utility, or production selection claim.
D1-2B remains the orthogonal typed-decision candidate under #158/#159; no new run
or performance claim before a fresh reference, pinned local runtime and model assets,
review budget and adoption limits are frozen.

### Disposition

The maintainer requested ready-for-review status. Engineering and protocol review may proceed
without claiming the scientific gate has passed. Do not enable auto-merge or merge this PR
until actual eligible-family/reference qualification and current-head required checks pass.
No threshold waiver, canonical promotion or scientific claim. Review should explicitly verify
the source rights and independence slots, direction adapter, reproducible negative receipts,
and confirmatory design. Keep #111/#158/#159 and T01.028–030/T01.043/T01.052 open.

## LFM development experiment — prospective design, 26 November

The maintainer requests testing Liquid AI models. The last condition-v3
reference failure is unchanged; do not iterate prompts on those formal held-out
controls. LFM3's newer hybrid architecture and native d1 decision approach
are plausible orthogonal methods, not established domain improvements.
Retain MiniLM and DeBERTa-xsmall as fixed comparators. Exact label order, both
directions, confidence and abstention semantics are unchanged.

**Design:** reuse the original 36 synthetic analyst-authored pairs only. Treat
all cases, including the former test stratum, as historical development; no
confirmatory claim, no threshold tuning or source wording. Preserve the original
split for descriptive strata. Opaque identifiers and source/candidate-only
inputs; existing five-class generative rubric and numbered evidence validator.
Compare individual challenger outputs to both incumbent predictions on identical
pairs. Report full confusion, abstentions, false equivalences, unique catches,
harmful changes, shared misses, disagreement and elapsed time. Do not infer
fixed-budget utility or natural-source qualification from this diagnostic.

| Challenger | Exact publisher revision | GGUF SHA-256 |
| --- | --- | --- |
| [LFM2.5-1.2B-Instruct Q4_K_M](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF/commit/4e7112f1437070cf9f49aeb93ad965b946029f75) | 4e7112f1437070cf9f49aeb93ad965b946029f75 | b1b3de114215d9507409a662a501a631095a479a419584e8a2ded6304b19b4f5 |
| [LFM3-1.7B Q4_K_M](https://huggingface.co/LiquidAI/LFM3-1.7B-GGUF/commit/b3f2ae5d73cd3c91bf40e8ba752c648aa05dffdf) | b3f2ae5d73cd3c91bf40e8ba752c648aa05dffdf | 3793e1e6e2266919d6e015287221b41100175a98eddaba92e111aed3b05c93c4 |
| [d1-2B Q4_0](https://huggingface.co/LiquidAI/d1-2B-GGUF/commit/4a181094d1b6addfaa3a0956f78e7ab2aa406a0c) | 4a181094d1b6addfaa3a0956f78e7ab2aa406a0c | ba3f4f437746636dfd51e3b68d5a7858b56de44b54299a189f91c246db0a08ea |

All three use the LFM Open License v1.0, not an OSI-approved permissive
licence. The publisher licence conditions commercial use above its revenue
threshold; this is a bounded non-commercial research experiment only, no
redistribution of weights or institution-wide deployment decision. Retrieve
and retain the exact revision licence. Native runtime [llama.cpp b11960](https://github.com/ggml-org/llama.cpp/releases/tag/b11960)
supports the LFM3 architecture and typed System One route. Official Ubuntu
CPU archive SHA-256 31cc3a6bc638ac6c48dc4b1b74888f1eaadf3d14227c1e5f67daf9a49541d97a,
verified from release asset metadata. No remote model code, no external
inference, no persistent server, no production dependency. Bind to loopback
only, terminate after each run, retain model/runtime/fixture receipts.
Generative temperature 0, seed 724, output cap 120 as before.
For native d1, compare direct five-class choice with separate A-implies-B,
B-implies-A and joint satisfiability choices. Validate probability support,
finite sums and argmax; abstain on ties, unknown or incompatible implications.
Direct threshold 0.5 (0.95 equivalence); each directional choice 0.8.
These predeclared exploratory thresholds are not calibration claims.
Native d1 route supports choice/score/noul; extraction is not yet supported.
No span-validity or independent adjudicator claim for the decision route.
The d1 Q4_0 choice is the verified bounded low-resource asset, not the
publisher's suggested Q8_0 fidelity reference. If useful, repeat on pinned
Q8_0 as a quantization ablation, not as a post hoc confirmatory result.

The LFM2.5-1.2B-Thinking model is a further candidate (official Q4_K_M
revision 6eef5895049f444e3436c6f583207e610a1485ce, SHA-256
7223a2202405b02e8e1e6c5baa543c43dc98c1d9741a5c2a0ee1583212e1231b).
Assess separately with a declared reasoning token budget and otherwise matched
conditions, only after the first results. A larger NLI comparator (DeBERTa-v3-large)
or ModernBERT-large NLI is a later scale/architecture ablation if residual errors
justify it. Prefer separate implication and compatibility assessments with
deterministic composition, reverse-order consistency, explicit applicability,
modality and counterexample evidence to adding a majority vote. For natural E2,
use independent source-only agents with locked reference and evidence; keep
abstention separate from resolved indeterminacy. For E3 freeze review budget,
tolerated harm and minimum useful gain before any new independent data are scored.

The existing five-class workflow adds a separate explicit label
`run-lfm-development`. It does not invoke the controlled-consensus job.
The source-probe job reuses the existing primary survey for ARRIVE/STROBE/STARD
and retries bounded issuer PDF transports without publishing content or repinning.
Transport success alone is not independent structural or rights qualification.
The source freeze and original scientific gate remain fail-closed. No merge or
auto-merge on these exploratory results. The first native decision-contract
unit tests were run in isolation (8 passing); the integrated harness and actual
inference require hosted receipts.


## Native inference observations and bounded follow-up

[Run 45754736904](https://github.com/edithatogo/standards_check/actions/runs/45754736904),
head 3d09ca6, tested merge 17a0bc78. Downloaded and SHA-256 verified the
[d1 artifact 15087556116](https://github.com/edithatogo/standards_check/actions/runs/45754736904/artifacts/15087556116)
(d796bdbc6a84830a7e3c702fbc6d08ce9fe9430175db5a4610b0ad0dfa2c2ae9),
[LFM3 artifact 15087517304](https://github.com/edithatogo/standards_check/actions/runs/45754736904/artifacts/15087517304)
(a0f979830385dfcf652edcf6bdfae1be8b7ca93bebe5f31a7c0ca380bf1df9d6),
and [source artifact 15087277719](https://github.com/edithatogo/standards_check/actions/runs/45754736904/artifacts/15087277719)
(24bf29448032d882d2f4d16a96090b471308b4641e69c4dd20364fe3f7a78ba8).
The original 36 synthetic cases remain development only.

| Method | Correct /36 | Abstentions | False equivalences |
| --- | ---: | ---: | ---: |
| MiniLM | 28 | 2 | 0 |
| DeBERTa-xsmall | 28 | 1 | 0 |
| d1-2B direct | 15 | 19 | 0 |
| d1-2B directional | 11 | 25 | 0 |
| LFM3 (120-token cap) | 0 | 36 | 0 |

d1 direct: against either incumbent, 13 both correct, 15 incumbent-only,
2 d1-only, 6 both wrong; no reason for production replacement. Directional
compilation was over-conservative, with no unique correct cases. d1 215.38 s.
LFM3 317.15 s, all 36 requests exhausted the 120-token limit in server logs,
all evidence spans absent. No valid LFM3 classifications; preserve this
failure. LFM2.5-Instruct failed at licence retrieval (404 at the weight-upload
commit). Repin to publisher revision 012803cf70d6cdcf698f0c65fa8f9b7175128770,
which adds LICENSE without changing the Q4_K_M hash. The exact d1 and LFM3
artifacts contain LFM Open License v1.0, not Apache-2.0. In particular,
section 5 conditions commercial use at the USD 10m annual revenue threshold.
Keep experimental noncommercial research boundary; do not confuse a
runtime/library licence or another checkpoint's licence with these weights.

Follow-up development-only budget ablation, without modifying labels,
rubric or the held-out scientific gate: LFM3 disable thinking via its
documented chat-template argument, max 256 output tokens; Instruct max 256;
LFM2.5-Thinking 512 (reasoning enabled); LFM2-2.6B Q4_K_M 256 as larger
LFM-family comparator. Thinking and 2.6B official immutable commit prefixes
b719458 and 7949a4d must resolve to complete 40-hex revisions before any
acquisition, and the previously verified weight hashes must match. Preserve
response finish reasons; truncate-to-abstain, no raw generated reasoning
retention. No new reference labels or threshold tuning. Existing protected
tests on head 3d09ca6: 741 passed, 3 skipped, 91.69% combined Python coverage
(99.21% new module); workflow policy failed on Ruff formatting of a tuple
return, corrected separately. Full checks on new head still required.

The source retry retrieved exact issuer PDF bytes: ARRIVE full author checklist
91e191d495f96472c0896ae3e489e9a12953648179f2a2a06b7035bb97a7327c (105723 bytes)
and STROBE combined checklist
63c2af4d91d04f5b211f4277a267a23da5d313fe927753c08f98139a8aab41b8 (19826 bytes).
All three primary article transports remained held. Follow-up replays those
pins and tries issuer ARRIVE poster and publisher PDF manifestations; reuse
the existing compare_guideline_formats reader with unchanged independent
denominators. Source drift, parser, identity, nested structure and rights holds
remain distinct. STROBE has no independent complete row denominator in the
current registry. Do not infer eligibility from byte retrieval or same-reader
agreement. Scientific cohort freeze remains held, zero admitted at last run.


### Source structural follow-up and Thinking asset correction

[Follow-up 45755775838](https://github.com/edithatogo/standards_check/actions/runs/45755775838)
source artifact 15087069857 ZIP SHA-256
81a8e111efc9e06264618a310da775791a075cc0ca04aed6965b58317c800276
downloaded and verified. Reproduced both issuer PDF pins; also retrieved ARRIVE
issuer poster (64a8f03f02496eac7eed4ba2b587ad8b9365670b946eb167bc68da5703d6c604),
ARRIVE publisher PDF (00957028eae5b9935a86a8bc912fd2a85b95ca9be11bf175fbfea65d97fe83fc),
and STROBE publisher explanation PDF (41de61bb60662cd007f0cb4655ae00c4fac3b6a8c2ab616a62cd741870947e46).
Five PDFs, zero comparable numbered rows from the maintained generic reader.
ARRIVE all 21 main items held, STROBE independent denominator absent, STARD
publisher HTTP 403. Primary XML routes all held. Next source work is
edition-specific column/subitem reconstruction using the existing readers and
source-local rights review, not repeated downloads or a threshold waiver.

LFM2.5-Instruct actual corrected-revision run: 9/36 correct, 0 abstentions,
0 false equivalences, six unique correct vs either incumbent, 25 baseline-only
correct, two shared misses. Retain poor standalone performance and possible
triage complementarity; 82.99 s. LFM2.5-Thinking failed at b719458 because
the fetched bytes did not match the earlier published Q4_K_M SHA-256.
Restore the exact publisher weight-upload revision 6eef5895049f444e3436c6f583207e610a1485ce
with the same published hash, retrieve LICENSE independently at the explicitly
pinned later publisher revision b719458, and retain both fully resolved
revisions. Do not repin observed mismatching bytes. Target only Thinking
on a separate label/concurrency group so other in-flight experiments remain
intact. No inference claim until actual receipt and no source/pack promotion.

Retrospective d1 calibration diagnostic on the verified 36-case receipt:
raw six-way argmax 31/36 correct, 35 covered, one abstained, zero false
equivalences. Uniform confidence thresholds 0.50, 0.60, 0.70, 0.80 yield
21/23, 18/19, 14/14, 6/6 correct among classified cases respectively.
Multiclass Brier score (sum across six classes) 0.33054; log loss 0.69864.
No threshold selected or revised for confirmation. Do not infer independent
calibration or safety from these development controls.

### Completed native LFM output-budget and scale ablations

All four successful follow-up ZIPs were downloaded and independently hash-verified.
Preserve the same 36 historical synthetic pairs and original decision rules; no new
confirmatory reference or production selection. Exact checked-out merge, receipt and
asset/license/environment files are in each artifact.

| Model / run | Correct /36 | Abstained | False equivalence | Unique correct vs each incumbent | Wall s | Peak RSS KiB | Artifact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| MiniLM / DeBERTa-xsmall | 28 each | 2 / 1 | 0 | baseline | see each receipt | separate | existing |
| LFM3-1.7B, no-thinking 256 | 21 | 0 | 0 | 1 | 181.116 | 2086032 | [15088176142](https://github.com/edithatogo/standards_check/actions/runs/45755775838/artifacts/15088176142) |
| LFM2-2.6B 256 | 26 | 0 | 0 | 7 | 130.054 | 3298364 | [15087841425](https://github.com/edithatogo/standards_check/actions/runs/45755775838/artifacts/15087841425) |
| LFM2.5-Instruct 256 | 9 | 0 | 0 | 6 | 82.989 | 1393608 | [15087756259](https://github.com/edithatogo/standards_check/actions/runs/45755775838/artifacts/15087756259) |
| LFM2.5-Thinking 512 | 12 | 0 | 24 | 1 | 63.657 | 1622072 | [15088500295](https://github.com/edithatogo/standards_check/actions/runs/45756199243/artifacts/15088500295) |

ZIP SHA-256, in table order for the four follow-ups:
- 3ae2e54c32e0f3cebc41547d9d672ff9324da62ff9fd6066f2674870e6fdfc36
- 87d674843a96d0d1787fd78098affd57f4963fed9ba731e0425b0415fcee5c43
- 6a6163c93e812c849dde84cc341687b45a3debc6409b9d3b628b87e4b583c683
- 36b60f507aeb01f4a7643d5d6f2ffd7af209e61a78a7c556fe25f56c522ea981

Receipt JSON SHA-256 respectively:
78cedd752a87011a5e7108223c36e4d14a18b49019859195dd7ab689c9c11a17,
d8d00618967d0d0c72ea50753e3b51c8d199d43b97520a0e509939531fb19f77,
24b29ffcb0160a34a4924a3dd2e295c46c42ab7adcd99b81335deae140e6f212,
db76294aeb6c9623b83be46a4b658a3ae28f4cceae6c33127e92d10d3798f2da.
All 36 completions stopped normally per follow-up; the initial 120-token LFM3
failure is retained. No attribution of improvement solely to architecture because
thinking/budget changed together. LFM2-2.6B both correct 19, incumbent-only 9,
challenger-only 7, both wrong 1, disagreement 17. This is descriptive paired
complementarity, not a usable oracle or justified majority vote. Thinking is a
negative safety result: all non-equivalent cases falsely classified equivalent.
Every downloaded checkpoint licence is LFM Open License v1.0. Pin 2.6B resolved
7949a4d1820bb11ce8e735872c31bd2dd7ec9c87; Thinking weight revision remains
6eef5895049f444e3436c6f583207e610a1485ce, licence revision
b71945805f7d4d87dabd73e26098d44bcad6c35f. Retain both original acquisition failures.

Assurance 45756191815 Python job 139695502850 reported 748 passed, 3 skipped and
91.72% combined coverage; workflow-policy failed at formatting in lfm_development.py
line 286. The next commit simplifies that condition, keeping the digest gate.
Current-head hosted checks and scientific gate remain required.

The new [specialist-pipeline protocol](../../../docs/research/specialist-pipeline-protocol.v0.1.0.md)
extends the publication programme without registering these retrospective results as
frozen runs. Prioritise stage-specific evidence, calibrated d1 triage, source-native
and layout-specialised ingestion, extractive tags, retrieval and exact validation.

### Requested specialist challenger panel

The [dated model challenger record](../../../docs/research/model-challengers-20261126.md)
preserves the actual 106-query neural retrieval result and verified artifact
hashes; E11 rerankers now use an exact frozen BGE top-ten pool. Include
K2-Horizon-3.7B, MiniCPM5-2B, d1.2-ultra and Jev 1.13 in the separate
development comparator plan, not the independent reference. Hosted services
require a separate authorized access and budget decision. Source-family and
scientific holds remain unchanged.
