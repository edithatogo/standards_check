# Catalogue classification and ontology addendum — snapshot 2

Status: exploratory. Supplements the immutable [first results](results-v1.md)
rather than replacing them. See [snapshot 2 receipt](snapshot-v2-receipt.json),
[inputs](inputs-v2.tsv), and [projections](panels-v2.tsv). Exact same compiler
and first 2,317 comparison records conserved; 74 original inputs, 99 distinct
panel labels and 3,087 numeric/null metrics. Seven new retained input files
and 20 new projection rules; no pooling incompatible panels. Full archive
and report tables retained in the user's personal Library, not publicly
redistributed. Replay is idempotent. This is not a new scientific freeze.

## S6. Catalogue-relative classification

Historical EQUATOR metadata: 720 identities, 719 titles, 16 study types,
45 clinical areas and 26 report-section labels. Five proxy identity-grouped
folds, not independently qualified families. Report per-facet denominators:
582 known study-type rows (1,099 associations), 412 clinical (637), 706 section
(1,343). Missing/unspecified/Other are not evaluated as concrete positives.

The 12 word/character x binary/count/TF-IDF x full/32D LSA arms and prevalence
control from merged #194 have their original complete predictions retained.
Full character TF-IDF R@3 .7495/.5462/.6379 versus prevalence
.6407/.1955/.6205; title-only report section is difficult, and prevalence
wins at K=5 on this facet. Shared positives missed by all 12 arms:
120 study type, 198 specialty, 275 report section; these are not
independently ascertained errors.

The matched six-arm follow-up (#195) restricts all methods to known-label
training rows per facet; weak negatives for logistic are not verified
absences. Exact original 719 assignments and fold digest conserved.

| Representation / classifier | Macro R@3 study | Clinical | Report section |
| --- | ---: | ---: | ---: |
| Word / kNN | .7503 | .4612 | .6136 |
| Word / logistic | .6561 | .3464 | .6597 |
| Word / balanced | .8134 | .5132 | .6644 |
| Character / kNN | .7663 | .5836 | .6366 |
| Character / logistic | .6714 | .4115 | .6693 |
| Character / balanced | .8124 | .5875 | .6761 |

Matched char balanced vs char kNN gains/losses 117/52 study, 63/56 clinical,
227/119 section; shared misses 176/236/480. Preserve case-level decisions,
per-label metrics and actual times. Class balancing influences the measured
representation effect; factor the classifier instead of selecting a
confounded embedding/model. No generalisable superiority claim.

## S7. Role and ontology candidates

Original #193 graph: 219 titles with a selected dictionary topic,
259 spans, 120 additional MeSH ancestor associations. Contextual cue audit
on the 259 title spans: 52 target candidates, one development candidate,
206 unresolved. One of 40 direct novel category associations has an explicit
target cue; other associations are not disproved. No classification
acceptance or measured role precision follows. Actual contextual neural
NER and independent role/span labels remain required.

The [v2 typed crosswalk](../catalogue/mesh-facet-candidates-v2.json)
retains all prior v1 candidates and verifies the ten previously
out-of-inventory MeSH descriptor identities against the NLM 2026
descriptor browser. Six additional observed descriptors provide related
topic leads for reliability, ethics/consent, conflict, funding and outcomes.
37 distinct MeSH descriptor IDs, no exactMatch or applicability claims.
DoCO and DEO source pins are exact upstream Git revisions and individual
class blobs. Ten separate structural edges (nine distinct section labels)
use candidate_document_component rather than subject-topic assertions.
Together with nine MeSH-covered section labels this gives 17 of 26
report-section labels with a candidate association; overlap is one label.
Study-type 13/16 and clinical 6/45 remain unchanged. Scope boundaries
remain explicit, including narrower topic and component coverage.
Unmapped labels are not negative evidence. No complete ontology freeze or
independent crosswalk accuracy claim.

## Pending inference and broader interpretation

The new explicit hosted BGE/Qwen matrix uses the exact catalogue, same
classifier choices and source/asset pins. First run 45836556902 stopped
before inference in both jobs because reconstruction of the prior folds
did not match their digest; all model asset hashes passed. Both original
failure archives and the v3 local report after repair are retained
separately and identified in the receipt. Immutable original fold
assignments now replace runtime-dependent recomputation in #195. Local
replay conserved all ranks and role outcomes, six focused tests and
16 overlay tests pass; hosted rerun and exact-head checks remain required.
Do not treat failure artifacts as a neural comparison or add them to
the current numeric table. Append them and subsequent real outcomes to
the next versioned snapshot.

The broader inference is that document scope, topical indexing, label
imbalance, representation and classifier choice are separable sources of
failure. A subject mention is not a governed design, and subject ontology
is not document anatomy. Preserve the citation/identity lane in #191,
source and independent reference qualification in #188, and shared
failure audit. Later test source-anchored contextual roles, neural embedding,
MeSH/DoCO/DEO and citation contribution independently on shared locked
inputs, then evaluate multicriterion choice using observed costs and
safety. No graph database or additional framework justified yet.
