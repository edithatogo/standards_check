# Real-source HTML and independent PDF qualification

Track 01 T01.5b/c; issues [#111](https://github.com/edithatogo/standards_check/issues/111), [#82](https://github.com/edithatogo/standards_check/issues/82) and [#95](https://github.com/edithatogo/standards_check/issues/95). Starting main: `83413e2dc64217539e962cc72a61f9fd127415d9`.

## Recovered actual evidence (not a new test run)

The exact [Assurance run 45287260785](https://github.com/edithatogo/standards_check/actions/runs/45287260785) for merged PR #138 completed successfully. Downloaded and inspected [coverage artifact 14872382116](https://github.com/edithatogo/standards_check/actions/runs/45287260785/artifacts/14872382116), tested synthetic merge `d847900978f654ecca9fb11a31bce3e021abd0c1`, PR head `15227ce899b4336548b28c4d5f2f8c712c72f745`. Official comparison JSON SHA-256 `d0367ffba8151d36ec7f3e80090a83863cee97cd018ed7e68c343ac73c565449`; offline comparison JSON SHA-256 `547e31514ecd7642ad6732f1229277f523fd37e1cb9e205c7872eb04d0d8dae1`.

- Official PDF, DOCX and XLSX downloaded bytes exactly match archived local SHA-256 pins in the preceding [EcoEvo receipt](ecoevo-format-benchmark-20261124.md). CSV remains an unconfirmed derivative.
- Poppler 24.02.0 found 89/89 unique item-ID tokens; pdfplumber 0.11.9 recovered 0/89 header-bound rows and reported `incomplete_or_ambiguous_header`. The official PDF rendering's extracted header contains a control marker in the sub-item label. CID-2 recognition is a bounded repair hypothesis, not an observed repair.
- DOCX/XLSX all 89 ordered requirement digests agree; CSV differs at 8.3. Do not infer authority from majority agreement. DOCX non-body parts and XLSX second-sheet structural hold are unchanged.
- Zero additional canonical packs promoted. This receipt supersedes the historical statement that official byte identity and PDF experiment execution were wholly pending. It does not establish independent full-row agreement.

## Next executable bounded cohort

**Must:** one genuine publisher HTML table (PRISMA-S 2021 Table 1, DOI 10.1186/s13643-020-01542-z), independently bound to the retained CC BY 4.0 JATS table's 16 printed IDs, complete topic/requirement digests, four ordered section headings and source anchors. Explicit URL: https://link.springer.com/article/10.1186/s13643-020-01542-z/tables/1. Hold missing bytes, conflicting identity, spans, missing/duplicate/reordered rows, unknown section or text differences. Rendered visibility remains separate. New publisher HTML bytes must be pinned and replayed before broader admission. No raw source publication.

**Must:** 42-item pinned PRISMA 2020 PDF positive control; independently run pdfplumber ruled-table extraction and the existing Poppler numbered-row parser on identical original bytes. Check full requirement-cell fingerprints and exact ordered ID/page correspondence, record versions and anchors. Preserve discrepancies; do not substitute legacy text or reuse the first parser's intermediate. Retry EcoEvo PDF header recognition only, retain the prior failed receipt and do not interpret Poppler ID recovery as full-row agreement.

**Should:** repeat on independent families/editions and qualify EcoEvo full-row layout, item 8.3 and source hierarchy. **Won't:** OCR, a new parser dependency, automatic source/rights admission or semantic model escalation in this slice.

Reproduction: `python -m scripts.qualify_real_source_formats --root . --html /tmp/prisma-s.html --output /tmp/qualification.json` (HTML must be explicitly acquired; omitted path yields a held receipt). Existing Assurance Python artifact includes the new receipt; ordinary CI is offline for source acquisition, changed qualifier/explicit workflow dispatch triggers the bounded fixed publisher request. Run exact-head tests and examine actual artifact before marking any qualification gate complete. The parser/receipt additions are independently revertible. Existing canonical and legacy runtime authority is unchanged.

## Disposition

Implementation candidate only until exact-head tests and real-source receipt are inspected. T01.5b and T01.5c remain open for actual complete source-side structural and independent PDF evidence, with separate rights, interpretation and pack-admission gates. No claim of a corpus-wide pass.
