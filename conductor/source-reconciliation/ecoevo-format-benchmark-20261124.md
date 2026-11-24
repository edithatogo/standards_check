# EcoEvo 2021: first cross-format structural benchmark

Track 01 T01.5b/T01.5c, #111/#95/#82. Reuse the merged source probe (#136),
not the legacy Markdown as an oracle. Edition identity: [PRISMA Executive
EcoEvo page](https://www.prisma-statement.org/ecoevo), primary DOI
10.1111/brv.12721 (PMC8518748), 2021 v1.0, and [official seven-page
checklist](https://www.prisma-statement.org/s/PRISMA-EcoEvo_PDFChecklist.pdf).
Printed identifier-only reference: 27 main groups, 89 sub-items, with group
counts encoded in the benchmark from the published checklist numbering.
Official PDF, Word and Excel locators are explicit links from the PRISMA page.
CSV is a local derivative and does not have a confirmed official link.
Bibliographic/filename agreement is not byte identity or a reuse permission.

## Actual artifact result (24 November 2026)

Downloaded and inspected [Python coverage artifact 14872326180](https://github.com/edithatogo/standards_check/actions/runs/45285963359/artifacts/14872326180)
from #136, tested synthetic merge revision
`5f220def92c9b11dd06b11d3f474c2435ecefdca`, head
`663d2a947da783c478974217e3f1fa26ea3dae68`, triage JSON SHA-256
`e9083d087cf4bf3c7db7637d301e9ad9774127c540b6c6eae873aff64226e242`.
The exact reviewed tree merged at `963121b9e536adce604e53d4352a871be24ad5b1`.
Source probe summary: 24 attempted / 18 extracted, 4 held structures,
2 observed structures, zero verified admissions. EcoEvo has four candidate files.

| Candidate | Ordered expected IDs | Duplicate IDs | SHA-256 |
| --- | ---: | ---: | --- |
| CSV | 89/89 | 0 | 14a818fa45179351b1d8257b0233f52e79f3ae83e7ab27419fb64416d2ba2618 |
| DOCX | 89/89 | 0 | 0d5f2795058cc25e4994563635866d973497df21c1e7b42b795db78f0ac1349c |
| XLSX | 89/89 | 0 | 601370bfdcb749f6c40240d3671324458ab4951ccf1b1508425e89310624bb84 |
| PDF | not measured structurally | unknown | db0a9fb221a1467a82c277419be96e18c7f8600b0deed25009bacb41322623ba |

Compared whole normalized requirement-cell digests after identifying explicit
sub-item and requirement column headers, not scoring/response columns.
DOCX↔XLSX: 89/89 exact; CSV↔DOCX and CSV↔XLSX: 88/89 exact each.
Only 8.3 differs. The XLSX has a second sheet without a complete requirement
header; the DOCX non-body-content hold remains. The PDF's prior flat probe
has zero matches among 78 long legacy phrases; this is not evidence that
it lacks the 89 items. Do not assume any candidate or majority is correct.
No rights-qualified text has been retained in this benchmark.

## Reproduction and next gate

```sh
python -m unittest tests.test_compare_ecoevo_formats -v
python -m scripts.probe_legacy_source_text --output /tmp/triage.json
python -m scripts.compare_ecoevo_formats --root . --report /tmp/triage.json --output /tmp/ecoevo.json
```

Six local synthetic benchmark tests passed, including a real minimal PDF
table, changed-source bytes, official-byte equality/difference/unavailable
states, missing and duplicate IDs, formula cells and scoring-column traps.
The committed script and test-file blobs match the tested local bytes. The
script reproduces all the above actual artifact results without any original
text or legacy-item text. With the checkout supplied, recheck each source
hash before using its receipt; try pdfplumber ruled-table row extraction and
independent Poppler layout-field ID tokens, recording versions and anchors
even if the first parser fails. Layout tokens are not full numbered-row proof.
Actual PDF parser results are still pending hosted execution.

Reuse the Assurance Python job and artifact; Poppler already exists in the
repository's canonical PDF check. No new Python dependency. Explicitly
changed benchmark code or workflow dispatch triggers a bounded official
download attempt (three fixed HTTPS URLs, disposable runner directory,
no raw source artifacts). Compare byte SHA-256 with the receipt; missing
downloads and mismatches stay held. Local download attempt was unsuccessful.
Do not claim official bytes equal until the hosted report actually records it.
Ordinary runs remain offline for source acquisition. Next reconcile 8.3
against the official edition, qualify the PDF row/header geometry and
independent source parser agreement; retain all source/rights gates and
zero promotions. T01.5b/c remain open.
