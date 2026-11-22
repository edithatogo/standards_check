# Track 02: Recipe text metrics

## Corrected behavior

The 22 November Ponytail review found that recipe layout used its declared padding
and line height, but discarded them when constructing the scene. SVG then used
fixed 18px padding and 20px line height, allowing valid compact layouts to overflow.

The scene now carries optional `node_padding` and `line_height` properties. Missing
values retain the historical 18/20 defaults; default values are omitted during
serialization, preserving the existing canonical JSON and rendered output bytes.
Recipe construction passes its values into the scene, and SVG uses those values
for label insets, vertical centering and line spacing. Its font size is at most
14px and is reduced to the line height for the permitted 10–13px compact range.

Rust and JSON Schema enforce padding 4–200 and line height 10–100. Rust also
rejects node rectangles that cannot contain the declared padding and text-line
height, using checked arithmetic before any renderer runs. This is geometric
line-box validation, not a new font-measurement or general accessibility claim.

The follow-up review also found that wrapping imposed a minimum capacity of 12
characters even when fewer fit inside the declared padding. Recipe validation and
wrapping now share one checked capacity calculation using each node's computed
width, including its column span. An 80px node with 36px padding and a declared
7px character width wraps at one character; 32px padding permits two. Positive
inner widths smaller than one character, zero or negative inner widths, and a
zero character width fail before layout with `SF-RECIPE-022`. A wider spanning
node remains valid when its own geometry has room. Both spaced words and long
unbroken tokens follow the same capacity.

## Compatibility

Existing serialized v1 scenes continue to deserialize and retain byte-identical
default JSON/SVG output. Nondefault metrics are explicit in scene JSON and survive
round-tripping. Older strict consumers must update before accepting those new
optional properties; Rust callers constructing `Scene` literals must provide the
two fields. The current repository has one such construction site, now updated.
No dependency or built-in PRISMA recipe changes were needed.

## Local verification, 23 November 2026

Linux, Rust 1.98.1. The compact-layout regression failed before the fix because
the serialized scene lacked its requested padding, then passed with the repair.
The narrow-width regression separately failed at its per-line capacity assertion
before the minimum-12 wrapping rule was removed, then passed with the repair.

- `cargo test --locked -p standardflow-artifacts --test hardening`: 15 passed,
  including five new regression tests for compact multiline output, historical
  JSON/SVG compatibility, invalid metrics or uncontainable line boxes, narrow
  labels, and impossible widths versus valid column spans.
- `cargo fmt -p standardflow-artifacts -- --check`: passed.
- `cargo clippy --locked -p standardflow-artifacts --all-targets --all-features -- -D warnings`: passed.
- JSON Schema validation accepted omission plus six valid boundary/default values
  and rejected ten out-of-range or incorrectly typed values.
- The CLI regenerated SVG, text and canonical scene JSON for all four PRISMA
  fixtures into a temporary directory after both repairs: all 12 matched
  committed bytes exactly.

The checks used the integrator's dependency-update working tree based on
`fe1df165863993deeae2e21f0515c3bc630345a8` plus these source changes. The verified
file hashes below bind this local receipt to the implementation before publication.
A final integration commit, whole-workspace checks and hosted results must be
recorded separately. Source rights, methodology, migration parity and independent
accessibility qualification remain open.

| Verified file | SHA-256 |
| --- | --- |
| `crates/standardflow-artifacts/src/recipe.rs` | `0456ebf5d463a3718550bcd9234964a9e165805838d63f5ceec6102c16fff59f` |
| `crates/standardflow-artifacts/src/scene.rs` | `48351a82b4ff0f4762f7a41d96088d225fb284d589e1e3d8d590eb79999c6628` |
| `crates/standardflow-artifacts/src/render.rs` | `5b66618b293550c67e28af4331c08eccba0a1346c558903af8b92970efeecdaf` |
| `crates/standardflow-artifacts/tests/hardening.rs` | `a29701c7b48eb7dde782518658e5aecce3a56799633b76a3d90119cb0a78149e` |
| `schemas/scene-graph.v1.schema.json` | `593f3fe0f426ad00d739ae4d5b64cc7e69002417a3c61902da5d4fe86f9bb4d0` |
