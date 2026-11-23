# Primary article checklist-table reconciliation

Track 01 / #111 and #95. Selected explicit primary versions from the issuing
groups' open-access statement articles, cross-checked through PubMed / PMC.
PRISMA-P (26 printed identifiers), PRISMA-S (16), PRISMA 2020 Abstracts (12),
and CHEERS 2022 (28) are the first bounded cohort. CHEERS uses the BMC
Public Health co-publication with clear CC BY 4.0, not the BMJ copy with
inconsistent copyright wording. ARRIVE 2.0 is deferred until its nested
lettered recommendations can be separately reconciled; 21 main rows alone
do not establish full coverage.

The source manifest selects the exact DOI/PMCID, table caption and label,
expected ordered item IDs, column offsets and source licence. The existing
Canonical Standard Pack workflow acquires only these fixed, openly retrievable
JATS XML records from Europe PMC (https://www.ebi.ac.uk/europepmc/webservices/rest/).
The acquisition runs in a disposable runner directory. XML length, article
identity, machine-readable CC BY 4.0, table identity, and complete row IDs
must pass. Each extracted row retains its anchor and normalized exact-text
SHA-256, and each article its original byte SHA-256. Only the selected
checklist table rows and comparison receipts are retained; no unrelated
article full text or images are uploaded. Attribution/change notices accompany
each extract. Separate table rights metadata blocks admission. The first successful hosted acquisition established the byte pins; the
manifest now requires exact byte SHA-256, byte length, table ID and ordered
row JSON SHA-256. Any source drift is a hard failure, never an automatic
edition update.

Legacy checklist rows are compared independently, with exact whitespace-
normalized complete requirement phrases and declared legacy numbering
reported separately. Same number is not a match; lexical similarity is only
a candidate for investigation. Editorial bold numbering and unnumbered bold topic labels ending in a
colon are stripped independently of declared item IDs. Strict equality
retains punctuation; a separate diagnostic flags a difference limited to
one terminal full stop. The initial receipt used first-line-only Markdown task extraction. It is superseded by the shared bounded reader described below; historical counts must not be compared without noting the changed extraction scope. Paraphrased rows may still be false mismatches, not scientific defects.
All item identifiers, mismatches and missing acquisitions are retained.

No automatically generated canonical pack, external validation, migrated
user completion state, blanket rights decision or methodological compliance
claim. New source-reconciled packs require explicit pinned source bytes,
licence/attribution, item-level verification, exact structure, contract and
lock checks. Legacy text cannot certify the new source. CHEERS is reporting
guidance and must not be turned into a methodological quality score.

Reproduce routinely from retained source-table snapshots (network-free), or supply the original pinned XML files to reproduce the extraction:

    python -m unittest tests.test_reconcile_authoritative_articles -v
    python -m scripts.reconcile_authoritative_articles --output /tmp/offline-reconciliation.json --require-all
    python -m scripts.reconcile_authoritative_articles --source-dir /path/to/xml \
        --output /tmp/authoritative-article-reconciliation.json --require-all

## First acquisition evidence

[Run 45268251861, job 138020843759](https://github.com/edithatogo/standards_check/actions/runs/45268251861/job/138020843759) successfully acquired all four selected XML articles and extracted **82/82** expected item IDs. The [source-table and item comparison artifact](https://github.com/edithatogo/standards_check/actions/runs/45268251861/artifacts/14864257046) was inspected and the ordered row digests independently recomputed before committing the pins. That first run contained a strict zero-match diagnostic; it did not account for unnumbered CHEERS labels or terminal full-stop-only differences. The follow-up comparison corrects these diagnostics without changing any primary-source text or source pin. It remains a source-reconstruction candidate; no canonical pack is promoted.

## Durable source row snapshot and routine CI

The attributed 82-item table extract is retained at `source/official/authoritative-article-rows.json` (Git blob `c29794b3bcf7863e9f30c4ebc83e70b8d1b05450`). The independently reconstructed artifact-derived Git blob matched exactly. It is a normalized table projection, not the original XML itself. Offline validation reconstructs each item text digest and checks the complete ordered table hash, item IDs, anchor, exact DOI/PMCID, licence and attribution against the pinned manifest. On changed source rows/manifest/comparator, or explicit workflow dispatch, the same workflow also reacquires the selected XML and verifies full article bytes and ordered row hash. An incidental publisher/archival XML revision is reported as drift; there is no automatic repin. Routine comparison does not depend on publisher network access.

## T01.5b — independent structure receipt (additional candidate)

The XML route now also records a fingerprint-only description of all body rows
(including rows skipped by the numbered-item projection), candidate section
headings, explicit and inherited cell coordinates, row/column spans, nested
paragraph/list/definition blocks, and footnote IDs/references. Block-aware and
flat text hashes are kept separate; a block-boundary difference, unclassified
row, duplicate footnote ID or unresolved footnote reference is held for
structural reconciliation. Nested tables, unsupported row groups and invalid
spans are held, not guessed. This covers the selected bounded rectangular JATS
dialect only; the structure is not an independently validated interpretation.
No additional source text, existing row fields, source-byte pins or row
digests are changed. The report schema advances to 2 with an explicit
structure status count. Offline flat snapshots report
`not_retained_in_flat_snapshot`: they cannot prove the original XML structure.
The existing `--require-all` remains the exact-row acquisition gate, not a
structural qualification gate. The raw pinned XML must be replayed to establish
the additional evidence; unsupported or discrepant structure cannot be
promoted by the existing row match.

Five new synthetic structure tests ran RED/GREEN locally on Python 3.13.5
against exact Git blobs. Four additional integration/negative tests exercise
the current XML/snapshot/CLI paths and address the previous patch-coverage
gap; hosted receipts and observed coverage are still required. Preserve
the source-only scope, zero promotions and original attribution. The shared legacy reader was subsequently integrated after #135 merged; see below.

## Shared legacy structural reader (after #135)

Both article and local-original probes now use `parse_legacy_tasks` from
`scripts/legacy_checklist_structure.py`. No second task-list regex or
editorial-label parser remains in the article comparator. Whole captured
requirements are normalized for comparison; nested checkbox parent ordinals,
section/line anchors, original indentation and warnings are retained separately
with a normalized requirement digest and exact view SHA-256. Declared labels
remain exactly distinct (e.g. S2 versus 2); do not infer identity by stripping
prefixes. Source row and article-byte pins are unchanged. A regression covers
multiline and nested tasks, ambiguity flags, and no raw legacy text in receipts.
Historical first-line match counts are not comparable without rerunning.
