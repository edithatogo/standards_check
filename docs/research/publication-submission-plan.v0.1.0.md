# StandardFlow publication and submission plan 0.1.0

Status: **supplemental draft; no submission, accepted paper or new experimental result**.
Planning and policy-review date: **2026-11-25**. Baseline implementation:
`82e4a1efc136187f42b31347ada44506d2d96bfa`.

This plan operationalizes the immutable [protocol 0.1.0][protocol] and
[representation profile 0.1.0][profile]. It does not change their hashes or the
[publication contract][contract]. That contract currently has three planned experiments,
no freeze, zero registered runs and zero observed claims. Historical operational or
experimental receipts must retain their original identity; they cannot be relabelled
as prospectively registered results. Data releases follow the [dissemination plan][data-plan].

## Recommended route and contribution

Develop **one integrated methods paper first**, targeting **BMC Medical Research
Methodology** after the planned source and assurance evaluation is complete. Its scope
includes healthcare research methodology, data quality and reporting [1]. The useful
claim to test is that source-bound, edition-aware representation and measured assurance
make reporting standards more faithfully reusable. Model superiority and autonomous
study-quality assessment are not required claims.

Prepare **arXiv as the default technical preprint route**, with category selection based
on the finished manuscript. Release it only after the paper and artifacts pass their
gates and the selected conference's anonymity policy has been checked. Target
**ESWC 2027 Posters and Demos** for an independently reproducible exchange demonstration;
its later deadline is more realistic than compressing the empirical programme into a
December full-paper submission. These are recommendations, not bookings or submissions.

Use **Scientific Data, Article** as an alternative lead venue if the eventual contribution
centres on the representation, resource and interoperability evaluation. A **Data
Descriptor** is a different article type and becomes appropriate only when a useful,
well-documented, technically validated and distributable dataset is ready. Reserve
**JOSS** for a later, distinct software contribution that meets its current development
and research-use requirements. Do not publish essentially the same evidence as separate
methods, data and software papers merely to increase output count.

### Prior art and the defensible gap

[Batista et al. (2022)][prior-art] already describes machine-actionable reporting models,
JSON-ScheeLD, MIRcat/FAIRsharing and CEDAR export. [CEDAR][cedar] already represents
modular metadata templates, constraints, instances and version history. These are
comparators and potential reuse targets. Machine-readable guidelines, schema composition
and generated forms alone are not new contributions.

The proposed incremental contribution needs evidence for source/edition reconstruction,
preservation of obligation scope, rights and interpretation boundaries, and auditable
assurance across heterogeneous reporting standards. The paper must include executable
mapping examples, explicit losses/holds and limitations against the actual upstream
models. A feature-comparison table with no tested exchange is insufficient to claim
interoperability or superiority.

## Methods and evidence improvements

### Preserve the prospective boundary

Use historical directory and model receipts to design the study and identify failure
families. Report them as exploratory. Before new confirmatory execution, finish the
protocol's sample/threshold/model-pin blockers, freeze the exact design and inputs,
and record the real decision in Git. If an experiment changes after freeze, create
a new versioned protocol/contract path, retain the previous freeze and all failed runs,
and use untouched evaluation material for the new confirmatory claim. Reuse the
existing contract validator and its baseline history guard.

The [receiving-main source census][census] conserves 720 identities, 176 acquisition
records, 21 held item fingerprints and 2,299 findings. It provides a concrete operational
baseline, not a completed E1/E2/E3 publication study. The [programme receipt][programme]
also records qualified limitations of earlier formal and natural-source experiments.
Green CI, exact hashes and formal-control accuracy cannot substitute for natural-source
evaluation or independent interpretation evidence.

### E1: coverage, reconstruction and exchange

- Freeze the catalogue denominator and distinguish entries, editions, source artifacts,
  printed items, subitems and evaluated mappings. Give acquisition, structural fidelity,
  text fidelity, interpretation and rights their own numerators and held reasons.
- Report repeated provider observations separately. An inaccessible source on one run
  does not erase previous evidence; a previously recovered source does not make the
  current acquisition successful. Avoid a monotonic coverage curve that merges these.
- Test headers, ordered rows, hierarchy, footnotes, inherited cells, exceptions and
  non-body text. Retain both strict byte/text comparisons and explicitly defined layout
  normalization; do not silently normalize away a material obligation difference.
- Add a small prespecified CEDAR/JSON-ScheeLD exchange panel covering the profile's
  required distinctions. Re-import exported examples and record exact conserved fields,
  intentionally external evidence and unsupported features. Describe those limits as
  observed interoperability results, with the tested versions pinned.
- Treat failure-family prioritization as an operational scheduling policy. Keep its
  selected acquisition subset separate from the unbiased or prespecified evaluation
  sample; otherwise practical triage can distort the reported denominator.

### E2: reference quality and uncertainty

Preserve the existing five-class definitions and direction. Lock family-level splits,
source-only blinded packets, adjudicator versions and prompts before predictions.
Independent sessions and different model architectures do not prove independent errors.
Keep initial adjudicator decisions, disagreements, resolver decisions and their anchors.

Call the result a **model-agent reference** unless an additional independent reference
has actually been obtained. A bounded audit by independent source/domain reviewers
would strengthen claims about issuer intent; it is a recommendation, not a completed
human-labelled benchmark or an automatic prerequisite for every exploratory experiment.
Without that evidence, limit conclusions to the stated reference and publish its
disagreements and stability checks.

The primary false-equivalence denominator remains **predicted-equivalent outputs with a
usable locked reference**. Unresolved equivalent predictions and usable-reference
coverage are separate outcomes. Zero predicted-equivalent cases gives an undefined
rate, not perfect precision. A resolved source-supported indeterminate class is distinct
from missing reference evidence. Report all five classes, their support, directional
inversions, abstentions and errors by family and format; high precision over one or two
classes cannot establish five-class qualification.

Choose sample size and uncertainty methods from the desired precision, expected usable
reference coverage and family clustering before confirmatory runs. Record the resulting
numerical thresholds in the next frozen design. Avoid treating paraphrases, repeated
editions or inverse pairs as independent observations. Report sparse strata as sparse
rather than producing an unsupported overall score.

### E3: complementary evidence at a fixed budget

Qualify d1-2B only through the existing isolated model lane and repository security policy.
Evaluate its incremental supported detections at a fixed review budget, with the same
inputs and locked reference as the retained baseline. Predeclare how probabilities and
disagreements change triage and what additional false flags are tolerable.

Report shared catches, unique catches, shared misses and harmful changes, together with
domain calibration, risk–coverage, cost and resource use. A candidate with lower standalone
accuracy may still add useful evidence; that benefit must be observed. Keep formal controls,
natural-source outcomes and development calibration separate. Preserve every attempted run
and report inconclusive or negative results. No model vote or probability promotes a pack.

## Manuscript artifacts and agent workflow

Reuse the [publication-evidence skill][skill], existing experiment commands, source
retrospective and contract harness. Add reviewable artifacts around them; do not build
a competing model executor or an autonomous submission service.

| Artifact | Producer and purpose | Acceptance evidence |
| --- | --- | --- |
| Protocol and amendment register | Coordinator binds questions, endpoints, sampling, budgets and stop rules. | Exact design/input hashes and real freeze decision preceding the relevant runs. |
| Prior-art and exchange matrix | Standards curator and adversarial reviewer test reuse and preservation. | Primary citations, exact comparator versions, executable examples and explicit unmapped semantics. |
| Source/rights ledger | Curator records every identity, source, permission and hold. | Complete denominator and reconciliation to released subsets; no inherited blanket permission. |
| Blinded reference packet and decision ledger | Separate adjudicators and resolver produce anchored decisions. | Access separation, model/prompt/source pins, initial disagreements retained and reference lock. |
| Reproducibility bundle | Runner and a fresh-context reproducer use existing commands. | All successes/failures, environment and output hashes, plus independent regeneration of reported tables. |
| Selective data-release package | Curator stages an explicitly permitted operational metadata subset; release reviewer checks its content. | The [offline dataset gate][dataset-validator] binds exact files, columns, source revisions, four reviews and a separate approval. The [initial release contract][dataset-contract] remains planned and blocked; no upload or DOI is claimed. |
| Analysis outputs | Analyst implements only the frozen primary analyses; exploratory work is labelled. | Full denominators, clustered uncertainty, negative controls, calibration and ablation receipts. |
| Manuscript and claim ledger | Writer uses only supported observations; citation verifier reads original sources. | Each quantitative claim maps to a result file/table and each external claim to a primary reference. |
| Submission dossier | Policy reviewer and accountable authors prepare the target-specific package. | Authorship/AI disclosures, permissions, overlap declaration, data/code access, fees decision and author approval. |

Plan figures and tables from their input contracts, before drafting conclusions: a source
coverage/hold table; a reconstruction discrepancy table; a prior-art/crosswalk matrix;
five-class confusion and coverage results; paired incremental-detection results; and a
provenance/authority diagram. Mark absent data as absent. No illustrative result may be
styled as an empirical finding.

The agentic increment is a bounded cycle: one specified question, one retained run or
comparison, an adversarial check, and a claim disposition. The writer cannot repair a
failed experiment by changing its endpoint or selecting a favourable run. Citation and
reproduction checks use fresh contexts and exact artifacts, while correlation among
agents remains an explicit limitation. External peer review and author accountability
are separate from these internal agents.

Venue policy is part of the workflow. BMC requires submission by an author, not a third
party [2]. JOSS currently prohibits AI use in author/editor/reviewer conversational
interactions except translation [6]. If JOSS is selected, authors handle that correspondence;
the general agent workflow does not override the venue's rule.

## Preprint and journal selection

| Route | Recommendation and readiness condition | Policy checked as of 2026-11-25 |
| --- | --- | --- |
| arXiv | Default technical preprint for the completed representation/assurance manuscript; choose the subject category from its actual contribution. | Requires a topical, refereeable scholarly contribution, author registration, appropriate rights and moderation; endorsement may be needed for a first/new-category submission [7]. A specification announcement alone is not the intended manuscript. |
| medRxiv | Alternative only if the final paper is a complete health-methodology study with detailed methods and results. Choose before posting elsewhere. | Tool announcements and guidelines are outside its stated scope. Its submission guide excludes manuscripts already posted elsewhere; do not assume automatic arXiv cross-posting is permitted [8]. |
| BMC Medical Research Methodology | **Primary journal target** for the integrated empirical methods paper. Proceed after the E1/E2 gates; E3 can remain conditional if its scope is declared. | Scope includes reporting and data quality [1]. BMC permits preprints and prior data sharing, requires disclosure of overlap and does not permit concurrent journal consideration of the same substantial work [3]. Ordinary submission guidance states no general closing date. Confirm current fees/waiver arrangements before author submission [2]. |
| Scientific Data, Article | Alternative for a paper principally about the validated representation, sharing workflow and interoperability resource. | Articles cover standards, ontologies, repositories and data-sharing mechanics [4]. Nature Portfolio permits preprints [5]. This is a venue fit assessment, not an assurance of editorial acceptance. |
| Scientific Data, Data Descriptor | Later option for a distinct, reusable dataset whose rights, documentation and technical validation are complete. | Requires access to the described data for review and public release for publication, and focuses on the dataset rather than hypothesis-testing claims [4]. Preserve a static reviewed version [9]. Check its related-publication policy before publishing a paper disclosing the same dataset identifier [10]. |
| JOSS | Conditional software paper with a contribution distinct from the methods paper. Audit actual public development and research use first. | Current gates include more than six months of active public history and demonstrated research use; preprints are allowed, publication has no fee, and AI assistance requires disclosure. Its special correspondence rule applies [6]. Repository age alone is insufficient. |

Do not announce a submission date from a development estimate. The journals' ordinary
submission paths are readiness-driven; special collections have separate calls. A preprint
is public disclosure and not acceptance. If a technical paper and a later methods/software
paper are pursued, record the distinct questions, reused data, new analyses and cross-citations
before submission and disclose overlap to each editor.

## Conference windows and sequencing

The following dates were verified on primary organizer pages for this planning snapshot.
Recheck them before any submission. AoE means 23:59 UTC-12 on the stated date.

| Venue/track | Actual window | Decision |
| --- | --- | --- |
| ESWC 2027 Resources | Abstract **10 December 2026**; full paper **17 December 2026**, AoE. Single-anonymous review [11]. | Relevant for a concrete public resource with tested reuse and a maintenance plan. Optional near-term route only if the resource and manuscript gates genuinely finish; do not accelerate rights or evaluation approval to meet it. |
| ESWC 2027 Research | Same abstract/full dates; decision **19 February 2027** [12]. | Appropriate only for a principled semantic-method contribution with evaluation. Its named-preprint restriction starts one month before submission and lasts through decision/withdrawal; that window has begun. Do not post or update a named preprint while pursuing this track. |
| ESWC 2027 Posters and Demos | Submission **18 March 2027**, AoE; decision **8 April 2027** [13]. | **Preferred conference target.** Prepare a functioning source-to-pack-to-exchange demonstration with explicit holds, a video or live demo, and an actual semantic-technology contribution. Five-page proceedings papers require overlap review; this is not simply an unarchived poster. |
| SWAT4HCLS 2027, Basel | Paper/poster/demo deadline was **30 September 2026**, AoE; event **1–4 February 2027** [14]. | Strong topical fit, but this submission window is closed. Consider a later announced edition; do not invent a late-breaking route. |
| AMIA 2027 Amplify Informatics Summit | Deadline was **3 September 2026, 23:59 Eastern** [15]. | Closed. Revisit a future published AMIA call when clinical research workflow evidence exists. |
| ISWC 2027 | Organizer association lists the event for **October/November 2027**, with location to be announced [16]. | Watchlist only: no verified submission deadline in the inspected official source. Do not substitute historical or aggregator dates. |

ESWC's Resources Track is single-anonymous; the Research Track preprint blackout must
not be generalized to it. Conversely, absence of an explicit resources-track blackout is
not an exemption from duplicate-submission or publisher rules. ESWC full papers cannot
be concurrently under journal review [11, 12]. A later BMC submission using an ESWC
five-page proceedings paper needs a substantive new contribution and explicit editorial
consideration; BMC's automatic allowance for short abstracts/posters does not cover every
conference proceedings paper [3].

## Upstream and repository issue structure

Use [EQUATOR-Network/equator-website#14][equator-umbrella] as the single upstream
umbrella for the proposed technical profile and optional reference implementation.
Keep its purpose small: identifier/edition stewardship, useful exchanges, rights contacts,
feedback and whether EQUATOR wishes to participate. A posted issue is not endorsement.

Keep implementation tasks in `edithatogo/standards_check`: profile/crosswalk governance,
source reconstruction and rights, selective data release, prospective evaluation, consumer
canaries and manuscript readiness. Link each task to the upstream umbrella and link the
umbrella to the maintained repository issue index. Use existing owners/issues where they
already cover the work; avoid asking EQUATOR to manage our model experiments or CI.
The root integration owns issue edits and the exact subissue inventory; this document
does not create or update external issues.

## Next concrete milestones

1. Complete the prior-art crosswalk and selective dissemination field inventory; preserve
   current source and scientific holds. The offline metadata release validator is now
   implemented; the actual package, permissions and review receipts remain outstanding.
2. Finish the prospective protocol/contract freeze with untouched family allocation and
   numerical decision limits. Keep historical results exploratory.
3. Produce the source/exchange evaluation and blinded reference through existing lanes;
   qualify and run E3 only when its model and security gates are ready.
4. Regenerate all proposed tables from retained receipts, perform adverse-case and citation
   review, and package only the approved public materials with exact versions.
5. Assemble the manuscript, target-specific policy record and author-review dossier.
   Authors choose the actual preprint/conference sequence and approve any submission.

No deadline or publication target changes the evidence required to support a claim.

## Primary sources

1. [BMC Medical Research Methodology aims and scope](https://link.springer.com/journal/12874/aims-and-scope).
2. [BMC Medical Research Methodology submission guidelines](https://link.springer.com/journal/12874/submission-guidelines).
3. [BMC editorial policies: preprints, duplicate publication and data sharing](https://link.springer.com/brands/bmc/editorial-policies).
4. [Scientific Data article types and review criteria](https://www.nature.com/sdata/policies/for-referees).
5. [Nature Portfolio preprints and conference proceedings policy](https://www.nature.com/nature-portfolio/editorial-policies/preprints-conference-proceedings).
6. [JOSS submission requirements, AI policy, preprints and fees](https://joss.readthedocs.io/en/latest/submitting.html).
7. [arXiv submission guidelines](https://info.arxiv.org/help/submit/index.html) and [endorsement](https://info.arxiv.org/help/endorsement.html).
8. [medRxiv submission guide](https://www.medrxiv.org/submit-a-manuscript) and [scope/FAQ](https://www.medrxiv.org/about/FAQ).
9. [Scientific Data preservation and static dataset policy](https://www.nature.com/sdata/policies/data-policies).
10. [Scientific Data related-publication policy](https://www.nature.com/sdata/policies/editorial-and-publishing-policies).
11. [ESWC 2027 Resources Track call](https://2027.eswc-conferences.org/calls/papers-resource-track/).
12. [ESWC 2027 Research Track call](https://2027.eswc-conferences.org/calls/papers-research-track/).
13. [ESWC 2027 Posters and Demos call](https://2027.eswc-conferences.org/calls/poster-demo/).
14. [SWAT4HCLS 2027 call and final deadline](https://www.swat4ls.org/workshops/basel2027/call-for-papers/).
15. [AMIA 2027 Amplify Informatics Summit call](https://amia.org/education-events/2027-amplify-informatics-conference/summit-proposals).
16. [Semantic Web Science Association official conference listing](https://swsa.semanticweb.org/conferences/).

[protocol]: publication-protocol.v0.1.0.md
[profile]: ../specifications/reporting-guideline-representation/0.1.0.md
[contract]: ../../contracts/publication/programme.v1.json
[data-plan]: ../architecture/DATA_DISSEMINATION.md
[dataset-validator]: ../../scripts/validate_dataset_release.py
[dataset-contract]: ../../contracts/datasets/standardflow-metadata.v0.1.0.json
[skill]: ../../.agents/skills/publication-evidence/SKILL.md
[programme]: ../../conductor/tracks/01-canonical-standard-pack/representation-programme-20261124.md
[census]: https://github.com/edithatogo/standards_check/actions/runs/45407700732
[prior-art]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9525592/
[cedar]: https://metadatacenter.readthedocs.io/en/latest/yaml-spec/cedar-model/
[equator-umbrella]: https://github.com/EQUATOR-Network/equator-website/issues/14


## Follow-up composition and ontology coverage programme

See [the prospective E4-E8 protocol](composition-graph-protocol.v0.1.0.md) and
[publication contract](../../contracts/publication/composition-graph.v0.1.0.json). Keep E1-E3 unchanged. Plan a distinct methods/utility contribution only if the empirical findings warrant it; recheck venue, preprint and reporting policies at submission. No independent results, ethics approval or submission claimed.

## Exploratory results supplement — 26 November 2026

The [first content-addressed results supplement](../../research/publication/results-v1.md) now consolidates observed and failed development experiments, compares within compatible panels, documents actual resource measures, and starts draft methods, results and discussion. Its 67 input pins, 2,317 metric records and original restricted evidence bundle are linked by the [snapshot receipt](../../research/publication/snapshot-v1-receipt.json). The immutable publication protocol, claim and freeze states remain unchanged. The bounded source-structure diagnostics do not qualify semantic references or close the full specialist factorial; retain existing source-intake and adjudication ownership.
