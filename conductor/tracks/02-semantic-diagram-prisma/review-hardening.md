# Track 02 review hardening

## Trigger

Post-implementation review of the semantic diagram and PRISMA 2020 reference
slice identified contract-parity, resource-exhaustion and
non-visual-equivalence gaps. These defects should remain visible as review
fixes rather than being hidden inside the original implementation commit.

## Required fixes

- Mirror JSON Schema size and cardinality limits in the Rust domain layer so
  callers cannot bypass them.
- Bound recipe and PRISMA input bytes before parsing and bound interpolated
  output growth.
- Enforce the cross-language safe-integer ceiling for PRISMA counts.
- Bound exclusion-reason counts and text and reject XML 1.0-invalid characters
  before SVG rendering.
- Ensure the text equivalent describes both nodes and flow relationships.
- Expose the complete text equivalent through the SVG accessible description.
- Add adversarial, schema-parity, CLI and accessibility regression tests.
- Regenerate and byte-compare every committed reference artefact.

## Evidence boundary

Passing tests can establish compiler and synthetic-fixture evidence for these
bounded invariants. They do not establish external accessibility
certification, methodological endorsement of the PRISMA mappings or production
readiness of arbitrary third-party recipes.
