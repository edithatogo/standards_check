# E9 synthetic layout development receipt — 26 November 2026

Status: **local development observation only; hosted exact-head replay pending**.
Protocol: [specialist E9](specialist-pipeline-protocol.v0.1.0.md), Track 01/05,
issue [#158](https://github.com/edithatogo/standards_check/issues/158).
Base main `d88f787ffd4647117bca4ca400cbb68d95197d40`; local overlay, not a checkout of the whole repository.
Open PRs #180 (orthogonal references) and #181 (native format qualification)
were inspected; no change to their branches. No canonical or production changes.

## Fixed inputs and actual commands

Reuse the byte-stable small synthetic PDF generator in
`tests/test_compare_ecoevo_formats.py`, extend with authored rows, nested
identifier, separate score, footnote and explicit condition. Independent of
reader output; **author-labelled synthetic**, not blinded or external.
Manual PDF-region anchors and reader page/line anchors are distinct. The common
decoder tests the explicit numbered-row/marker dialect only; it is not a
general PDF parser, OCR, box-IoU or cross-page reconstruction benchmark.
Rows require exact normalized complete content (including qualifiers); nested
and qualifier edge recovery is scored separately and does not imply complete
parent text. Duplicate predictions count as false positives. Unclear score
boundaries are not silently deleted. No source rights inferred.

```sh
python -m unittest tests.test_layout_development -v
python -m scripts.layout_development --reader pdfplumber --expected-version 0.11.9 --revision d88f787ffd4647117bca4ca400cbb68d95197d40+local-overlay --output pdfplumber.json
python -m scripts.layout_development --reader poppler --expected-version 25.06.0 --revision d88f787ffd4647117bca4ca400cbb68d95197d40+local-overlay --output poppler.json
```

Initial red: module not implemented (import error); after implementation:
five focused tests passed. Both actual reader processes exited successfully.
Full repository suite not executed in the local isolated overlay. Local
Python 3.13.5, Linux x86_64/glibc 2.41; pdfplumber 0.11.9, pdfminer.six
20251230, pypdfium2 5.8.0, Pillow 12.3.0, cryptography 46.0.4, cffi 2.0.0,
charset-normalizer 3.4.7, pycparser 3.0; Poppler 25.06.0. All preinstalled,
zero download bytes this run; model weights not applicable (0 bytes).
Implementation SHA-256 bce38736bb155f261106021e077e241c54efc39041464cfc53c4006aa406e918.
Raw reader output and individual reference/prediction anchors in
[versioned local receipt](e9-layout-development-local-20261126.json).

| Endpoint | Denominator | pdfplumber TP/FP/FN | Poppler TP/FP/FN |
| --- | ---: | ---: | ---: |
| Exact rows | 4 | 1/3/3 | 4/0/0 |
| Nested links | 1 | 1/0/0 | 1/0/0 |
| Footnote | 1 | 1/0/0 | 1/0/0 |
| Qualifier-to-item links | 2 | 2/0/0 | 2/0/0 |

Wall time 0.0625394 s vs 0.0282197 s; maximum individual process peak RSS
102416 vs 95780 KiB (Linux, including worker overhead; not summed concurrent
RSS and not a controlled resource comparison). Single observation per reader.

Three exact rows lost to score-column contamination in flat text. Layout
preserves the separation for this fixture; no improvement in nested, note
or qualifier edge counts. Retain the three false-positive rows and three
missing references. Source retrospective: layout/column boundary loss, not
source drift or identity/rights issue; expand held-out annotated cases with
numeric requirements, page continuations, complex cells and note ambiguity.
The source-census retrospective tool expects a different receipt schema;
no fabricated source-survey result.

Hosted opt-in workflow uses the existing CI hash lock (pdfplumber 0.11.11),
Poppler upstream 24.02.0 check, and records exact distro package builds,
wheel download size and installation log. Distro build and Python patch
are not yet frozen for confirmatory evaluation. No neural model downloaded.
Pin and qualify Granite-Docling only if additional residual failure warrants
it. E10/E11 remain planned in existing Conductor plans. Independent rights
and family-component reference freeze, reproducible hosted receipt and
scientific acceptance remain open. Rollback: remove this opt-in lane; default
production extractor and all canonical contracts remain unchanged.

## Formatting follow-up

The original receipt is bound to commit `92c9ff9d0271d462c1932635a3cf52718f9bebf3`.
The follow-up aligns the script with the maintained double-quote/multiline style;
local Python AST comparison was exactly equal, and all five focused tests passed
again. Formatted script SHA-256 `6dd941156df7a037e6b20d4ec2b971f556a6c8de4d2247e53f405491cf124e15`.
Ruff/Bandit are not installed locally; hosted full checks remain required.
