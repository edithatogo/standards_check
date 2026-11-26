# Independent guideline family intake — 26 November 2026

Track 01 T01.052, T01.050 and T01.053; issues #95, #111, #158.
This is a development/source-qualification batch, not the frozen E4–E8 population.

The 25 November main census artifact [15031534787](https://github.com/edithatogo/standards_check/actions/runs/45635380131/artifacts/15031534787)
was downloaded and its SHA-256 matched the API (21046589502f064d54800c9f495d72d18b97184a1db376f06da773b84bde3f01).
It accounts for 720 directory entries; all six priority acquisitions were held.
Historical [45407700732 artifact 14925188826](https://github.com/edithatogo/standards_check/actions/runs/45407700732/artifacts/14925188826)
verified 21 ARRIVE main row IDs across the two tables but both structures were held for block boundary differences.
The new main [45737558138](https://github.com/edithatogo/standards_check/actions/runs/45737558138)
retained 82 exact pinned candidate rows (26 PRISMA-P, 16 PRISMA-S, 12 PRISMA Abstracts, 28 CHEERS);
all four flat snapshots lack structural evidence. PRISMA 2020's separate PDF comparison verified 42 rows.
Only that one source-reconciled canonical pack is admitted; no independent interpretation acceptance implied.

## Bounded acquisition

Use the existing priority survey and source retrospective in
[equator-catalogue.yml](../../.github/workflows/equator-catalogue.yml).
The [issuer co-publications page](https://www.consort-spirit.org/published-statements)
confirms identical 2025 statements across journals. PLOS primary versions
(CONSORT DOI 10.1371/journal.pmed.1004587, PMC11996237;
SPIRIT DOI 10.1371/journal.pmed.1004589, PMC12037212)
are explicit additional source manifestations, not separate independent families.
The publisher documents [single-article JATS download](https://api.plos.org/text-and-data-mining.html).
For explicitly selected PLOS sources, use that fixed-host, bounded, no-redirect path first,
then the existing Europe PMC and PMC OAI routes on acquisition failure. Do not fall back
to alternate editions after a source identity, rights or structure failure.
Record all attempts, response digests and item/structure holds; no automatic repin.
No new third-party content is committed by this change.

The selected independence components are provisional: PRISMA (including P/S/abstracts),
CHEERS, ARRIVE, harmonized CONSORT/SPIRIT (including co-publications), STROBE, STARD,
and TRIPOD+AI. Shared base/extension or derivative text links may merge components
before sampling. A group containing both trial protocol and report remains one
component for leakage prevention, not one applicability scope. CARE co-publications
reviewed have restrictive licences; defer. BMJ copies of CONSORT, STARD and TRIPOD
display inconsistent commercial-reuse wording; hold until exact-manifest review.
CHEERS BMC article expressly describes CC BY 4.0 and 28 items; ARRIVE PLOS
statement describes CC0. Item/table rights and independent wording/structure remain separate.

Do not use 42 + 82 as an independent sample size: PRISMA descendants are correlated.
Acquire raw representations and source-local rights, compare ordered printed identifiers,
nested blocks, footnotes, complete anchors and exact words against a separate
issuer/publisher representation. No hashes or reader counts imply equivalence.
A reviewed family source inventory can precede pack promotion; it must not enter a
frozen benchmark before source, rights, interpretation and independence gates are met.

The clinical methods reference will be constructed on eligible development families
only; review target labels independently from retrieval predictions, include the
complete bounded target pool (or retain known sampling probabilities), and keep
ontology concept/role labels separate from directional obligation relations.
Do not create gold labels from TF-IDF, a single model or the acquisition reader.
No actual human adjudicator has been enrolled in this increment.
