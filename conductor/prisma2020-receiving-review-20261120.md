# PRISMA 2020 receiving review (20 November 2026, Australia/Brisbane)

## Reviewed state and source evidence

This review starts from main commit `da7e780dad139980cadfc40fb0fec44d90f6af50`, which merged [PR #83](https://github.com/edithatogo/standards_check/pull/83). The live PRISMA pack contains **42 individually numbered items**, `source_reconciled` status, item-specific normalized-text hashes and a committed pack lock. The earlier [27-item source and rights assessment](prisma2020-source-rights-20261119.md) remains a historical record.

The retained official source is [`source/official/prisma-2020-checklist.pdf`](../source/official/prisma-2020-checklist.pdf): **67,506 bytes**, SHA-256 **`2eedbd5452741f9615307a0bce21a8198c0597ce2a0a8a0fd7e140d64b08c625`**, from the recorded [PRISMA Executive PDF URL](https://www.prisma-statement.org/s/PRISMA_2020_checklist-ab3g.pdf). The receiving review rehashed the committed snapshot and independently extracted its numbered rows. All 42 rows, page assignments and complete texts match the ledger after Unicode NFKC and whitespace normalization; the live pack's verbatim strings match the ledger. This is verification of the retained source, not a new retrieval receipt or scientific qualification.

The [PR #83 source-comparison job](https://github.com/edithatogo/standards_check/actions/runs/44607909955/job/135856426381) passed at `4ace3d0230063b7090961d52404e8001d537915d`. The older [receipt stored in the pack](https://github.com/edithatogo/standards_check/actions/runs/44508730776/job/135507112818) belongs to `1c727d362bc40b9d84c0a5d42fa13f30d9c2231d`; it must not be relabelled as acceptance of a later revision. Both jobs used the earlier comparator, whose weaknesses are addressed below.

## Receiving defects and bounded repair

| Finding at the reviewed baseline | Repair and acceptance assertion |
| --- | --- |
| Rust tests still expected 27 items and an unverified warning; the [Windows job](https://github.com/edithatogo/standards_check/actions/runs/44607909955/job/135856427071) failed that assertion. | Require exactly 42 reconciled items and no warning for the live pack. Preserve imported-pack warning and nullable-member behavior through separate synthetic fixtures. |
| The migration preview read the now-42-item live pack while correctly requiring the old 27 IDs. | Freeze the exact historical predecessor and its provenance; retain the strict 27-item input contract and all legacy aliases. |
| A source anchor only needed a matching URL prefix. | Require the complete expected URL and the declared, correct page; reject malformed and mismatched anchors. |
| The PDF comparator accepted any matching page substring, including text from another numbered item or a short fragment. | Extract complete numbered PDF rows and require item order, page and full normalized-text equality for both ledger and live pack. Extract from the same bytes whose digest was checked. |
| An altered live text could pass the promotion audit after refreshing its self-reported hash. | Bind the audit to fixed official source identity and the independent ledger's text, item and anchor. The separate PDF job binds both ledger and pack to source bytes. |
| Two positive assurance fixtures hashed text with a different normalization convention. | Use the documented NFKC/whitespace normalization consistently while retaining negative assurance cases. |
| Source-only changes could miss the pack workflow's path filters. | Trigger the same pack/source checks for the retained official source and historical preview fixture. |
| Conductor records still described the live pack as 27 items and unverified. | Record the current 42-item transcription state while preserving historical receipts and separate acceptance gates. |

The repair preserves the live pack, PDF, rights declarations, verification status and lock. It changes validation, integration fixtures and evidence records. A correct current transcription does not justify a validator accepting incorrect future input.

## Verification and remaining gates

Local receiving-repair verification passed 182 Python regressions and 62 Rust tests, Rust 1.98.1 formatting and strict Clippy, and the documented source audit, historical preview and actual-PDF comparison commands. A separate review ran 15 CLI cases with the real pinned PDF and extractor: the unchanged baseline passed, and all 14 altered inputs were rejected, including coordinated ledger/pack text changes and refreshed self-reported hashes. These checks exercise the complete comparison path; synthetic unit-test layout fixtures alone are not source evidence.

The exact committed tree and subsequent hosted results are recorded in the follow-up pull request. Earlier source and runtime receipts do not transfer automatically to its head or receiving main. The retained pack lock remains the source of content-drift verification. The offline audit checks consistency with the ledger; the separate PDF job is necessary to establish agreement with the authoritative bytes. Both gates remain enabled.

The following remain outside this source-text reconciliation: independent correctness of normalized interpretations and evidence expectations, migration semantic parity and legacy-consumer compatibility, broader legacy-corpus rights, independent methodological evaluation, usability/accessibility and publication acceptance.

[PR #67](https://github.com/edithatogo/standards_check/pull/67) was merged separately with its original offline-security caller. At this review, the [receiving-main offline job](https://github.com/edithatogo/standards_check/actions/runs/44607955871/job/135856587068) is queued with no runner assigned and no executed steps. Its upstream rollout [PR #126](https://github.com/edithatogo/repository-standards/pull/126) still records image, policy and runner qualification gates. This repair neither changes that caller nor supplies its missing execution evidence. A merged caller and a queued check do not establish offline-security acceptance.
