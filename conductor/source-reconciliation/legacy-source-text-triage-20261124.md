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
