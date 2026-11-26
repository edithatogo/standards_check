# Workflow

## Change protocol

1. Read `conductor/index.md` and the active track.
2. State the authority boundary and affected canonical contracts.
3. Add or amend acceptance assertions before implementation.
4. Implement the smallest vertical slice that can produce deterministic evidence.
5. Test locally using the appropriate quick, full, deep or release profile.
6. Record limitations and evidence level; do not promote claims automatically.
7. Open a focused pull request with migration, security, rights and rollback notes.

## Plan and issue reconciliation

Every plan checkbox has a stable `Txx.nnn` identifier and one or more canonical
issue links. Keep existing identifiers stable; append new identifiers instead of
renumbering old work. Every repository issue, including completed history, belongs
in `contracts/project/conductor-issues.v1.json` and owns at least one plan item in
each declared track. The issue body retains the exact track marker and links back
to its plan. The dependency dashboard uses its registered retained comment because
the updater owns its body.

Run `python scripts/validate_conductor_links.py` locally and the same command with
`--live` in authenticated CI. The latter reads all issue pages and registered bot
comments; it makes no writes. New issues can make the event-driven check fail until
triage assigns their owner and updates the versioned registry. An unfinished plan
item must retain an open issue. Completing a bounded implementation does not close
an umbrella's scientific, rights, operational or external acceptance gates.

Issue and PR templates request the ownership and acceptance evidence. A future
GitHub Project displays these records; it does not introduce another independently
maintained completion ledger.

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

## Optional human review

Automation proceeds on required machine evidence and normal protected merge rules.
Human review is available, not a prerequisite for routine workflow execution or
merge. A real unresolved concern or intentional hold must be addressed; do not
fabricate approval or bypass checks. Use native review, draft, cancel, rerun and
per-PR auto-merge controls. See [operational policy](../docs/development/optional-human-review.md).
Model-relative work can proceed with independent blinded agents; retain actual
scientific reference, rights and external authorization boundaries.
