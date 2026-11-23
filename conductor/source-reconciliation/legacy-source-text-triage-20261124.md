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
