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

## Source reconciliation

- [EQUATOR directory discovery and rights boundary](./source-reconciliation/equator-catalogue-20261123.md) — version-pinned published-source inventory, not canonical checklist content.

## Architecture

- [Platform architecture](../docs/architecture/STANDARDFLOW_ARCHITECTURE.md)
- [Canonical Standard Pack](../docs/architecture/CANONICAL_STANDARD_PACK.md)
- [Diagram and artefact engine](../docs/architecture/DIAGRAM_ENGINE.md)
- [Research ecosystem](../docs/architecture/RESEARCH_ECOSYSTEM.md)
- [Assurance and release engineering](../docs/architecture/ASSURANCE.md)

## Agent capability

- [Conductor router](../.agents/skills/conductor/SKILL.md)
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
