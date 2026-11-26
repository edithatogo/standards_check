# Track 04 — pinned consumer exchange characterization (2026-11-27)

## Scope and authority

T04.001–004; [#161](https://github.com/edithatogo/standards_check/issues/161), [Searchright #843](https://github.com/edithatogo/searchright/issues/843). This is a bounded source-level/fixture characterization, not a receiving-service canary, adapter, specification approval, pack admission, new publication result, or permission to export real data. StandardFlow owns standard identity, rights, source anchors, interpretations, recipes and derived artefacts. Searchright owns review state and PRISMA counts. No producer or consumer runtime dependency, schema, passport, licence decision, search decision or count is changed.

## Exact inputs

- [StandardFlow receiving base](https://github.com/edithatogo/standards_check/commit/ede0ac97e787c44d5288308eb2f378684d431c3e): native synthetic pack blob `21d442e22285504a78ae54797582da9c9e2d727c`, envelope schema blob `d9ffc0541226da8791582a2283d81a839822b605`.
- [Searchright source](https://github.com/edithatogo/searchright/commit/444c5199c0887c0259fe47c3d2545b5c6b877d6d): [passport](https://github.com/edithatogo/searchright/blob/444c5199c0887c0259fe47c3d2545b5c6b877d6d/integration/passports/standards-check-reporting-packs.json) blob `ffe89ec515620fcc3c094a25a2058e64e4cd62ee`, [contract suite](https://github.com/edithatogo/searchright/blob/444c5199c0887c0259fe47c3d2545b5c6b877d6d/integration/consumer-contract-suite.json) blob `81840a63bd2fd8bb1b3b302a7e3680294054796f`. Both directions are prepared, not executed. The passport still pins StandardFlow `f1e7b6c6e283865c1b7dbb34dbe33d8bf6f6c799`; its licence status is review-required and revision updates, network access and external writes are disabled.
- Retained unmodified, MIT-licensed schema and synthetic fixture snapshots in `tests/fixtures/searchright-exchange/` with original licence. Sources at the exact Searchright revision: `contracts/json-schema/standard-pack.v1.schema.json` (blob `271de4643fc480fda20c2b43e06b7d7ca78a5242`), `contracts/json-schema/prisma-flow.v1.schema.json` (blob `f875e09380ae1e3d3e339e7239ca42bf4c4c6009`), `integration/fixtures/standardflow-review-flow-evidence.json` (blob `ae30c2135f2af0a23c194b8319a097b87f67cac2`). SHA-256 checked in the tests. These are not copies of restricted reporting guideline text.

## Observations and preservation requirements

| Check | Observed | Disposition |
| --- | --- | --- |
| Native synthetic pack against consumer schema | Rejected; different schema identity and strict object shape. No native structured authority, verification, rights or requirements field in consumer schema. Consumer control accepted; adding the native rights field rejected. | Hold lossless exchange. Do not translate source identity, field-level rights or verification to an unqualified label or discard them. |
| Historical Searchright review-flow envelope | Accepted by native ecosystem envelope schema, but artifact provenance is a mutable PR head. False immutable flag, altered authority and producer rejected. | Require a real immutable receipt from the producer; do not rewrite historical provenance. |
| Envelope counts against Searchright flow schema | Nine required fields missing, two extra fields. A separate complete synthetic control passes; omission of each of its 16 required fields, a negative count and an extra aggregate field fail. | Keep the fixture held for rendering; request explicit complete count evidence and preserve unknown vs zero. No inference of reason-level counts. |
| StandardFlow recipe/pack identifiers | Historical fixture uses `prisma/2020` and `prisma-2020/new-review/databases-and-registers`; current recipe declares `org.prisma/prisma/2020` and `org.prisma/prisma-2020/new-databases-registers`. | Require explicit edition/recipe mapping and tests, not string similarity. |

The missing flat flow fields are schema_version, review_id, records_databases, records_registers, records_other, automation_removed, other_removed, full_text_exclusions and reports_included. The aggregate-only records_identified and reports_excluded are not fields of that strict flow schema. The native flow contract is also structured by template, source stream, prior review and included counts; a schema-valid outer envelope is not evidence that the render payload is complete.

## Same-version schema drift

Compared the parsed schema definitions at the consumer passport pin and current StandardFlow base:

| Schema | Old Git blob | Current Git blob | Material changes |
| --- | --- | --- | --- |
| standard-pack.v1 | 975c069f6e5074e51460c12ff858251293b53586 | 01e45d12e6bf64e0a4ddcdced5aee8c7ee3e4771 | Required verification, explicit rights fields, requirement display/verbatim/guidance fields, stricter identity and evidence expectations. |
| artifact-recipe.v1 | 7e22adbf2c2eee8f5370d36837b3345f2f984d09 | 032b243037a50a3798e70b1154fd9b89e7557e46 | Generic inputs replaced by explicit source, contract, layout, nodes, edges and reading order; output restrictions. |
| ecosystem-evidence.v1 | d9ffc0541226da8791582a2283d81a839822b605 | d9ffc0541226da8791582a2283d81a839822b605 | Unchanged bytes. |

The nominal version identifiers did not change. This demonstrates why exact content pins matter and why a reviewed compatibility/version decision must precede a consumer repin. No old version overwritten and no new version approved in this increment.

## CEDAR and MIRcat reuse (bounded inspection)

- [MIRcat MIACA project description](https://github.com/FAIRsharing/mircat/blob/3953ebe2f7d6447deaa9acb275b4c1fb82b7fd0f/miaca/schema/project_description_schema.json), blob `e09f41a6470bc0ca6b72b6a3b1dfe403977102ba`, is an observed JSON Schema draft-04 domain model with explicit required content and references. Reuse the approach to domain fields and JSON-LD/context mapping; test source-anchor, requirement identity, rights and interpretation-status preservation separately. Its particular controls array uses minLength rather than minItems; that is a candidate constraint test, not a finding about all MIRcat models.
- [CEDAR template validation schema](https://github.com/metadatacenter/cedar-model-validation-library/blob/f57f0327728164f080d25a048014dda84f0eb821/schema/template.json), blob `ecc6ab2ec4f179eedaae0a50edff87c65d5da71a`, has a distinct draft-04 template/artifact model with version, context and UI metadata. Reuse existing template mechanisms where applicable. Do not assert that they preserve the StandardFlow obligation, provenance or evidence distinctions without a real synthetic import/export and validation receipt.

These are source observations only. No CEDAR/MIRcat validator, service or full round-trip was executed; no new interchange format proposed as a substitute.

## Verification and next gate

Local isolated replay using jsonschema 4.26.0: `python -m pytest -q --import-mode=importlib tests/test_searchright_exchange.py` — three tests passed, using byte-verified consumer snapshots and exact Git blobs for the native pack/envelope. Mutation of the retained pack-schema bytes failed the digest test; restored bytes. Full repository CI and receiving-runtime validation remain pending. No real round-trip, release, scientific qualification or complete directory-wide implementation claimed.

Next: jointly agree a loss-accounted read-only mapping with Searchright #843, including explicit source/edition/version, immutable authority and provenance, item identity/order, independent verification and per-item rights/holds. Test wrong edition, missing counts, mutated values and rollback with synthetic inputs. Keep the prior consumer passport and degraded native-render mode until both sides have accepted receipts. Qualify CEDAR/MIRcat with actual native template tools in a separate bounded fixture exercise. Keep T04.001–004 open until their complete acceptance evidence exists. Do not change the representation draft or extend schema authority merely to make the tests pass.
