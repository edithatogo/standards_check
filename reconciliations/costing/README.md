# Costing and valuation reconciliation

This catalogue connects costing-related reporting requirements with shared economic concepts.
It records a bounded primary-source review checked on **8 November 2026**, with **26 source
records, 31 semantic domains and 106 verified item or principle identifiers**. It is an editorial
research seed requiring independent review, not an endorsed consensus standard or an exhaustive
international systematic review.

The 26 records include six context publications (development/study protocols and evidence
reviews), as well as reporting, methods, appraisal and historical instruments. They are not
26 current reporting guidelines. Verified identifiers remain **`research_seed_review_required`**:
source-ID verification does not validate the editorial semantic mappings.

## Contents and verification scope

- [Source registry](costing-standards-registry.json): publication, version, category, status,
  applicability, primary URLs, verification dates, coverage and remaining gaps.
- [Item mappings](costing-item-mappings.json): original source identifiers, short original topic
  labels, source locations and many-to-many associations with shared domains.

| Instrument and source used | Verified identifiers | Scope |
| --- | ---: | --- |
| [CHEERS 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC8749494/) | 28 | Table 1 numbered items |
| GHCC reference case (principle pages below) | 17 | Methodological principles, not all detailed checklist subrows |
| [AGREEDT 2018](https://journals.sagepub.com/doi/10.1177/0272989X18797590) | 44 | Table 1 numbered diagnostic economic-reporting items |
| [CHEERS-VOI 2023](https://www.valueinhealthjournal.com/article/S1098-3015%2823%2903031-0/fulltext) | 6 | Table 2 supplemental items S1-S6; inherited/elaborated items are not transcribed |
| [iDSI reference case](https://www.sciencedirect.com/science/article/pii/S1098301516304405) | 11 | Table 1 numbered methodological principles |

GHCC identifiers were checked against its official principle pages:
[study design, 1-5](https://ghcosting.org/pages/standards/principles/study_design.php),
[resource measurement, 6-10](https://ghcosting.org/pages/standards/principles/resource_use_measurement.php),
[valuation, 11-14](https://ghcosting.org/pages/standards/principles/pricing_and_valuation.php), and
[analysis/reporting, 15-17](https://ghcosting.org/pages/standards/principles/analysing_and_presenting_results.php).
Every individual mapping also records its actual source URL and table/principle locator.

Other records are verified at publication/scope level and deliberately have zero item mappings.
Their presence does not imply that a full checklist was retrieved, transcribed or reviewed.
Some publication and scope verification relied on primary publisher search extracts or PubMed
records where full-text opening was intermittently unavailable. Consult each original source
for its exact wording, recommendations and conditions of use.

Mappings use `covers_topic`: this is an editorial association, not logical equivalence. Domains
and mapping IDs are stable metadata identifiers; they do not rename original checklist items.

## Relationship to the checklist pipeline

This directory contains reconciliation metadata. It adds **zero full checklist transcriptions**
and is separate from the source-to-canonical-to-format pipeline. It must not be used to generate
purported official checklists from abbreviated topic labels.

The existing [CHEERS source sidecar](../../source/archetypes/cheers-2022.yml) and
[canonical Markdown](../../markdown/en/archetypes/cheers-2022.md) remain the checklist records.
To add another complete instrument, follow [CONTRIBUTING.md](../../CONTRIBUTING.md):

1. Verify the original, reuse permission, exact edition and identifiers.
2. Register it in `source/index.yml` and ingest originals with provenance in `source/`.
3. Use the repository scaffolding workflow for canonical Markdown.
4. Produce Typst and LaTeX through the existing pipeline, preserving source numbering.

Each new instrument should link back to this catalogue where useful. A metadata record alone
does not satisfy source-ingestion, transcription or format-parity requirements.

## Keep instrument purposes distinct

| Purpose | Included examples | Interpretation |
| --- | --- | --- |
| General reporting | CHEERS 2022 | Reporting completeness, not a numerical quality score |
| Conditional reporting | AGREEDT, CHEERS-VOI, CHEERS-AI | Apply according to study/intervention characteristics |
| Costing methods and reporting | GHCC, TDABC, iDSI, ISPOR BIA | Preserve methods and context-specific recommendations |
| Sector reporting | Immunisation, UNAIDS strategic-plan costing | Adaptation to a defined service or programme |
| Jurisdictional costing | AHPCS 4.2, NHS England 2026 | Accounting, allocation and reconciliation obligations |
| Measurement and valuation tools | PECUNIA | Harmonised units and methods; retain access/use conditions |
| Appraisal and validation | COI 2023, CHEC, Philips, AdViSHE | Separate judgements about methods and validation evidence |
| Historical instruments | CHEERS 2013, BMJ 1996 | Legacy interpretation and provenance |
| Protocols and evidence reviews | Xu 2016, CHEERS ClimatE, genomic studies | Evidence or development plans, not completed generic standards |

`published_current_identified` means an applicable published edition was found and no successor
was identified in this search. It is not proof that no successor exists. `published_established`
denotes an established publication without a claim of a uniquely current edition. `published`
denotes a published study/review. `legacy` and `superseded` preserve history.
`protocol_only_verified` explicitly excludes treating development plans as completed guidelines.

For new costing work, combine CHEERS and GHCC with applicable modules. Screening and genomic
strategies particularly benefit from AGREEDT. Budget-impact analysis needs a budget-specific
profile. CHEERS-AI is conditional on the intervention using AI, not merely the analyst using an
AI coding or writing tool. Country-specific methods should be versioned policy profiles.

## Evidence and assessment semantics

Keep reporting completeness, methodological appropriateness, computational correctness and
empirical validation as separate assessments. A field's presence cannot establish that its
method is appropriate. A result should retain its source observations, assumptions, allocations
and valuation policy. Preserve justified not-applicable, missing, not-reported, unclear and
not-assessed states rather than collapsing them into one boolean.

The 31 domains support integration with an ontology while preserving each external source's
identity. They are conceptual domains, not a new item numbering scheme. Shared economic objects
should distinguish physical quantities from their valuation, resource costs from tariffs and
payments, and accounting reconciliation from economic opportunity-cost estimation.

## Coverage limitations and next steps

- No completed universal successor to the 2016 microcosting checklist protocol was verified.
- CHEERS ClimatE was verified as a 2025 protocol/proposal; its final consensus checklist remains
  unverified in this review. Climate impacts do not cover all environmental effects.
- No formal CHEERS-DCEA extension, generic CHESS costing checklist or universal newborn-screening
  microcosting checklist was verified. These are bounded search findings, not claims of absence.
- Complete original-table verification for TDABC, CHEERS-AI, COI, BIA, immunisation, UNAIDS and
  jurisdictional profiles before claiming item-level coverage.
- Review the semantic mappings independently. Maintain source-specific conflicts and exclusions.
- Continue national HTA manual, specialty, translation and successor-version surveillance.
- Select study-design adjuncts such as CONSORT, STROBE/RECORD, STARD, TIDieR and PRISMA separately.

Only short original summaries and semantic mappings are included. Original source permissions
remain applicable; the repository's documentation licence does not relicense external sources
or permit redistribution of restricted instruments or spreadsheets.

## Validation

From the repository root:

```sh
python3 scripts/validate_costing_reconciliation.py
bash scripts/validate_md.sh
bash scripts/validate_index.sh
```

The dedicated validator uses the Python standard library. It checks identifiers, source/domain
references, source URLs, status distinctions, verification scope, dates, duplicate items and
declared-versus-actual verified counts. It rejects transient retrieval IDs. It does not verify
the accuracy of sources or endorse the mappings. The existing Markdown/index validators inspect
the canonical pipeline, not this catalogue; inspect their messages as well as exit codes.
