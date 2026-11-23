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

## Hosted first-pass alignment evidence

At candidate head `91de403c676be189c563aaa0b8749d36c894165b`,
the [read-only extraction job](https://github.com/edithatogo/standards_check/actions/runs/45144383189/job/137589937451)
executed **seven** Python regression tests successfully, then reconciled the
**56** existing entries against **719** upstream published pages at
EQUATOR `bbd7bc55fcb0698ef493ae66685924b5b2ddc276`. The
[retained source and alignment artifact](https://github.com/edithatogo/standards_check/actions/runs/45144383189/artifacts/14802458653)
contains the full metadata and original-file SHA-256 evidence. One upstream
page changed relative to the committed `discovery.json` pin; no update was
silently made.

| First-pass observation | Count | Interpretation |
| --- | ---: | --- |
| EQUATOR candidates | 42 | 9 direct EQUATOR URLs, 3 DOI candidates, 20 exact slug candidates, 7 family slug candidates, 3 acronym candidates; **none** is source-content admission |
| No confident candidate | 14 | Source-identity investigation required; includes the ACE appraisal-tool mismatch and alias/edition ambiguities |
| Present original-file assets | 17/56 | SHA-256 recorded, but a local copy is not proof that it is the authoritative edition |
| Existing legacy Markdown | 55/56 | Text/item counts are evidence to audit, **not** verification or a source oracle |
| Repeated legacy item arrays | 4 records | Duplicate 3-item placeholder structures must not be accepted as distinct standards |
| Orphan legacy parent references | 3 | SPIRIT extension references to absent `spirit-2013` |
| Possible edition mismatches | 5 | Includes CONSORT 2010 against the current CONSORT page |
| Counts inconsistent with independent item-ID fixtures | 5 | ARRIVE 22 vs 21; CHEERS 27 vs 28; COREQ 26 vs 32; PRISMA-P 19 vs 26; SPIRIT 32 vs 53 |
| Legacy PRISMA vs canonical pack | 27 vs 42 | An old aggregate view is not the current 42-item pack |
| Index/sidecar licence declaration differences | 29 | Differences in **claims**, not an automated copyright verdict |
| Index checksum discrepancies | 2 | CONSORT 2010 and STROBE 2007 index digests differ from present assets and sidecar claims |
| Other sidecar checksum discrepancy | 1 | PRISMA-EcoEvo: investigate the intended format/source bytes |
| Sidecars claiming `verified: true` | 17 | Historical flag has no authority to promote a canonical pack |

The initial acronym heuristic falsely suggested PRISMA for Abstracts
(`prisma-a`) was PRISMA for Acupuncture because EQUATOR uses the overlapping
PRISMA-A label. A failing synthetic regression preceded the correction: acronym
matching must now have a discriminating title-token agreement. The revised
source-only job confirms **14 unresolved candidates** rather than silently
assigning this false pair.

**Next automated stage:** for each selected edition, first obtain and pin
the issuing body's versioned source (when access and rights permit); use
separate publisher/DOI/PMID and source-file evidence; extract complete
numbered item/subitem spans; compare exact normalized wording and chapter
anchors to the local legacy text and the canonical pack, recording discrepancy
receipts and independent extractor disagreement. Optional NLP/NLI may route
cases for investigation, not confer a source-rights, method or licence decision.
All unresolved records remain unadmitted indefinitely in a no-human workflow.

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
