# Local original-versus-legacy checklist text triage — 24 November 2026

**Conductor:** Track 01 source identity, Track 03 legacy corpus, Track 05 assurance.

Existing sources and legacy Markdown are *untrusted audit inputs*. A locally
stored PDF can be outdated, incomplete, rights-restricted, or attached to the
wrong edition; an old `verified: true` sidecar is not independent evidence.

The additive `scripts/probe_legacy_source_text.py` reads only already-present
original PDF, DOCX, CSV and TXT bytes. It rechecks SHA-256 against the scanned
inventory; uses existing `pdfplumber` and `python-docx` plus stdlib extractors;
limits inputs to 20 MB and 80 PDF pages; and compares normalized complete
legacy task-list phrases as conservative substrings. It returns **only**
fingerprints, counts, paths, extractor identities and error types — no copied
checklist text, no source acquisition and no new external dependencies.

The existing Python coverage job saves `legacy-source-text-triage.json` with
its normal revision-bound CI evidence. Reproduce offline with:

```sh
python -m unittest tests.test_probe_legacy_source_text
python -m scripts.probe_legacy_source_text --output /tmp/source-triage.json
```

**Claim boundary:** `verified_by_this_process=0` and
`qualification=unverified_original_and_legacy_text` always. Successful
extraction, identical substrings or a matching file hash cannot establish an
authoritative edition, item identity, rights clearance, applicability,
completeness, semantic equivalence or scientific/methodological validation.
Scanned PDFs without usable text remain unresolved, not auto-OCR verified.
See [EQUATOR alignment](legacy-equator-alignment-20261123.md), source/rights
[#111](https://github.com/edithatogo/standards_check/issues/111) and held
arrays [#95](https://github.com/edithatogo/standards_check/issues/95).

**NLP:** use this deterministic report to prioritise discrepancies first.
Only if measured false positives/negatives justify it, use a pinned secondary
parser or NLI model as an independent *discrepancy detector*, with source spans,
negative fixtures and recorded model revision. A model cannot grant licence
permission or certify scientific interpretation; unresolved cases stay held.
The PRISMA 2020 42-item primary-PDF comparator is a separate, higher-evidence
source reconciliation gate. Neither pipeline requires a human to *run*, but
the software must not invent human/external approval.

Rollback: revert the additive script/tests/CI invocation; no pack,
repository index, rights metadata, original file or user progress is mutated.

## T01.5a — additive item diagnostics

The existing report retains its historical `exact_substring_matches` count for compatibility, not as an exact-text claim. New aggregate metrics count meaningful (at least 40 lexical characters) token-bounded lexical hits and case/punctuation-preserving NFKC/whitespace-normalized phrase hits separately. Every legacy task-list entry, including short or empty lexical entries, receives its ordinal (not a printed source ID), normalized text SHA-256, occurrence counts, short-item flag and diagnostic outcome. Repeated and overlapping hits remain ambiguous. No raw text is added to the artifact. A normalized phrase can occur inside a different row, in narrative text or even in a negated requirement; neither comparison is complete-row fidelity or semantic equivalence. Source identity, rights, external validation and `verified_by_this_process=0` remain unchanged.

Synthetic regressions exercise partial-token false hits, case/punctuation differences, Unicode/whitespace normalization, repeated/empty/short items and negated-context phrase hits. The first three focused new tests were run RED/GREEN against the comparator extracted into an isolated local Python harness; full repository CI and receiving-main evidence are separate gates. Next: inspect the existing authoritative article-table work and actual diagnostics before adding another parser or NLP dependency.

## T01.5b — bounded legacy structure increment

The dependency-free shared reader `scripts/legacy_checklist_structure.py` preserves task lines, indented wrapped text, ordinary nested bullets, nested task parent ordinals, declared numbered/lettered/decimal/S-prefixed labels, section line anchors and original indentation. It separates editorial IDs from task ordinals. It excludes top-level fenced examples and flags ambiguous lazy wrapping, empty items and nested fenced content. This is the bounded task-list dialect used by legacy views, not a general Markdown parser. Unsupported forms, non-task content and source structure still need independent qualification. Duplicate declared IDs are reported, not accepted. Non-task nested bullet markers remain in text for conservative diagnostics; formatting can cause false mismatches.

The existing probe now compares full captured task text, not just the first line. Report schema 2 adds a fingerprint of the exact legacy Markdown bytes, source line numbers, indentation, section anchors, declared IDs, parent relationships and warnings; raw legacy text is omitted. Prior lexical aggregates retain their meaning as phrase counts but are not directly comparable across changed extraction scopes. Existing original-file read is bounded at 20 MB plus one byte before parsing. No authoritative source rows, pack, rights status, or user progress changed; zero automatic promotions.

Six focused synthetic reader tests passed locally in an isolated Python 3.13 harness; the committed source/test blob IDs match those tested. Integration and bounded-read tests run in the existing Python suite. Full-repository local testing is unavailable in this environment. On receiving #132, reuse the same reader for the primary-article comparator; do not mutate pinned article rows or source digests. T01.5b remains open for source-side hierarchy, complete row/subitem reconciliation, and independent parser comparison.

## T01.5b — structured DOCX and tabular sources

The local original audit now uses `scripts/structured_source.py` for DOCX,
CSV and XLSX, with the same source-byte limit and digest checks. It preserves
DOCX body order, nested tables, physical cell coordinates, horizontal spans,
vertical merge origin and numbering metadata; rendered numbering, non-body
parts, unsupported content and inconsistent grids are held. CSV retains
logical rows, physical line ranges and cells (including empty and multiline
values); ragged rows are explicit. XLSX retains sheet ordinals, row/cell
coordinates, merged ranges, hidden state, data types and cell hashes. Formulas
are not evaluated; non-cell content is held. ZIP expanded-size and member
limits, DOCX nesting/node limits and XLSX preflight grid bounds are applied
before expansion of large merged ranges. No workbook macros are executed.

The existing report advances to schema 3. Whole normalized row/cell/block
fingerprints can be compared with legacy item fingerprints independently of
the flat phrase match. Anchor counts are retained with up to twenty candidate
anchors; these are exact normalized text candidates, not independently
verified printed identities. Raw source text, formula expressions and sheet
names are not emitted. Format-native numeric-looking values are candidate
labels only. Source structure, identity, rights, interpretation and admission
remain separate; `verified_by_this_process` remains zero. Historical flat
phrase counts may change because physical DOCX duplicates and lost nested
content have been corrected.

A pinned `openpyxl==3.1.5` is justified by the actual archived PRISMA-EcoEvo
Excel checklist; reuse python-docx's existing lxml dependency for safe bounded
XML preflight. Include only the two explicitly named archived EcoEvo DOCX/XLSX
files as filename-based unverified candidates, never as authoritative sources.
The generic local scanner also recognizes `.xlsx`. No new runtime, crawler,
source bytes or canonical packs. Five synthetic local parser tests passed on
Python 3.13.5 with python-docx 1.2.0 and openpyxl 3.1.5; exact helper/test blob
hashes matched. The end-to-end audit regression and actual archive probes
require hosted qualification. Reuse existing Python coverage artifact;
rollback this additive parser, dispatch and dependency together.

### Review hardening

The XLSX preflight now independently caps cumulative merged-range area across the workbook, not just the enclosing rectangular grid, before normal loading. Formula-bearing rows have no whole-row fingerprint; literal cell anchors remain eligible but formula cells and partial rows cannot count as exact structural matches. Two focused tests reproduced both failures against the existing XLSX function in an isolated local harness and passed after the repair (Python 3.13.5, openpyxl 3.1.5). The existing audit integration fixture now also checks that a formula-bearing row contributes only its literal-cell anchor. Full exact-head hosted checks remain required.

## Static HTML table increment

The existing structured-source dispatch additionally supports UTF-8 HTML via the existing lxml dependency. It preserves table ordinals, captions, row groups (including implicit body rows), physical cell coordinates, heading-cell scope, row/column spans and inherited cell anchors. Inline markup preserves word continuity and block markup separates text. Incomplete cells and rows (including rows with inherited text that was not physically repeated) cannot produce exact whole-cell/row digests. Nested tables and invalid spans are held. Script/style/media content is not executed or fetched; parser recovery and unevaluated rendered visibility are flagged. This is authored static table structure, not a browser rendering or whole-page checklist extractor. No source HTML candidates were present in the inspected tree; qualification is synthetic until genuine rights/edition-qualified sources are available.

Four focused HTML tests passed in an isolated local harness, and the tested function and test-file Git blob hashes were checked before committing. The audit integration fixture remains for hosted verification. No new dependency, no new crawler, no new schema, no content promotion.

Review hardening: non-element table children no longer split implicit row groups, and h1–h6 preserve block text boundaries. Both regressions reproduced RED and passed GREEN in the isolated local harness (six HTML tests passed). No source promotion or new dependency.
