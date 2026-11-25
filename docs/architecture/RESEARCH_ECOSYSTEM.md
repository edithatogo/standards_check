# Research ecosystem architecture

The repositories remain separately releasable products joined by exact-pinned, consumer-driven contracts.

| Product | Owns | StandardFlow consumes or provides |
| --- | --- | --- |
| SearchRight | review planning, retrieval, screening, study linkage, living updates and PRISMA count state | supplies review/PRISMA evidence; consumes standards packs and artefact recipes |
| SourceRight | canonical CSL, provider evidence, reference reconciliation and citation integrity | supplies citation evidence; consumes evidence expectations and profiles |
| AuthenText | bounded text-pattern findings and editorial suggestions | supplies spans, rule/version IDs and uncertainty; never authorship/misconduct decisions |
| StandardFlow | standards identity, applicability, requirements, evidence states and artefact generation | validates, composes and renders without duplicating the other cores |

A later umbrella workbench may orchestrate all four through MCP and shared research-object contracts. It must remain a composition layer, not a fifth copy of the domain logic.

All integrations are network-off and write-off by default, exact revision pinned, schema versioned, fixture tested, capability bounded, reversible and covered by a degraded mode.


CiteWeft owns the neutral scholarly-document and source-span extraction surface. Its
producer identity is not yet in ecosystem-evidence v1. Use a pinned, versioned consumer
contract rather than silently widening that schema. The [composition and graph retrieval
design](CHECKLIST_COMPOSITION.md) distinguishes retrieval candidates, accepted obligation
relations, manuscript evidence, and citation verification. No cross-repository runtime
coupling is introduced by the candidate preview.
