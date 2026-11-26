# Native format qualification candidate

This isolated E18 probe is not a workspace member or a production dependency.
The manifest is deliberately a candidate template, not an admitted Cargo graph.
Candidate pins are Typst syntax 0.15.1 (Apache-2.0), tree-sitter 0.25.10 (MIT),
codebook-tree-sitter-latex 0.6.1 (MIT), and rustfst 1.3.1 (MIT or Apache-2.0).
The prototype targets unique, exact parsed label spans and competing weighted
paths, epsilon transitions and unmatched input. It must compile and pass against
the exact locked native versions before any normalization capability is claimed.
LaTeX grammar parsing cannot establish TeX macro expansion or catcode semantics.
Never execute an untrusted document or fetch imports.

In a disposable no-secret checkout, copy the manifest template to Cargo.toml,
resolve and retain Cargo.lock, verify dependency sources/checksums, license and
advisory policy plus MSRV and compiler evidence; only then fetch the exact locked
graph and execute cargo test --locked --offline. Compare against independently
enumerated output/weight references; preserve error and resource-bound controls.
A successful probe would still not establish full general WFST qualification.
No unreviewed native dependencies are installed in this change. Local Rust and
network access were unavailable; candidate source is not a verified build.
