# Catalogue enrichment v1 — E4/E6 exploratory panel

**Status:** executed internal descriptive baseline, 26 November 2026. No scientific, applicability, equivalence, canonical admission or public release decision.

## Inputs and method

Reuse the historical 720-entry EQUATOR catalogue archive (run 45635380131, artifact 15031534787) and the admitted PRISMA 2020 requirement pack. Do not infer that catalogue classifications are issuer-validated or that unavailable source text has been inspected. The archive retains study type, clinical specialty and report section, but not the live site's searchable keyword field. One entry lacks title and all three facets.

The selected 41 MeSH descriptor records contain observed 2026 labels and tree positions, with local curated lexical variants and separately marked broad study-type hints. Each source record is resolvable through its NLM descriptor identifier. This is a small versioned descriptor projection, not a full frozen MeSH release. Compare preferred-label-only matching with a curated dictionary as descriptive baselines. Exact character spans, word boundaries, longest nonoverlapping matching and span hashes preserve provenance. The comparison is not a controlled recall experiment. No neural inference has run.

Conserve original catalogue identities, facet assertions and admitted requirement identities. Traverse observed MeSH tree-position prefixes only; do not treat all hierarchy edges as logical subclass or applicability assertions. Keep direct mentions, ancestry, local hints and proposed classifications separate. The source rights gate excludes unadmitted packs. Reject duplicate identities, ambiguous alias links and unbound graph edges. Do not export source prose or automate promotions.

## Observed results

| Measure | Result |
| --- | ---: |
| Catalogue identities | 720 |
| Recorded facets | 719 |
| Study types / clinical specialties / report sections | 16 / 45 / 26 |
| Explicitly unspecified study design / specialty | 131 / 307 |
| Preferred label only title matches | 42 |
| Curated dictionary title matches | 219 |
| Titles with multiple concepts | 27 |
| Unique entry-concept pairs (direct) | 247 |
| Additional ancestor associations | 120 |
| Candidate study-type pairs / already declared | 188 / 148 |
| Additional candidates | 40 |
| Unspecified-design entries with a candidate | 2 |
| Admitted PRISMA requirements with direct topic mention | 10 / 42 |
| Nodes / typed edges | 890 / 3905 |

The 40 additional study-type candidates comprise 32 systematic review, three observational, three clinical trial and two qualitative suggestions. Agreement with existing categories (148/188) is not accuracy. Inspection shows why: a title may mention a systematic review used to develop the reporting guideline, not the study design the guideline governs. A topic mention is not a target-study assignment. Generic guidelines need not acquire a specific design label. Unmatched titles do not establish absent topics. MeSH ancestry increases candidate reach, not verified applicability. The graph does not establish requirement coverage gaps.

Selected ancestor results: Review Literature as Topic, 3 direct to 65 expanded entries; Clinical Trials as Topic, 45 to 56; Artificial Intelligence, 14 to 20. The expansion counts include direct matches. All nodes/edges retain provenance and distinctions; no canonical packs were promoted.

## Reproduce and retain

See [run receipt](../../research/catalogue/catalogue-enrichment-v1-receipt.json). With the exact retained archive and pack, run:

```sh
python research/catalogue/ontology_projection.py \
  --catalogue-artifact github-actions-artifact-15031534787.zip \
  --pack packs/org.prisma/prisma/2020/pack.json \
  --output equator-ontology-graph-v1.json
PYTHONPATH=. python -m pytest --import-mode=importlib -q tests/test_catalogue_enrichment.py
```

Five focused tests passed in the local extracted working set; deterministic repeat preserved the content identity (elapsed time excluded). Full checkout, repository quick target, and hosted checks remain unverified. Exact code/test/descriptor blobs, input hashes, snapshot identity, graph and TSV hashes are retained. The evidence bundle is in the researcher's personal Library under standards_check/publication-evidence/catalogue-enrichment-v1-<snapshot_sha256>/evidence.zip. The historical catalogue archive is already separately retained in the publication evidence snapshot. Do not replace either snapshot or commit the full derived graph publicly before rights/export review.

## Next experiment and crosswalk

Use existing E4/E6 and T01.052/053, #158. Keep #188 source qualification, #180 typed ontology assertion validation, #191 bibliographic recovery and #192 publication synthesis separate. This is a supplementary observational panel for the next publication snapshot, not a new benchmark registry.

- Freeze official MeSH release, OBI investigation concepts and STATO statistical concepts with versions, checksums and licence/usage conditions; use EDAM for computational/data operations and disease/phenotype ontologies only for justified scope.
- Independently annotate rights-qualified titles, then abstracts/scope statements and requirement text. Distinguish target study type, development method, background topic, reporting obligation, condition, exception and negation. Include ambiguous links, generic scope, absent terms and hard negatives. Hold out whole guideline families. Do not use existing facets as independent truth.
- Compare dictionary matching, neural span extraction, ontology linking, and role-qualified linking. Test direct versus hierarchical expansion and lexical/dense candidate generation at equal budgets. Measure span precision/recall, top-k linking, role accuracy, candidate recall, false scope assignments, time and review burden. Include abstention and uncertainty. Use the existing full/constrained factorial plan where eligible common inputs allow; this title-only baseline does not populate unexecuted factorial cells.
- Evaluate graph increment and co-occurrence after role qualification. Keep concept mappings separate from requirement relations. No missing obligation or reporting-quality claims without independently established applicability and source completeness.

No new dependency or workflow. Existing focused tests are discoverable in ordinary CI; the archive replay requires the retained data. Rollback is removal of this independent advisory projection and receipt, without changes to existing contracts or canonical packs.
