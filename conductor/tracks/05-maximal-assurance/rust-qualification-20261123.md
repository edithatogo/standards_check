# Bounded Rust assurance, 23 November 2026

The strengthened Rust suite passes 72 tests. Eight generated properties pass 256 cases each
under three recorded seeds, for 6,144 successful generated cases within the bounds below.
Real mutation testing exposed two missing assertions; both are now covered and the affected
eight-mutant campaign passes. These are local software-contract results, not scientific,
independent accessibility, source-rights, release or offline-security acceptance.

The [machine-readable receipt](rust-qualification-20261123.json) retains exact input SHA-256s,
commands, unmodified native outcome records, log digests and both initially missed mutants.
Its base is `ba6b0888806e84276e5f54afc07e4e555220c4ea`; the modified Rust inputs are identified
by the receipt hashes. A hosted job must record its own commit before claiming hosted acceptance.
Production Rust logic, canonical pack data and the imported legacy source are unchanged.

## Applicable techniques and observed checks

| Surface | Applicable technique | Executed evidence and remaining limit |
| --- | --- | --- |
| Canonical JSON | Generated contracts and metamorphic testing | Integer/null/Boolean/string values survive encode/decode; canonicalization is idempotent; wire key order and whitespace preserve bytes; float rejection retains escaped error paths. These properties describe the supported integer-only profile. |
| Stable identifiers | Generated positive and negative contracts | Requirement and pack identifiers round-trip; invalid separators, traversal, backslashes and uppercase pack segments fail closed. Existing schema/parsing fixtures remain separate. |
| Pack locks | Filesystem metamorphic and negative tests | Equivalent contents created in different orders produce the same lock. Writing the lock excludes itself. Same-length edits and renames invalidate verification; reversing each change restores the original digest without rewriting the lock. Symlink, bounded-read and failed-exclusive-create tests remain active. |
| PRISMA arithmetic | Bounded generated conservation and mutation checks | Moving one record between database/register sources preserves validity. Each of six downstream one-count corruptions and an extra excluded report must fail. Generated updated-review totals accept addition and reject one-count drift. The exact cross-language safe-integer ceiling is accepted; out-of-range counts remain rejected. |
| Scene projections | Metamorphic, contract and golden checks | Reversing stored nodes preserves SVG and plain-text reading order. Existing scene round-trip/default-metric checks and 12 golden artefacts remain in the normal suite. These checks do not replace assistive-technology or methodological review. |
| Stateful/distributed simulation | Not applicable to this synchronous Rust slice | There is no network transport, distributed scheduler, virtual clock, retry queue, replica or concurrent state machine to simulate. Reassess when such a consumer exists. Native filesystem boundaries still require their concrete failure/race tests; this exclusion does not waive them. |

The identifier migration preview has its own Python reversible-mapping assertions and source
ledger. It is not a general reversible migration engine and this Rust campaign does not promote
one. API, Python schema, legacy runtime and release qualification require their own receipts.

## Property bounds and replay

The existing `proptest` dependency is reused. The two previously implicit property configurations
now explicitly use 256 cases, at most 4,096 shrink iterations, and source-adjacent regression
seed persistence. `PROPTEST_RNG_SEED` remains an environment override; normal local runs can
still explore random seeds. Persisted failures are replayed before generated cases.

| Generator | Bound |
| --- | --- |
| General canonical JSON | Full signed/unsigned 64-bit integer leaves; strings up to 32 characters; recursive depth 4, target size 64, branch size 8; generated vectors/maps have 0–7 entries. |
| Canonical object-order property | 1–7 object entries, keys up to 16 characters, each containing the bounded JSON strategy. |
| Float diagnostic paths | Generated prefix/suffix of 0–12 ASCII letters/digits and array index 0–7; inserted `~/` exercises escape order. |
| Pack identifiers | 2–5 generated segments, each 1–17 ASCII characters; the older namespace/family/edition property also remains active. |
| Requirement identifiers | One alphanumeric character plus 0–48 permitted ASCII suffix characters. |
| Database/register flow | Database count 1–999,999; register count 0–99,999; removal/exclusion candidates bounded below 10,000 or 1,000 and clipped to the preceding valid stage. |
| Updated-review totals | Prior study count and additional report count each 0–999,999; resulting reports are below 2,000,000 before adding the fixed new-review fixture. |

All eight properties passed with each of `0`, `721114987` and `20261123`. No unmutated failure
regression file was generated. The final arithmetic assertions were replayed with all three seeds
after the mutation findings were fixed; unchanged core results were retained.

```sh
PROPTEST_RNG_SEED=721114987 cargo test --locked -p standardflow-core \
  --test canonical_properties --test pack_contract -- --test-threads=1
PROPTEST_RNG_SEED=721114987 cargo test --locked -p standardflow-artifacts \
  --test prisma -- --test-threads=1
```

The generated cases qualify these particular bounds. They provide no exhaustive-input or
repository-wide coverage percentage. The separate fixed test at `9,007,199,254,740,991`
exercises the inclusive upper endpoint that the smaller generated examples cannot reach.

## Mutation campaign and corrections

`cargo-mutants` 27.1.0 (MIT) was installed as an external development tool, with its lockfile.
No workspace/runtime dependency was added. Track 05's maintainer owns this campaign; remove
the documented command and uninstall the tool if it is replaced by an equivalent harness.
The tool builds copies of the source tree and does not inject mutations into the working tree.

| Campaign | Selected | Caught | Missed | Unviable | Timed out |
| --- | ---: | ---: | ---: | ---: | ---: |
| Initial six-function selection | 26 | 23 | 2 | 1 | 0 |
| Complete rerun of the two affected functions after fixes | 8 | 8 | 0 | 0 | 0 |

The initial misses were useful findings:

- Replacing the assessed/excluded/included equality guard with `true` survived because earlier
  corrupt-count cases also tripped neighbouring validators. Every generated valid flow now gains
  one uniquely named additional excluded report with all other counts unchanged. The test requires
  the specific `SF-PRISMA-030` diagnostic and refusal to render.
- Replacing the count limit's `>` with `>=` survived because the suite rejected oversized values
  without accepting the exact endpoint. A fully balanced upper-bound flow must now validate and
  produce a valid scene.

The unviable mutant attempted `Ok(Default::default())` for lock verification. Rust rejects it
because `LockVerification` has no `Default` implementation. It is not a caught mutant.

Acceptance for this bounded selection is **zero unresolved viable mutants**. The 18 unaffected
selected mutants retain their original outcomes (17 caught, one unviable); all eight mutants in
the affected functions were rerun. No global mutation percentage or threshold is inferred from
this selection, and the original missed outcomes remain in the receipt.

The initial copied-tree baseline passed 60 tests in core plus artifacts; the corrected campaign's
baseline passed 28 artifacts tests. This tool version applies `--test-workspace=true` to each
mutant, while the baseline still runs the selected mutated packages. A separate final unmutated
`cargo test --workspace --all-targets --all-features --locked` passed all 72 tests. Strict Clippy
and `cargo fmt --all -- --check` also passed.

```sh
cargo install --locked cargo-mutants --version 27.1.0
PROPTEST_RNG_SEED=721114987 CARGO_BUILD_JOBS=2 cargo mutants \
  --gitignore=true --test-workspace=true --jobs 2 --timeout 30 \
  --build-timeout 120 --no-shuffle \
  --re 'write_value|verify_pack_lock|validate_difference|validate_updated_totals|validate_assessed_outcome|validate_count' \
  --file crates/standardflow-core/src/canonical.rs \
  --file crates/standardflow-core/src/lock.rs \
  --file crates/standardflow-artifacts/src/prisma.rs \
  --cargo-arg=--locked --cargo-arg=--offline --all-features -- --all-targets
```

Use the repository's Rust 1.98.1 toolchain and install locked dependencies before the offline
campaign. The recorded correction rerun narrowed the function expression to
`validate_assessed_outcome|validate_count` and selected only `prisma.rs`.

Tool interpretation follows the versioned upstream documentation for
[mutation filters](https://docs.rs/crate/cargo-mutants/27.1.0/source/book/src/filter_mutants.md),
[results](https://docs.rs/crate/cargo-mutants/27.1.0/source/book/src/using-results.md) and
[test selection](https://docs.rs/crate/cargo-mutants/27.1.0/source/book/src/workspaces.md).
The native command records, rather than a general description of defaults, establish which tests
actually ran here.

## Scheduled-job command qualification

The final complete 26-mutant campaign was rerun using the literal scheduled-job commands
after both assertion repairs: 25 caught, one specifically identified unviable, zero missed
or timed out. The inventory guard accepted this report and rejected missing-mutant, failed-
baseline, unexpected-unviable and survivor fixtures. The native final report SHA-256 is
`63a8dff652291662b03863b28d096d42c8380f97c64959f466752330834f35c9`.
This was local execution; the scheduled/manual GitHub job still requires its own receipt.
