# Bibliographic recovery and Searchright consumer — 26 November 2026

Existing #111/#95/#158, Track 01 T01.025/031/052/053/064 and Track 05
T05.049/063. This is the coordinator's read-only bibliographic recovery and
consumer-contract increment; Layout/#188 retains source-byte acquisition,
edition/rights/structure and blinded reference locking. Offline and Orthogonal
retain their evidence/decision responsibilities. No new source or publication
registry, no canonical merge, no new provider client or production dependency.

## Observed complete-census diagnostic

Actual original main census archive
[15031534787](https://github.com/edithatogo/standards_check/actions/runs/45635380131/artifacts/15031534787)
verified SHA-256 21046589502f064d54800c9f495d72d18b97184a1db376f06da773b84bde3f01,
source revision e34dd7d8559a5df0fe4b7185c093978e4b2d6cbe.
Join catalogue/source-link/metadata receipts by exact source revision, ID
and source blob. Keep all 720 identities, no guideline deduplication.
Historical source observations remain historical. Existing metadata 644
identities with at least one work identifier: DOI 638, PMID 639, PMCID
273, OpenAlex 6 (overlapping denominators). Two conflicting metadata
identities held. The 76 previously missing identifiers split into
49 literal link identifier candidates, 17 issuer landing leads, four
direct asset leads and six title discovery candidates; 37/56 incomplete
lookups also expose literal link IDs. Two RAMESES catalogue identities
share a candidate PMID 25642521: keep both guideline IDs, separate
bibliographic work candidate from scope/edition/obligations. No automatic
primary-publication selection or fuzzy destructive deduplication.
909 distinct queued metadata tasks before any live lookup, prioritizing
gap candidates; DOI/PMID/PMCID and titles round-robin, no ranking by
citation counts. Keep prior attempts by hash-bound checkpoint, do not
repeat an unchanged failure. Link hints parsed for known exact URL shapes,
query/credential material stripped from stored locators, not dereferenced.

Actual local 9 tests passed (six recovery tests and three bridge tests,
initial bridge RED missing module then GREEN). Source/test blobs exactly
match local files. Local offline complete output SHA-256
09d9e9df1cd03a8fc07965e1d7024d99005a546219d362b4ef6077f3969e1f31.
No live provider results, document downloads or additional qualified
identities in that execution. Fixed public-metadata canary: eight tasks
(max 16 requests, initial selection 11), existing fixed-host bounded
fetch adapter; one-second spacing, three consecutive errors per provider
circuit breaker, no paid queries, no credentials or raw response storage.
Current first-party Crossref REST documentation and OpenAlex authentication
documentation (observed 26 Nov 2026) support bounded public metadata
queries; exact singleton and three-result title discovery only. Record
errors/deferred tasks and actual response hashes; no source rights or
primary-edition inference. Title search is discovery only and ambiguous
candidates are retained; issuer-linked provenance/edition still required.
No repeat full-text failure sweep. Resume via explicitly hash-pinned
prior ZIP and bounded workflow dispatch, not automatic every push.

## Consume Searchright rather than duplicate it

Pinned Searchright main
[444c5199](https://github.com/edithatogo/searchright/commit/444c5199c0887c0259fe47c3d2545b5c6b877d6d).
Read source-policy, discovery-method and bibliographic record contract
by exact Git blobs. Also read **unmerged advisory** PR #844 at
703f9ede74d78ac3aa58ee322c48471875f2a80e for its 12 sources and 10
directory entries; do not call these accepted or executable. The consumer
crosswalk retains all 44 declared records (6 policy endpoints + 16
supplementary methods + 12 advisory source entries + 10 advisory
directories, overlaps retained). Pins in searchright_bridge.py.
Source and platform records remain separate; review dates, policies,
access, and execution-authority false retained; no new catalogue.

- Publication identity: existing Crossref, Europe PMC, OpenAlex and
  PubMed/NCBI exact ID routes; PMC ID converter and official JATS/issuer
  asset paths stay in Layout. PubMed ESearch/ESummary/EFetch are distinct
  capabilities. Title discovery is candidate-only.
- Citation/impact: Crossref reference DOIs and cited-by count, OpenAlex
  referenced work IDs and cited-by count, Europe PMC metadata counts.
  Preserve provider/date/coverage, zero vs missing, reference truncation,
  correction/version/retraction relations and provider disagreement.
  OpenCitations is fixture-only on pinned Searchright; use its discovery
  graph only after verified permitted execution. Manual backward references
  and forward citations are bounded leads, not equivalence.
- Author/institution: ORCID assertions from work metadata with checksum
  validation; no person identity from name or work ID, no invented ORCID.
  Independent author verification and ROR affiliations only when warranted.
- Other advisory source/platforms: MEDLINE/PubMed/Ovid, Embase, CINAHL,
  PsycInfo, CENTRAL/CDSR, Scopus, Web of Science; licensed access/export
  stays explicitly authorized and distinct from database/platform IDs.
  No automatic licensed queries. Compare incremental coverage on the
  same held worklist when legitimately available.
- Repository and grey-literature discovery: OSF, Zenodo, Figshare,
  Dataverse, institutional repositories, conference/thesis/policy/issuer
  websites, documented contact/handsearch. Trial registry links via
  ClinicalTrials.gov, WHO ICTRP and ANZCTR may identify development
  studies; not guideline publication identifiers. Use only relevant,
  permission-qualified routes; no indiscriminate querying.
- RefHunter, DBIS, FAIRsharing, OpenDOAR, re3data, OpenAIRE PROVIDE,
  WHO ICTRP network, Grey Matters, ISSN ROAD and UQ source-selection guide:
  advisory discovery of appropriate resources, not article providers.
  Reference Searchright #834–#845/#847/#848; no bulk directory mirror.
  #813 proposes Unpaywall, Semantic Scholar, CORE, bioRxiv/medRxiv,
  DOAJ: assess exact implementation/permissions and incremental yield,
  not supported main providers inferred from issue claims. Consider
  DataCite for supplementary data/preprints and ROR for institutions
  through existing Searchright/Sourceright ownership where justified.

Searchright Rust facade/CLI and dedup are unpublished, Python SDK is
contract-only; exact pinned main Security 45178867913 and Privacy
45160349186 failed, #831 remains open. No new Rust dependency, no execution
of unqualified Searchright code. Existing public metadata adapters reused.
Project only exact DOI-confirmed provider work observations with actual
publication title, per-provider receipt and original catalogue IDs to
Searchright bibliographic-record.v1. Missing data remains missing, no
catalogue title as publication metadata, abstract not persisted. Validate
with exact upstream JSON schema. Distinct provider observations preserved.
This is candidate work-level interchange, not guideline/edition truth.
Once upstream security/privacy and exact consumer evidence qualify,
exercise pinned source checkout and actual `searchright deduplicate`
CLI on schema-valid metadata (no live or destructive merge); compare
cluster conflicts and retained records against identifier-only baseline.
Prefer neutral evidence-search-contracts/core or admitted CLI boundary
over a vendored runtime. Use Sourceright for citation integrity if needed.
Cross-reference Searchright #835/#843 (reciprocal consumer), #844 and
#831; no competing upstream implementation.

## Interpret bibliometrics and recursive improvement

Produce publication-to-guideline-to-edition/manifestation evidence links,
not collapsed identities. Keep co-publications, revisions, corrections,
withdrawals, supplements, translations, extensions and shared authorship
as typed candidate relations. Count citations by exact work/provider/time;
do not sum duplicates, infer zero when coverage unknown or treat citation
count as quality/rights. Once edges are sufficiently observed, compare
citation, co-citation, bibliographic coupling, author collaboration and
guideline family/ontology networks; age/field/source coverage and
co-publication dedup sensitivity are required. Discover underlinked
methods and revisions, prioritize source-gap work by actual marginal
yield, not popularity. Preserve corpus-wide missingness and family lock.
No impact-adjusted admission or evidence decisions.

Extend the existing source-reconciliation-retrospective skill into a
bounded recursive improvement cycle. One coordinator, existing source/
metadata/semantic/verification owners; independent blinded adjudication
and adversarial review roles preserved. Every cycle: inspect live main/PRs,
review exact receipt and compare same denominator, identify dominant
bottleneck, predeclare one minimal falsifiable change and harm/cost limits,
run failing then passing tests, opt-in matched-budget benchmark, independently
review and integrate through protection, version negative results and stop
or resume from actual evidence. Default no model, no external writes,
no destructive edits or automatic scientific promotion. New methods or
provider access need their own owner and gates. Stop on unchanged provider
failure, missing qualified references, no incremental benefit or worsening
harm; do not create agent loops that recursively tune on held-out labels.
Workflow executes deterministic projection/canary/checkpoint, not an
autonomous model agent or scheduler. Reuse existing #188 source worklist,
#183 locked join, and #184/#190 evidence policy. Full independent
family/reference locking remains a hold.

Rollback: remove this opt-in research lane/skill append, leaving original
catalogue, Searchright, source admissions and existing production unchanged.


## Persistent missing checklist audit and Searchright-first migration

Receiving main b48e7adafea41e09f4aa07d9db6f7e9117618c10: #185 merged normally; exact head
449689ac43696587886055e9e1ae5a9891d96a1a and receiving tree
bdd6fb7ad21086532c9b8a1ca0136a7f628a833f match. Prior #191 head passed
all seven required contexts, CodeQL and patch/component checks. Reconcile
receiving main without overlapping changed paths; fresh checks required.

### Actual repeated observations and gap reasons

Verified earlier survey artifact 14901554121 ZIP SHA-256
12a009fdcdfd8174daacfb606cb97a5c2648940c80df733a3b55a24ff6a14460
(source revision d74413b15d266334067e1e5c104957601be3ba6c) versus existing
15031534787, source revision e34dd7d8559a5df0fe4b7185c093978e4b2d6cbe.
Same 720 catalogue IDs, 708 unchanged source blobs. 122 unchanged
unresolved rows: 75 missing identifier, 47 incomplete lookup (42 earlier
incomplete, 3 unresolved, 2 conflicting). 210 earlier incomplete become
metadata-only and 74 OA XML candidate among unchanged rows. Retain changed
source rows separately. Current 132 gaps (76 missing, 56 incomplete;
two conflict flags within these). Persistent routes: 76 literal link IDs,
17 issuer landing pages, 14 existing IDs needing reconciliation, 7 direct
assets, 6 title discovery, 2 conflicting identities. No inference that a
checklist is absent from an identifier failure.

Actual [metadata canary 45817003412/artifact 15115248937](https://github.com/edithatogo/standards_check/actions/runs/45817003412/artifacts/15115248937)
verified ZIP SHA-256
c409624a581a6d637e4ef19cca41ec5c82c6877ee1054b9750289158771627e1,
tested merge e01e21e3cefcd2e79f22b63d60a36f9b0eb67288. Eight tasks,
eleven requests: six exact DOI metadata observations across PRISMA-IPD,
CONSORT factorial and CONSORT-C; one exact PMID candidate ORION PMID
17376385, DOI 10.1016/s1473-3099(07)70082-8; two Europe PMC timeouts
(STROBE-NUT PMCID and second ORION PMID); two title searches with no
exact normalized title. Six Searchright wire-schema work projections.
Crossref/OpenAlex citation counts 1989/2357, 91/100, 2/2 respectively,
provider/date-specific, not additive impact or evidence qualification.
58 OpenAlex ORCID assertions across the three works, not authenticated
person identities. No new qualified checklist or independent label.

Bounded 26 November follow-up on six title-only gaps (public landing and
metadata observations, not document downloads):

| Catalogue title/slug | Lead | Next |
| --- | --- | --- |
| Participatory action research | [Publisher DOI 10.1177/0011000010376416](https://journals.sagepub.com/doi/10.1177/0011000010376416); extraneous title suffix 1Ψ7; prior first Crossref candidate | Exact DOI provenance and review discrepancy |
| ecohealth | [EQUATOR](https://www.equator-network.org/reporting-guidelines/ecohealth/) lists Lancet Planetary Health in press, updated 30 Sep 2026 | Observe publication release; no repeat unchanged title sweep |
| Behavioural clinical psychology case reports | [Original journal 2008, 8:765–777](https://aepc.es/ijchp/articulos.php?coid=English&id=304), PDF lead | Layout exact bytes/rights |
| Colorectal tumour case series | [OpenAlex W2055994389](https://openalex.org/W2055994389), DOI 10.1007/s101510050023; [EQUATOR](https://equator-network.org/reporting-guidelines/guidelines-for-reporting-case-series-of-tumours-of-the-colon-and-rectum/) matches 1999, 3:93–97 | Exact publisher reconciliation |
| RATS | [EQUATOR](https://www.equator-network.org/reporting-guidelines/qualitative-research-review-guidelines-rats/) cites Clark 2003 book chapter | Book/chapter and issuer route |
| HuGENet handbook | [EQUATOR](https://equator-network.org/reporting-guidelines/the-hugenet-huge-review-handbook-version-1-0-guidelines-for-systematic-review-and-meta-analysis-of-gene-disease-association-studies/) cites CDC 2006 handbook | Institutional/archive and edition-specific source |

Separate source-byte gap: bulk checkpoint 15107508921 contains 205
worklist IDs, 200 deferred, four held after transport/OAI failures, one
observed XML inventory unreconciled. Six priority editions held across
both historical surveys, not all absent. CONSORT/SPIRIT 95/95 ordered
printed IDs in artifact 15113361829, marker-level agreement distinguished
from exact row agreement; source/structure/issuer/rights holds remain.
Priority-structure artifact 15116098103 verified SHA-256
e27aad9b976d663c765926fa38cddc665ef70bcbbb198cfac7aa78d28a515f82:
TRIPOD+AI 52/52 expected printed IDs DOCX, STROBE 11/22 main IDs DOCX,
both source-observation-only, research-use approval field true, public
redistribution and scientific qualification false. Layout owns the
source/rights/anchor reconciliation; no inference of 720 independent
guideline families, missing checklists, or downstream failures.

### Default Searchright strategy mechanism, no implicit fallback

Use actual Searchright strategy, query AST and compiled-strategy schemas
at pinned main 444c5199, exact Git blob pins in searchright_recovery.py.
No independent query compiler or provider runtime. Generate literal title
and identifier terms, preserve exact-ID postfilter requirement and
catalogue IDs, route assets/landing/conflict to Layout, deduplicate
provider+kind+value, exclude the 11 prior observed provider-query attempts
including failures. Eight-strategy next batch, max three records/one
page/15s/zero retries per strategy when qualified host available.
Default workflow uses native strategy generation, not legacy live calls.
Legacy remains explicit comparator only (run-bibliographic-legacy-comparator
label or legacy_comparator=true); resume via hash-verified receipt.

Actual local replay: 720 rows retained, all 132 current gap IDs accounted
for, 106 IDs with 886 distinct strategies (101 Crossref, 327 OpenAlex,
230 PubMed, 228 Europe PMC), 26 source/identity routes (17 landing,
7 asset, 2 conflict). Of 122 persistent IDs, 96 have native strategies
and 26 are non-search. All 886 validated against byte-exact upstream
schemas reconstructed from connector response and Git blob checks.
Offline schema registry, no remote ref retrieval. Receipt SHA-256
persistent-gaps.json 8b25c87c1a02c153760f7373c1b27af8799e6054364ebdb5e380dd7926550308,
searchright-strategies.json e71f45880e730faebbec94f3ee170a080b70cc373181179ba72c29c8e706e1ed.
RED missing module then GREEN 15 focused tests (nine prior, six new).
Exact source/test blobs 003ebae80898b755400a3db1494a0d6242c82114,
f877d94a0de5937434ffec567de6508f09e4e98f. Hosted default workflow
explicit run-searchright-recovery label; retains actual historical canary
metadata, no new provider calls or inferred qualification.

Actual compiler adapter calls genuine qualified Searchright CLI
`searchright compile <strategy.json> --dialect ...` with exact binary
digest and caller-verified qualification receipt. Temporary directory,
no inherited credentials, bounded time, exact result schema and
strategy/dialect binding, retains translation warnings/loss codes,
review_required and fidelity. At most eight; no live authorization.
Synthetic mocked compiler tests are not executed upstream compiler.
Local cargo/rustc absent, GitHub raw DNS failed; no admitted binary.
Pinned upstream Security/Privacy failed; inspected
SearchrightEngine::execute_search explicitly denies live (H-002,
fixture preview only; CLI apply requires trusted host). Do not bypass
this facade through low-level provider calls. Actual Searchright
compilation and live search remain unqualified; native strategy
preparation and compiler interface implemented, not a claim of runtime
cutover. Coordinate exact compiler and approved read-only live host
receipt via existing Searchright #835/#843/#831 and downstream matched
budget canary. No fake execution or automatic fallback.

Recursive improvement: use persistent source and prior-provider receipts,
route new evidence rather than unchanged failure, measure unique
identity recovery, transport/no-match/conflict, rights, structure,
resource and review budgets separately. No repeated blind acquisition,
automatic repin, semantic merge, new registry, source rights or
independent reference promotion. Preserve #188 owner, #183 locked
stage join and #95/#111/#158/T01.052/T05.049. Rollback removes this
opt-in consumer increment; historical evidence and canonical packs unchanged.


### Hosted schema retrieval failure and targeted repair

First native planning workflow 45821045254 on head 9e6dc00b stopped in
Prepare Searchright-native strategies by default with ValueError: Searchright
blob mismatch; hosted focused tests had passed but no native strategy receipt
was generated. Failure artifact 15117079100 SHA-256 d23c7dea762ec6fc0fb321e09b0c808e6fa779eee95b6d8a05cee588c4aa4b62 retained. Exact offending raw schema was not identified by the generic error; do not infer upstream schema drift. Change only three new schema acquisitions to Git blob API at exact pinned object IDs, decode base64 strictly, validate returned object ID and recomputed Git blob hash and retain per-schema SHA-256. No relaxation, no new pin or source/provider query; code and local 15 passing tests unchanged. Fresh hosted replay and protected checks required.


### Verified native planning and measured next recursive increment

Receiving #185 merge b48e7adafea41e09f4aa07d9db6f7e9117618c10 tree
bdd6fb7ad21086532c9b8a1ca0136a7f628a833f equals tested head 449689ac.
Receiving main eb95f610ff78b620cb1c687fed544ed2b5475ff1 incorporates catalogue enrichment/vector selection;
preserve those append-only Track 01 additions without duplicating their work.

Hosted [45821391956](https://github.com/edithatogo/standards_check/actions/runs/45821391956)
succeeded on exact prior head f3e71a9ade2e3ec159fa244de301c29efe0c2ba6. Independently downloaded
artifact 15117882759, ZIP SHA-256
0bf1a7a434ed21549998c9e04c55f3a72b37fd82797bb0db866dcf98612c2cec.
Both persistent-gaps.json and searchright-strategies.json match the
previous local member hashes byte for byte. All 886 strategies and
44 crosswalk rows retained; 6 historical provider-work records exported,
11 previous attempts excluded; zero native compilations, live
executions, or independent qualifications. All seven required checks,
CodeQL and patch/component coverage passed on that prior head;
offline security separately queued. Fresh checks required after reconciliation.

Recheck the original survey 15031534787 against the exact 122 persistent IDs:
75 missing identifiers; among the 47 incomplete lookups, 43 explicitly
provider_request_failed and four deferred_provider_circuit_breaker
(CARE-DN, PRISMA network meta-analysis, PRISMA-ScR, REFINE).
These are recorded transport/defer outcomes, not proven non-existence.
Examples of held identity/source paths: RIGHTCARE-PR and SPIRIT identity
conflicts; ICMJE disclosure form, Be PRECISE, PhyCARE, SUCCEED and WIDER
direct assets; SAGER and STROBE abstracts issuer landing; ecohealth in
press observation, RATS chapter and HuGENet handbook title routes.
Keep the distinction between publisher availability, identity match,
full checklist bytes/rights/structure and reference eligibility.

Bounded improvement: the former next batch spent three of eight slots
on the same shared RAMESES PMID. Use greedy marginal distinct persistent-ID
coverage, then total uncovered catalogue IDs, then prefer unused
query tokens, exact identifier over title, provider balance, stable ID.
Prior successful metadata leads (four catalogue IDs, not qualified
editions) are lower priority, not removed. Hard cap two per provider,
eight total. No added strategy, query, request, provider, credential,
rights inference or library execution. Preserve original batch as
comparator and emit both summary and ID lists in batch_comparison.

Executed against exact hosted 886-strategy member e71f45880e730faebbec94f3ee170a080b70cc373181179ba72c29c8e706e1ed:
baseline eight slots / six distinct query tokens / seven persistent IDs;
challenger eight slots / eight distinct query tokens / nine persistent
IDs, same two slots per each of four providers. RAMESES pair remains
separate catalogue identities; CHART and STROBE-nut gain planned slots.
This is +2 planned ID coverage, not acquisition or recall gain.
Local RED missing module then GREEN three focused tests, including
ordering determinism, caps, invalid authorization, and prior observation
priority. Exact blobs recovery_batch.py c20fe28fe60497f8208c82a5eb5c14de7d362dd6,
test_recovery_batch.py 0ab46aff10b5b6bd41fa47b3670c45549bfe8d06.
Local diagnostic SHA-256 cf210501f94eb94ae30e9d89414df1658f8fb74f2d02726b3ddf1a748cb3477d.
The new workflow imports the tested selector and executes its regression
tests; full checkout validation still required. Do not tune on eventual
search successes until independently separated receipts permit comparison.

Searchright upstream main remains 444c5199, #831 open; unmaintained
dependency advisory and failed Security/Privacy checks, H-002 live host
authority still held. The default strategy mechanism is Searchright;
not a qualified native search runtime. Preserve actual compiler
qualification, source policy and trusted host requirements; request
existing upstream owner supply admitted binary and permitted execution
receipt. No implicit legacy provider calls. Next: qualify native
compilation then a bounded live matched-budget batch once authorized;
compare unique exact identity leads, errors, deferrals, rights/edition
holds and actual resources, not just number of planned queries.
No new branch owner, registry, canonical admission or scientific
reference lock. Layout continues #188.


### Protected integration and role-aware recovery increment (27 November)

#191 normally merged at [ede0ac97](https://github.com/edithatogo/standards_check/commit/ede0ac97e787c44d5288308eb2f378684d431c3e).
All seven required contexts, CodeQL and component/patch coverage passed
on c3480879; receiving tree 0fe04b9a93232359a061318cd112ad3e19f2f693
equals tested head tree. Dedicated offline security remains held (#30).
No protection change. Receiving main for this successor: ede0ac97e787c44d5288308eb2f378684d431c3e.

The verified parent planning artifact 15125576531, ZIP SHA-256
2a0f6fb0605e1995b38ec3755dc9dd0e8e161e6c78140a3e525ac15c170c8e0b
fixes the eight selected strategies and nine covered catalogue IDs.
Independently checked the exact eight query tokens in public bibliographic
metadata (PubMed connector for six PMIDs returned five, public NLM page
then resolved the remaining shared PMID; publisher/PubMed pages for two
DOIs). This is a **manual metadata observation**, not native Searchright
provider execution, a matched-request/provider experiment or qualified
source recovery. No actual response byte count or provider seconds
available for this manual check; record unknown, not zero. No document
bytes retained.

| Catalogue identity | Exact planned token | Observed DOI / role | Evidence |
| --- | --- | --- | --- |
| RAMESES meta-narrative and realist | PMID 25642521 | 10.3310/hsdr02300, related development report (not either primary standard) | [NLM](https://pubmed.ncbi.nlm.nih.gov/25642521/) |
| IMPRINT | PMID 25225072 | 10.1016/j.fertnstert.2014.08.002, primary candidate | [NLM](https://pubmed.ncbi.nlm.nih.gov/25225072/) |
| GRIPS | PMID 21407265 | 10.1038/ejhg.2011.25, PMC3172920, primary candidate | [NLM](https://pubmed.ncbi.nlm.nih.gov/21407265/) |
| Music-based interventions | DOI 10.3389/fpsyg.2025.1551920 | exact DOI, PMID 40528854, PMC12171218, primary candidate | [Publisher](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1551920/full) |
| CHEERS 2022 | PMID 35012427 | 10.1080/13696998.2021.2014721, co-publication candidate | [NLM](https://pubmed.ncbi.nlm.nih.gov/35012427/) |
| CHART | PMID 40753040 | 10.1016/j.artmed.2025.103222, co-publication candidate | [NLM](https://pubmed.ncbi.nlm.nih.gov/40753040/) |
| STROBE-nut | PMID 27587981 | 10.1111/nbu.12217, PMC4988500, co-publication candidate | [NLM](https://pubmed.ncbi.nlm.nih.gov/27587981/) |
| Big Q qualitative values-based guidelines | DOI 10.1080/14780887.2024.2382244 | exact DOI, primary candidate, 2024 online/2025 issue | [Publisher](https://www.tandfonline.com/doi/full/10.1080/14780887.2024.2382244) |

Eight exact publication records observed, seven primary/co-publication
candidates directly, one related report spanning two catalogue IDs.
Targeted follow-up resolves two distinct *primary article leads*:
RAMESES realist DOI 10.1186/1741-7015-11-21, PMID 23360677,
PMC3558331 ([NLM](https://pubmed.ncbi.nlm.nih.gov/23360677/));
meta-narrative DOI 10.1186/1741-7015-11-20, PMID 23360661, PMC3558334
([NLM](https://pubmed.ncbi.nlm.nih.gov/23360661/)).
Never merge these obligations or use the development report as the
primary source; preserve co-publication and shared development links,
keep one conservative dependence component for evaluation. Nine
catalogue IDs now have candidate primary/co-publication leads after
manual follow-up, but zero newly qualified sources/independent positives.
Do not subtract nine from the 122 persistent identity-gap denominator
until the responsible owner reconciles identities against exact editions.

Additional source routes, observed publicly and assigned to Layout:
- [CHART interactive checklist](https://equator-network.org/reporting-guidelines/chart/chart-checklist.html)
  identifies BMJ Medicine DOI 10.1136/bmjmed-2025-001632; separate full and
  abstract forms. [EQUATOR](https://equator-network.org/reporting-guidelines/chart/index.html)
  records simultaneous publication. Reconcile HTML/Word/PDF and edition.
- [CHEERS source page](https://equator-network.org/reporting-guidelines/cheers/index.html)
  identifies downloadable PDF/interactive checklist and multiple journals;
  BMJ DOI 10.1136/bmj-2021-067975. Distinguish the checklist's rights
  statement from journal-copy rights and record exact file bytes.
- [STROBE-nut](https://equator-network.org/reporting-guidelines/strobe-nut/index.html)
  lists PLoS Med PMID 27270749 and Nutrition Bulletin PMID 27587981;
  fillable checklist in explanation/elaboration supplement.
- Publisher pages for music interventions (Table 1) and Big Q qualitative
  (Table 1 with CSV option) give structured manifestation candidates.
- [ICMJE](https://www.icmje.org/news-and-editorials/updated_disclosure_form_2021.html)
  replaced the older form in 2021; do not silently substitute edition.
- [WIDER derived checklist](https://link.springer.com/article/10.1186/1748-5908-8-52)
  has staged DOCX supplements; distinct from original recommendations.
- [Be PRECISE](https://www.equator-network.org/reporting-guidelines/reporting-guidelines-for-precision-medicine-research-of-clinical-relevance-the-beprecise-checklist/),
  [SUCCEED](https://equator-network.org/reporting-guidelines/succeed/index.html)
  and [SOS-Prehab](https://equator-network.org/reporting-guidelines/sos-prehab/index.html)
  list downloadable checklist assets.
- [RATS](https://www.equator-network.org/reporting-guidelines/qualitative-research-review-guidelines-rats/)
  is a 2003 BMJ Books chapter (Clark, pp 219-235): seek exact library/publisher version.
- [HuGENet](https://www.researchgate.net/publication/254247831_The_HuGENet_HuGE_review_handbook_version_10)
  is an author-deposit lead for 2006 handbook v1.0, corroborated by
  EQUATOR; independently verify archival/institutional provenance and rights.
All twelve supplementary lead records and exact batch/source-blob IDs
retained in local manual-identity-check.json SHA-256
a2cde67ff47e90febed6a6e836e7f03e9e7f48c2dc66fab7e1ef818bccf6b527.
No downloaded checklist, reuse/rights determination, canonical source
repin or independent reference. Layout consumes this handoff; do not
run duplicate document intake. Next search cycle preserve related-report
roles and favor new qualified primary identity evidence, not repeat the
shared related PMID as if it were either primary checklist.

Historical actual yield/cost: executable recovery_yield.py joins exact
census 15031534787 and legacy canary 15115248937 at source revision and
source-blob level, verifies exact identifier bindings, counts provider
responses and deduplicates work IDs, retains source route, query type,
observed age, overlapping study types and provisional family proxy.
11 requests, 7 exact responses, 4 distinct work IDs and 4 catalogue IDs;
30.465917144 seconds recorded per-request processing, 210382 response
bytes for 9/11 responses (2 absent, not zero). No dollar/full-runtime
or document-acquisition cost inferred.

| Provider | Requests | Exact | Unique work IDs | Observed seconds |
| --- | ---: | ---: | ---: | ---: |
| Crossref | 5 | 3 | 3 | 0.407233488 |
| OpenAlex | 3 | 3 | 3 | 0.386727442 |
| Europe PMC | 3 | 1 | 1 | 29.671956214 |
| Deduplicated total | 11 | 7 | 4 | 30.465917144 |

Link-ID route 9 requests/7 exact/30.1761 s; title route 2/0/0.2899 s.
Observed publication age 0-4 years: 4/4 exact, 10+ years 2/2,
unknown 1/5; ascertainment and route confounding, not age effect.
Clinical trial labels 5/7, experimental 3/4, observational 1/4,
systematic review 2/2, other 1/2, unspecified 0/1; overlapping strata,
not independent family counts. Family-proxy summaries retained, no
independent family or provider superiority claim. Generated historical-yield.json
SHA-256 14f04dc2aef9deca2af7b02d95e355222985cc74269b145d80ed1d76c7c4b867.
Re-run using the existing fixed input ZIPs; default hosted planning
now also retains this receipt.

### Native compiler candidate feasibility; H-002 remains a live hold

Upstream exact main 444c5199 tree 0929bd9b17b81d98f8b59cca2d41367f8f95aafc
remains unchanged. SearchrightEngine::compile_strategy invokes the real
QueryCompiler; CLI compile calls that facade. Engine execute_search rejects
network capability other than Disabled or policy.live_enabled, and CLI apply
requires trusted host verification. Actual upstream #831 remains open.
Do not declare the binary admitted or invoke any lower-level live path.

An explicit label run-searchright-compiler-canary extends the existing
read-only hosted recovery workflow. Fetch exact public upstream source/tree
and locked dependencies in disposable runner; then compile actual
searchright-cli with the exact Rust 1.97.1 toolchain, locked offline Cargo,
unprivileged separate network namespace and cleared environment. No
provider credentials, no runtime network, no live calls, no production
dependency, no release. Probe all eight exact existing strategies using
the native CLI, validate actual upstream compiled schema, retain exact
strategy binding, binary digest, warnings/loss/fidelity, time, RSS and
failures. Test upstream fixture_execution_previews_then_commits_without_network
offline, including its explicit live-denial assertion. Fixture local
writes are temporary test state only; no production apply. If toolchain,
dependency fetch, isolation, build, compile or test fails, retain actual
stage/exit and logs; never fall back to host networking. No successful
compile or authorized host asserted before actual receipt. An isolated
compiler feasibility result cannot clear upstream supply-chain/privacy
gates or H-002, and no real native search can run until its owner supplies
the qualified host. Preserve actual old comparator and manual leads as
separate evidence, not implicit execution fallback.

Local RED missing modules, GREEN four focused tests passed (historical
dedup/resource counts and ID mismatch; compiler binding, warnings,
authority false, bounded held batch). Exact code/test blobs retained.
Full repository regression and native compiled/denial receipts pending.
Reuse existing #158/#111/#95, T01.025/031/052/053/064 and T05.049/063,
no new canonical or publication registry. #188 latest verified artifact
15125352116 SHA-256 ebc1c2ab584bc460f5d4d8fbb6ba0daad3548de74767e2d2a64bb7f9ef54fa42
still source_observation_only for TRIPOD+AI/STROBE: 52 ordered TRIPOD IDs,
46 exact rows; STROBE no independently comparable compound rows.
Research-use approval does not establish public redistribution or
reference independence. Layout retains exact source/rights/anchor
and blinded lock; #183 join ready but no qualified ledger to execute.
No production or scientific promotion. Rollback isolated successor
increment; original #191 plan and evidence remain.
