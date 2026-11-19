# PRISMA 2020 source and rights reconciliation (19 November 2026)

This assessment records the **pre-PR #83, 27-item state** and its original promotion decision. PR #83 later promoted the live pack to 42 source-reconciled items. The current source identity, comparison scope and receiving integration repairs are recorded in the [20 November receiving review](prisma2020-receiving-review-20261120.md). References to the current or committed pack below mean the pack at the time of this original assessment.

## Authoritative evidence and rights

- PRISMA Executive official [2020 checklist](https://www.prisma-statement.org/prisma-2020-checklist): provides original checklist in PDF and Word and explicitly states checklist redistribution, adaptation and commercial reuse under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) **with attribution**.
- The [PRISMA 2020 statement](https://www.prisma-statement.org/prisma-2020-statement) identifies the primary publication as Page MJ et al., *BMJ* 2021;372:n71, DOI [10.1136/bmj.n71](https://doi.org/10.1136/bmj.n71). The source includes **27 numbered sections with lettered sub-items**.
- The current pack cites the primary BMJ PDF with previously recorded SHA-256. This audit has **not independently re-downloaded and rehashed those original bytes**. Its existing hash is a legacy claim, not an independently confirmed current retrieval receipt.
- The checklist licensing is **cleared for this particular work** at the stated CC BY terms, subject to attribution and identification of modifications. It does not extend to unrelated publisher content, photographs, trademarks, or third-party standards.

## Actual item-level reconciliation boundary

The committed pack has **27 aggregate entries**, but the authoritative checklist contains **42 separately numbered items/subitems**. The six split groups are:

| Main item | Required subitems | Existing representation |
| --- | --- | --- |
| 10 | 10a, 10b | One aggregate entry |
| 13 | 13a through 13f | One aggregate entry |
| 16 | 16a, 16b | One aggregate entry |
| 20 | 20a through 20d | One aggregate entry |
| 23 | 23a through 23d | One aggregate entry |
| 24 | 24a through 24c | One aggregate entry |

The existing aggregate text omits independently assessable requirements. For example, 16b (excluded apparently eligible studies and reasons), 24b (protocol access), and 24c (protocol amendments) are not separately represented. The 13 and 20 subitems likewise cannot be considered individually reconciled.

**Decision:** retain `verification.status = imported_unverified`. Changing it to `source_reconciled` without a complete, source-comparison receipt would be false assurance. The current pack's licence record is supported by the official PRISMA rights statement, but a licence verification is not content verification.

## Required promotion work

1. Acquire and checksum a specific **official** PRISMA Word/PDF checklist release, record URL, retrieval time, exact bytes and reproducible digest. Retain a rights-aware source manifest.
2. Split the existing aggregate 10/13/16/20/23/24 items into independently addressable lettered requirements; preserve mappings from legacy IDs and evidence anchors, including migration compatibility.
3. Verify all 42 individual source wordings, item numbers, sections and source locators against the pinned source; record reviewer, date, source fingerprint, corrections and any differences. Preserve `verbatim_text`, normalized interpretations and guidance as separate evidence fields.
4. Regenerate the canonical pack hash and pack lock, test old-to-new migration and cross-format parity, then promote to `source_reconciled` only after the exact revision passes the gate and receives documented review.
5. Leave `externally_validated`, methodological correctness, translation and publication-level acceptance as **separate, later gates**.

Run `python scripts/validate_prisma_source_assurance.py` to emit a deterministic machine-readable inventory, and `python -m unittest tests.test_prisma_source_assurance` for regression assertions. The offline audit **fails** if source status is promoted before the underlying item/subitem inventory and evidence preconditions are satisfied; it reports incompleteness without failing merely because a provisional pack remains correctly labelled.
