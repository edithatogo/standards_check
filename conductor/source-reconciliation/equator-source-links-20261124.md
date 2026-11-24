# EQUATOR source-link discovery — source-only increment (24 November 2026)

Primary Conductor Track **01**; affected Track 03 legacy crosswalk and
Track 05 source assurance. This stage follows the merged published-directory
import (#112) and existing-file reconciliation (#127).

**Boundary:** 719 upstream Quarto pages and the 56 legacy records are discovery
inputs, *not* trusted checklist wording or licenses. The read-only existing
monthly workflow now emits a third report of URL candidates, with links
identified from `downloads`, `relevant-urls` and
`full-bibliographic-reference`. All rows retain the exact upstream commit,
page blob and unverified status. Relative `.qmd` pages, full-text landing
pages, DOI links and direct PDF/DOCX links are distinguished; no content is
downloaded, copied or automatically admitted.

**Reproducibility:** run `python -m unittest tests.test_equator_source_links`
and `python scripts/equator_source_links.py --source /path/to/pinned/equator-git
--catalogue /path/to/equator-catalogue.json --output /tmp/source-links.json`.
The script validates the complete Git tree, all 719 source blob identities and
source revision before exporting. Reuse of the existing Quarto sparse checkout
keeps dependencies to Python stdlib + already-pinned PyYAML. URL discovery is
bounded and filters non-http(s), credential-bearing and local/private addresses.

**Limitations:** markdown links are only candidates, including possible
explanation articles and translations; even a DOI cannot prove an edition,
item wording or copyright clearance. The next real source-fidelity stage
requires independently pinned issuing-organisation original bytes and an
edition-specific rights policy. Disagreement is retained as an exception.
No automatic NLP or similarity score confers `source_reconciled` or
`externally_validated`. Cross-repo selection remains with Searchright #843.
