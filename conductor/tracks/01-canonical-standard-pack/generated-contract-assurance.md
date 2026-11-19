# Generated canonical-contract assurance

This bounded maintenance leaf adds four production-facing properties at 256
cases each, using the existing locked proptest dependency and canonical Rust
1.98.1 profile. Inputs are synthetic integer JSON and portable identifiers:

1. Canonical encoding preserves every admitted JSON value, is idempotent after
   decoding, retains its SHA-256 and has no trailing newline. The generator
   includes signed/unsigned integer boundaries, Unicode strings, arrays and maps,
   bounded to four recursive layers and seven children per container, with a
   generation size target of 64.
2. Reversed object order and added wire whitespace yield identical canonical
   bytes. The test constructs reversed JSON text directly, avoiding a vacuous
   check through an already-sorted in-memory map.
3. A non-integer number nested under a generated key containing both `~` and `/`
   fails with the correct escaped diagnostic path and array index.
4. Valid generated PackIds survive serialization. Added leading/trailing/empty
   separators, traversal segments, backslashes and uppercase segments fail both
   the public parser and deserialization.

The normal foundation CI already runs this integration target. A separate
path-scoped PR/weekly/manual workflow runs the bounded campaign with seed `721114987`, records
compiler/commit/seed and test logs, and retains any minimized proptest regression
files. Its build budget is nine minutes, execution budget two minutes and job
budget twelve minutes; artifacts remain for fourteen days. Other seeds can be
run locally with `PROPTEST_RNG_SEED`; ordinary PR properties retain their default
random seed for additional exploration. Failures must be reproduced and their
minimized inputs reviewed before any regression fixture is committed.

```sh
PROPTEST_RNG_SEED=721114987 cargo +1.98.1 test --locked -p standardflow-core \
  --test canonical_properties -- --test-threads=1 --nocapture
```

This extends deterministic contract assurance without changing production code,
source/rights evidence, PRISMA content, dependency versions, track acceptance or
release gates. Coverage-guided native fuzzing and sanitizer execution are not
claimed by these property tests. The implementation PR records observed checks
and any unavailable profiles; a configured workflow alone is not a pass.
