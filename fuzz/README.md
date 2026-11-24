# Native pack ingress fuzzing (candidate)

Track 05, issue #116. Use the existing Rust pack parser without a second parser or runtime dependency. cargo-fuzz 0.13.2 and libfuzzer-sys 0.4.13 are isolated in this test-only workspace, with a dated nightly compiler. Existing seeded property and Python XML mutation tests remain independent.

Seed the campaign with the rights-qualified maintained PRISMA pack already used in the Rust property tests. Retain the compiler, dependency lock, seed SHA-256, exact checkout and fuzzer log. A panic, sanitizer finding or timeout is a failing test. No claim of exhaustive validation, and no scorecard claim based solely on adding a harness.

This draft's first hosted run produces a candidate fuzz/Cargo.lock. **Do not merge** until the actual generated lock has been reviewed and committed, the workflow requires that exact lock rather than generating it, the fuzz graph has passed applicable dependency policy/inventory checks, and the campaign passes on the protected receiving revision. The draft explicitly does not alter the production Cargo workspace or its lock.

Reproduce the campaign after the lock is admitted:

    rustup toolchain install nightly-2026-11-23 --profile minimal
    cargo +nightly-2026-11-23 install cargo-fuzz --version 0.13.2 --locked
    mkdir -p fuzz/corpus/pack_ingress
    cp packs/org.prisma/prisma/2020/pack.json fuzz/corpus/pack_ingress/prisma.json
    cargo +nightly-2026-11-23 fuzz run pack_ingress -- -seed=721114987 -max_total_time=60 -max_len=262144 -timeout=5 -rss_limit_mb=1024 -print_final_stats=1

Upstream guide: https://rust-fuzz.github.io/book/cargo-fuzz/ci.html
