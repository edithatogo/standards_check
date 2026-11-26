# Synthetic compact-model placement — 26 November 2026

Development-only author-labelled controls; issue #158, T01.025/063–064 and T05.063; complementary to PR #182 (Poppler, existing grid fixture) and PR #183 (retained inference replay). Exact starting main d88f787ffd4647117bca4ca400cbb68d95197d40. No source rights, pack, equivalence, independent calibration or release gate changes.

## Reproduce

In a separate research environment, not production dependency installation: Python 3.13.5, Linux x86_64, scikit-learn 1.8.0, numpy 2.3.5, PyMuPDF 1.26.7, pdfplumber 0.11.9, reportlab 4.4.9, pytest 9.0.2. Record full dependency lock and licences before hosted promotion. PyMuPDF licensing requires separate review before any deployment. No downloaded model weights or external inference. This is not the maintained repository pdfplumber version 0.11.11.

```sh
cd research/model-placement
python -m pytest -q test_synthetic.py
python synthetic.py --output /path/to/run
```

Local RED (missing module), GREEN 2 focused tests passed; full executed synthetic receipt and rendered first page generated. Exact script blob fadc890b21125909caa8f48019e3f159ce7140b9, script SHA256 daf852956be1fbef1d62549e260eb7f4b7c4eda41f2ccd38a5e989cf3d35cbfd; generated PDF SHA256 02ff1c437ab1b0cd034cae94b71463a5f49bdf664e12777cd56969765e69fcca; receipt SHA256 4e91d4648d50b843000c23838494479a4b176f6898c94b86ace0e72c41743bf5 (includes variable resource observations). Linux process wall 0.755539 s, peak RSS 207516 KiB, model download 0 B. Not per-arm resource isolation. All predictions, region boxes, span offsets, family partitions, reference and candidate identities retained by the executable receipt. No third-party guideline wording.

## Design and results

Six family-labelled synthetic controls, not independent guideline families. PRISMA/CHEERS development, CONSORT/STARD/ARRIVE/TRIPOD held out; exact actor/condition/exception offsets and source row/footnote references authored before the run. Small templates share structure; no claim of natural generalization. Linear classifiers and eight-dimensional LSA fit only on development families. Graph is section membership and adjacent synthetic dependencies, not validated guideline graph. Lexical comparator in this new fixture is development-fitted char TF-IDF, not live BGE. Historical five-class and BGE comparisons are in #183.

| Layout reader/placement | Exact nested-ID rows | Footnotes | Co-extracted body/note pairs (not links) |
| --- | ---: | ---: | ---: |
| pdfplumber whole-page text | 0/36 | 36/36 | 0/36 |
| PyMuPDF whole-page sorted | 0/36 | 36/36 | 0/36 |
| PyMuPDF detected rectangle crops | 36/36 | 36/36 | 36/36 |

Known drawn boxes, both columns and explicit synthetic footnote identifiers. The paired-presence metric uses each authored reference only to check whether the body and its expected note were both extracted. No reader predicts an association here. Qualifier linkage is unmeasured, not 36/36 recovered links. This is a bounded geometry/co-extraction control, not scan/OCR, parent hierarchy reconstruction, TEDS, or real issuer qualification. Use the independent explicit-marker edge endpoint from #182 separately; test wrong-owner, duplicate and ambiguous-marker controls on independently annotated pages before any linkage claim.

| Exact held-out span | Rules TP/FP/FN | Linear tagger TP/FP/FN |
| --- | --- | --- |
| actor | 48/0/0 | 42/0/6 |
| condition | 24/0/24 | 25/9/23 |
| exception | 40/0/8 | 48/0/0 |

Rule F1 100.0/66.7/90.9%; model 93.3/61.0/100.0%. No wholesale replacement; exceptions are a candidate supplemental signal. Tagging enriches retrieval and supplies typed evidence verification. Separate tag-free vs tagged pair classifier ablation and independently annotated natural spans still outstanding.

| Held-out retrieval | Hit@1 /24 | Hit@3 /24 | Candidates |
| --- | ---: | ---: | ---: |
| lexical | 24 | 24 | 72 |
| tag enrichment | 24 | 24 | 72 |
| graph simple | 23 | 24 | 72 |
| graph diffusion | 24 | 24 | 72 |
| graph simple rerank | 23 | 24 | 72 |
| graph-feature rerank | 24 | 24 | 72 |
| dense LSA | 23 | 24 | 72 |
| lexical+dense RRF | 23 | 24 | 72 |
| learned reranker lexical pool | 24 | 24 | 72 |
| learned reranker fused pool | 24 | 24 | 72 |
| combination tag+graph | 24 | 24 | 72 |

The perfect baseline creates a ceiling; no demonstrated incremental retrieval benefit. Fixed pool checks for reranking. The learned ranker and atom classifiers are binary synthetic feasibility controls, not substitutes for five-class NLI. Direct equivalent decision: 21/24 TP, 0/120 FP, 3 FN; separate actor/condition/exception/action judgments compiled by conjunction: 7 TP, 0 FP, 17 FN. No evidence for hard atom agreement. Second retrieval: first one 24/24 correct; both fixed and score-triggered extra candidate allocations 24/24 at 48 candidates, no gain. Score abstention 21/24, 3 withheld, no unsupported top-one accepted on this easy fixture.

| Verifier placement | Valid accepted | Invalid accepted | Valid withheld |
| --- | ---: | ---: | ---: |
| exact claim anchor | 144/144 | 144/288 | 0 |
| exact+typed span role | 115/144 | 0/288 | 29 |
| relationship+exact cited anchor | 21/24 | 21/264 | 3 |
| relationship+typed cited role | 7/24 | 0/264 | 17 |

Unsupported citation acceptance (correct substring, wrong role) is distinct from false equivalence. Exact-anchor checks are necessary and not semantic validation. Typed checks improve rejection with major coverage loss; only review/escalation candidate. This is no proof of semantic sufficiency.

## Remaining

The local git transport failed DNS; no GLiNER, Granite-Docling, pretrained GNN or new neural reranking weights acquired. The classical alternatives actually ran. Keep independent source rights/annotation, harder family-disjoint retrieval, first-pass frozen budgets, genuine cross-reference graph, full relation classes, separate learned evidence sufficiency, exact per-arm CPU/RSS/model byte receipts and hosted exact-head qualification outstanding. Add only opt-in runners, after maintained checks; no routine network, new dependency or acceptance bypass. Retain original negative results, not just the favorable cells.


## Exception-specific stress and verifier-placement follow-up (26 November)

Executed fresh local fit using original development partition, plus 32 newly
authored synthetic cases (24 exception present, eight absent, four family-labelled
groups). Same original model, no evaluation cases supplied for training.
An exploratory expanded regex adds explicit surface cues excluding, other than,
but not, outside and semicolon boundaries. Its design shares the vocabulary
of the authored challenge: not an independent reference or evidence of
generalisation. Missing-only learned fallback does not overwrite any rule span.
No automatic acceptance or release changes.

```sh
cd research/model-placement
python -m pytest -q test_tagging_followup.py
python tagging_followup.py --output tagging-receipt.json
```

RED missing module; GREEN two tests passed. Actual run wall 0.181836 s, peak
161300 KiB RSS, no model download. Same local research environment as above.
Receipt SHA-256 3edbf13d6b98165f131a7be4bf06d3ccdf232ae244f66ae06a6f22b60f839387
(includes non-deterministic timing/resource observations). Exact per-case
spans, review flags, family summaries, paired gains and losses regenerable.

| Method | Original exceptions TP/48 | Stress TP/24 | Stress FP | Stress FN | Stress F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original rules | 40 | 4 | 4 | 20 | 25.0% |
| Compact learned | 48 | 0 | 23 | 24 | 0.0% |
| Missing-only learned fallback | 48 | 4 | 26 | 20 | 14.8% |
| Expanded rules | 48 | 24 | 0 | 0 | 100% |
| Expanded rules + fallback | 48 | 24 | 8 | 0 | 85.7% |

Original rule omissions recovered by expanded surface rules; learned tagger
fails on all new exact exception boundaries. Expanded+learned introduces
eight spurious exception claims on absence controls. The 100% regex result
is a cue-matched ceiling on these authored examples, not external validity.
No adoption of a learned exception fallback. Further challenge implicit
exceptions, cue polysemy, nested and cross-sentence scopes, independent span
references before promoting any rule expansion.

Typed verifier follow-up on original 432 claims (144 valid, 288 invalid):

| Review flag method | Invalid flagged | Valid flagged |
| --- | ---: | ---: |
| Exact anchor only | 144 | 0 |
| Rule-typed | 288 | 32 |
| Learned typed | 288 | 29 |
| Rule-typed + missing-only learned exception fallback | 288 | 24 |

The hybrid reduces unnecessary flags by five vs the learned verifier and
eight vs rule-typed on the original controls; all 288 invalid claims flagged.
This does not override the new negative stress result. Keep hybrid as an
experimental review-prioritisation signal only, not an automatic rejection
or authorisation rule. Need harder mixed-validity and natural citation
judgments and fresh pretrained tagging before scientific qualification.


## Hosted E10 operator completion and E11 heading context — retrospective replay

Reused downloaded, hash-verified synthetic hosted artifacts. No fresh inference in
these two replays, no model downloads, no independent source labels or production
admission. All four new source and test blobs match locally executed files.
Six focused tests passed; graph replay RED was missing-module before implementation.
Use existing interpreter and lexical helper; local isolated overlay, not a full checkout.

### E10: preserve operators without treating overlap as correctness

Run [45795503022](https://github.com/edithatogo/standards_check/actions/runs/45795503022),
artifact [15105041814](https://github.com/edithatogo/standards_check/actions/runs/45795503022/artifacts/15105041814),
ZIP SHA-256 5ad26ba90e3aefb2d2fbc28011f73762723acf7774c9dff1cbb7bfe4aa7a57fb.
Tested merge a694942dcf98a3302a022c29c3c6941560d0a68b.
Both retained model and rule results use identical 16 cases and 17 gold spans.
Complete a learned span only to a uniquely enclosing same-type rule span;
guarded completion discards unsupported spans. Union preserves distinct spans.
Use exact typed offsets and maximum one-to-one typed positive-character overlap
as separate metrics; do not use reference spans in completion.

| Arm | Exact TP/FP/FN | Exact F1 | Overlap F1 |
| --- | --- | ---: | ---: |
| Rules | 14/2/3 | .8485 | .9091 |
| GLiNER2.5-small | 1/6/16 | .0833 | .3333 |
| Completed | 4/3/13 | .3333 | .3333 |
| Guarded | 4/0/13 | .3810 | .3810 |
| Rule union raw | 14/8/3 | .7179 | .7692 |
| Rule union completed | 14/5/3 | .7778 | .8333 |

No new exact gold span beyond rules in any arm. Guarded completion retains four
exact spans, drops ten rule-correct spans and has twelve empty-output cases.
Do not promote either learned union. Next: independently framed extraction
tasks and independently held-out source references, not a larger checkpoint
selected on these exposed examples. Local replay wall .0078 s; 96,396 KiB RSS.
Receipt SHA-256 6e0604cd461709955c6b72fa3c351ab6cae6d1d2e7f847265d804d92138b0a58
includes runtime observations.

### E11: simpler heading-context comparator and fixed-pool placement

Run [45795402697](https://github.com/edithatogo/standards_check/actions/runs/45795402697),
artifact [15103968915](https://github.com/edithatogo/standards_check/actions/runs/45795402697/artifacts/15103968915),
ZIP SHA-256 f3f106a3b8855eaf8d464fe638a15476327ee9d94411c445e52e3768fff05df2.
Tested merge 7c48bc6f1c71ddd953808c35ce95d2d314004610.
Use the exact #187 fixture (SHA-256
4aa25eb689a62a7b2758e19d6821f09708563a0d0c627c91b102cd84a3ca066d):
25 targets, 10 queries, 17 reference associations. Recompute every baseline
lexical score and confirm exact identity against the artifact. Compare parent-only
field bonus, complete graph and simple heading-prepended text with the unchanged
word/bigram and char-trigram lexical method. No weight fitting. For each, test
candidate generation across the full universe and fixed-pool reranking of the
original top ten; retain per-family and query-level scores, paired hits, gains,
losses and candidate counts at 1/3/5/10.

| Arm | Word R@5 / hits | Char R@5 / hits |
| --- | --- | --- |
| Incumbent lexical | .90 / 15 | .90 / 15 |
| Parent generation | 1.00 / 17 | .95 / 16 |
| Full graph generation | 1.00 / 17 | .95 / 16 |
| Heading text generation | 1.00 / 17 | 1.00 / 17 |
| Parent fixed pool | 1.00 / 17 | .95 / 16 |
| Full graph fixed pool | 1.00 / 17 | .95 / 16 |
| Heading text fixed pool | 1.00 / 17 | .95 / 16 |

Heading-text generation gains two and loses zero associations at five for both
methods. Character R@10 is .95 for every fixed-pool arm and 1.00 for all three
generation arms; one additional association requires changing the pool.
The parent signal suffices for the observed full-graph R@5 gain. Heading
concatenation is the simpler comparator and should precede any graph model;
structural edges remain useful for source provenance, not automatic semantic
equivalence. This small exposed fixture is not a general performance conclusion.
The #187 edge-type factorial and rewired control remain separate.
Actual replay wall .0160 s, peak RSS 97,040 KiB. Receipt SHA-256
d7fbc4c805eb31f67fbbf2a7d1aee7aea4317626c59b28895f943075a4a991d2
includes runtime observations.

Reproduce from repository root with exact artifacts downloaded by ID, plus
the exact #187 fixture obtained from that branch:

```sh
PYTHONPATH=. python -m pytest -q research/model-placement/test_qualifier_replay.py research/model-placement/test_graph_context_replay.py
PYTHONPATH=. python research/model-placement/qualifier_replay.py --artifact /path/to/github-actions-artifact-15105041814.zip --output qualifier-replay.json
PYTHONPATH=. python research/model-placement/graph_context_replay.py --artifact /path/to/github-actions-artifact-15103968915.zip --fixture /path/to/graph-retrieval-v1.json --output graph-context-receipt.json
```

Reconciled receiving #182 main (08e86696180936ef6722e539a32d6ebbd2222625)
without replacing any existing Track 05 evidence or changing production
contracts. Full exact-head CI and offline security remain required.


## Shared recall coordination reconciliation — 26 November

Receiving main `776ed1dbfbe19d16365310ef0fa07d29a793611a` includes #187's
source-anchored graph and factorial ablations. The #185 experimental source,
fixture identities, exact previous receipts and negative findings remain unchanged.
The shared audit and its executable reference-bound stage join are owned solely
by [#183](https://github.com/edithatogo/standards_check/pull/183) under #158;
see its [verified full-checkout and handoff record](https://github.com/edithatogo/standards_check/blob/2cedd83859a3e697a8bfc1b8c3ebf951b2d14637/research/model-placement/replay.md#full-checkout-reproduction-and-locked-stage-handoff--26-november).
The coordinator imported the existing #185 heading-context results, rather
than rerunning this benchmark. Verified hosted audit run 45802682924
reproduced all 1186 included observations; the 68 local heading observations
are separately retained and explicitly absent from that hosted job. With
#189's 68 additional span outcomes the shared local audit has 1322 rows
on 175 distinct editorial/synthetic IDs, not independent positives.
Do not duplicate the audit, reference registry, graph, extraction or evidence
experiments. Next dependency is #188's actual source/rights/anchor-qualified
blinded family lock and same-case Offline/Orthogonal evidence. Existing
T05.049/T05.063 acceptance and #30 offline-security hold remain open.
This reconciliation is documentation and current-main ancestry only;
new exact-head checks required, no new inference or promotion.


## Shared recall integration receiving reconciliation

PR #183 merged through normal active branch protection as
[413626c44da6d5d5faaa19a60f4d7ae0751f1fb7](https://github.com/edithatogo/standards_check/commit/413626c44da6d5d5faaa19a60f4d7ae0751f1fb7)
after all seven required contexts, CodeQL and three component coverage uploads
passed on head 2cedd83859a3e697a8bfc1b8c3ebf951b2d14637. Receiving tree
6e9cfa541eafaca1fa737597c40c3cce925d8941 equals tested head/merge tree.
The extended [audit 45804985347](https://github.com/edithatogo/standards_check/actions/runs/45804985347/artifacts/15109472517)
passed 12 hosted focused tests; archive SHA-256
020834bdbb13f84e8e0f2e024b8bc446d136791a7b545b7da23cf43e2909fc8e.
All 1186 prior hosted observations unchanged; 68 imported #189 observations
give 1254 hosted rows on unchanged 175 reference IDs. #185's 68 local heading
observations remain separate. Zero independent positives. Offline security
execution remains separately queued under #30; no change to protection.
Reconcile this branch with receiving main by merging its exact ancestry and
preserving all previously tested experimental source and test blobs. Prior
#185 head a64b561fd991029c51fb547666b9fcb84e8c45a4 passed all seven required
contexts and Codecov patch/component checks; fresh exact-head checks required
on the receiving reconciliation. No fresh inference or duplicate benchmark.

Latest #188 structural source receipt
[45805487210 / 15109287625](https://github.com/edithatogo/standards_check/actions/runs/45805487210/artifacts/15109287625),
verified SHA-256 5091c91a02ecc2b0cef641fb1efda4442c678cfd580af1f423b09841e234d9da:
CONSORT and SPIRIT exact printed IDs 42/42 and 53/53; cross-format exact
normalized text 41/42 and 53/53; CONSORT item 26 differs. Non-body part and
issuer identity holds remain for both, numbering unresolved for CONSORT.
Both remain held in one conservative family component. No independent
reference lock, no same-ID downstream scientific evidence and no pipeline
adoption. Layout retains source, rights and blinded adjudication; Offline
and Orthogonal retain their stage evidence. Shared join now lives on main
under the existing #158/T01.064/T05.063 convention.


## Review correction: co-extraction is not qualifier linkage

Normal protected merge of prior head c775cb4257310a2a7d6a299d9e9881ac2d81df80 was rejected (405:
unresolved conversation) despite all seven required checks, CodeQL and
Codecov patch/component success. Review comment 4707523186 correctly
identified reference-driven pairing: both expected strings appearing in
the extracted chunks does not establish that the extractor linked them.
Rename the metric and per-row field to co_extracted_body_note_pairs and
body_and_note_present, respectively, with qualifier_linkage_measured=false.
Do not add a second linkage implementation competing with Layout/#182.
Correct the table and interpretation above; preserve historical receipts
and the actual original failure/limitations. No numerical change to
the co-presence observations and no claim of recovered link accuracy.

RED: new actual-layout regression failed with KeyError for missing
qualifier_linkage_measured. GREEN: three focused layout/fixture tests
passed; all eleven #185 isolated tests passed. Exact local/remote Git blobs:
synthetic.py 32abd5c6303c2cca1980706818cc5083896264a4;
test_synthetic.py fcf2721c231520883ce91c390df88eec8fc1a4e9.
Regenerate the same synthetic pages and extract the actual three reader
arms; all per-case references, boxes, extracted-row/footnote flags and
renamed co-presence results equal the historical layout member.
Corrected layout-only receipt SHA-256
9c168ef6516136bfd274d6dc64df3a7d7782e1d05de9aa475477ba85f8ec3b5b.
The regenerated scoring PDF SHA-256
cc80a2bc63d4d994373a41fd1ae70ee205bbbcb6285cb034e4868840561c383c
matches the PDF hash *inside* the original synthetic receipt
(4e91d4648d50b843000c23838494479a4b176f6898c94b86ace0e72c41743bf5).
The separately archived illustrative PDF hash 02ff1c437ab1b0cd034cae94b71463a5f49bdf664e12777cd56969765e69fcca
does not match the original scoring member; retain it as illustration,
not the byte-exact scoring input. The corrected regeneration is the
actual input matching the historical score receipt. No fresh model inference.
Fresh exact-head checks required after this real measurement correction.

## Corpus-wide coverage and incremental research priorities

Cross-workstream coordinator under existing #158/T01.064/T05.063; do not
duplicate Layout intake, Offline evidence replay or Orthogonal verification.
Read complete main tree at 413626c44da6d5d5faaa19a60f4d7ae0751f1fb7 (1941 tree entries,
one packs/.../pack.json, org.prisma/prisma/2020); catalogue denominator
is not a canonical pack denominator or a software-coverage metric.
Use only the existing exact hash-verified receipts:

- Priority replay 45802602832 artifact 15108328164, ZIP SHA-256
  e442a484cd20abd396d40c2dde03e7c0e5e10af327bd69522a21876d086a5e53:
  catalogue-coverage.json, all 720 distinct catalogue identities.
- Bulk checkpoint 45802629341 artifact 15107508921, ZIP SHA-256
  be0c2221b737042d0bb4656d1f1f4145324dbaf820112b1e366ba7f402e8676a:
  pack-evidence-inventory.json and equator-article-survey.json.
- Extended shared audit 45804985347 artifact 15109472517, ZIP SHA-256
  020834bdbb13f84e8e0f2e024b8bc446d136791a7b545b7da23cf43e2909fc8e:
  recall-audit.json full rankings, not a selected success subset.

Actual bounded local read-only projection of these three receipts:
corpus-diagnostic.json SHA-256
098cd04ebdc7a5dd77f33a77e627fe183decbdc23c0268a6e2adce9e4549ce11.
No new reference labels, inference, dependency, source acquisition or
promotion. All source/eligible query/target denominators checked.
Catalogue 719 metadata-extracted/unverified, 317 source-link candidates,
209 OA XML candidates, 115 both, 16 legacy-original candidates.
Union of those three candidate routes 411; 309 with none (also neither
link nor OA XML candidate). 76 missing publication identifiers, of which
70 have source-link candidates and 7 legacy original candidates;
56 incomplete lookups, of which 49 have source links. Rights not
recorded 132, unassessed article/table reuse 588. End-to-end qualified
from catalogue receipts zero. Do not interpret absence of an observed
link as absence of an obtainable or lawful source. Preserve all 720 IDs
and report availability/rights/qualification states separately.
205 bulk worklist IDs, 200 deferred, 4 held, 1 inventory observed/unreconciled.
Study-type categories overlap (1253 memberships, not 1253 guidelines).

| Study type | Entries | OA XML candidates |
| --- | ---: | ---: |
| Mixed methods | 21 | 11 |
| Economic evaluations | 30 | 12 |
| Observational studies | 244 | 92 |
| Clinical trials | 254 | 83 |
| Systematic reviews/Meta-analyses/Reviews | 67 | 18 |
| No study design specified | 131 | 21 |
| Reliability/Agreement | 4 | 0 |

All strata retained in the local projection, including AI/ML and unclassified;
do not choose independent evaluation from ease of XML acquisition alone.
The inventory certificate concerns all 42 PRISMA declared parent items,
not independent semantic/clause or manuscript references. 35/42 declare
multiple evidence kinds; 17 Methods, 11 Results, 6 Other information,
4 Discussion, 2 Introduction, Title and Abstract one each. Document
span all 42; synthesis plan six, synthesis results four, outcome
catalogue three, registration identifier three, other structured
types retained. One explicit source cross-reference in this inventory.
Masked source-identity recovery word R@1 41/42 (20d at rank two),
char 42/42; both R@3 and R@5 42/42. Identity/near-copy ceiling,
not semantic recall or satisfaction. Multiple declared kinds do not
prove each kind mandatory; applicability/bundle references need independent
adjudication. Use Orthogonal and Offline typed bundles and owner receipts.

Full ranking depth diagnostic, exactly 106 queries, 125 editorial known
positives, 31 targets. For k in 1,3,5,10,15,20,31, intersect known positive
IDs with each arm's order[:k] and sum paired set differences vs BGE.
Equal k across arms; 106*k candidate slots, no actual review/compute parity
or adjudicated negatives. Association micro counts below (not macro R@k).

| k | Slots | BGE | Qwen+BGE | Exact lexical | Parent-topic proxy | Fusion gains/losses |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 106 | 41 | 47 | 37 | 43 | 10/4 |
| 3 | 318 | 70 | 79 | 55 | 60 | 15/6 |
| 5 | 530 | 87 | 93 | 63 | 66 | 8/2 |
| 10 | 1060 | 97 | 104 | 81 | 77 | 10/3 |
| 15 | 1590 | 110 | 115 | 92 | 90 | 7/2 |
| 20 | 2120 | 118 | 119 | 102 | 100 | 3/2 |
| 31 | 3286 | 125 | 125 | 125 | 125 | 0/0 |

A wider pool reduces the fusion advantage to one known association at 20.
Do not equate full enumeration with an operational equal-review-budget
decision or assume unknown positives are negatives. At matched 10/5
budgets, prior instrument/domain analysis in #158 comment 7190469008
retains all 125 associations; improvement heterogeneous, including iDSI
pool regression and GHCC review regression. Results-disaggregation 0/3
and diagnostic-pathway 16/20 at ten in both dense arms. No model choice
or per-instrument tuning on these exposed observations. Scientific
false-equivalence/unsupported-discharge risk not estimable from this
positive-only seed. Retain independently labelled negative and unknown
pairs and real referral resolutions in confirmatory evaluation.

### Change priorities and conditional fine-tuning

1. Layout/#188/#95/#111/T01.052: use actual source-link/issuer candidates
   for missing DOI/PMID cases; no universal identifier gate before
   issuer-source observation, no rights or edition shortcut. Keep
   source-unavailable/rights-held, anchor/structural loss, and unmeasured
   downstream outcomes distinct. Report whole-catalogue attrition and
   study-type/format/edition missingness, not convenience-sample accuracy.
   Include distinct-family and hard structural cases, not only easy OA XML.
   CONSORT/SPIRIT share one provisional component; item 26 and non-body,
   numbering and issuer/rights holds still unresolved. No new source parser
   or parallel acquisition in this lane.
2. T01.064: preserve full candidate-universe oracle diagnostic; compare
   native exact clause, heading text, typed evidence/explicit links and
   instructed Qwen+BGE against BGE. Predeclare label-blind variable-depth
   policies at the same total candidate, acquisition, review and compute
   budgets. Hold review cutoff independently of pool size; preserve missed
   and uniquely recovered positives, regressions and common failures.
   Reuse #185 heading-text and #183 MiniLM R@5 negative control, no new
   reranker scale sweep. Do not tune weights, cutoffs or routing on this
   retained costing reference.
3. T01.027/T01.063/T05.063: if qualified independent development-family
   residuals justify it, compare compact supervised boundary/typed-span
   or contrastive embedding fine-tuning to strong deterministic/native
   and pretrained baselines. Hard negatives include shared topic but
   different methods/results, population/denominator, scope, trigger,
   operator, exception and directional parent/component; no identity
   copies or near-duplicate co-publications across folds. Require exact
   boundaries and wrong-owner link controls, unique gains and regression
   counts; include implicit/nested/cross-sentence qualifiers. Do not
   fine-tune on exposed editorial or synthetic evaluation cases.
   Freeze model/runtime/assets, training/negative construction, hyperparameter
   selection, calibration and final evaluation by family component. Test
   fine-tuned vs base and simple comparator on untouched families; only
   continue where incremental benefit is supported at matched costs.
4. Offline/#184 and Orthogonal/#180: preserve explicit evidence-bundle
   coverage, verified applicability/direction, unknown vs negative vs
   referral resolution; 35 multi-kind declared PRISMA items motivate
   multi-component evidence challenges, not a reference shortcut. Assess
   both missed true matches and false equivalence/unsupported discharge;
   proof-related abstention and incomplete evidence are separate stages.
   No source-only evidence credit for manuscript satisfaction.
5. T05.049/T05.063: after actual qualified blinded source-only reference
   lock, run all eligible cases in family-component-disjoint folds.
   Separate metadata/source eligibility and reference denominator from
   downstream successes. Predeclare paired family-macro and association
   recall, uncertainty clustered by family, coverage, selective risk,
   false equivalence, unsupported discharge, workload and resource
   endpoints; strata by study design, format, requirement complexity,
   explicit/implicit qualifiers, evidence kind and family, with sparse
   or empty denominators explicit. Do not infer population significance
   from overlapping strata or same-source identity recovery.
   Set material gains/harm noninferiority limits prospectively with
   reference sample precision; no per-stratum threshold fishing.
   Use the existing locked_join on identical opaque IDs. No full factorial
   or adoption until component value and scientific gates qualify.

Receiving main remains 413626c44da6d5d5faaa19a60f4d7ae0751f1fb7 at this review correction.
#185 protection requires fresh checks and genuine review resolution.
Reference lock has not been received; independent same-ID joins, scientific
confirmation, pipeline changes and release remain held. No new registry,
canonical schema, external submission, model acquisition or gate relaxation.
