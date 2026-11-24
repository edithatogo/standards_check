# Prepared update to EQUATOR issue 14

Prepared 25 November 2026. Status: **not posted in this attempt**. The GitHub connector returned HTTP 403 (`Resource not accessible by integration`); the connected browser timed out and the alternate browser has no authenticated session. The existing [upstream discussion](https://github.com/EQUATOR-Network/equator-website/issues/14) remains open. [Internal issue 118](https://github.com/edithatogo/standards_check/issues/118) contains the refined implementation links. No native cross-repository parent/subissue relationship is asserted.

## Proposed replacement body

Hello EQUATOR maintainers,

I’m developing [StandardFlow](https://github.com/edithatogo/standards_check), an independent open-source project for machine-readable reporting-standard representation, reconciliation and assurance. Would you welcome discussion of a small, versioned technical interoperability profile, with an optional reference implementation?

The concrete proposal is [draft profile 0.1.0](https://github.com/edithatogo/standards_check/blob/03d00800436a0263b00b6f00833f920275601f7f/docs/specifications/reporting-guideline-representation/0.1.0.md), with a [version/approval registry](https://github.com/edithatogo/standards_check/blob/03d00800436a0263b00b6f00833f920275601f7f/contracts/representation/releases.json) and [prospective evaluation protocol](https://github.com/edithatogo/standards_check/blob/03d00800436a0263b00b6f00833f920275601f7f/docs/research/publication-protocol.v0.1.0.md). The profile separates issuing authority, exact editions and stable item identities; source anchors and reuse rights; original wording and interpretation; applicability and directional requirement relationships; and reproducible evidence. It is a draft with no recorded approval or endorsement. StandardFlow’s existing Canonical Standard Pack is an experimental implementation, not a mandatory format.

We recognize existing work such as [machine-actionable metadata models, MIRcat/JSON-ScheeLD and CEDAR](https://doi.org/10.1038/s41597-022-01707-6). We would evaluate interoperability and reuse before proposing another representation or claiming novelty. The specific problem we are investigating is faithful reconstruction and comparison of heterogeneous reporting-standard sources, retaining uncertainty, source rights and edition differences.

The current directory workflow accounts for 720 published source identities at a pinned website revision. This is discovery coverage, not 720 implemented or validated checklists. Only one 42-item PRISMA 2020 pack has bounded source-text reconciliation; interpretation and broader scientific qualification remain separate. Failed acquisitions and unassessed rights remain explicit, and catalogue inclusion is never treated as permission to redistribute third-party wording, figures or translations.

We would value guidance on:

1. Preferred durable identifiers and relationships for guidelines, editions, extensions, translations and supersession, and the preferred versioned catalogue exchange.
2. How to represent provenance and reuse permissions while preserving the distinction between EQUATOR metadata and issuing groups’ content.
3. Whether an implementation-neutral technical profile, synthetic/rights-cleared examples and conformance tests would be useful, and the appropriate process for feedback on both the specification and reference implementation.
4. Existing EQUATOR or partner initiatives with which this work should align.

If useful, we can prepare a small export or documentation contribution following your preferred process. There is no request for blanket reuse permission, a hosted API or endorsement. Reporting recommendations remain under their issuing groups’ authority.

If GitHub Issues is not the appropriate venue, please advise the preferred channel. Thank you.

## Implementation tracking

This is the single upstream discussion for the profile and optional implementation. Detailed implementation and evaluation work is tracked in the project repository, including completed work, so maintainers can follow progress without a separate EQUATOR issue for every workstream.

| Workstream | Project issue | Current boundary |
| --- | --- | --- |
| Engagement and feedback | [#118](https://github.com/edithatogo/standards_check/issues/118) | Feedback and any requested changes remain open |
| Representation versioning | [#164](https://github.com/edithatogo/standards_check/issues/164) | Bounded implementation completed; profile 0.1.0 remains an unapproved draft |
| Directory and source reconciliation | [#111](https://github.com/edithatogo/standards_check/issues/111) | Acquisition and source qualification remain explicit |
| Rights and semantic qualification | [#95](https://github.com/edithatogo/standards_check/issues/95), [#82](https://github.com/edithatogo/standards_check/issues/82) | No automatic admission of held wording or interpretations |
| Analytical exports and consumer interoperability | [#149](https://github.com/edithatogo/standards_check/issues/149), [#161](https://github.com/edithatogo/standards_check/issues/161) | Versioned contracts and consumer evidence are separate gates |
| Prospective evaluation and publication | [#158](https://github.com/edithatogo/standards_check/issues/158) | Planned experiments; no scientific acceptance inferred from CI |
| Reviewed metadata dissemination | [#162](https://github.com/edithatogo/standards_check/issues/162) | Selective rights-reviewed export only; no blanket source-content upload |
| Assurance and plan/issue reconciliation | [#31](https://github.com/edithatogo/standards_check/issues/31), [#163](https://github.com/edithatogo/standards_check/issues/163) | Traceability and software checks remain distinct from endorsement |

These links do not presume an upstream project relationship or assignment of work to EQUATOR. We can adjust the structure to your preferred process.
