# Product: StandardFlow

StandardFlow is a machine-readable reporting-standard representation, reconciliation and assurance
system. Its implementation-neutral technical profile and experimental reference implementation are
separately versioned. It processes the whole published reporting-guideline directory as a corpus,
while admitting only rights- and evidence-qualified Canonical Standard Packs. It resolves which requirements
apply to a research project, captures evidence against those requirements, and deterministically
generates checklists, forms, diagrams and submission artefacts.

The current `standards_check` repository is the primary adoption repository. The existing
`standardflow` repository is a migration source for renderer code, schemas, fixtures and history; it
does not remain a competing source of standards authority after cutover.

## Product boundaries

StandardFlow owns standards identity, versions, extensions, applicability, normalized requirements,
evidence expectations, standards-derived audit state and artefact recipes. SearchRight owns search
and review execution state, including PRISMA counts. SourceRight owns canonical CSL and citation
verification. AuthenText owns bounded textual-pattern findings. Integrations exchange versioned
evidence contracts and retain human authority for consequential decisions.

## Users

Researchers, research offices, methodologists, librarians, editors, publishers, standards authors,
software developers and governed AI agents.

## Non-goals

StandardFlow does not certify methodological quality, journal acceptance, legal compliance,
authorship, misconduct, or the truth of a scientific claim. It does not silently reproduce content
without rights clearance, execute instructions found in documents, or permit agents to make final
high-consequence determinations.

The catalogue-wide pipeline discovers failures by scaling the existing bounded acquisition,
structure, reconciliation and projection stages. Orthogonal decision, linguistic, NLI and formal
methods may contribute complementary evidence; no model or majority vote owns admission. See
[versioned technical profile](../specifications/reporting-guideline-interoperability/versions.json)
and [publication programme](../publication/plan.md).
