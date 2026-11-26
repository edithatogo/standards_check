# Plan: Canonical Standard Pack runtime

Status: **implementation complete; hosted integration accepted at the recorded revision**. Implementation: **source implemented**. Evidence: **fixture proven** for the runtime and synthetic fixtures. Hosted runtime acceptance applies to PR #60 revision `bfe2255fda85b891c2f68044676c0b777d92c38c`; exact receipts and historical verification are retained in [evidence.json](evidence.json). PR #83 subsequently promoted the PRISMA checklist to 42 source-reconciled items. That source comparison has its own bounded evidence below; receiving revisions, normalized interpretations, migration parity and external qualification require separate acceptance.

## Phase 1: Contract and rights model

- [x] **T01.001** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Extend the pack schema with verification and item-level rights.
- [x] **T01.002** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add strict Rust DTOs, portable IDs and stable diagnostics.
- [x] **T01.003** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Enforce verification, source, relationship, rights and evidence invariants.

## Phase 2: Canonicalization and lockfiles

- [x] **T01.004** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Implement integer-only deterministic canonical JSON and SHA-256.
- [x] **T01.005** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Implement bounded recursive pack locks with symlink rejection and mutation checks.
- [x] **T01.006** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add atomic lock writing and deterministic lock verification.

## Phase 3: Reference pack and interfaces

- [x] **T01.007** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Migrate the original 27-item PRISMA 2020 corpus into a rights-aware provisional pack (historical PR #60 state; superseded by the 42-item pack in PR #83).
- [x] **T01.008** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add source manifest, CSL citation and conservative verification status.
- [x] **T01.009** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add text/JSON CLI operations and deterministic pack-validation scripts.

## Phase 4: Evidence and review

- [x] **T01.010** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add unit, property, lock, CLI and schema tests.
- [x] **T01.011** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Generate and commit the dependency lock and PRISMA content lock in CI.
- [x] **T01.012** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Obtain passing Linux lint/test, cross-platform test and pack-drift receipts for the recorded original head.
- [x] **T01.013** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Review automated PR findings and implement bounded-read, checked-arithmetic, required-field, URI and portable-path corrections.
- [x] **T01.014** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add regression tests for pack/lock input limits and atomic temporary-file ownership.
- [x] **T01.015** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Add an RFC 6901 regression test while retaining the correct tilde-before-slash escape order.
- [x] **T01.016** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Remove all one-use transfer and review workflows from the branch.

## Integration and remaining evidence gates

- [x] **T01.017** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Merge foundation PR #59 into main as `a8bfec446d219b770e76a23b44d1f08d9e00465d`.
- [x] **T01.018** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Retarget PR #60 from the former foundation branch to `main`.
- [x] **T01.019** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Reconcile the repaired runtime with current-main legacy, dependency and workflow changes.
- [x] **T01.020** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Record passing hosted checks at `bfe2255fda85b891c2f68044676c0b777d92c38c`, including Linux, macOS and Windows.
- [x] **T01.021** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Reconcile all 42 PRISMA checklist texts to the retained official PDF, with source identity, item numbers, page anchors and item-specific receipts.
- [ ] **T01.022** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Complete independent review of normalized interpretations and evidence expectations; retain broader legacy-corpus rights and later external/publication acceptance separately.
- [ ] **T01.023** ([#82](https://github.com/edithatogo/standards_check/issues/82)) Complete migration parity and independent methodological/usability/accessibility qualification.

Hosted integration acceptance is recorded for the exact revision above; it does not transfer
automatically to later changes. Checklist transcription, rights, migration parity, independent
methodological/accessibility qualification and publication have separate evidence scopes.

## PRISMA source and rights review, 19 November 2026

The initial [source and rights evidence assessment](../../prisma2020-source-rights-20261119.md) documented the official CC BY 4.0 checklist licence and correctly retained the then-27-item pack as unverified. It describes the state before PR #83, not the current pack.

## Receiving review, 20 November 2026

PR #83 merged as `da7e780dad139980cadfc40fb0fec44d90f6af50` with 42 items, `source_reconciled` status and a regenerated lock. The retained 67,506-byte official PDF has SHA-256 `2eedbd5452741f9615307a0bce21a8198c0597ce2a0a8a0fd7e140d64b08c625`. All 42 current texts match its complete numbered rows after Unicode NFKC and whitespace normalization.

The [receiving review](../../prisma2020-receiving-review-20261120.md) records the integration regressions and bounded repair: preserve the historical 27-item migration input, update current-pack test expectations while retaining unverified-fixture coverage, and bind both ledger and live pack to complete numbered PDF rows. Source reconciliation does not establish correctness of normalized interpretations, migration semantic parity, external methodological validity, accessibility or publication acceptance.

## Phase 5: Automated triangulated source reconciliation (incremental, planned)

Own this work in Track 01; Track 03 owns legacy repair/migration ([#95](https://github.com/edithatogo/standards_check/issues/95)); Track 05 owns independent qualification. [#111](https://github.com/edithatogo/standards_check/issues/111) owns source discovery/acquisition, [#82](https://github.com/edithatogo/standards_check/issues/82) owns PRISMA interpretation. Preserve the accepted runtime's status: this is additional **source preparation and assurance**, not a change to the production checklist runtime or a claim of external validation.

The [local original text triage](../../source-reconciliation/legacy-source-text-triage-20261124.md) and [authoritative article-table PR #132](https://github.com/edithatogo/standards_check/pull/132) are complementary: reuse their source selection, parsers and receipts; do not duplicate acquisition or build a second importer. PR #132 has merged at `739d9ed4b7a4f7879e7932131cc9dc4e828be110`; the retained 82-row candidate ledger passed the receiving-main Canonical Standard Pack offline comparison at `a60dce3670f77391b1ee85dae40392f5e52aff27` ([run 45290073823](https://github.com/edithatogo/standards_check/actions/runs/45290073823)). This is not a fresh live acquisition, complete source-side hierarchy qualification or four new admitted packs.

### Ordered deliverables and stop rules

- [x] **T01.024** ([#111](https://github.com/edithatogo/standards_check/issues/111)) **T01.5a — lexical diagnostic baseline.** Extend the existing local probe with item-by-item outcomes, stable legacy ordinals, fingerprint-only evidence, token-bounded lexical comparison and a separate punctuation/case-preserving normalized comparison. Distinguish short, absent, ambiguous/repeated and present phrases; retain aggregate metrics and the unconditional zero-admission boundary. Synthetic tests must cover substring false positives, punctuation/negation changes, duplicates, short items and no source-text leakage. Reuse the current Python coverage artifact, no new dependencies. Bounded implementation merged in [#134](https://github.com/edithatogo/standards_check/pull/134) at `43f95026989eb32363d2bcfcf3c71f3dfbae8092`; no semantic or source-admission claim. Receiving-main and corpus-wide evidence remain separate.
- [ ] **T01.025** ([#111](https://github.com/edithatogo/standards_check/issues/111)) **T01.5b — structure before semantics.** Prefer primary JATS/XML/HTML tables, then CSV/DOCX tables, then digital PDF. Reuse the existing article-table parser and PRISMA numbered-row comparator; require exact edition, source hash, printed IDs, complete rows, order, hierarchy, subitems and page/table/span anchors. Independently extract from source before consulting legacy text. Never treat a legacy count or heading as an oracle. Compare full text, with a documented fidelity normalization distinct from tolerant search. Missing/duplicate/reordered rows or ambiguous anchors remain held; no cross-edition substitution. Legacy-side bounded extraction merged [#135](https://github.com/edithatogo/standards_check/pull/135) at `f3740d54b89c32b1b750f641bfca307f604f204d`; shared reader integration and live XML structural receipts merged in [#132](https://github.com/edithatogo/standards_check/pull/132) at `739d9ed4b7a4f7879e7932131cc9dc4e828be110`; exact-head authoritative table and patch coverage passed, receiving and independent hierarchy qualification remain separate. Keep this stage open for independent source-side hierarchy/subitems, supported-format coverage, and live pinned replay; do not treat flat snapshots as complete structure. Bounded DOCX/CSV/XLSX extraction merged in [#136](https://github.com/edithatogo/standards_check/pull/136) at `963121b9e536adce604e53d4352a871be24ad5b1`, including the reviewed XLSX expansion and formula-row repairs, explicit unverified EcoEvo archive cohort and exact fingerprint-to-anchor diagnostics; see the [local triage evidence](../../source-reconciliation/legacy-source-text-triage-20261124.md). Qualify on actual bytes before advancing. The bounded static HTML table reader merged in [#137](https://github.com/edithatogo/standards_check/pull/137) at `a60dce3670f77391b1ee85dae40392f5e52aff27`. Source HTML corpus qualification remains open. The EcoEvo cross-format benchmark merged in [#138](https://github.com/edithatogo/standards_check/pull/138) at `04dce6c931ac95af21123e77c4b075f1e703b9ad`; retained CSV/DOCX/XLSX candidate evidence is recorded in [the benchmark receipt](../../source-reconciliation/ecoevo-format-benchmark-20261124.md). Independent official-byte/PDF-row qualification remains open.
- [ ] **T01.026** ([#111](https://github.com/edithatogo/standards_check/issues/111)) **T01.5c — independent parser benchmark.** Compare existing pdfplumber and already-used pdftotext (Poppler) first, preferably independent official representations of one edition. Measure layout/row failures before evaluating additional Rust parsers or bounded OCR for scanned files. A second parser consuming the same flawed intermediate text is not independent evidence. Preserve source bytes, parser versions and anchors; no OCR-only certification.
- [ ] **T01.027** ([#158](https://github.com/edithatogo/standards_check/issues/158)) **T01.5d — classical NLP comparator.** Begin with regex, token-boundary matching and stdlib difflib on aligned rows. Test clause segmentation, negation, modality, applicability, quantifiers, conjunction/disjunction, temporal conditions and argument preservation. Only if residual errors justify it, benchmark spaCy Matcher/DependencyMatcher as an offline reference, then Rust regex, unicode-segmentation, sentencex or other maintained Rust equivalents as needed. Do not port working Python solely for language uniformity or link NLP into `standardflow-core`.
  [PR #154](https://github.com/edithatogo/standards_check/pull/154) is the opt-in field-level reference; see [classical NLP evidence](classical-linguistic-nlp-20261124.md). Observed v1 recall 70.83% to 91.67% with dependency parsing, but precision 89.47% to 57.89%; all 14 added false fields were role alerts. Bounded v2 role/scope repair is a development iteration, not independent qualification. [PR #155](https://github.com/edithatogo/standards_check/pull/155) separately owns NLI and blinded model-agent adjudication; do not duplicate its pipeline. Keep the existing #150 projection marker baseline and zero-admission boundary.
- [ ] **T01.028** ([#158](https://github.com/edithatogo/standards_check/issues/158)) **T01.5e — statistical alignment and NLI.** Test lightweight cross-encoder NLI (e.g. MiniLM) on source/candidate pairs in both directions, with optional in-memory retrieval only if exact IDs/lexical alignment fail. Entailment both ways is a signal, not proof; one-way entailment, contradiction and neutrality are separate diagnostics. Evaluate Rust ort/tokenizers versus existing Python reference inference only when the measured benefit warrants a runtime dependency. No vector database.
- [ ] **T01.029** ([#158](https://github.com/edithatogo/standards_check/issues/158)) **T01.5f — decision and tiny-model experiment (conditional).** If residual errors merit it, compare a source-span/typed-output decision model (verify actual Liquid AI model ID, weights, licence, runtime and capabilities before pinning; d1-2B is a candidate) and a tiny generative comparator (LFM2.5-230M or comparable). Test classification, source-span extraction, conditionality and layout localisation only where relevant. No unreviewed remote model code or automatic weight download in ordinary CI.
- [ ] **T01.030** ([#158](https://github.com/edithatogo/standards_check/issues/158)) **T01.5g — small model escalation (conditional).** Benchmark one additional small model (e.g. Qwen 0.8B-class or LFM 1–2B-class, exact model to be qualified) only when previous layers leave material errors. Constrained schema/grammar output via an existing compatible runtime such as llama.cpp; independently check all fields against original spans. No custom inference engine, multi-agent orchestration, service, vector index or fine-tuning infrastructure absent measured need.
- [ ] **T01.031** ([#111](https://github.com/edithatogo/standards_check/issues/111)) **T01.5h — unattended reconciliation and admission.** Escalate at item/field level; independently sample apparently successful cases to detect correlated false acceptance. Keep unresolved cases held with explicit reasons. Run deterministically offline after explicit pinned acquisition; candidate pack validation, rights, interpretation, external methodological approval and publication remain distinct gates. No automatic promotion from parser/model agreement.

### Independent benchmark and evidence

See [cross-family format benchmark](cross-family-format-benchmark.md) for the
edition-scoped extension. Retain qualified EcoEvo dialect and independent PDF geometry;
other unsupported formats and unknown denominators remain held.

Use the accepted 42-item PRISMA primary-source comparator as a bounded positive control, not ground truth for normalized interpretation; the historical 27-item migration and ten STARD-copy rejections as independent structural/negative controls. Use PRISMA-EcoEvo PDF/CSV discrepancies as unlabelled diagnostics, and qualify selected independent guideline editions as they become available. Add synthetic single-change negatives (missing negation/condition/subitem, wrong item binding, duplicates/reorder, modality, numeric quantifier, AND/OR). Split development/test by guideline family and edition, not individual sentences; no validation against unqualified legacy arrays.

Measure item/subitem precision/recall/completeness, exact anchored text fidelity, false acceptance among accepted cases, abstention/coverage, semantic discrepancy detection, time and peak memory; use risk–coverage curves and calibration metrics for probabilistic methods. Report paired incremental improvement and uncertainty on held-out data; do not set an arbitrary confidence cutoff or equate zero observed errors with zero risk. Retain a new method only if it improves error detection or coverage at an acceptable resource cost without weakening required gates. Thresholds must be justified and pinned before the held-out run.

Use existing revision-bound CI artifacts and contracts: source/edition, byte hashes, extractor and normalization identity/version, item/anchor or explicit missing-anchor status, field-level findings, exact tool/model/tokenizer/runtime/prompt/quantization pins when applicable, test split, run configuration and limitations. Rights-unclear text stays out of public artifacts; use hashes, offsets and diagnostics. No new evidence service, schema framework or model runtime until a specific measured requirement exists. Routine CI remains offline and model-free; experimental qualification runs separately with explicitly acquired/pinned assets. Roll back each additive comparator independently; no change to canonical pack or user progress.

**Ponytail stop rule:** implement the first deterministic slice, test and merge it before adding more machinery. Reassess the residual errors, already-installed tools and maintenance burden at each boundary. Skip or reorder experimental stages when evidence supports it; record why. All unchecked stages are planned, not implemented or qualified.

### T01.5b/h — catalogue-wide acquisition batch (24 November 2026)

**Decision:** run the published EQUATOR catalogue as one logical census, rather
than requiring a separate investigation or GitHub issue for every record.
Use deduplicated bounded provider requests, stable source IDs, explicit
failure/abstention outcomes and existing source readers. The census is not
a declaration that every listed resource is an applicable, rights-cleared
reporting checklist.

- Producer ownership and coverage remain in [#111](https://github.com/edithatogo/standards_check/issues/111).
  [#139](https://github.com/edithatogo/standards_check/pull/139) is the
  candidate implementation for catalogue-wide exact DOI/PMID resolution and
  OA XML leads using Europe PMC, plus acquisition of six selected primary
  statement articles. Do not mark this candidate merged or its census
  successful until the hosted artifact and exact receiving commit are observed.
- The priority manifest selects ARRIVE 2.0 (21 main rows, nested lettered
  components held), CONSORT 2025 (42 printed rows), SPIRIT 2025 (53), STARD
  2015 (34), TRIPOD+AI 2024 (52), and STROBE 2007 (separate source table and
  study-design artifacts requiring identification). These are independent
  source expectations, **not observed successful extraction counts**.
  [#120](https://github.com/edithatogo/standards_check/issues/120) retains
  CONSORT/SPIRIT diagram and source rights boundaries; the existing
  [#121](https://github.com/edithatogo/standards_check/pull/121) is a separate
  metadata/synthetic diagram lane. Keep TRIPOD 2015 separate from 2024.
- Preserve all catalogue rows, even where identifiers are absent, malformed,
  ambiguous, conflicting or lookup is incomplete. Deduplicate repeated
  publications before source acquisition. Record coverage and the distinct
  counts of metadata candidates, actual downloaded sources, supported source
  structure, independently reconciled rows, held rows and admitted packs.
- After inspecting the census, run eligible OA acquisitions as one explicitly
  scoped, bounded batch (using the provider's supported access routes). Reuse
  the existing JATS/HTML/DOCX/CSV/XLSX/PDF extraction layers; avoid a new
  crawler, arbitrary download URLs, or reprocessing unchanged verified bytes.
  Resume unresolved work by source identity rather than starting over.
  Keep a separate ledger for source identity, licence, edition, item/row
  fingerprints, full subitem/condition/applicability and cross-format evidence.
- Full-catalogue processing is a census of observable extraction outcomes, not
  statistical proof of semantic accuracy. The existing 82-row and 42-row
  reference cohorts are bounded regression controls, not a random sample of
  the catalogue. Independently evaluate error modes and false acceptance on
  held-out families/formats before promoting a new parser or automated decision
  rule. Do not automatically admit a pack from a successful metadata lookup,
  an OA flag, matching counts, parser agreement or similarity.
- Receiving-main pack workflow passed offline on the stated revision; its
  separate Assurance run [45290073575](https://github.com/edithatogo/standards_check/actions/runs/45290073575)
  failed preparing the Python job's locked Rust CLI (unsupported metadata
  version in the existing installation). This remains an operations/Track 05
  qualification issue, not source-table failure or proof that main is fully green.

**Disposition:** T01.5b, T01.5c and T01.5h remain open for actual acquisition,
independent structure/comparison, rights, semantics and admission. Keep
T01.5d–g conditional on measured residual errors. No new model or service
is required for the census.

### Trial-reporting edition metadata and synthetic examples

[#121](https://github.com/edithatogo/standards_check/pull/121) corrects CONSORT/SPIRIT publication metadata and identifies TRIPOD+AI 2024 separately from 2015. Trial-reporting source entries and synthetic examples remain unqualified; no Canonical Pack, checklist rights, source-byte or methodological claim follows. Continue exact-edition acquisition and item/subitem reconciliation under [#120](https://github.com/edithatogo/standards_check/issues/120), retaining #95/#82 holds and the [guideline admission checklist](../../../CONTENT_POPULATION_WORKFLOW.md). The earlier 719-record catalogue is historical; current survey evidence remains in the Phase 5 record.

### T01.5c/d/h and analytical projections — implementation increment

See [requirements and design](source-reconciliation-design.md) for the MoSCoW
acceptance criteria, Mermaid dataflow and disposition model. The candidate
implementation adds whole-row independent Poppler layout comparison, rule-based
linguistic discrepancy diagnostics, an offline review queue with deterministic
sampling, and typed Parquet projections from pinned sources and canonical packs.
Keep T01.5c/d/h open for actual corpus replay, independent held-out error
measurement, receiving CI and resumed live acquisition (#142). No NLI or model
runtime is required. Existing runtime status is unchanged. Refs #111/#95/#82;
Track 05 independent qualification and Track 04 consumer handoff remain separate.

### Independent EcoEvo geometry follow-up

See [EcoEvo geometric reconstruction](ecoevo-pdf-geometry.md); independent native vector and Poppler raster/word geometry replaces one-line header assumption. Closed-band and page-tail qualification, actual 89-item replay and pairwise comparison required. Source/rights gates remain held.


## 24 November — programme of deterministic source resilience

- [x] **T01.032** ([#111](https://github.com/edithatogo/standards_check/issues/111)) Inspect both historical EQUATOR source receipts at upstream revision
  `d74413b15d266334067e1e5c104957601be3ba6c`. First run: 305 identity successes;
  later run: 57 non-overlapping successes, 586 incomplete, 77 missing identifiers.
  No successful full-text acquisition among the later six priority candidates.
- [x] **T01.033** ([#111](https://github.com/edithatogo/standards_check/issues/111)) Qualify the bounded OA inventory and historical-receipt resume (#142), with separate verified current/historical artifacts and receiving-main run 45407700732.
  Historical 362 identity observations are candidate evidence, not a new
  successful receiving run. Changed or conflicting identities remain held.
- [ ] **T01.034** ([#111](https://github.com/edithatogo/standards_check/issues/111)) Qualify the weekly automated acquisition retrospective, fresh-dispatch
  drift comparison, shared XML boundary and 512-case seeded mutation regression.
- [ ] **T01.035** ([#111](https://github.com/edithatogo/standards_check/issues/111)) Configure an authorized PMC ID-converter contact, then verify new provider
  observations. Keep title/author matching and ORCID optional disambiguators;
  registry agreement is not checklist semantic or rights verification.
- [ ] **T01.036** ([#95](https://github.com/edithatogo/standards_check/issues/95), [#111](https://github.com/edithatogo/standards_check/issues/111)) Resolve remaining #111 and #95 source and item-level rights/anchor gates
  before any canonical pack promotion. Preserve #82 independent review gates.

### Versioned acquisition evidence handoff

See [EQUATOR analytical snapshot](equator-analytical-snapshot.md). Reuses #142 scheduled source and retrospective evidence with a strict versioned Parquet export; separate canonical projections and Searchright #843. Historical receipt replay and live receiving evidence remain distinct. No promotion.


### Receiving-main acquisition reconciliation

The #142 candidate retains prior receipt and current live projection observations (artifacts 14918300555 and 14916344312) and the Searchright #851 historical consumer canary. Reconcile hardened source XML ingress with the already-merged #154 opt-in linguistic reconciliation; neither implementation is overwritten. Retain discovery-only identity conflicts, acquisition rights and held candidate statuses, and validate item-count, fingerprint and anchor conservation. No new source authority, rights or canonical pack promotion. Hosted current-base tests and live/replay evidence required before merge.


## Phase 6: Versioned representation and directory assurance

Scope: #158 research programme, #111 directory/source work, #118 technical-specification engagement,
#82/#95 interpretation/rights, and Track 05 empirical publication qualification.
The bounded runtime is complete; the broader representation programme is in progress.

- [x] **T01.037** ([#164](https://github.com/edithatogo/standards_check/issues/164)) Preserve RGI-01–14 in immutable draft profile 0.1.0, with distinct pack/schema,
  guideline-edition, model and profile versions; explicit directional relation semantics.
- [x] **T01.038** ([#164](https://github.com/edithatogo/standards_check/issues/164)) Implement profile digest/contract-pin checks, an append-only baseline comparison,
  and separate hash-bound approval records. No specification has been approved.
- [x] **T01.039** ([#111](https://github.com/edithatogo/standards_check/issues/111)) Integrate #142 after seven exact-head protected checks and actual current/historical
  artifact inspection; reuse its four-table directory projection and existing writer.
- [x] **T01.040** ([#111](https://github.com/edithatogo/standards_check/issues/111)) Observe all seven #142 receiving-main checks; merge #153 after current-base checks
  and retain strict/layout-normalized differences and all fourteen-family holds.
- [x] **T01.041** ([#31](https://github.com/edithatogo/standards_check/issues/31)) Observe #153 and #160 on receiving revisions e2797940 and 82e4a1ef; all seven protected checks passed, with successful native Pages deployment at 82e4a1ef.
- [x] **T01.042** ([#158](https://github.com/edithatogo/standards_check/issues/158)) Define d1-2B as a conditional complementary-evidence experiment; standalone
  superiority is not required. Predeclare useful gain, harmful changes and review budget.
- [ ] **T01.043** ([#158](https://github.com/edithatogo/standards_check/issues/158)) Freeze untouched family strata and thresholds, qualify the existing #155 benchmark,
  then run the isolated d1-2B experiment if source/model/runtime prerequisites pass.
- [ ] **T01.044** ([#161](https://github.com/edithatogo/standards_check/issues/161)) Validate implementation-neutral conformance with a real downstream consumer;
  technical approval, item-level admission and EQUATOR feedback remain distinct.

[Current evidence and sequence](representation-programme-20261124.md) is the
single receipt for this increment. No additional crawler, exporter, database or
production model is introduced.

## Data conservation and external review

- [ ] **T01.045** ([#149](https://github.com/edithatogo/standards_check/issues/149)) Complete the analytical-projection acceptance and consumer conservation obligations, preserving the existing four-table producer and disposing of competing proposals explicitly.
- [x] **T01.046** ([#118](https://github.com/edithatogo/standards_check/issues/118)) Post the versioned profile and optional reference implementation to EQUATOR; upstream `equator-website#14` was read back after the authorized browser submission.
- [ ] **T01.047** ([#118](https://github.com/edithatogo/standards_check/issues/118)) Record actual EQUATOR feedback and version any resulting normative amendment; delivery is not endorsement.
- [ ] **T01.048** ([#162](https://github.com/edithatogo/standards_check/issues/162)) Prepare and qualify a selective metadata/evidence dataset release with separate source rights and export permission.

## Multi-checklist composition and requirement mapping

- [ ] **T01.049** ([#82](https://github.com/edithatogo/standards_check/issues/82), [#149](https://github.com/edithatogo/standards_check/issues/149)) Qualify the bounded identity-conserving union and sparse cross-pack candidate preview. No similarity-based deletion.
- [ ] **T01.050** ([#158](https://github.com/edithatogo/standards_check/issues/158)) Freeze and compare statistical retrieval with one qualified embedding challenger; separate retrieval utility from directional equivalence evidence, retain all failures.
- [ ] **T01.051** ([#82](https://github.com/edithatogo/standards_check/issues/82), [#149](https://github.com/edithatogo/standards_check/issues/149)) Qualify reviewed equivalence display groups, applicability-aware implication, conflict and graph projections with original identities conserved.

See [composition and requirement graph design](../../../docs/architecture/CHECKLIST_COMPOSITION.md). The first bounded preview does not authorize merging distinct semantic obligations or admitting new packs.

Composition follow-up (26 November): word and character TF-IDF comparison and optional conservative local display partition; see [composition design and synthetic development receipt](../../../docs/architecture/CHECKLIST_COMPOSITION.md). T01.049–051 remain open for independent real-source, applicability and reviewed-relation qualification. T04.007–008 remain open for pinned consumer evidence. No automatic semantic merge.

## Ontology coverage, network analysis and prospective validation

- [ ] **T01.052** ([#95](https://github.com/edithatogo/standards_check/issues/95), [#111](https://github.com/edithatogo/standards_check/issues/111)) Freeze multiple qualified guideline families and ontology releases (MeSH, OBI, STATO first), eligible concept/scope universe, reference and source rights for E4-E6.
- [ ] **T01.053** ([#82](https://github.com/edithatogo/standards_check/issues/82), [#149](https://github.com/edithatogo/standards_check/issues/149), [#158](https://github.com/edithatogo/standards_check/issues/158)) Produce validated graph, vector, concept mapping, citation/co-citation and gap-audit tables with explicit denominators, sensitivity and matched figures (E4-E7).

The [follow-up protocol](../../../docs/research/composition-graph-protocol.v0.1.0.md) and [analytical contract](../../../contracts/analysis/requirement-graph.v0.1.0.json) define the planned output and workflow registry. Existing T01.049-051 remain open for independent scientific evidence; the merged #171 candidate is only a bounded synthetic implementation (684 tests, 91.21% combined Python coverage on its qualified head). No empirical gap or relation admission.

The [independent-family acquisition batch](../../source-reconciliation/independent-family-intake-20261126.md) uses existing priority survey and retrospective evidence with explicit publisher co-publications. T01.052 remains open for source and rights qualification, family-disjoint sampling and independent review; no new canonical or benchmark admission.

### Five-class blinded adjudication and comparator qualification

See [semantic reconciliation qualification](semantic-reconciliation-qualification.md). T01.5d/e: retain the prior synthetic and first blinded receipt; improve insufficient agreement using numbered evidence spans and stronger separately pinned model-agent processes, freeze a family-disjoint five-class controlled benchmark from actual pinned source rows and separate natural candidate pairs. T01.5f/g: one additional NLI comparator only on a predeclared material baseline deficit against independent formal controls or qualified agent consensus. No automatic admission; insufficient consensus stays held. No human labelling or adjudication in this benchmark.

Witness-v2 scientific gate failed (artifact 14924523529); experimental DeBERTa 29/30 vs MiniLM 16/30 on formal controls. Condition-v3 bounded follow-up preserves the scientific threshold and natural-pair hold. See the semantic qualification receipt.

26 November integration hold (#155): prior Assurance run 45626930697 failed maintained Ruff (95 violations) and combined Python coverage (85.86%, 7987/9302 versus 90.5% floor). The semantic scripts remain in the maintained coverage denominator. Current-base deterministic checks must qualify before explicitly authorizing the separate model experiments. Original reference failure and thresholds are unchanged. Legacy experiment labels describe B relative to A; RGI-06 describes A relative to B. Preserve historical receipts, and implement a tested, explicit direction adapter/version before downstream graph use. No source or semantic admission.

26 November assurance increment (#155): merge receiving main `341f5388` without overwriting
the composition, ontology or independent-family intake work. Prior run
[45637024692](https://github.com/edithatogo/standards_check/actions/runs/45637024692)
failed maintained lint (95 diagnostics) and combined Python coverage (86.28%, floor 90.5%).
Apply the pinned Ruff repair from [45751013372](https://github.com/edithatogo/standards_check/actions/runs/45751013372);
all four resulting blob prefixes matched the diagnostic, and its temporary workflow was removed.
Add offline behavioral tests and the explicit direction adapter; six isolated direction tests
passed against the extracted relation implementation, with full hosted verification outstanding.
Keep T01.028–030 and T01.043 open: condition-v3 still fails scientific qualification, and the
new independent-family intake remains held. Do not treat repeat controls or related CONSORT/SPIRIT
editions as independent confirmatory families. No model execution, auto-merge, or admission.

26 November review handoff (#155): all seven required workflow groups passed on head
`2779f19`, with [Assurance 45751485991](https://github.com/edithatogo/standards_check/actions/runs/45751485991)
reporting 724 Python tests passed and 91.59% combined coverage (90.5% floor).
The [qualification receipt](semantic-reconciliation-qualification.md) now records the hash-verified
main source census, prospective independent-family intake slots, and paired historical model
complementarity. Zero of eight priority source candidates qualified for a fresh confirmatory freeze.
Keep T01.028–030, T01.043 and T01.052 open. Ready for code and protocol review is not ready
to merge; no auto-merge, new model run, scientific claim or pack promotion.

### LFM complementary development and source retry

User explicitly requests evaluating Liquid AI models. Separate the exploratory
synthetic lane from E2/E3 and the condition-v3 scientific hold. Reuse the original
36 analyst-authored pairs without retuning; all are development evidence now,
including the former test stratum. Run one challenger at a time against both
retained ONNX comparators, with independent jobs and no combined vote or promotion.
Use the native decision API for d1 and the same existing blinded structured prompt
for LFM3 and LFM2.5. The [qualification receipt](semantic-reconciliation-qualification.md)
records model/runtime pins, predeclared thresholds and limits. Retry the selected
official article transports and alternate issuer files; acquisition is not admission.
T01.028–030, T01.043 and T01.052 remain open. Do not authorize merge from these
synthetic results; fresh independent eligible source components and actual scientific
qualification remain required.


26 November LFM follow-up: actual d1 and LFM3 native inference receipts and exact issuer
PDF acquisition are recorded in [semantic qualification](semantic-reconciliation-qualification.md).
Keep prior failure and original thresholds; extend only the exploratory synthetic lane with
bounded thinking/scale and output-budget ablations and reuse the structural comparator on new
source manifestations. T01.028–030, T01.043 and T01.052 remain open. No source freeze or merge
from diagnostic results.


26 November source structure follow-up: five issuer/publisher PDFs acquired and hash-bound,
zero comparable rows with the existing generic reader; STARD transport and source rights held.
See [semantic qualification](semantic-reconciliation-qualification.md). Restore the Thinking
weight pin at the original publisher upload and verify the later licence independently.
Do not reopen or tune historical scientific control sets; independent cohort freeze held.

### Specialist pipeline and publication extension (26 November)

See [specialist pipeline protocol](../../../docs/research/specialist-pipeline-protocol.v0.1.0.md)
and [prospective E9-E14 contract](../../../contracts/publication/specialist-pipeline.v0.1.0.json).
T01.025, T01.027-030, T01.043, T01.050-053 retain their existing owners and gates.
Use source-native extraction first; compare tiny document/layout models only on held
formats. Test GLiNER boundary tags with exact offsets, a small dense retrieval/reranker
against the existing lexical method, and NLI/d1 on separate evidence tasks. Do not
use models for identity, arithmetic, applicability-rule execution or acceptance.
The costing metadata cohort is a development-only editorial topic-ranking pilot;
keep independent family, rights, reference, ontology and scientific holds explicit.
All native LFM follow-up results and negative evidence are in the qualification receipt.
