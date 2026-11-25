# Native pack ingress fuzzing

Track 05, issue #116. Use the existing Rust pack parser without a second parser or runtime dependency. cargo-fuzz 0.13.2 and libfuzzer-sys 0.4.13 are isolated in this test-only workspace, with a dated nightly compiler. Existing seeded property and Python XML mutation tests remain independent.

Seed the campaign with the rights-qualified maintained PRISMA pack already used in the Rust property tests. Retain the compiler, dependency lock, seed SHA-256, exact checkout and fuzzer log. A panic, sanitizer finding or timeout is a failing test. No claim of exhaustive validation, and no scorecard claim based solely on adding a harness.

The initial hosted campaign ([run 45368679480](https://github.com/edithatogo/standards_check/actions/runs/45368679480)) executed 932,153 inputs in 61 seconds with no crash or sanitizer finding (cov 3305, peak RSS 481 MB). Its [artifact 14907823633](https://github.com/edithatogo/standards_check/actions/runs/45368679480/artifacts/14907823633) generated the exact 62-package lock, SHA-256 `68de4a21ca9728bdb8329dce00e9278d1d6609adb2c5c2cf7fa9eab0e477dbce`. The committed Git blob matches the artifact bytes. Later lock updates require ordinary dependency review. Subsequent campaigns require committed lock, locked fetch and metadata, offline build and identical post-run lock. The existing dependency policy and SBOM receipt include the fuzz graph; admission remains pending their actual run. This is a bounded test campaign, not a vulnerability absence guarantee.

Reproduce the campaign with the committed lock:

    rustup toolchain install nightly-2026-11-23 --profile minimal
    cargo +nightly-2026-11-23 install cargo-fuzz --version 0.13.2 --locked
    cargo +nightly-2026-11-23 fetch --locked --manifest-path fuzz/Cargo.toml
    cargo +nightly-2026-11-23 metadata --locked --offline --manifest-path fuzz/Cargo.toml --format-version 1
    mkdir -p fuzz/corpus/pack_ingress
    cp packs/org.prisma/prisma/2020/pack.json fuzz/corpus/pack_ingress/prisma.json
    CARGO_NET_OFFLINE=true cargo +nightly-2026-11-23 fuzz run pack_ingress -- -seed=721114987 -max_total_time=60 -max_len=262144 -timeout=5 -rss_limit_mb=1024 -print_final_stats=1

Upstream guide: https://rust-fuzz.github.io/book/cargo-fuzz/ci.html

## Licence-policy qualification

The locked graph's initial cargo-deny check ([job 138364791634](https://github.com/edithatogo/standards_check/actions/runs/45370956988/job/138364791634)) passed advisories, bans and sources but rejected the declared `(MIT OR Apache-2.0) AND NCSA` expression of `libfuzzer-sys` 0.4.13, and the unpublished fuzz package lacked a licence declaration. Use the repository's dual MIT/Apache-2.0 licence for the local package and a version-specific NCSA allowance for the test-only libFuzzer dependency, following the [cargo-deny exception configuration](https://embarkstudios.github.io/cargo-deny/checks/licenses/cfg.html). Retain licence notices; no global licence relaxation or advisory suppression. The subsequent locked campaign ([job 138364791384](https://github.com/edithatogo/standards_check/actions/runs/45370956988/job/138364791384)) completed 629,873 inputs in 61 seconds (cov 3103, peak RSS 468 MiB), without a reported crash or sanitizer finding. Require both dependency-policy and the new exact-head locked campaign to pass before marking the PR ready.

## Previous exact-head run and receiving qualification

The earlier exact PR head `f1354701dfbbaea54940f46b1764faa4b779f63d` passed native fuzzing, dependency policy and maintained inventories. [Native job 138397589437](https://github.com/edithatogo/standards_check/actions/runs/45380390860/job/138397589437) reports 974,312 executed inputs in 61 seconds, peak RSS 478 MB. This is historical bounded evidence, not evidence for current main. Reconciliation onto `ef4fb0dd4c4e01fca4527041e464e816f6f4d73e` preserves the committed fuzz lock and the maintained foundation inventory. Require a fresh locked campaign, its dependency policy, the full protected assurance checks and the receiving-main receipt before closing the integration hold.
