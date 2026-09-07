# Assurance and release engineering

## Core properties

- canonicalization is deterministic and idempotent;
- stable identifiers do not depend on filenames or display numbering;
- rights restrictions survive every projection and export;
- untrusted document content cannot become instructions or capabilities;
- agents cannot silently make final consequential assessments;
- PRISMA and other arithmetic invariants are machine checked;
- schema and pack migration is explicit, reversible and compatibility tested;
- releases are reproducible, signed and accompanied by SBOM and provenance.

## Harness

Quick, full, deep and release profiles progressively add unit/integration/doc, property, metamorphic, golden, differential, mutation, fuzz, Miri, cargo-careful, concurrency exploration, Kani, coverage, hostile-input, performance, cross-platform, offline, reproducibility, SBOM, attestation, signing, canary, restore and rollback evidence.

CI uses least privilege, immutable action pins, timeouts, concurrency cancellation, untrusted-fork separation, no persistent credentials and generated-drift gates. A configured job is not a passing receipt until observed.
