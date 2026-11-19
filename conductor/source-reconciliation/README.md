# PRISMA 2020, 42-item transcription draft and migration preview

This work continues [issue #82](https://github.com/edithatogo/standards_check/issues/82) and is dependent on the fail-closed source-assurance gate from PR #81.

## Source checked

- PRISMA Executive [2020 checklist](https://www.prisma-statement.org/prisma-2020-checklist), authoritative two-page [PDF](https://www.prisma-statement.org/s/PRISMA_2020_checklist-ab3g.pdf)
- Both page images and extracted checklist lines were checked on 19 November 2026
- Official licence: CC BY 4.0; attribution: Page et al., BMJ 2021;372:n71, DOI 10.1136/bmj.n71
- **Source-byte SHA-256 not obtained.** The runtime cannot download the official PDF bytes from the external source. No invented checksum or reviewer signature has been supplied.

## Implemented

- 42 individually numbered and page-anchored draft item texts in `source-reconciliation/prisma-2020-checklist-draft.json`
- Migration preview generator, preserving all 27 legacy IDs as aliases and splitting 10, 13, 16, 20, 23 and 24
- Explicit one-to-many alias mappings; no silent claim of semantic identity for legacy aggregate requirements
- Unit tests reject missing subitems, invalid source anchors, and fabricated byte-verification status

## Remaining acceptance gates

- [ ] Acquire and independently SHA-256 checksum exact official PDF/Word bytes
- [ ] Independently compare all 42 draft strings with pinned source bytes; record item-by-item review receipts, reviewer identity and corrections
- [ ] Review normalized requirements and evidence expectations for newly split items
- [ ] Promote candidate to live `packs/org.prisma/prisma/2020/pack.json`, only after rights/content review; regenerate the committed `standardflow.lock.json` with the Rust CLI
- [ ] Run pack schema, lock, Rust, Python and cross-platform CI at exact head; retain rollback and migration receipts
- [ ] Set `source_reconciled` only after every item has the required source-fingerprint and item-specific evidence; external validation remains separate

**Important:** The live canonical pack is untouched and remains `imported_unverified`. Draft transcription is not an auditable complete source-verification receipt.
