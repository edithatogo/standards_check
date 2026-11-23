# PRISMA source reconciliation status, 23 November 2026

The current pack contains **42 individually numbered entries** with `source_reconciled`
status. [PR #83](https://github.com/edithatogo/standards_check/pull/83) merged the promotion
at `da7e780dad139980cadfc40fb0fec44d90f6af50`;
[PR #86](https://github.com/edithatogo/standards_check/pull/86) repaired the source gate and
integration at `1aef9b5b95582d447d9b539c94d4b5dcf4366679`. Issue #82's older statements
that the pack has 27 items and PR #83 remains open describe superseded states.

## Retained-source and integration evidence

The [official PDF](../../../source/official/prisma-2020-checklist.pdf) is 67,506 bytes with
SHA-256 `2eedbd5452741f9615307a0bce21a8198c0597ce2a0a8a0fd7e140d64b08c625`.
The [source provenance and attribution](../../../source/official/README.md) identify the
PRISMA Executive URL, the 19 November 2026 hosted retrieval, CC BY 4.0 and the unmodified
snapshot. This review rechecks retained bytes; it does not claim a new publisher download.
The separate historical BMJ article's retained bytes also match its sidecar SHA-256
`00804b505724d73e8e82326493ca5b5010c649753652684e1d15b88120201c2e`; it is not substituted
for the authoritative checklist.

The strengthened comparator checks the same PDF bytes that were hashed, complete numbered
rows, item order, page anchors, normalized full text and live-pack agreement. The source
comparison passed independently at the
[PR #86 head](https://github.com/edithatogo/standards_check/actions/runs/44611403091/job/135868653680)
`a17b05ef1d718c8e43f102d15637917dd7fa25f3` and
[receiving main](https://github.com/edithatogo/standards_check/actions/runs/44614868013/job/135880716494)
`1aef9b5b95582d447d9b539c94d4b5dcf4366679`. The same main
[pack workflow](https://github.com/edithatogo/standards_check/actions/runs/44614868013)
also passed contracts, Rust quality and Linux/macOS/Windows checks. These are historical
revision-specific receipts, not acceptance of every later change.

The 23 November recheck of the source files retained at
`ba6b0888806e84276e5f54afc07e4e555220c4ea` passed:

- 39 focused Python tests and 12 subtests across source assurance, migration preview and PDF comparison.
- The source audit: 42 entries, no missing/duplicate/aggregate identifiers, complete licence
  metadata, matching source identity/text/anchors and `item_level_source_reconciled=true`.
- The actual retained PDF comparison: all 42 rows and live-pack source parity.
- Rust 1.98.1 pack-lock verification: five files, tree SHA-256
  `65d142301724ab098eb8b1a5de35d24194dc1136740b69aeda13ef094e2b01f2`.

Reproduce the focused checks from the repository root:

```sh
python -m pytest --import-mode=importlib -q tests/test_prisma_source_assurance.py tests/test_prisma42_candidate.py tests/test_prisma_source_pdf.py
python scripts/validate_prisma_source_assurance.py
python -m scripts.compare_prisma_source_pdf --pdf source/official/prisma-2020-checklist.pdf --output /tmp/prisma2020-source-comparison.json
cargo run --locked -p standardflow-cli -- pack lock packs/org.prisma/prisma/2020 --check
```

## Remaining issue #82 acceptance

The 27-to-42 mapping preserves all historical identifiers and explicitly marks groups 10,
13, 16, 20, 23 and 24 for semantic reassessment. It does not transfer old aggregate compliance
decisions to every new subitem. Independent review of normalized interpretations and evidence
expectations, migration semantic parity and consumer compatibility remain open. The current
source-text comparator does not establish those claims or independently assess topic/section
semantics. Broader legacy-corpus rights, independent methodological evaluation,
usability/accessibility and publication acceptance also remain separate.

Keep issue #82 open for these remaining obligations. The source fidelity and technical
promotion steps can be marked completed without promoting the pack to `externally_validated`.
