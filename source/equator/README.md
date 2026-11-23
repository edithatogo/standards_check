# EQUATOR reporting-guideline directory (discovery only)

The [EQUATOR Network](https://equator-network.org/reporting-guidelines/) publishes
source pages in [EQUATOR-Network/equator-website](https://github.com/EQUATOR-Network/equator-website).
This directory indexes that **published** Quarto catalogue without scraping HTML or
copying guideline/checklist bodies. `discovery.json` contains immutable-source
paths and Git blob IDs; the optional `catalogue.json` adds unverified descriptive
metadata from each page's YAML frontmatter. Both retain the exact upstream commit.

```sh
git clone --filter=blob:none --depth=1 --sparse \
  https://github.com/EQUATOR-Network/equator-website.git /tmp/equator-website
git -C /tmp/equator-website sparse-checkout set --no-cone \
  'reporting-guidelines/*/index.qmd'
python scripts/sync_equator_catalog.py --source /tmp/equator-website \
  --mode discover --output source/equator/discovery.json
python scripts/sync_equator_catalog.py --source /tmp/equator-website \
  --mode catalogue --output source/equator/catalogue.json
```

A read-only [GitHub Actions workflow](../../.github/workflows/equator-catalogue.yml)
runs on source-related PRs, monthly, and on demand. It creates a full descriptive
metadata catalogue and addition/removal/revision report **as an artifact for
review**, never an automatic overwrite of the curated source inventory.

`--check` replaces output writing with a deterministic drift assertion. For review,
compare the new commit, added/removed/changed `equator:<slug>` IDs, and source
links before accepting any update. Reclassification and guideline succession are
editorial decisions, **not** inferred from acronym or a newer date. The
`under-development` directory is excluded from the published catalogue.

The upstream website repository is MIT licensed as code, but **that does not
license all linked articles, PDF/DOCX checklists, diagrams or publisher works**.
EQUATOR's [terms of use](https://equator-network.org/terms-of-use.html) and
individual publisher rights still apply. The catalogue copies **only metadata**:
no checklist items, full bibliographic text, file downloads, or rights assertions.
Every row has `metadata_status` (not extracted / extracted but unverified), and
the collection has an explicit `rights_status`. The existing `source/index.yml`
and Canonical Standard Packs remain separately curated. Promotion of individual
item text requires independently verified source, edition, item IDs, licence,
anchors, comparison evidence and review; see existing issue #95.

Ownership: `standards_check`/StandardFlow holds the standards catalogue and
qualified packs. Searchright consumes version-pinned references and stays
responsible for review/search state and PRISMA counts. This is not evidence of
methodological adequacy, complete checklist transcription or clinical validity.
