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
one terminal full stop. Markdown task-list first-line scope is explicit, so
multiline/paraphrased rows may be false mismatches, not scientific defects.
All item identifiers, mismatches and missing acquisitions are retained.

No automatically generated canonical pack, external validation, migrated
user completion state, blanket rights decision or methodological compliance
claim. New source-reconciled packs require explicit pinned source bytes,
licence/attribution, item-level verification, exact structure, contract and
lock checks. Legacy text cannot certify the new source. CHEERS is reporting
guidance and must not be turned into a methodological quality score.

Reproduce offline with the same explicitly acquired XML files:

    python -m unittest tests.test_reconcile_authoritative_articles -v
    python -m scripts.reconcile_authoritative_articles --source-dir /path/to/xml \
        --output /tmp/authoritative-article-reconciliation.json --require-all

## First acquisition evidence

[Run 45268251861, job 138020843759](https://github.com/edithatogo/standards_check/actions/runs/45268251861/job/138020843759) successfully acquired all four selected XML articles and extracted **82/82** expected item IDs. The [source-table and item comparison artifact](https://github.com/edithatogo/standards_check/actions/runs/45268251861/artifacts/14864257046) was inspected and the ordered row digests independently recomputed before committing the pins. That first run contained a strict zero-match diagnostic; it did not account for unnumbered CHEERS labels or terminal full-stop-only differences. The follow-up comparison corrects these diagnostics without changing any primary-source text or source pin. It remains a source-reconstruction candidate; no canonical pack is promoted.
