# EQUATOR catalogue — bounded source-reconciliation increment (2026-11-23)

**Canonical ownership:** StandardFlow track 01 (standards identity / metadata),
with prospective track 04 (Searchright consumer). `source/equator/` is discovery
metadata, NOT a Canonical Standard Pack or an item-level transcription.

**Source:** `EQUATOR-Network/equator-website`, branch `main`, revision fixed in
each generated catalogue. The upstream website listing includes direct child
`reporting-guidelines/*/index.qmd`, explicitly excluding `under-development`.
The index was independently inspected on 2026-11-23: **719** published source
pages and **236** separate under-development pages at revision
`46124ee9d420cf5477b1b0b1d7e39d2fcf469bc1`.

**Acceptance (source-only):**

1. Every published direct-child `index.qmd` yields exactly one stable
   `equator:<slug>` ID, canonical page URL, source path, source Git blob SHA,
   and repository commit. Under-development entries are excluded.
2. Metadata extraction accepts only Quarto YAML frontmatter and a whitelist of
   descriptive fields. It never imports original checklist item bodies, journal
   article contents, source files, or implied licences.
3. A missing source file, modified checkout or duplicate ID fails. Missing or
   invalid upstream frontmatter is retained with `metadata_status: needs_review`,
   a reproducible diagnostic and a summary count; no title or DOI is invented.
   `--check` detects reproducibility drift.
4. Updates require human review of additions, removals and revisions; changing
   cataloguing metadata does not promote a Standard Pack or change Searchright
   research protocols, PRISMA ledgers, or method/evidence claims.

**Verification boundary:** network-free synthetic unit checks can prove parser
contracts but not that all upstream metadata fields are correct, that the site
catalogue is complete, that publication rights are cleared, or that a full
upstream checkout has been processed. The Git-tree-sourced `discovery.json`
is pinned and leaves all metadata unextracted. The first hosted source-check
identified an empty title in `strobe-metepi`; it is treated as explicit review
work, not dropped. Full metadata qualification and per-standard source/rights
qualification remain separate from a successful parser run.

**Rollback:** revert the additive catalogue commit; existing packs and review
state are unchanged. Cross-repository linkage requires an exact consumer contract
and downstream Searchright acceptance, not a copied directory or merged monorepo.
