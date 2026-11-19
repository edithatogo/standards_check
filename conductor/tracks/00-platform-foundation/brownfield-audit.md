# Track 00 brownfield audit

Run `python scripts/audit_foundation.py` from a Git checkout to produce a deterministic JSON inventory and verify Conductor context. The inventory counts tracked source, Markdown, generated and canonical areas, and lists explicit TODO/TBD markers without interpreting file presence as source verification.

## Authority and migration debt

| Area | Risk | Follow-up |
| --- | --- | --- |
| source/index.yml and sidecars | mapped and licensed claims are not independently verified | Check authoritative version, publisher, checksum and item-level redistribution rights |
| markdown/ | stubs and transcriptions are legacy views, not canonical authority | Reconcile item anchors, preserve legacy until parity |
| html/, pdf/, docx/, latex/, typst/ | generated output presence is not reproducibility or publication acceptance | Verify regeneration and compare against canonical projections |
| packs/org.prisma/ | imported_unverified pack is not rights-cleared | Independent rights and content reconciliation |
| schemas/, contracts/, crates/, tests/ | compilation and schema checks do not prove methodology | Carry forward bounded receipts and external review |

Conductor submodule SHA and context links fail closed in CI. Placeholder debt is reported but does not fail CI because deleting an unresolved placeholder would conceal source debt. Repository-standards profile alignment, source rights, historical migration, scientific validity and external acceptance remain open, separate obligations.
