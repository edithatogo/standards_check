# Exploratory results and supplementary analysis — snapshot 1

Status: development synthesis, 26 November 2026. Not a manuscript submission,
scientific qualification, release approval, or amendment of the frozen protocols.

Snapshot: `42b3a00545ebc855295687218deae8a249134938be2fd6e3c441662a1d6e084e`.
The snapshot includes 53 digest-verified hosted archives and 14 local reports
(67 inputs), 141 explicit projections, 79 distinct panel labels and 2,317 metric
records. See [receipt](snapshot-v1-receipt.json), [input manifest](inputs-v1.tsv)
and [projection definitions](panels-v1.tsv). The exact original ZIP and derived
comparison table have been retained in the researcher's personal file Library,
not published in this repository. Repository artefact IDs are not a substitute
for retained bytes: Actions artefacts expire. Raw logs, model/source payloads
and rights-held materials require clearance before public redistribution.
This inventory covers the scoped linked experiments, not all repository history.

## Methods draft

Use paired comparisons within identical cases, candidate pools, reference
standards, budgets and outcome definitions. Distinguish operational census
entries, source rows, editorial positives, authored synthetic cases, authored
formal controls and independently adjudicated references. Preserve the original
split and family grouping. Repeated case-configuration observations are not
independent samples. Treat post-hoc choices, including parent-first, as
exploratory. Retain null and negative outcomes, rejected actions, failures,
abstentions, unsupported proofs and rights-held cases. Do not count referrals
as resolved until an independently adjudicated result exists.

Separate retrieval/candidate-generation failures from ordering failures and
decision failures. Report exact spans, recall at each cutoff, false-equivalence
counts and accepted-equivalence denominators separately. Zero accepted
equivalences does not establish zero conditional false-equivalence risk.
Record resource measures as actually observed (calls, selected words, wall
time, RSS, weights, load time); do not combine heterogeneous timing runs or
infer a matched token or monetary budget. No unobserved cost is imputed.

The offline compiler projects only numeric or null values from pinned JSON
members. The denominator column records panel study size/context, not a
universal rate denominator; precision uses TP+FP, recall uses the appropriate
positive reference, macro recall is averaged by query. Empty values are
unknown/not defined, not zero. Identical arm names across runs do not establish
identical methods. Compare using panel, file, member, selector, arm and metric.

## Results draft

### S1. Source acquisition and structural recovery

| Population | Observed result | Interpretation |
|---|---|---|
| Dated EQUATOR directory | 720 entries | Directory denominator, not independently qualified corpus |
| First bulk checkpoint (205 worklist entries) | 200 deferred; 4 held; 1 observed, not reconciled | No inferred permissions or successful ingestion |
| PRISMA 2020 | 42 admitted source-reconciled rows | One admitted pack; no independent semantic label set |
| Four candidate article editions | 82 pinned rows | Structural qualifications remain held |
| CONSORT 2025 | 30/42 direct topic fingerprints; 42/42 after merge-origin closure | 12 gains, zero losses |
| SPIRIT 2025 | 34/53 direct; 53/53 after closure | 19 gains, zero losses |

The real-source diagnostic uses the literal and DOCX evidence independently
extracted in [run 45808364894, artefact 15110837213](https://github.com/edithatogo/standards_check/actions/runs/45808364894/artifacts/15110837213).
The two manifestations are not independent scientific adjudicators. CONSORT and
SPIRIT share an interconnected guideline lineage. Both intake statuses remain
held; no source or semantic admission follows. The original whole-row comparison
was 41/42 and 53/53 respectively. The narrow subsequent item-26 layout projection
is a separate observation, not a replacement of the original receipt.

For one explicit printed PRISMA cross-reference (13a to 5), bind all 42 pack
requirements to the independently extracted PDF row fingerprints in
[artefact 15105308560](https://github.com/edithatogo/standards_check/actions/runs/45797308061/artifacts/15105308560).
Test every combination of word/character ranking, heading context off/on and
explicit link traversal off/on among the other 41 requirements.

| Ranking | Heading | Rank without link | Rank with link |
|---|---|---:|---:|
| Word TF-IDF | No | 8 | 1 |
| Word TF-IDF | Yes | 7 | 1 |
| Character TF-IDF | No | 4 | 1 |
| Character TF-IDF | Yes | 4 | 1 |

All eight arms executed, each scoring 41 candidates. Single local timings
were approximately 0.0013–0.0040 seconds; context diagnostic plus retrieval
took 0.0206 seconds. Timing includes only this bounded local processing, not
source acquisition, inference or repeated benchmarking. Topic closure
recovered 31/95 additional contexts without loss. Explicit traversal reached
the literal-reference diagnostic ceiling at rank one; it is not an independently
adjudicated semantic-relevance benchmark. Retain the full row/anchor report
`structural-recovery-v1.json` (input manifest) in restricted evidence storage.

### S2. Layout and qualifier extraction

| Comparator | Exact result | Seconds | Peak RSS (KiB) |
|---|---:|---:|---:|
| pdfplumber | rows 1/4 | 0.108915 | 40,868 |
| Poppler | rows 4/4 | 0.013145 | 24,152 |
| Rules | span F1 0.848485 | 0.005473 | 22,236 |
| GLiNER2.5 original | span F1 0.083333 | 9.640118 | 1,138,092 |
| GLiNER clause names | span F1 0.160000 | 9.229019 | 1,140,148 |
| GLiNER operator first | span F1 0 | 9.342108 | 1,142,788 |

Layout fixture: four rows, one nesting link, one footnote, two qualifier links.
Both readers recovered the other expected links. Qualifier fixture: 16
authored cases, 17 exact typed spans. Rules TP/FP/FN = 14/2/3;
original GLiNER = 1/6/16; clause names = 2/6/15; operator first = 0/3/17.
Later clause and per-type arms F1 0.100 and 0.1053; tested supervised
span-boundary and token-BIO baselines F1 0. These small reused fixtures
do not justify a universal comparison of model families. No weights
required for the readers/rules; original GLiNER used 295,567,700 bytes.
Sources: artefacts 15100692740, 15105999587, 15107111276.

### S3. Retrieval, candidate bottlenecks and reranking

| Arm | Macro R@1 | Macro R@5 | Macro R@10 |
|---|---:|---:|---:|
| Word TF-IDF | 0.2547 | 0.3821 | 0.3962 |
| Character TF-IDF | 0.2877 | 0.5236 | 0.6840 |
| BGE | 0.3443 | 0.7201 | 0.8003 |
| BGE then MiniLM on top ten | 0.4009 | 0.6824 | 0.8003 |
| Qwen reranker | 0.3868 | 0.6840 | 0.8003 |
| Qwen embedding, raw | 0.3632 | 0.7013 | 0.8192 |
| Qwen embedding, domain-index instruction | 0.3947 | 0.7343 | 0.8522 |
| Instruction-aware Qwen + BGE fusion | 0.3962 | 0.7626 | 0.8569 |

Costing editorial fixture: 106 queries, 125 known associations, 31 candidate
domains; no independent positives. These are same-fixture exploratory arms,
not a controlled hardware comparison. BGE recorded 0.5113 s; the BGE+MiniLM
arm 1.5545 s. At the fixed BGE ten-candidate pool, 97/125 known positives were
retrieved; 28 were absent before reranking and 87/125 at the five-candidate
cutoff before reranking. MiniLM gained four and lost nine at five. The fused
pool has its own paired accounting; do not mix pool identities. In a separate
10-query synthetic graph fixture, word R@5 rose 0.90 to 1.00 and character
0.90 to 0.95; parent-only matched full-graph gain. Rewired controls and
heading-only baselines are necessary. All other tested rankers, ablations,
costs, failures and negative observations remain in the compiled panels
and original receipts. Sources: 15088716936, 15105542356, 15090675906,
15090704998, 15105947458, 15108373345 and the ranker-specific archives.

### S4. Decision and proof (separate panels)

| Arm | Correct | Abstained | False-equivalence count |
|---|---:|---:|---:|
| DeBERTa, full authored fixture | 28/36 | 1 | 0 |
| K2 Horizon direct | 29/36 | 0 | 5 |
| LFM2 direct | 26/36 | 0 | 0 |
| d1 initial direct | 15/36 | 19 | 0 |
| LFM2.5 thinking direct | 12/36 | 0 | 24 |
| MiniCPM5 direct | 7/36 | 29 | 0 |
| Lexical terminal, reused test cases | 18/24 | 6 | 0 |
| Strict NLI terminal | 20/24 | 2 | 0 |
| Proof-required terminal | 12/24 | 10 | 0 |
| Formal verifier, separate authored controls | 4/4 | 0 | 0 |
| Lexical, same formal controls | 1/4 | 0 | 3 |

The 36-case full-fixture observations include development cases. The
24-case terminal panel uses exposed held-out-family cases; the four formal
controls were deliberately constructed and are not an estimate of error
prevalence. Neural agreement can share wrong directional/scope decisions.
Eight true equivalences remain withheld by the proof gate in the 24-case
fixture. On 14 matched accepted cases, confidence-only advisory was 14/14
correct and proof-required 12/14; this cannot establish safety equivalence.
Separate historical failed five-class qualification and generation failures
are preserved. No unsupported proof is counted as acceptance.

### S5. Acquisition factorial, costs and policy

On the 24 exposed test pairs, repeated search gave 18 correct/48 retrieval
calls; deficit routing 22 correct/44 retrieval calls + 4 semantic calls;
early deficit routing 22 correct/29 retrieval calls + 4 semantic calls.
No review resolutions. Original acquisition factorial executed eight cells
with 16 feasible orders (384 repeated outcomes): expansion plus parent
23 complete/18 correct at 48 calls; adding reranking retained 23/18 at
72 calls. Order and costs matter. A separate matched two-new-fragment
comparison raised completeness from 18/24 to 20/24; hybrid showed no gain
over the best matched arm and both rank-only approaches reached 20.
These are not independently adjudicated outcomes.

| One-call or adaptive policy | Complete /24 | Gated correct /24 | Calls | Reranks |
|---|---:|---:|---:|---:|
| Expansion-first, one call | 19 | 11 | 24 | 0 |
| Contextual bandit, one call | 20 | 12 | 24 | 9 |
| Fitted Q, one call | 20 | 12 | 24 | 9 |
| Original adaptive rule | 23 | 14 | 29 | 1 |
| Parent-first, one call (post-hoc) | 23 | 14 | 24 | 0 |

The parent-first policy matches the two-call hindsight oracle's completeness
and gated correctness, but synthetic parent links supply complete text.
The real-source diagnostics above support testing structural recovery on
less favourable data; they do not yet validate this routing policy across
a population. Eight natural equivalences remain unproved. All arms retained
the gate. The oracle is label-informed, not deployable.

Whole-family CV on 36 cases in six families and 288 repeated
case-configurations: beta baseline Brier 0.17296, log loss 0.52956;
hierarchical Bayes 0.17675 / 0.51820; ridge logistic 0.18422 / 0.52207;
XGBoost 0.18084 / 0.55011. No predictive complexity advantage established.
Avoid inferring independent statistical power from repeated configurations.

## Discussion draft

The evidence favours representation-aware engineering and selective
escalation before model complexity. In document retrieval, candidate
availability and explicit structure are separate from scoring; improving
top-one precision can reduce top-five coverage. A reader/representation
change may recover evidence at lower computational cost than a model.
For normatively sensitive requirements, similarity and entailment do
not demonstrate equivalence of obligations, applicability, qualifiers
or exceptions. Formal proof is representation-bound and must be
distinguished from an unresolved referral. A gated conservative decision
can reduce coverage while preventing unsupported equivalence; measure both.

Potential wider relevance: retrieval-augmented generation, enterprise
document search, legal/regulatory crosswalks, and clinical documentation
or policy compliance review. These are hypotheses for transfer, not
demonstrated improvements in those fields, clinical safety, diagnosis,
or a claim of novelty over the literature. Stronger designs need
independently anchored family-disjoint references, counterexamples
with non-equivalence, prospective budgets, repeated resource measures
and transparent failure attribution. Keep a simple policy and a
label-informed ceiling before learning; test learning only in strata
where residual headroom and sufficient independent data exist.

## Next execution and publication boundary

- Continue #188's source/rights/edition qualification and #183's shared
  locked-reference joins rather than duplicating their lanes.
- Extend the full factorial only on compatible, genuinely eligible
  strata, preserving the complete held/missing worklist. 720 x 64 =
  46,080 directory-configuration planning slots, not completed trials:
  zero fully executed six-factor slots in this snapshot.
- Freeze independently adjudicated applicability/equivalence references,
  source anchors, family-disjoint splits and estimands before confirmatory
  runs. The eight new real cross-reference arms are a bounded
  three-factor diagnostic, not six-factor specialist execution.
- Measure structural acquisition success, complete evidence, accepted
  correctness and error types, resource budgets and realistic costs.
  Establish rule/oracle gaps on common observed transitions first.
  Revisit RL only with a demonstrable gap, paired family-level
  evaluation and no weakening of the verification or refusal gate.
- Populate the main methods/results/discussion using the above text
  and the frozen supplement. Report negative findings and nonexecuted
  cells explicitly. The existing publication contracts remain unchanged:
  no scientific freeze, new registered claim, authorship decision,
  submission or release in this change.

## Reproduce and extend

After retrieving the exact internally retained evidence archive, extract
its raw directory locally. From the repository root:

```sh
python -m research.publication.compile_snapshot \
  --inputs /path/to/retained/raw \
  --manifest research/publication/inputs-v1.tsv \
  --panels research/publication/panels-v1.tsv \
  --output /path/to/snapshots

python -m research.publication.structural_recovery \
  --artifacts /path/to/retained/raw \
  --output /path/to/new-structural-report.json

python -m pytest -q tests/test_publication_snapshot.py tests/test_structural_recovery.py
```

The compiler requires exact hashes, deterministic explicit metric projections
and immutable output directories. Append a new versioned manifest and
projection specification (including failed runs and the prior inputs);
do not replace v1. A new output identity depends on compiler bytes,
manifest bytes, projection bytes and compiled comparison. Copy original
artefacts before expiration, and record missing inputs as a blocked
version rather than dropping them. The structural timing rerun has a
different report hash; preserve it as a separate input. Public releases
must use only rights-cleared, reviewed projections. Five focused tests
passed locally across the two modules; the real diagnostic also replayed
with exact timing-free equality on the extracted-function overlay.
Full repository checks still required on this PR.
