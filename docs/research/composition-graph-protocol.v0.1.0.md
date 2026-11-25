# Composed reporting obligations, ontology coverage and editorial utility

Version 0.1.0 | 26 November 2026 | Draft for prospective qualification.
No study has been registered, frozen, executed or approved by an ethics body.
This is a follow-up to the existing E1-E3 reporting assurance programme, not a
replacement for its immutable protocol or a claim of scientific validity.
Owners: Track 01 and Track 04; issues #82, #95, #111, #149, #158, #161 and #162.
Machine-readable plans: [publication contract](../../contracts/publication/composition-graph.v0.1.0.json) and
[analytical output contract](../../contracts/analysis/requirement-graph.v0.1.0.json).
The existing [composition architecture](../architecture/CHECKLIST_COMPOSITION.md)
and RGI-01-14 remain authoritative for the proposed technical profile.

## Research question and prior work

Can an identity-conserving, ontology-linked representation of reporting obligations
support cross-guideline retrieval, valid study-specific checklist compression,
recognition of under-specified reporting topics, and evidence-grounded editorial review?
Machine-actionable minimum information checklists and metadata composition already exist:
Batista et al., Scientific Data 9:592 (2022), doi:10.1038/s41597-022-01707-6.
Compare CEDAR, JSON-ScheeLD/MIRcat and relevant established editorial tools against
specific preservation and utility criteria. Do not claim priority for checklists,
ontology mapping, vector retrieval or graph-based retrieval. The proposed contribution
is independently measured conservation, directional relations, calibrated uncertainty,
applicability-aware coverage and incremental editorial utility across standards.

PR 171 implements a local sparse retrieval and display preview. Its designed six-query,
twelve-candidate panel yielded word TF-IDF recall@1 3/6, recall@3 4/6 and MRR 0.628;
character trigram 4/6, 6/6 and 0.833. These are development observations only,
not independent equivalence labels. The historical #155 five-class benchmark failed
its scientific gate; preserve its original receipts and direction convention.
Only PRISMA 2020 has a source-reconciled admitted pack at programme inception.
Directory identities, retrieved editions, item-level reconciliation, rights and
eligibility remain different denominators. Do not proceed to empirical cross-pack
claims on the current single-pack scope.

## Design and sampling

Use exact edition, language, item and source-anchor identities, not checklist titles.
Freeze a complete eligible inventory and a signed-off analysis decision in Git before
evaluation. Define the target population (medical/health research reporting guidelines)
and study/report-type strata: trial protocol, trial report, observational, diagnostic,
prediction, evidence synthesis, economic evaluation, qualitative, implementation and
other designs where qualified. Sample extension/base-guideline pairs and unrelated
families, short/long, conditional, numerical, coordination, negation, overlapping,
broader/narrower and contradictory requirements. Keep protocol/report roles distinct.
Translations, editions, parent/extension and paraphrases must remain together in one
development or held-out family component. Use frozen dev-only model selection and
thresholds; no tuning on evaluation results. An unsupervised retrieval corpus may be
indexed at evaluation time, identically for all methods, but report train-only IDF
as sensitivity; never use held-out labels to fit vectors. Record training-overlap
limitations for external checkpoints.

Pilot with a small rights-qualified development sample from at least four independent
family components; target an evaluation design with at least eight distinct family
components, increased if precision/heterogeneity demands it. These are provisional
planning minima, not a power calculation or available sample. Before freeze estimate
intraclass correlation, prevalence of relevant pairs and reviewer variance on
development-only data; calculate required queries, families, groups, manuscripts and
reviewers for the primary endpoints. Report clustered confidence intervals, not
independent-pair binomial precision when observations share a guideline or reviewer.
If the required population cannot be acquired, report feasibility and descriptive
results only. Record eligible, sampled, reviewed, missing, held and excluded units
with reasons. For natural retrieval labels, enumerate the complete bounded target
pool independently of retrieval where feasible; otherwise use union pooling plus
probability-sampled nonretrieved pairs and appropriate weights with explicit
incomplete-reference bounds. Never call recall over a biased retrieved pool full recall.

## Independent reference and blinding

Create independent reference layers for relevance, five directed relations, concept
mapping, applicability and manuscript evidence. Two domain-trained adjudicators
independently review exact rights-qualified source anchors under a common rubric;
a third resolves disagreements with original votes retained. For exploratory work,
three independent source-only model-agent references can be used with a separate
resolver and an independently sampled human audit. Label such references as
model-relative, not ground truth. Human expert validation is required for claims about
true issuer intent, material reporting gaps and editorial utility. Reference reviewers
cannot see candidate scores, methods, prior decisions or held-out predictions.
Report agreement, confusion, unresolved cases, adjudication time, source anchors and
limitations. Use raw agreement and kappa or an appropriate multi-rater statistic
with prevalence/context; consensus itself is not correctness. Preserve contradictory
witnesses. For RGI-06, narrower means A imposes a stronger obligation than B in the
same explicit applicability universe; retain historical B-relative-to-A labels with
a versioned tested adapter rather than overwriting old results.

## E4: Retrieval and ontology-linking performance

Compare exact/lexical, word unigram-bigram TF-IDF, character trigram TF-IDF and BM25
against one pinned dense bi-encoder; then a separate hybrid reciprocal-rank fusion
candidate (predeclare weights and rank constant on development). Use the same frozen
queries, eligible target pool, candidate budget and normalization. Keep retrieval
relevance (which pairs deserve review) distinct from equivalence. Use public model
cards, licence, exact model/tokenizer/config hashes, reviewed runtime, no remote code,
no silent truncation, same hardware and independent reference. Screen an efficient
sentence-transformer or domain/multilingual encoder on the development population
rather than choose by general leaderboard. Reuse ONNX/CPU first; GPU only where a
measured bottleneck justifies it. Compare macro family-level recall@5 as the primary
endpoint, recall@1/3/10, precision@k, MRR, nDCG, candidate-pair reduction, calibration
where probabilities are meaningful, held/unretrieved counts, timing, peak RSS and
index bytes. Compute paired family-cluster resampling intervals and sensitivity to
pool completeness. Candidate minimum improvement and acceptable cost must be agreed
and frozen before evaluation; no model promotion from the designed panel.

Evaluate ontology multi-label linking separately on the same held-out families:
exact concept ID precision/recall/F1, mapping type confusion, abstention, hierarchy
distance as a secondary measure, multiple-parent sensitivity and independent
adjudicator agreement. Exact ID misses must not be excused by ancestor similarity.
Freeze complete reference annotations or clearly state partial-reference limits.

## E5: Composition and directional assurance

Compare manual expert consolidation, naive similarity grouping (negative comparator),
simple union and the conservative reviewed-group method on matched study scenarios.
Do not expose a risky naive composition as a production feature. Assess identity,
edition and anchor conservation; semantic completeness and additional constraints;
false equivalence, false discharge of a mandatory obligation, unresolved applicability,
conflicts and added/removed obligations; compression ratio, review minutes and
coverage of evidence expectations. Every selected original requirement has exactly one
display membership or explicit held disposition. Require 100% original identity
conservation, zero unreviewed group closure, zero held/unknown omissions and tested
invariance to selection order, repeated packs, direction inversion, rights change,
version drift and negation/quantifier/conditional controls. Compare all-pairs review
with independently authored study-specific reference groups. The primary endpoint is
reference-confirmed material obligation loss per applicable original requirement;
report per-composition risk, unresolved denominator and cluster-aware upper confidence
bound. A proposed safety target is upper 95% bound <=2% among adjudicable applicable
requirements, with unresolved group risk reported separately; final margin and sample
size need owner and expert approval before freeze. Zero observed errors is not proof
of zero risk. Only equivalence reviewed in the identical scope may compress display;
broader/narrower relations never silently discharge a requirement. The current local
hash declarations are not authenticated reviews.

## E6: Ontology coverage, gaps and sensitivity

Start with three independent source layers, frozen by release and artifact hash:
MeSH (NLM descriptors, publication types, qualifiers, tree positions;
https://www.nlm.nih.gov/databases/download/mesh.html and https://id.nlm.nih.gov/mesh/),
Ontology for Biomedical Investigations (OBI; https://obofoundry.org/ontology/obi.html),
and Statistical Methods Ontology (STATO; https://obofoundry.org/ontology/stato.html).
MeSH is a controlled indexing vocabulary, not a normative list of required report
items. OBI covers investigations, study design, protocols, assays and analysis;
STATO covers statistical methods. Use EDAM (https://edamontology.org/) for informatics
methods, data and formats; screen OCRe (doi:10.1016/j.jbi.2013.11.002) for clinical
study design/eligibility after verifying maintained artifact, version and licence.
Use IAO/PROV-O and SKOS/SSSOM-compatible mapping exports where a consumer requires
them, without equating topical mappings to logical implication. Record ontology
release, source URI/hash, import closure, obsolete/replaced IDs, licence and review
permission; no blanket ontology or term redistribution. Select exact production
snapshots, not moving latest URLs. Preserve native IDs/IRIs, hierarchy relation types,
multiple tree placements and independent source identities.

A method concept can be discussed, used as an applicability condition, or be an
object of a reporting obligation. Keep these edge types distinct. Only reviewed
obligation-to-concept mappings count toward reporting coverage. Retain unlinked
requirements and held concepts. Build an independent eligible concept-by-scope
universe from the frozen method taxonomy, literature demand sample and expert rubric
before looking at observed coverage. Sample across depth and rare/emerging methods,
avoid defining the universe only by already mapped concepts. Separate out-of-scope
topics, no reporting need, unknown applicability and held sources. For each eligible
concept-scope cell distinguish covered, partial, candidate gap and unknown. Report
coverage lower bound = reviewed covered/eligible; upper bound =
(reviewed covered + partial + unknown)/eligible, treating the bound as identification
uncertainty, not confidence. A missing map, inaccessible edition or insufficient
ontology granularity is not evidence that a guideline omits a requirement.
Report direct and ancestor-rolled mappings separately; de-duplicate multiple tree
paths, compare equal and fractional weights, depth cutoffs, release changes and
alternative taxonomies. Do not infer quality from centrality or a high citation count.

Classify apparent gaps as incomplete source coverage, unresolved mapping, granularity
mismatch, no applicable guidance found, insufficient specificity, incompatible scope
or independently supported candidate reporting gap. Include exact searched corpus,
ontology concept and scope, evidence of reporting relevance, counterevidence and
expert disposition. Compare algorithmic gap nominations against stratified blind
expert audit of nominated and non-nominated cells; primary endpoint is descriptive
expert-supported gap yield with coverage and uncertainty bounds. Estimate sensitivity
only when the reference universe supports it. Prioritization may combine eligible
gap evidence with independent methodological demand and materiality, not popularity
alone. Neither an ontology nor the graph creates a new reporting obligation.

## E7: Bibliometric and network validation

Pin guideline-edition publication DOI/PMID/OpenAlex IDs through Sourceright and
retain supplements, retractions, ambiguous identifiers and multiple papers per edition.
Acquire references from Crossref (https://www.crossref.org/documentation/retrieve-metadata/rest-api/),
OpenAlex (https://help.openalex.org/data/works/citations/) and where useful PubMed or
OpenCitations. Use Searchright for reproducible search cohort definition and retrieval;
avoid a duplicate reference matcher or crawler. Freeze provider timestamps, query,
pagination, licence and completeness. Use one deduplicated citing work per time
window, count directed citations separately from undirected co-citation and
bibliographic coupling. Co-citation counts distinct citing works that reference both
guideline publications; coupling counts shared cited references of two publications.
Retain denominators, unmatched/unobserved reference coverage, provider disagreements
and publication version uncertainty. Zero observed citations is not zero true
citations. Do not treat co-citation as endorsement, use of a checklist, similarity,
equivalence or coverage. If necessary sample citation contexts using CiteWeft's
anchored spans to distinguish mentions, stated use and explicit use evidence.

Compute raw weights, cosine-normalized co-citation/coupling and Jaccard; compare
association strength and full/fractional counting; stratify by year, field, language,
guideline age and source completeness. Avoid pooling time-dependent snapshots.
Construct separate weighted graphs for reviewed requirement relations, candidate
sparse/dense similarity, ontology hierarchy/mapping, edition relations, citations
and co-citations. Keep node types and edge layers separate and visible. Analyze
components, isolation, degree/strength, betweenness, community stability (seeded
Louvain/Leiden only if useful), assortativity, cross-family mixing and edge overlap.
Use existing Polars and NetworkX when sufficient; use sparse edge lists, chunked
vector comparison and approximate neighbors only when recall/time evidence warrants.
Compare semantic, ontology and citation layers using family/age-matched permutation
or degree-preserving nulls; report robustness across thresholds, seeds, missing
sources and weighted/unweighted networks. Treat 2D PCA/UMAP as display only,
pin parameters and seed, report neighborhood fidelity, never infer semantic groups
from a projection. Network hypotheses are exploratory unless frozen; multiplicity
control or clearly descriptive intervals, with negative/inconclusive analyses retained.

## E8: External editorial utility

Use a consented or otherwise authorized manuscript cohort with full versioned
document evidence, separate from development and held-out requirement training.
First use rights-cleared and synthetic cases including known absent, present,
partial, ambiguous, not-applicable and misleading evidence; then a prospective
multi-editor evaluation only after institutional/ethics determination and agreement
with participating journals. Do not upload private manuscripts or benchmark labels.
Use counterbalanced randomized crossover or matched parallel evaluation on distinct
matched manuscripts to minimize carryover and memorization. Compare usual checklist
review, simple union/lexical retrieval and hybrid graph/vector evidence with equal
review budget and blinded independent finding adjudication. Freeze sample size,
reviewer/manuscript allocation, primary analysis, timing rule, safety/noninferiority
margin and protocol deviations before enrolling. Primary endpoint: paired difference
in independently confirmed material reporting issues per reviewer-hour; model
reviewer and manuscript clustering, order and design effects. Secondary: missed
material issues, false-positive flags, unsupported findings, time, usability and
reviewer agreement. Use a pilot feasibility report if insufficient precision.
Assess added value of graph traversal over sparse/dense retrieval alone and of
citation verification separately. Each finding includes pack/requirement, exact
manuscript anchor, evidence sufficiency, counterevidence, scope and abstention.
Missing retrieved evidence is not proof of absence. No methodological-quality,
publication decision, claim-truth or misconduct inference.

## Planned deliverables and publication

The analytical contract declares table grains, keys, joins, finite metrics, status
and access boundaries. Reuse the nine canonical/diagnostic and four directory
Parquet outputs rather than re-export source prose or invent duplicate authority.
A derived graph is a versioned snapshot of those identities plus new mapping,
relation, citation and evidence tables. Every join is snapshot-bound; preserve
unknown/held denominators, stable IDs, exact producer revisions, source hashes,
parameter manifests, rights and review receipts. Use JSON Schema and the existing
Polars writer after qualifying numeric fields and foreign-key/row conservation.
Outputs include flow counts, retrieval curves, confusion matrices, conservation/
compression plots, ontology heatmaps and coverage bounds, candidate gap audit,
bipartite/network layouts, citation and coupling overlays, sensitivity displays and
editorial paired effects. Each figure has a corresponding machine-readable table,
denominator, legend, accessible alternative and artifact hash. Publication figures
are generated from frozen outputs, not manually transcribed or illustrative scores.
Use the existing research publication contract validator, append-only run receipts,
failed runs and evidence review. Reuse protected CI for schema/contract checks and
synthetic negatives. Acquire real sources only in an explicit scope; expensive
model runs require independently approved, frozen inputs and deliberate dispatch.
The protocol proposes a follow-up paper on composition, ontology-informed coverage
and editorial utility, distinct from E1-E3 representation/semantic qualification;
combine if evidence supports one coherent manuscript rather than salami-slice.
BMC Medical Research Methodology is a candidate for the methods paper; a separate
data descriptor requires a reusable rights-cleared validated dataset, not just an
ontology proposal. Recheck venue rules and appropriate reporting guideline(s) before
submission. No manuscript, DOI, protocol registration or external approval claimed.

## Contract presentation and dissemination

GitHub is the authority. A private static Space,
https://huggingface.co/spaces/edithatogo/standardflow-contracts,
is the intended read-only mirror of authored, planned contracts and protocols.
The existing selective dataset release contract remains held. This preview must
never include source prose, vectors, item fingerprints, unapproved ontology content,
private manuscripts, reference labels or raw citation exports. Deployment must use
a minimal allowlisted package with exact checkout and file digests; no paid compute
or production inference is required. Any future data release needs its own
versioned manifest and review of rights, privacy, secrets, benchmark exposure,
licence and approval under #162. Graph and embedding data are not automatically
safe merely because derived. Separate static preview evidence from real dataset or
consumer deployment. Do not mark a created but empty Space as published.
