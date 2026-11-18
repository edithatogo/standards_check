# Technology stack

## Production authority

- Rust **1.98.1**, Edition 2024, exact-pinned through `rust-toolchain.toml`.
- A dependency-minimal workspace with domain crates separated from CLI, API, MCP, WASI/WASM and renderer adapters.
- JSON Schema Draft 2020-12 as the portable wire-contract baseline, with generated Rust types only after round-trip and compatibility tests exist.
- JSON-LD/SKOS/SHACL projections for semantic interoperability; the filesystem pack remains canonical.
- SVG as the primary deterministic visual output, with PDF, raster and accessible HTML projections.

## Experimental acceleration

Mojo is permitted only in an isolated experiment lane. It may be evaluated for SIMD normalization, large-batch transforms or layout kernels after a stable, open toolchain is pinned. Promotion requires semantic parity, deterministic output, fuzz parity, cross-platform packaging, a measured end-to-end benefit and a maintained Rust fallback.

## Interfaces

One application facade serves CLI, static JSON, OpenAPI/HTTP, MCP, WASI components, WASM/PWA and thin SDK/editor/publisher adapters. Interface layers must not reimplement standards logic.

## Assurance tools

Rustfmt, Clippy with warnings denied, unit/integration/doc tests, property/metamorphic tests, mutation testing, cargo-fuzz, Miri, cargo-careful, Loom or Shuttle, Kani for bounded invariants, coverage, reproducible builds, SBOMs, SLSA provenance, artifact attestations, dependency review, CodeQL, cargo-deny, cargo-vet, actionlint, zizmor and OpenSSF Scorecard. Advanced gates earn evidence only when their receipts are observed.
