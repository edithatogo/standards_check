# Research and publication programme

Owner issue [#158](https://github.com/edithatogo/standards_check/issues/158).
Conductor 01 representation and corpus; 04 consumer interoperability; 05
verification and research qualification. Use [protocol 0.1.0](protocol-v0.1.0.md),
[agent contract](contract.json), [historical evidence](evidence-2026-11-24.json)
and [versioned profile](../specifications/reporting-guideline-interoperability/versions.json).
No approved profile or submission yet.

| Output | Research deliverable | Release/acceptance gate |
| --- | --- | --- |
| P1 technical specification/RFC | Versioned normative profile, examples, conformance matrix and reference implementation links | Explicit owner version approval, prior-art gap analysis, stakeholder comment ledger, independent consumer example |
| P2 methods manuscript | Full-directory census, format/rights holds, paired method ablations, independent labels/witness limitations, robustness/calibration and error taxonomy | Freeze/register prospective protocol, execute source/analysis receipts, reproduce tables and figures independently, disclose limitations and AI |
| P3 software manuscript | StandardFlow architecture, reproducible installation, rights-safe examples, downstream research use, support and maintenance | Qualified versioned release, signed/reproducible artifacts, consumer/usability/accessibility tests, journal eligibility |
| P4 secondary papers if warranted | Cross-edition and translation fidelity or manuscript evidence-assessment methods | Distinct research question, protocol/cohort and independent evidence, no redundant publication |

Candidate methods venues: BMC Medical Research Methodology, Journal of Clinical
Epidemiology, or a suitable informatics journal after scope/requirements review.
JOSS is a separate software paper, not the methods results; its current
[submission criteria](https://joss.readthedocs.io/en/latest/submitting.html)
require meaningful research impact, feature completeness and sustained public
development. Do not infer eligibility now. RFC/DOI archive through the existing
release process after explicit approval; no automatic registration or submission.

## Sequence and outputs

1. Literature and prior-art map: search MEDLINE/PubMed, Crossref/OpenAlex,
   relevant scholarly databases and repositories for computable reporting
   guidelines, normative requirement representations, checklist automation,
   provenance/rights and document extraction/NLI; register exact queries,
   dates, selection and evidence. Reuse Searchright and SourceRight/CiteLattice
   where exact consumer contracts permit. Distinguish implementation from
   independent validation; no unverified references or self-asserted novelty.
2. Freeze the protocol and contract with owner decision. Use current directory
   acquisition/retrospective and source projections; route all entries and
   expand structural candidate extraction as real source errors become visible.
3. Freeze prospective evaluation strata/labels and run existing harness;
   independently reproduce quantitative results, compare orthogonal methods,
   record failed receipts and revisions. Generate tables/figures from validated
   evidence, never copied LLM-generated numbers. Evidence ledger is descriptive
   until future prospective receipts are accepted.
4. Draft separate technical, methods and software manuscripts. Every material
   claim references an evidence ID/receipt or verified cited primary source;
   label limitations and hold unsupported assertions. Independent skeptical
   methods, citation and rights reviews, then owner signoff on final bytes.
5. Produce rights-cleared reproducibility bundle (RO-Crate/DOI when useful,
   pinned code, schemas, fixtures, aggregate data, checksums, reproducible
   scripts, CRediT and AI disclosure, change log). Submit only with explicit
   owner approval and actual destination/journal checks.

Use [ICMJE AI policy](https://www.icmje.org/recommendations/browse/artificial-intelligence/),
[EQUATOR development toolkit](https://equator-network.org/toolkits/developing-a-reporting-guideline/)
if substantive reporting guidance is ever proposed, and the applicable
reporting standards for each study design. If this becomes a consensus
reporting-guideline development study, consult ACCORD and the relevant
development guidance rather than claiming consensus from agents. This is
currently a technical interoperability profile. No authorship for agents.

## Initial execution receipt

Six isolated tests passed (directory routing and profile/evidence guards).
Actual 720-entry artifact replay passed with no canonical promotions.
The exact historical data and digest are in the evidence ledger; this is
not a prospective scientific acceptance. Witness-v2 gate failed despite
DeBERTa improving formal-control classifications. No natural consensus.
Run `python -m scripts.publication_contract --output target/publication/receipt.json`
for offline consistency; add `--directory-artifact <verified zip>` for exact
historical directory replay. Full repository CI and scheduled receiving
workplan integration are separate.
