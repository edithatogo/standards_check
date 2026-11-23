# Plan: Canonical Standard Pack runtime

Status: **implementation complete; hosted integration accepted at the recorded revision**. Implementation: **source implemented**. Evidence: **fixture proven** for the runtime and synthetic fixtures. Hosted runtime acceptance applies to PR #60 revision `bfe2255fda85b891c2f68044676c0b777d92c38c`; exact receipts and historical verification are retained in [evidence.json](evidence.json). PR #83 subsequently promoted the PRISMA checklist to 42 source-reconciled items. That source comparison has its own bounded evidence below; receiving revisions, normalized interpretations, migration parity and external qualification require separate acceptance.

## Phase 1: Contract and rights model

- [x] Extend the pack schema with verification and item-level rights.
- [x] Add strict Rust DTOs, portable IDs and stable diagnostics.
- [x] Enforce verification, source, relationship, rights and evidence invariants.

## Phase 2: Canonicalization and lockfiles

- [x] Implement integer-only deterministic canonical JSON and SHA-256.
- [x] Implement bounded recursive pack locks with symlink rejection and mutation checks.
- [x] Add atomic lock writing and deterministic lock verification.

## Phase 3: Reference pack and interfaces

- [x] Migrate the original 27-item PRISMA 2020 corpus into a rights-aware provisional pack (historical PR #60 state; superseded by the 42-item pack in PR #83).
- [x] Add source manifest, CSL citation and conservative verification status.
- [x] Add text/JSON CLI operations and deterministic pack-validation scripts.

## Phase 4: Evidence and review

- [x] Add unit, property, lock, CLI and schema tests.
- [x] Generate and commit the dependency lock and PRISMA content lock in CI.
- [x] Obtain passing Linux lint/test, cross-platform test and pack-drift receipts for the recorded original head.
- [x] Review automated PR findings and implement bounded-read, checked-arithmetic, required-field, URI and portable-path corrections.
- [x] Add regression tests for pack/lock input limits and atomic temporary-file ownership.
- [x] Add an RFC 6901 regression test while retaining the correct tilde-before-slash escape order.
- [x] Remove all one-use transfer and review workflows from the branch.

## Integration and remaining evidence gates

- [x] Merge foundation PR #59 into main as `a8bfec446d219b770e76a23b44d1f08d9e00465d`.
- [x] Retarget PR #60 from the former foundation branch to `main`.
- [x] Reconcile the repaired runtime with current-main legacy, dependency and workflow changes.
- [x] Record passing hosted checks at `bfe2255fda85b891c2f68044676c0b777d92c38c`, including Linux, macOS and Windows.
- [x] Reconcile all 42 PRISMA checklist texts to the retained official PDF, with source identity, item numbers, page anchors and item-specific receipts.
- [ ] Complete independent review of normalized interpretations and evidence expectations; retain broader legacy-corpus rights and later external/publication acceptance separately.
- [ ] Complete migration parity and independent methodological/usability/accessibility qualification.

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

The [local original text triage](../../source-reconciliation/legacy-source-text-triage-20261124.md) and [authoritative article-table PR #132](https://github.com/edithatogo/standards_check/pull/132) are complementary: reuse their source selection, parsers and receipts; do not duplicate acquisition or build a second importer. The latter is a separate in-flight lane; its results must not be assumed accepted.

### Ordered deliverables and stop rules

- [ ] **T01.5a — lexical diagnostic baseline.** Extend the existing local probe with item-by-item outcomes, stable legacy ordinals, fingerprint-only evidence, token-bounded lexical comparison and a separate punctuation/case-preserving normalized comparison. Distinguish short, absent, ambiguous/repeated and present phrases; retain aggregate metrics and the unconditional zero-admission boundary. Synthetic tests must cover substring false positives, punctuation/negation changes, duplicates, short items and no source-text leakage. Reuse the current Python coverage artifact, no new dependencies.
- [ ] **T01.5b — structure before semantics.** Prefer primary JATS/XML/HTML tables, then CSV/DOCX tables, then digital PDF. Reuse the existing article-table parser and PRISMA numbered-row comparator; require exact edition, source hash, printed IDs, complete rows, order, hierarchy, subitems and page/table/span anchors. Independently extract from source before consulting legacy text. Never treat a legacy count or heading as an oracle. Compare full text, with a documented fidelity normalization distinct from tolerant search. Missing/duplicate/reordered rows or ambiguous anchors remain held; no cross-edition substitution.
- [ ] **T01.5c — independent parser benchmark.** Compare existing pdfplumber and already-used pdftotext (Poppler) first, preferably independent official representations of one edition. Measure layout/row failures before evaluating additional Rust parsers or bounded OCR for scanned files. A second parser consuming the same flawed intermediate text is not independent evidence. Preserve source bytes, parser versions and anchors; no OCR-only certification.
- [ ] **T01.5d — classical NLP comparator.** Begin with regex, token-boundary matching and stdlib difflib on aligned rows. Test clause segmentation, negation, modality, applicability, quantifiers, conjunction/disjunction, temporal conditions and argument preservation. Only if residual errors justify it, benchmark spaCy Matcher/DependencyMatcher as an offline reference, then Rust regex, unicode-segmentation, sentencex or other maintained Rust equivalents as needed. Do not port working Python solely for language uniformity or link NLP into standardflow-core.
- [ ] **T01.5e — statistical alignment and NLI.** Test lightweight cross-encoder NLI (e.g. MiniLM) on source/candidate pairs in both directions, with optional in-memory retrieval only if exact IDs/lexical alignment fail. Entailment both ways is a signal, not proof; one-way entailment, contradiction and neutrality are separate diagnostics. Evaluate Rust ort/tokenizers versus existing Python reference inference only when the measured benefit warrants a runtime dependency. No vector database.
- [ ] **T01.5f — decision and tiny-model experiment (conditional).** If residual errors merit it, compare a source-span/typed-output decision model (verify actual Liquid AI model ID, weights, licence, runtime and capabilities before pinning; d1-2B is a candidate) and a tiny generative comparator (LFM2.5-230M or comparable). Test classification, source-span extraction, conditionality and layout localisation only where relevant. No unreviewed remote model code or automatic weight download in ordinary CI.
- [ ] **T01.5g — small model escalation (conditional).** Benchmark one additional small model (e.g. Qwen 0.8B-class or LFM 1–2B-class, exact model to be qualified) only when previous layers leave material errors. Constrained schema/grammar output via an existing compatible runtime such as llama.cpp; independently check all fields against original spans. No custom inference engine, multi-agent orchestration, service, vector index or fine-tuning infrastructure absent measured need.
- [ ] **T01.5h — unattended reconciliation and admission.** Escalate at item/field level; independently sample apparently successful cases to detect correlated false acceptance. Keep unresolved cases held with explicit reasons. Run deterministically offline after explicit pinned acquisition; candidate pack validation, rights, interpretation, external methodological approval and publication remain distinct gates. No automatic promotion from parser/model agreement.

### Independent benchmark and evidence

Use the accepted 42-item PRISMA primary-source comparator as a bounded positive control, not ground truth for normalized interpretation; the historical 27-item migration and ten STARD-copy rejections as independent structural/negative controls. Use PRISMA-EcoEvo PDF/CSV discrepancies as unlabelled diagnostics, and qualify selected independent guideline editions as they become available. Add synthetic single-change negatives (missing negation/condition/subitem, wrong item binding, duplicates/reorder, modality, numeric quantifier, AND/OR). Split development/test by guideline family and edition, not individual sentences; no validation against unqualified legacy arrays.

Measure item/subitem precision/recall/completeness, exact anchored text fidelity, false acceptance among accepted cases, abstention/coverage, semantic discrepancy detection, time and peak memory; use risk–coverage curves and calibration metrics for probabilistic methods. Report paired incremental improvement and uncertainty on held-out data; do not set an arbitrary confidence cutoff or equate zero observed errors with zero risk. Retain a new method only if it improves error detection or coverage at an acceptable resource cost without weakening required gates. Thresholds must be justified and pinned before the held-out run.

Use existing revision-bound CI artifacts and contracts: source/edition, byte hashes, extractor and normalization identity/version, item/anchor or explicit missing-anchor status, field-level findings, exact tool/model/tokenizer/runtime/prompt/quantization pins when applicable, test split, run configuration and limitations. Rights-unclear text stays out of public artifacts; use hashes, offsets and diagnostics. No new evidence service, schema framework or model runtime until a specific measured requirement exists. Routine CI remains offline and model-free; experimental qualification runs separately with explicitly acquired/pinned assets. Roll back each additive comparator independently; no change to canonical pack or user progress.

**Ponytail stop rule:** implement the first deterministic slice, test and merge it before adding more machinery. Reassess the residual errors, already-installed tools and maintenance burden at each boundary. Skip or reorder experimental stages when evidence supports it; record why. All unchecked stages are planned, not implemented or qualified.
