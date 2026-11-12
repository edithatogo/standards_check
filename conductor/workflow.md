# Workflow

## Change protocol

1. Read `conductor/index.md` and the active track.
2. State the authority boundary and affected canonical contracts.
3. Add or amend acceptance assertions before implementation.
4. Implement the smallest vertical slice that can produce deterministic evidence.
5. Test locally using the appropriate quick, full, deep or release profile.
6. Record limitations and evidence level; do not promote claims automatically.
7. Open a focused pull request with migration, security, rights and rollback notes.

## Development rules

- Test-driven for parsers, resolvers, arithmetic, state machines and renderers.
- Conventional Commits; one logical change per commit where practical.
- Generated files must be reproducible and checked with `git diff --exit-code`.
- Dependencies require a documented owner, purpose, licence and removal path.
- Network access, telemetry and external writes are explicit opt-ins.
- Fuzz, mutation and formal checks are risk-targeted, not badge collection.
- Fixtures must be synthetic, public/rights-clear, or securely referenced without redistribution.
- Cross-repository revisions are exact pins with consumer-driven fixtures and rollback.

## Verification profiles

- **quick:** format, lint, unit, schemas, fixtures, generated drift, secrets and workflow policy.
- **full:** workspace integration, coverage, contracts, cross-target, document and visual checks.
- **deep:** mutation, fuzzing, Miri, cargo-careful, concurrency exploration, model checking, performance and hostile-input suites.
- **release:** clean-room/offline builds, reproducibility, SBOM, provenance, signatures, downstream canaries, restore and rollback rehearsal.
