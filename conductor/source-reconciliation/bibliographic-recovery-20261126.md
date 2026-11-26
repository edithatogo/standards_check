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
