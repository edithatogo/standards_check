# Catalogue vector representations, classification crosswalk and tool selection

Status: exploratory development, 26 November 2026. Extends merged #193 and T01.052/053/064.
No independent semantic reference, canonical applicability assertion, publication admission,
or full six-factor specialist execution. Preserve #191 bibliographic and #188 source ownership.

## Executed vector factorial

Historical 720-entry catalogue (archive 15031534787); 719 titles, 617 proxy groups.
Five deterministic grouped folds (144,144,144,144,143). Groups union exact DOI,
PMID, normalised titles and leading acronym stems; this is not a validated
family lock. Fit vocabulary, weighting and SVD on training folds only.
Compare word (1–2) vs character (3–5) n-grams, binary/count/TF-IDF weighting,
full vs 32-dimensional LSA, all 12 valid cells. Same cosine-weighted five-neighbour
classification and top 1/3/5 label budget per facet. Include training-fold label
prevalence without text. Every arm retains all 720 identities; missing, unspecified
and Other labels are not evaluated as concrete positives. These are catalogue-relative
positive recovery metrics, not true negative ascertainment or independent accuracy.
Report precision at fixed K (including unfilled slots), row-macro recall, micro recall
and per-label counts. No hyperparameter tuning or new neural inference.

| Facet | Eligible | Concrete associations | Macro R@3 prevalence | Word TF-IDF | Char TF-IDF | Char TF-IDF + LSA |
|---|---:|---:|---:|---:|---:|---:|
| Study type | 582 | 1099 | .6407 | .7348 | .7495 | .7008 |
| Clinical area | 412 | 637 | .1955 | .4303 | .5462 | .2724 |
| Report section | 706 | 1343 | .6205 | .6156 | .6379 | .5885 |

Char TF-IDF full has best row-macro R@3 in tested grid, but prevalence beats it
on report sections at K=5 (.7331 vs .7245). Char arm recorded .9295 seconds
for all five folds and all facets in a single local run; no repeated hardware-matched
cost claim. Do not claim the observed maxima generalise.

Hard positives missed by all 12 arms at K=3: 120/1099 study type, 198/637 clinical,
275/1343 report section. Best-char per-label recovery: reliability 0/4,
protocols 7/30, mixed methods 5/21, clinical practice guidelines 5/19,
qualitative 18/58, animal preclinical 10/24, diagnosis/prognosis/prediction 21/41;
ethical issues 0/24, results 5/70, study characteristics 24/119.
Sparse specialty and report-section labels are particularly difficult from titles;
missing evidence, imbalance, label ambiguity and scope must be separated from
ranking error. Keep failures and denominators. Existing #183 shared missed-match
audit owns stage-level joins: do not create a second incompatible failure registry.

## Typed graph and citation triangulation

Keep the #193 catalogue -> mention -> MeSH graph. Candidate facet crosswalk has
13/16 study types, 6/45 clinical areas and 5/26 report sections; every unmatched
label remains explicit. These are related/broader/narrower topic leads, not exact
mappings. The selected MeSH browser records do not constitute a frozen ontology
snapshot. No comprehensive official crosswalk established in the limited search.
Separate MeSH descriptor topics and publication types. Consider OBI for study
design and experimental processes, EDAM for data and computational methods,
and CiTO for citation relations; reuse existing ontology assertion contracts
and qualify ontology versions, licences and direction before promotion.

Observed cross-facet co-occurrence: study/clinical 320 eligible rows, 233 unique
label-pair edges; study/section 573,205; clinical/section 408,388. The 826 edges
carry support, directional conditional frequency and Jaccard on the both-known
denominator. This is empirical association, not semantic hierarchy or causality.

The bounded citation triangulation receipt includes three exact primary-paper
PubMed records (CONSORT 2025, ARRIVE 2.0, PRISMA 2020), their observed indexed
MeSH labels and role distinctions, and five source-supported guidance relationships.
Wrong/missing identity lookups are rejected, not silently linked. CONSORT has
trial-reporting scope and Delphi/scoping-review development methods; treating
the latter as governed study designs would be a classification error.
A citation indicates a relationship, not endorsement, applicability or equivalence.
Link original and updated editions, explanation papers, references and citing works
through #191 Searchright integration; do not bypass its current holds. Separate
issuer statements, NLM indexing, exact mention spans, contextual roles and
bibliographic evidence. Test direct references, bibliographic coupling and
co-citation independently, normalising for age, popularity and co-publication.
Only train/test with family and temporal separation; no future citation leakage.
Use citation contexts to distinguish derivation, extension, method, example,
background and criticism. Source rights/identity, source role and independently
anchored reference precede any accepted mapping.

## Next experiments: representation factor and information extraction

Do not replace the existing 64-cell factorial with every possible incompatible
cross-product. Treat representation as a categorical factor nested within retrieval
at first; full valid crossed design within a common qualified stratum. Freeze
input field (title, title+abstract, source-anchored item/context), representation,
query formulation, similarity, dimensions, candidate budget, optional graph and
rank stage, and gold relation type. Compare sparse binary/count/TF-IDF/BM25,
dense BGE-small and Qwen3-Embedding-0.6B first on identical IDs/folds; reuse
existing pins/runtime and full scoring receipts. Include word/character and
instruction variants, then compression/dimension and quantisation on the same
model with paired quality, memory/latency. The earlier costing editorial panel
(106 queries,125 positives) has BGE R@5 .7201 and instructed Qwen+BGE .7626;
BGE with MiniLM reranking .6824. This is a distinct historical neural panel,
not a catalogue-title embedding result. No fresh catalogue neural inference yet.
If residual misses justify it, qualify multi-vector/learned sparse BGE-M3,
citation-informed SPECTER2 (explicit citation leakage control), and biomedical
entity-linking representations such as SapBERT. Preserve all failed attempts.
Never convert representation scores into accepted obligation equivalence.

NER should predict exact spans and link to versioned concepts. Distinguish
target study, guideline development method, illustrative example, cited
background, methodological construct, governed output, actor, condition,
exception and scope. Test dictionary, contextual role tagging, entity linking,
and typed graph propagation separately; use independently annotated offsets
and roles, negative controls and abstention. Earlier GLiNER qualifier experiment
is not evidence on this new task. Use cross-facet labels as auxiliary evidence,
not gold. Test graph traversal/embedding only after measuring residual direct
retrieval misses; no graph database or new production dependency now (Ponytail).
No citation or ontology inference should close gaps by itself.

## Noncompensatory multicriterion decision framework

First gate source rights, admissible input/role, reference qualification,
privacy/security, exact executable pin and unsupported inference. Missing
hard evidence means hold; no weighted score can compensate. Then compare
matched task, denominator, resource budget and risk. This increment calculates
per-facet Pareto frontiers on row-macro R@3, P@3, equal-label macro R@3 and
observed elapsed seconds. Missing measurements are unranked. The full evidence
report contains each criterion; all production_eligible lists empty.
Char TF-IDF full and word count/TF-IDF full appear on all three frontiers;
char count full additionally on study-type and report-section frontiers.
The prevalence control has no comparable recorded timing and is not ranked
in timed Pareto. Resource seconds represent all facets, not isolated task cost.
Sensitivity to weights/budget, repeated costs, uncertainty, actual reviewer
burden, coverage and risk come before deployment. For retrieval require
candidate recall; for exact structure/identity prefer deterministic tools;
for qualifiers require role-specific span evaluation; for equivalence require
proof/anchored admissible evidence, not model confidence. Do not introduce
RL or universal composite ranking without demonstrated headroom.

## Reproduction and retention

Run the versioned optional research scripts with NumPy 2.3.5 and scikit-learn
1.8.0, not a maintained application dependency. Full exact reports retained
in the user's access-controlled Library. Receipt binds archive, scripts,
crosswalk and reports; new runs with different timing or inputs require new
report identity. Five local focused tests passed; no full checkout/hosted result
claimed. Add this receipt to the next content-addressed snapshot under #192
without replacing prior supplement. E9–E14 prospective and independent
reference/release holds remain unchanged.

```sh
python -m research.catalogue.vector_classification --artifact /path/to/archive.zip --output vector.json
python -m research.catalogue.tool_selection --report vector.json --report-sha256 <actual-hash> --archive /path/to/archive.zip --crosswalk research/catalogue/mesh-facet-candidates-v1.json --output selection.json
python -m pytest --import-mode=importlib -q tests/test_vector_classification.py tests/test_tool_selection.py
```
