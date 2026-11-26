# StandardFlow project context

## Definition

- [Product](./product.md)
- [Product guidelines](./product-guidelines.md)
- [Technology stack](./tech-stack.md)

## Delivery

- [Workflow](./workflow.md)
- [Roadmap](./roadmap.md)
- [Tracks](./tracks.md)
- [Technical-preview readiness and EQUATOR engagement](../docs/preview-readiness.md)
- [Repository maturity plan](tracks/05-maximal-assurance/maturity-plan-20261125.md)
- [Frontier evaluation and test efficiency evidence](../docs/research/frontier-evaluation-20261125.md)
- [Complete plan/issue registry](../contracts/project/conductor-issues.v1.json)

## Source reconciliation

- [EQUATOR directory discovery and rights boundary](./source-reconciliation/equator-catalogue-20261123.md) — version-pinned published-source inventory, not canonical checklist content.

## Architecture

- [Track 01 source reconciliation requirements and design](tracks/01-canonical-standard-pack/source-reconciliation-design.md) — MoSCoW, Mermaid and analytical projections.

- [Platform architecture](../docs/architecture/STANDARDFLOW_ARCHITECTURE.md)
- [Canonical Standard Pack](../docs/architecture/CANONICAL_STANDARD_PACK.md)
- [Reporting guideline interoperability and assurance](../docs/architecture/REPORTING_GUIDELINE_INTEROPERABILITY.md) — proposed conformance requirements, evidence receipt, triangulation, model shortlist and publication plan.
- [Diagram and artefact engine](../docs/architecture/DIAGRAM_ENGINE.md)
- [Research ecosystem](../docs/architecture/RESEARCH_ECOSYSTEM.md)
- [Composed checklists and requirement graph](../docs/architecture/CHECKLIST_COMPOSITION.md)
- [Assurance and release engineering](../docs/architecture/ASSURANCE.md)

## Representation and publication delivery

- [Versioned profile 0.1.0](../docs/specifications/reporting-guideline-representation/0.1.0.md) and
  [approval registry](../contracts/representation/releases.json); draft, independently versioned from pack schemas.
- [Current programme receipt](tracks/01-canonical-standard-pack/representation-programme-20261124.md).
- [Publication protocol](../docs/research/publication-protocol.v0.1.0.md) and
  [machine-readable experiment/claim contract](../contracts/publication/programme.v1.json).
- [Publication submission plan](../docs/research/publication-submission-plan.v0.1.0.md)
  and [selective data dissemination policy](../docs/architecture/DATA_DISSEMINATION.md).
- [Prepared EQUATOR issue refinement](tracks/01-canonical-standard-pack/equator-issue-14-refinement-20261125.md).

## Agent capability

- [Publication evidence](../.agents/skills/publication-evidence/SKILL.md) — frozen experiments, blinded model-agent references and source-bound claims.
- [Conductor router](../.agents/skills/conductor/SKILL.md)
- [Source reconciliation retrospective](../.agents/skills/source-reconciliation-retrospective/SKILL.md) — evidence-led session and extraction review; [initial receipt](source-reconciliation/retrospective-20261124.md).
- Exact upstream plugin gitlink: `.agents/plugins/conductor`
- Expected upstream revision: `metadata.revision` in the [router](../.agents/skills/conductor/SKILL.md),
  checked against the gitlink by `scripts/audit_foundation.py`.

## Source reconciliation

- [Automated EQUATOR and legacy checklist alignment](./source-reconciliation/legacy-equator-alignment-20261123.md) — source hashes and provisional candidates, never automatic content or rights admission.

## Evidence rule

Track status, implementation completeness and evidence level are independent. A configured gate,
source file, generated artefact or merged pull request is not evidence of live operation,
methodological validity, accessibility, rights clearance or external acceptance unless an explicit
receipt records that observation.

## Follow-up analytical and publication programme

- [Composition, ontology gaps and editorial validation protocol](../docs/research/composition-graph-protocol.v0.1.0.md).
- [E4-E8 publication contract](../contracts/publication/composition-graph.v0.1.0.json) and [planned graph/vector/citation outputs](../contracts/analysis/requirement-graph.v0.1.0.json).

- [Optional human review and unattended assurance](../docs/development/optional-human-review.md).

- [Orthogonal statistical and formal assurance](../docs/research/orthogonal-assurance-20261126.md) — conformal rank oracle, symbolic applicability and alignment, syntax/normalization, leakage and differential verification; prospective qualification, not an approved protocol.
