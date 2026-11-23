# Maximal assurance, release and external validation

## Objective

Qualify the maintained Rust, Python and API contracts with proportionate, reproducible checks
and close the executable gaps in issues #29 and #30. Later release and external acceptance
remain separate stages; starting this track does not complete the wider roadmap.

## Acceptance

1. Property campaigns record generators, bounds, seeds and failure replay; metamorphic checks
   exercise canonicalization, locks, arithmetic, renderer order and API list/item agreement.
2. Bounded mutation campaigns retain the initial findings, each outcome and justified exclusions.
   Every selected viable mutant must be caught; compile failures are never counted as catches.
3. Schema, CLI and HTTP contracts reject invalid input with the expected nonzero/error status.
4. Component coverage emits actual reports bound to the tested revision and enforces the recorded
   floors. Codecov upload and commit-status acceptance require separate hosted observations.
5. Workflow, dependency-review, baseline dependency SBOM, secret/privacy and CodeQL gates are inventoried against policy.
   Managed-file comparisons name an exact upstream revision and preserve local instructions.
6. A solo-maintainer ruleset requires qualified automation and PRs, disallows force pushes/deletion,
   requires zero human approvals and retains owner recovery without routine bypass.
7. Release reproducibility, provenance/signatures, downstream contracts, migration semantics,
   rights, independent methodology and accessibility each receive their own evidence before claim.

The [verification record](verification.md) defines applicability and current limits. Track 04's
future ecosystem contracts are required before ecosystem release acceptance; they do not block
the current local assurance work on Tracks 00–03.
