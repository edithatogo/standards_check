# PRISMA 2020 source ledger and historical migration preview

This work continues [issue #82](https://github.com/edithatogo/standards_check/issues/82). PR #81 introduced the promotion gate; PR #83 subsequently promoted the live canonical pack to **42 items with `source_reconciled` status** and regenerated its lock. The [20 November receiving review](../prisma2020-receiving-review-20261120.md) records the current evidence and integration repair.

## Retained source

- PRISMA Executive [2020 checklist](https://www.prisma-statement.org/prisma-2020-checklist), authoritative two-page [PDF](https://www.prisma-statement.org/s/PRISMA_2020_checklist-ab3g.pdf).
- Retained bytes: [`source/official/prisma-2020-checklist.pdf`](../../source/official/prisma-2020-checklist.pdf), 67,506 bytes, SHA-256 `2eedbd5452741f9615307a0bce21a8198c0597ce2a0a8a0fd7e140d64b08c625`.
- Official licence: CC BY 4.0; attribution: Page et al., BMJ 2021;372:n71, DOI 10.1136/bmj.n71. Source attribution and retention details are in the [source README](../../source/official/README.md).
- The receiving review rehashed the committed snapshot; it does not claim a new download from the publisher.

## Ledger and reproducible preview

`prisma-2020-checklist-draft.json` retains the original 42-item draft ledger, including its historical draft status, empty reviewer list and unverified-byte fields. Those fields describe the draft's original stage, not the later live pack. The live pack has separate verification receipts.

The migration preview reads the immutable [27-item predecessor](../../contracts/examples/prisma-2020-legacy27.pack.json), whose [provenance](../../contracts/examples/prisma-2020-legacy27-provenance.md) identifies its exact commit and digest. It preserves all 27 legacy IDs as aliases, splitting groups 10, 13, 16, 20, 23 and 24 through explicit one-to-many mappings. It does not assert semantic identity between an aggregate requirement and every resulting subitem.

```sh
python scripts/build_prisma42_candidate.py --output /tmp/prisma42-draft.json
python scripts/validate_prisma_source_assurance.py
python -m scripts.compare_prisma_source_pdf --pdf source/official/prisma-2020-checklist.pdf --output /tmp/prisma2020-source-comparison.json
```

The comparator requires the pinned PDF bytes, complete numbered rows, exact expected item order and page, full normalized text equality, and agreement between the source ledger and live pack. Normalization uses Unicode NFKC and removes whitespace; it does not remove punctuation. The promotion audit independently checks fixed source identity and item-specific ledger text and anchors. The PDF job establishes correspondence with the retained source bytes.

## Remaining acceptance boundaries

- Independent review of normalized requirements, interpretations and evidence expectations for the newly split items.
- History-preserving migration parity and compatibility across legacy formats and consumers.
- Revision-specific pack schema, lock, Rust, Python and cross-platform CI evidence for subsequent changes.
- Independent methodological, usability/accessibility and publication acceptance. `source_reconciled` does not mean `externally_validated`.

The original draft is an auditable migration input. Its existence alone is not a complete source-verification receipt.

## Additional authoritative-edition source candidates

[Primary article table reconciliation](authoritative-article-reconciliation-20261124.md) describes the first additional cohort of four primary, open-access editions and 82 independently sourced numbered rows. The retained source-table snapshot and manifest under `source/official/` enable deterministic legacy discrepancy reports and explicit primary-source reacquisition. They do not yet constitute additional admitted canonical packs or validated migration semantics.

- [EcoEvo cross-format benchmark](ecoevo-format-benchmark-20261124.md) — first observed candidate sub-item agreement, official-source and independent PDF parser experiment (T01.5b/c; not admission).
