# Canonical Standard Pack runtime

## Objective

Implement the first executable Canonical Standard Pack vertical slice: strict Rust types, deterministic semantic validation and canonicalization, content-addressed pack locks, a machine-readable CLI, and one real but conservatively labelled PRISMA 2020 migration pack.

## Authority boundaries

- Pack files are canonical; Markdown, HTML, PDF, DOCX, Typst and LaTeX are later generated projections.
- `verbatim_text`, `normalized_requirement` and `guidance` remain distinct.
- Rights are resolved per item and cannot be weakened by rendering.
- `imported_unverified` is not represented as source reconciliation.
- SearchRight remains authoritative for review state and future PRISMA diagram counts.

## Acceptance assertions

1. Unknown contract fields and malformed identifiers fail closed.
2. Every requirement has a stable ID, source anchor, rights policy and evidence expectation.
3. Non-cleared effective rights reject verbatim text.
4. Canonical bytes and SHA-256 are independent of JSON object order.
5. Lockfiles are deterministic, exclude themselves, reject symlinks and detect mutation.
6. The CLI exposes validation, canonicalization, digest and lock operations with JSON output.
7. The PRISMA pack contains 27 unique items and exactly one unresolved-transcription warning.
8. Rust unit, property, CLI, cross-platform and generated-drift checks pass before promotion.
