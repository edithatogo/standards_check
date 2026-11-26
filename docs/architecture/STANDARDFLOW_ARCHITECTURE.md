# StandardFlow architecture

## Planes

1. **Standards knowledge:** identities, editions, extensions, requirements, source anchors, rights, translations and semantic relationships.
2. **Canonical packs:** authoritative source data, schemas, normalized canonical JSON, lockfiles, signatures and generated projections.
3. **Artefacts:** checklists, forms, diagrams, evidence reports, documents and submission bundles.
4. **Applicability and evidence:** project classification, deterministic rules, evidence expectations, anchors, audit states, human adjudication and version migration.
5. **Interfaces:** one Rust application facade exposed through CLI, static API, HTTP/OpenAPI, MCP, WASI/WASM, PWA and thin adapters.
6. **Federation and assurance:** registries, ecosystem contracts, preservation, operations, security, external validation and governance.

## Canonical flow

```text
authoritative source
  → immutable source evidence + rights + anchors
  → reviewed Standard Pack source
  → deterministic canonical JSON + content lock
  → checklist / diagram / document / API / MCP projections
  → evidence-bearing assessment and research-object export
```

Generated representations never write back to canonical authority. Graph databases and search indexes are disposable projections. Models may help classify projects and locate candidate evidence, but deterministic code resolves standards, validates arithmetic and changes audit state.

## Specialist inference boundary

Source-native parsers and exact provenance precede optional document-layout/vision
models; extractive encoders suggest anchored tags; retrieval and reranking nominate
candidates; directional NLI and decision models suggest evidence, never approval.
Grammar masks are an optional syntax layer. The full schema, Rust semantic validator,
content lock, approved applicability rules and deterministic arithmetic remain
authoritative. Bounded symbolic solvers may supply counterexamples for reviewed
rules; an unknown or timed-out proof remains held. See the prospective
[specialist pipeline evaluation](../research/specialist-pipeline-protocol.v0.1.0.md)
for stage-specific comparators, experiments and scientific gates.
