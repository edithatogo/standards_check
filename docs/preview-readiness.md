# StandardFlow technical-preview and collaboration boundary

**Assessment snapshot:** 23 November 2026. This is a dated capability/evidence
assessment, **not** a release certificate, clinical recommendation, EQUATOR
Network partnership, research quality judgement or claim of current guideline
validity. For live implementation truth, consult
[Conductor tracks](../conductor/tracks.md) and the linked issue/verification
receipts, not this static snapshot alone.

## What can responsibly be demonstrated

| Surface | Demonstrated capability | Explicit limit |
| --- | --- | --- |
| Canonical Rust core | Source-verified strict Standard Packs, canonicalisation, CLI, hashes and locks; one PRISMA 2020 pack with 42 source-reconciled items | Independent meaning, migration, licensing and wider-standards qualification remain open in [#82](https://github.com/edithatogo/standards_check/issues/82) and [#95](https://github.com/edithatogo/standards_check/issues/95) |
| Semantic flows | Four PRISMA 2020 flow families with 12 golden representations and recorded native/synthetic verification | No general assurance that every study diagram or submitted report is methodologically adequate |
| Legacy web and documents | [Public HTML checklist previews](https://edithatogo.github.io/standards_check/), source Markdown and generated PDF/DOCX/LaTeX/Typst pathways | Legacy `source/index.yml` status `mapped` is **not** proof of checklist wording, currency, rights clearance, or Canonical Standard Pack admission; browser interactions and assistive technology require actual deployment checks |
| EQUATOR source discovery | [Read-only 719-page directory candidate](https://github.com/edithatogo/standards_check/pull/112), pinned to the official upstream Git commit; 1 missing upstream title flagged for review | Metadata only, not official EQUATOR API, licence permission, bulk checklist transcription, endorsement or consumer integration |
| Integration | Separate product boundaries and planned contracts with Searchright, Sourceright and AuthenText | [Track 04](../conductor/tracks.md) remains planned; no interoperability-release claim without a pinned consumer acceptance receipt |
| Security and quality | Required protected GitHub checks, CodeQL, ALint, RepoHealth, OpenSSF Scorecard, dependency inventories, coverage and privacy scanning | RepoHealth **93/100** and OpenSSF **7.3/10** at the documented 2026-11-23 snapshot; high scores are not proof of maximal security. See [#116](https://github.com/edithatogo/standards_check/issues/116) and [#30](https://github.com/edithatogo/standards_check/issues/30) |

## Public-facing description (suitable for a technical preview)

> StandardFlow is an experimental, open-source platform for versioned
> reporting-standard metadata, rights-aware checklist representations and
> reproducible research-reporting artefacts. Its current capabilities include
> an early canonical PRISMA implementation and a separate legacy HTML/document
> preview. Further guideline coverage, downstream integrations and
> independent validation remain in development.

**Attribution:** EQUATOR Network and individual reporting-guideline authors
retain ownership of their respective resources. StandardFlow is independent
and **not endorsed by or affiliated with EQUATOR Network**. Reporting
guidelines help authors describe research transparently; they are not
standards for study design, risk-of-bias appraisal or methodological quality.

## Minimum checks before inviting public preview users

- [ ] Actual protected main deployment and HTTPS/browser probe at the deployed
  Pages URL (not just a build artifact).
- [ ] Direct index and representative nested pages work in desktop and 320px
  mobile layouts; no blank/404 pages or broken source links.
- [ ] Browser JS loads at HTTP 200; native task-list checkboxes are not
  duplicated; one check correctly changes the progress count, notes survive
  reload, and Import/Export round-trip a **synthetic** checklist safely.
- [ ] Keyboard-only navigation and assistive-technology spot checks for at
  least the index and PRISMA. Full WCAG 2.2 AA compliance is **not** assumed.
- [ ] Legacy catalogue links are labelled as previews, with clear edition
  attribution and unresolved rights. `mapped` must never appear as a
  claim of verified official text.
- [ ] Complete current required security/quality gates on the exact deployed
  revision; no stale badges or waived findings.

[Web-output correction PR #117](https://github.com/edithatogo/standards_check/pull/117)
owns the missing JS asset, duplicate checkbox logic and legacy label fixes.
Any defect found at live deployment must be recorded there or in a bounded
follow-up, with exact page, viewport, expected/observed behaviour and test
receipt. Browser appearance alone is not functionality acceptance.

## Before formal release or claims of full implementation

In addition to the preview checks: prove item-level source edition/rights and
meaning; complete relevant canonical packs and migrations, cross-runtime
and downstream contracts, broader security and accessibility, reproducible
release/signing/SBOM, rollback and independent methodological acceptance.
The current repository roadmap explicitly includes deferred medium- and
long-horizon features. **Not all features are implemented**, and a successful
source import does not change this.

## EQUATOR engagement

A narrowly framed [technical interoperability proposal](https://github.com/edithatogo/standards_check/issues/118)
is ready for external review. Ask about a stable machine-readable descriptive
metadata export, durable guideline identifiers/version relationships and
metadata attribution/rights guidance. Offer a small optional upstream
contribution; **do not** imply EQUATOR approval, a bulk content licence,
partnership, or that all 719 directory entries are validated checklists.
The GitHub connector lacks write permission to create issues in EQUATOR's
repository; issue #118 is the maintained proposal until an authorised external
submission is made and its URL is recorded.

## Higher-value next increments (not a new framework)

1. Finish deploy/browser functional repair and truthful preview labels.
2. Resolve item-level rights, known-source gaps, and version/extension relationships;
   prioritise a few authoritative standards rather than 719 speculative packs.
3. Add exact-pinned Searchright interoperability only with consumer fixtures.
4. Qualify the remaining existing assurance/dependency/fuzzing decisions in
   [#116](https://github.com/edithatogo/standards_check/issues/116), then
   independent accessibility/methodology and release gates.

Do **not** add a generic crawler, a second catalogue owner, copied publisher
content, dummy tests for a quality score, or an unrelated marketing site.
