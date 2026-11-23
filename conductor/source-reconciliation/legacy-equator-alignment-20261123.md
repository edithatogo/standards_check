# Existing checklist-to-EQUATOR reconciliation (23 November 2026)

## Source-of-truth and automation boundary

The maintained legacy `source/index.yml` has **56 records** (36 `mapped`,
10 `new`, 10 without a state). Those labels describe an old scaffold and
**do not verify text, item identities, licensing or suitability**. Existing
PDF/DOCX/CSV originals and legacy Markdown can be hashed and compared, but
they are not the reference against which truth is certified. The approved
PRISMA 2020 Canonical Standard Pack and its retained official-PDF source
comparison are a separate, narrowly supported exception.

The canonical published-source discovery is
[`source/equator/discovery.json`](../../source/equator/discovery.json)
at EQUATOR upstream commit `46124ee9d420cf5477b1b0b1d7e39d2fcf469bc1`:
719 published guideline pages, 236 separate under-development records, and
one known empty title (`strobe-metepi`).

## Automatic reconciliation

The existing monthly [EQUATOR catalogue workflow](../../.github/workflows/equator-catalogue.yml)
now runs `scripts/reconcile_equator_sources.py` and retains
`equator-legacy-alignment.json` in the same **read-only CI artifact**
as the full frontmatter catalogue. It scans legacy item IDs, source URLs,
provisional titles, edition years, parent references, present PDF/DOCX/CSV
bytes with SHA-256, and existing Markdown item count and fingerprint.
It proposes exact URL/DOI, matching slug, acronym or title-similarity
candidates, and flags missing sources, duplicate legacy item arrays,
orphan parents, and possible edition differences. No source is modified.

A candidate match—even exact URL—is **not** an item-level content
comparison, licensed redistribution decision or scientific validation.
The report labels **zero legacy entries as newly verified**; source rights
remain `unassessed` until separately evidenced. Machine similarity scores
are only aids to triage and are never automatic promotion criteria.

## Selected manual source-identity checks (not exhaustive)

- `consort-2010` and `consort-2025` both relate to EQUATOR's current
  CONSORT page, which features **CONSORT 2025**. That does not make 2010
  texts interchangeable with 2025 or automatically update older extensions.
- `tripod-2015` points to a group now associated with **TRIPOD+AI**;
  do not assume the new identity/version supersession is semantically simple.
- Several SPIRIT variants cite `spirit-2013`, which is absent from the
  56-entry inventory. Their parent graph therefore contains missing nodes.
- `ace` is an *appraisal of clinical evidence* tool marked as a CONSORT
  variant in the legacy index; classification requires correction against
  the original issuing body rather than assuming EQUATOR coverage.
- `prisma-a` is described as PRISMA for Abstracts; do not confuse it
  with PRISMA for Acupuncture. The index uses different aliases for several
  extensions, including PRISMA-P, PRISMA-NMA, SPIRIT N-of-1, and dose-finding.
- A legacy `mapped` entry can lack an original asset. Original PDFs in
  `source/archetypes` or `source/variants` may be outdated, unlicensed,
  incorrectly transcribed or unrelated to a current edition.

## Fully unattended operation vs qualification claims

Collection, hashing, catalogue matching, ID preservation, provenance
checks, original-document text extraction when permitted, numbered-item
comparators, deterministic source-drift detection and CI reports **can run
without a human in the loop**. Rights-unclear, edition-discordant or
text-conflicting records remain link-only/held without blocking others.

A fully automatic process cannot honestly assert rights it cannot prove
or invent independent methodological, legal or usability validation.
An optional policy may accept explicit verifiable public licences and
deterministic source-to-item comparisons automatically; other records
must remain unqualified, whether or not anyone reviews them.

### Triangulation / NLP only where it adds value

Use independent evidence channels: primary publication/PDF and metadata,
official publisher/DOI/PMID, edition-specific item number/section anchors,
and extracted item text. Normalize Unicode, whitespace and numbering,
then compare exact item counts and source spans **before** approximate
text similarity. The current report's stdlib `difflib` title similarity
provides low-cost candidate discovery, not validation.

If disagreements remain after deterministic alignment, evaluate optional
controlled NLP/NLI or embedding models as **discrepancy detectors**, with
grounded citation spans, test fixtures, model/version provenance and
adversarial false-match cases. No new embedding service, AI dependency or
LLM attestation is required by the first increment. High similarity is
neither source authenticity nor entailment of reporting requirements.

## Reproducible diagrams

StandardFlow Track 02 already has a deterministic versioned recipe +
scene-graph pipeline for **four PRISMA 2020 flows** and 12 golden
SVG/plain-text/scene-JSON projections. This is the basis for reproducibility;
Searchright owns authoritative review counts. Mermaid and GraphML **are
not currently tested export formats**. Add them as bounded, deterministic
*projections of the same validated semantic scene* only when consumer
requirements justify them. GraphML can preserve directed graph identity
and attributes for tools such as Gephi; Mermaid is useful for docs and
editable text diagrams. Neither should recompute evidence counts or
be treated as a separate source of truth. Full visual/semantic parity
must be tested, not inferred from serialization.
