# StandardFlow data dissemination and reuse

Status: **supplemental plan with an implemented offline gate; no Hugging Face release authorized**.
Planning date: **2026-11-25**. Baseline implementation:
`82e4a1efc136187f42b31347ada44506d2d96bfa`.

This plan supplements the immutable [representation profile 0.1.0][profile] and
[publication protocol 0.1.0][protocol]. It does not amend their bytes, approve a
specification, change source rights, or register new experimental results. The
[submission plan][submission] describes how these artifacts support publication.

## Decision

Use Hugging Face Hub for **selected, versioned, documented data releases**. Prepare a
metadata and evidence package first, then extend it as individual source rights and
scientific gates are resolved. The selected Hugging Face connector is an interface to
the Hub and its capabilities; reading documentation through it does not upload the
repository, create a dataset, or run a model. No dataset repository, remote job, model
invocation or upload was performed for this plan.

Keep the existing GitHub repository authoritative for code, profiles, contracts and
review decisions. A Hub dataset should be a reproducible distribution generated from
exact approved inputs, with a persistent citation when ready. It must preserve the
distinction between discovery, acquisition, transcription, interpretation, rights and
qualification. Hub availability is an access property, not source or scientific approval.

The selected connector's live documentation was inspected for dataset cards, privacy,
gating, Parquet, revision pinning and DOI behavior. Account-wide data unrelated to
StandardFlow is outside this release scope.

## What the current evidence can support

The inspected [receiving-main census][census] at
`15f8470a440c946eebfe0421ae0a4cb8d55a9aaa` contains 720 directory identities,
176 acquisition records, 21 item fingerprints and 2,299 review findings. Its source
revision is `d74413b15d266334067e1e5c104957601be3ba6c`. All acquisitions and item
fingerprints remain held for review; the 21 fingerprints belong to ARRIVE 2.0 and retain
a block-boundary structural discrepancy. All source rights remain unassessed and no
new canonical pack was promoted. The earlier current observation with zero fingerprints
and the historical replay with 95 fingerprints are separate snapshots, not pooled coverage.
The [programme receipt][programme] records their exact artifacts and hashes.

These observations already support operational diagnostics and conservation checks.
They do not yet constitute a rights-cleared full-text corpus, an independently validated
semantic benchmark, or evidence that automated manuscript assessment is reliable.

## Useful additional applications

The proposed applications below are product and research recommendations. Existing
infrastructure is identified explicitly; planned behavior requires its own acceptance evidence.

| Application | Existing foundation | Next useful increment and acceptance boundary |
| --- | --- | --- |
| Acquisition planning | Directory census, source candidates, provider failures, budget deferrals and deterministic retrospectives. | Prioritize unresolved source/format families and expected information gain per review effort; retain the full census denominator. Evaluate the scheduling policy separately from extraction success. |
| Edition and dependency monitoring | Exact source revisions, byte fingerprints, source anchors and pack locks. | Detect changed artifacts and prepare edition-specific requirement diffs; verify additions, deletions, scope changes and extension dependencies before declaring semantic drift. A changed hash alone identifies a change, not its meaning. |
| Requirements and coverage graphs | Stable requirement identities and explicit five-class relation semantics. | Query requirements by applicability, reporting section and evidence expectation; distinguish issuer-declared relations from inferred candidate edges. Uncertain equivalence must not generate transitive closure. |
| Retrieval with provenance | Catalogue identities, source links and held evidence records; optional reconciliation methods have separate qualification. | Retrieve exact edition/anchor candidates with visible source and rights status. Benchmark relevance and edition correctness; a high retrieval score must not approve an obligation mapping. |
| Reproducible evaluation datasets | Receipt-bound source projections, formal controls and the existing experiment lane. | Publish development fixtures and, after evaluation, permitted reference/output subsets with provenance. Keep natural-source cases, synthetic controls and model-agent references distinguishable. |
| Knowledge and metadata exchange | Existing pack/evidence schemas and consumer canaries. | Test a thin CEDAR/JSON-ScheeLD mapping and consumer import/export against explicit preservation assertions. Reuse established representations before adding another format. |
| Editorial and research planning support | Reporting items and evidence expectations in the canonical pack model. | Offer an edition-specific checklist or evidence collection plan. Manuscript evidence assessment needs a separate corpus, privacy decision and validation protocol; reporting coverage must not be presented as study quality. |
| Research on maintainability and coverage | Repeated operational snapshots with holds and failure reasons. | Study where sources become unavailable, which structures need specialist readers and how much review effort is required. Separate directory change from provider availability and algorithm change. |

MIRcat/JSON-ScheeLD already addresses machine-actionable reporting models and composition;
CEDAR already supplies reusable metadata schemas and instances. The comparison should test
which existing features preserve StandardFlow's required distinctions, rather than claim
machine-readable guidelines or generated forms as new inventions. [Batista et al.][prior-art]
and the [CEDAR model documentation][cedar] are the initial primary references.

## Distribution tiers

Two decisions are independent: **may these bytes be distributed?** and **what scientific
claim do they support?** A permitted diagnostic export can describe an unresolved source;
that permission must not change the source's original `unassessed` rights or held status.

| Tier | Material | Proposed destination and release condition |
| --- | --- | --- |
| Public evidence metadata | Reviewed stable IDs, source URLs/revisions/hashes, acquisition outcomes, hold codes and aggregate counts; original project-authored schema documentation and synthetic examples. | First Hub package after file/column allowlist, provenance, licensing, privacy and benchmark-leakage review. Review catalogue/database reuse terms as well as individual prose rights. |
| Public source-derived content | Guideline wording, tables, translations, normalized requirements, parser outputs or embeddings derived from those materials. | Separate release only after artifact/item-specific permission and attribution review. Open-access flags and the repository's general documentation licence do not resolve third-party exceptions. |
| Public development and retired evaluation materials | Explicitly designated development controls; released labels, prompts and outputs for a completed evaluation. | Separate configurations and manifests. Label the material's role, reference type and exposure history; released tests cease to be untouched future evaluation sets. |
| Restricted evaluation materials | Unreleased family assignments, adjudication packets, reference labels and evaluation prompts. | Keep in the existing authorized evaluation environment until its release decision. A public Hub repository with omitted README links is not a private test set. |
| Excluded material | Credentials, raw session/provider logs containing sensitive material, confidential reviews or correspondence, unauthorized source files and future private manuscript content. | Exclude from the public package and from Git history of the export. Do not upload merely to obtain a scan or model opinion. |

Hugging Face distinguishes [private repositories][hf-settings] from [gated datasets][hf-gated].
Gating controls access requests and defaults to automatic approval unless changed; it can
collect requester information. It is not a substitute for source permission, an embargo
decision or evaluator blinding. Public dissemination also means recipients may retain copies;
a later visibility change cannot restore an untouched benchmark.

## Proposed first Hub package

Candidate destination: **`edithatogo/standardflow-source-evidence`**, subject to a later
explicit release decision and availability check. This is a proposed name, not a created
repository. Start from one inspected source/projection snapshot; give each later snapshot
its own immutable manifest instead of silently updating earlier counts.

| Proposed path | Contents and boundary |
| --- | --- |
| `README.md` | Dataset card: purpose, scope, version, provenance, data dictionary, licence/attribution, limitations, intended uses, exclusions and citation. State prominently that discovery and held candidates are not qualified standard packs. |
| Release contract outside the staged package | Exact producer commit, upstream revisions, input receipt hashes, export version, file hashes, row counts, column permissions and distribution decision. The initial contract is `contracts/datasets/standardflow-metadata.v0.1.0.json`; a package must not contain a recursively self-hashed manifest. |
| `data/identity_metadata.parquet` | Allowlisted identity references, URLs, hashes and statuses. The implemented first profile excludes titles, categories and other free text; adding them requires a separately reviewed profile change. |
| `data/acquisition_diagnostics.parquet` | Acquisition identity, source hash when present, status, counts, rights status and hold reason; no source prose or raw provider response. |
| `data/review_findings.parquet` | Reviewed diagnostic codes and their stable evidence keys, with the observation/baseline explicitly identified. |
| `ATTRIBUTION.md` | Reviewed source citations and licence notices. Include the project citation in the README initially; do not invent a dataset DOI or infer EQUATOR endorsement. |
| Future `schemas/`, `examples/synthetic/` and `CITATION.cff` | Useful later additions, after extending and testing the closed release profile. Original examples must not conceal natural-source evaluation cases. The first validator deliberately rejects these extra files. |

The existing `acquisition_items` table is excluded from the initial proposal pending its
own source/benchmark review; fingerprints and anchors can still identify short source
passages or reveal a held-out set. Preserve the complete original receipts in their
existing evidence store. Any exported subset must explain exclusions and reconcile
its counts to its parent; it must not masquerade as the unchanged original projection.

Hugging Face [dataset cards][hf-cards] use README content and YAML metadata. Prefer
explicit table configurations such as `identity_metadata`, `acquisition_diagnostics`
and `review_findings`, with an operational `snapshot` split where supported by the
configuration, rather than labelling these observations as model training/test data.
Reuse the existing Parquet writer. The Hub's [automatic Parquet conversion][hf-parquet]
uses a separate conversion branch, so the exact uploaded manifest and data commit remain
the reproducibility reference. Check viewer output against them rather than trusting
an automatically generated preview as a second authority.

## Implemented offline release gate

The [dataset validator][validator], [planned contract][dataset-contract] and
[negative regression tests][dataset-tests] implement a bounded first increment. They
reuse the publication contract's canonical hashing and the source projection's table
checks; Parquet reading uses the repository's existing Polars dependency. They perform
no upload, model invocation, permission decision or DOI assignment. The final promotion
command additionally executes the local exact overlap scan; ordinary structural validation
does not access the restricted corpus.

```sh
python -m scripts.validate_dataset_release
python -m scripts.validate_dataset_release path/to/release.json --root private-staging \
  --require-publishable --restricted-overlap-manifest private-staging/evidence/overlap.json
```

The default command validates all `contracts/datasets/*.json`. A structurally valid
`planned` contract reports `publishable: false` and actionable blockers while returning
success for routine repository validation. The second command is the promotion gate:
it returns failure until every requirement is satisfied, including an exact restricted-source
overlap scan of the entire staged artifact inventory. An invalid `ready` contract
also fails without that flag. Unknown top-level fields and unsupported states are
errors, not approvals. The committed sample is planned, has no staged files, no licence
decision and no review or approval receipts. Its source/producer revisions are planning
references; a prepared release must identify the actual export-producing revision.

| Gate | Implemented requirement |
| --- | --- |
| Identity and destination | Exact 40-character producer/source revisions; readable, SHA-256-bound source receipts; semantic export version; explicit Hub repository, visibility, licence, attribution and `operational` benchmark role. Moving branch names and other benchmark roles fail promotion. |
| Closed package | Relative canonical paths; no traversal or symlinks; exact file inventory and hashes; at most 10 MB per bound file. JSONL and Parquet tables need positive exact row counts, unique nonempty keys and exactly the declared scalar columns. |
| Explicit permission | Every file and every exported table column needs its own `approved` export decision. `source_content_rights` is a separate field; clearing source rights alone cannot authorize export. |
| Restricted content profile | Only the validator's named metadata columns are accepted. Source-text, relation-label and item-fingerprint columns, nested payloads and unknown columns fail. String values cannot contain whitespace, and status fields use a closed operational vocabulary. README and ATTRIBUTION are the only supported Markdown files. |
| Bound reviews | Separate rights, privacy, secrets and benchmark-leakage receipts, plus a separate approval receipt, must each record a passing outcome, reviewer, timezone-bearing date and summary. Each receipt is itself hashed and binds the digest of the entire release object. |
| Mutation resistance | Changing files, column permissions, sources, destination, licence or other release fields invalidates existing review and approval bindings. Rehashing a changed data file in the manifest alone cannot preserve approval. |
| Exact restricted overlap | Promotion additionally requires an authorized private reference inventory, ordered extraction witnesses and exact artifact path/hash coverage; references and extracted fragments must remain outside the export package. Missing, malformed, mismatched or held scans block promotion without echoing excerpts. The structural validator alone cannot authorize release. |
| Claim boundary | The result always records `scientific_acceptance: false`; successful structural validation does not promote a source, pack, scientific result or model. |

Review receipts have the fields `kind`, `release_sha256`, `outcome`, `reviewer`,
`reviewed_at` and `summary`; the contract references each by relative path and SHA-256.
The `release_sha256` is the canonical digest of the complete `release` object, not the
mutable outer contract status or its receipt references. Keep the contract and review
receipts outside the staged package so review files cannot become accidental exports.

These mechanical restrictions do not establish that a reviewer exists, a permission is
valid or a scan conclusion is correct. Nor can a small validator detect every secret or
semantic leak hidden in an otherwise allowed value or documentation. Actual content
review remains necessary. A top-level licence cannot waive third-party terms, and a
hash is integrity evidence rather than anonymization. The first gate supports operational
metadata only; source-derived content, embeddings and evaluation labels require their
own reviewed release profile instead of relaxing this one silently.

After a separately authorized upload, retain a receiving receipt with the actual Hub
commit, downloaded file hashes, schema/row equality, card/configuration checks and
observed access behavior. Resolve [Hub revisions to full commit hashes][hf-revisions].
That receiving check is a later transport acceptance step; no such upload or receipt
is claimed here.

## Citation, persistence and discoverability

Retain both the exact Hub commit and the export manifest digest. An approved static
release can receive a [Hub DOI][hf-doi]; the current documentation supports assigning
a new DOI to a new revision. DOI assignment also restricts deletion, renaming and
visibility changes without support, so complete the release review first. Decide
whether the target journal also requires an archive in a recognized preservation
repository; a GitHub Actions retention window is not archival preservation.

Hugging Face can expose [Croissant metadata][hf-croissant] for supported datasets.
Inspect this generated discovery metadata and add a thin DCAT/RO-Crate mapping only
when a consumer needs it. Neither an automatic JSON-LD description nor a DOI establishes
that reporting obligations, source rights or evaluation results have been validated.

The next order is: review the initial metadata field inventory; build a concrete package;
resolve permissions and obtain the actual review receipts; pass the offline promotion
gate; then obtain the external release decision and verify receiving Hub bytes. Broader
source content and evaluation releases follow their own evidence gates.

## Primary references

Policy and product documentation checked for this 2026-11-25 planning snapshot:

- [Hugging Face dataset cards][hf-cards], [repository visibility][hf-settings],
  [gated datasets][hf-gated], [revision pinning][hf-revisions],
  [Parquet conversion][hf-parquet], [DOI][hf-doi] and [Croissant][hf-croissant].
- [Batista et al., Machine actionable metadata models, Scientific Data (2022)][prior-art].
- [CEDAR model and versioned metadata artifacts][cedar].

[profile]: ../specifications/reporting-guideline-representation/0.1.0.md
[protocol]: ../research/publication-protocol.v0.1.0.md
[submission]: ../research/publication-submission-plan.v0.1.0.md
[validator]: ../../scripts/validate_dataset_release.py
[dataset-contract]: ../../contracts/datasets/standardflow-metadata.v0.1.0.json
[dataset-tests]: ../../tests/test_dataset_release.py
[programme]: ../../conductor/tracks/01-canonical-standard-pack/representation-programme-20261124.md
[census]: https://github.com/edithatogo/standards_check/actions/runs/45407700732
[hf-cards]: https://huggingface.co/docs/hub/datasets-cards
[hf-settings]: https://huggingface.co/docs/hub/repositories-settings
[hf-gated]: https://huggingface.co/docs/hub/datasets-gated
[hf-revisions]: https://huggingface.co/docs/huggingface_hub/quick-start#download-files
[hf-parquet]: https://huggingface.co/docs/dataset-viewer/parquet
[hf-doi]: https://huggingface.co/docs/hub/doi
[hf-croissant]: https://huggingface.co/docs/dataset-viewer/croissant
[prior-art]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9525592/
[cedar]: https://metadatacenter.readthedocs.io/en/latest/yaml-spec/cedar-model/
