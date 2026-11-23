# Hosted Rust qualification: first PR #100 head

[Manual run 45097644451][run] completed successfully on 23 November 2026 for
commit `12b7b00737124aa7c0feaead893c930124332489`, tree
`d78a8d83327a67172544f04a716e4eef5950a9aa`. This records the bounded Rust
campaign at that first PR head. The separate boundary setup and aggregate
assurance failures in [the historical hosted receipt][first-head] still apply
to the overall candidate.

| Executed gate | Result |
| --- | --- |
| [Canonical workspace job 137440940618][canonical] | 72 tests passed, zero failed or ignored; Rust 1.98.1, all workspace targets/features, locked dependencies, seed 721114987 and 256 cases per property. |
| [Native mutation job 137441198127][mutation] | cargo-mutants 27.1.0 selected 26 mutants: 25 caught, one known unviable, zero missed, timeouts or other outcomes. The strict inventory/outcome step passed. |

Both artifacts were downloaded and their SHA-256 digests matched GitHub's
metadata. Their `commit.log` files identify the exact source commit above.
Canonical artifact **14784485216** is `canonical-properties-rust-1.98.1`;
mutation artifact **14783734131** is `bounded-rust-mutation-1.98.1`.
The [machine-readable receipt][json] retains archive, report and log digests,
actual job links and source-binding details.

## Scope verified from the native evidence

The complete 26-mutant identity set matches the original local inventory across
`write_value`, `verify_pack_lock`, `validate_difference`,
`validate_updated_totals`, `validate_assessed_outcome` and `validate_count`.
Every caught mutant built successfully, then failed its workspace test phase
with exit code 101. The sole unviable mutant replaces `verify_pack_lock` with
`Ok(Default::default())`; its log confirms Rust E0277 because `LockVerification`
does not implement `Default`. It is excluded from the viable denominator.

cargo-mutants' own unmutated baseline passed **61 tests** in the selected core
and artifacts packages. Version 27.1.0 uses those packages for its baseline and
the workspace for each mutant. The preceding canonical job independently ran
all **72 workspace tests**. These are distinct executed scopes.

All 26 tracked Rust source, manifest, lock and toolchain inputs match the
existing receipt's final input manifest, the tested commit and the working tree
at verification. The canonical workflow also matches the tested commit. The
[original local receipt][local] remains unchanged, retaining the initial two
misses, subsequent strengthened assertions and three local property seeds.
This hosted run executed one property seed.

## Later revisions

The replacement head remains explicitly unknown in this receipt. Reusing this
bounded Rust evidence for a later revision requires the complete Rust input
manifest and workflow to remain unchanged; other modified components need their
own checks. This record does not certify a later whole candidate, receiving main,
scientific interpretation, global mutation score or release artifacts.

[run]: https://github.com/edithatogo/standards_check/actions/runs/45097644451
[canonical]: https://github.com/edithatogo/standards_check/actions/runs/45097644451/job/137440940618
[mutation]: https://github.com/edithatogo/standards_check/actions/runs/45097644451/job/137441198127
[json]: rust-hosted-first-head-20261123.json
[local]: rust-qualification-20261123.json
[first-head]: hosted-first-head-20261123.json
