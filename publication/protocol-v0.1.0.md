# StandardFlow prospective evaluation protocol 0.1.0

**Draft for owner review; not registered or approved.** Issue #158. Historical
observations in the evidence ledger are exploratory and precede this protocol;
do not reclassify them as prespecified validation. Amend by new version with
rationale/date before exposing the corresponding new holdout.

## Research questions and design

1. How much of the pinned published EQUATOR directory can be represented with
   traceable identities, complete anchored structure, exact source fidelity,
   explicit applicability and rights? Conduct a longitudinal full-directory
   census; unit of discovery is directory entry, of acquisition unique
   edition/artifact, of extraction source row/subitem and of analysis aligned
   requirement pair. Preserve the denominator, duplicates/aliases, versions,
   translations, non-checklist resources, missing/ambiguous sources and rights.
2. How much incremental error detection and useful coverage do independent
   readers, classical methods, dependency parsing, bidirectional NLI, formal
   constraints, decision models and blinded witness agents contribute?
3. Can two independent consumers reproduce the same versioned representation,
   identity/rights/status and deterministic projections without silently
   losing requirements? Separately test usability, evidence linking and
   accessibility. A reporting check is not study-quality appraisal.

## Corpus and prospective sampling

Use the existing read-only catalogue census and bounded resume workflow.
Freeze source revision, source/edition identity, byte digests, links, rights,
extraction logs and all held outcomes. Use all eligible sources for acquisition
and structural discrepancy discovery; no restriction to successful formats.
Independently reconstruct selected complete official tables/rows using distinct
engines and, where available, issuer-equivalent formats; distinguish common
source/layout bias. Freeze a family-disjoint development/validation/test split
before exposing labels or predictions; cluster editions/extensions/translations
in a family. Archive historical development pairs separately. For new
evaluation, sample natural source/candidate disagreements and randomly selected
apparently exact pairs, stratified by family, format, layout and error type;
include formal controls for all five relations with independently constructed
truth sets. Do not combine their denominators. Preregister feasible sample
size after actual eligible corpus counts and before examining test predictions;
report sparse strata, selection and attrition, with an explicit precision-based
sample size calculation for a primary error rate. No retrospective power
justification or arbitrary accuracy target.

## Index methods and independent reference

Use existing exact/fingerprint comparison, Unicode rules, spaCy dependency
reference, exact bounded truth sets and the existing #155 NLI/witness harness.
Pair sources in both directions. Freeze trusted assets, licences, hashes, label
maps, prompts, token/context bounds, runtime and seeds. Two isolated agents
receive opaque inputs, not algorithm predictions or one another's answers;
retain independent outputs, supporting spans, invalid/abstain and consensus
counts. Validate actual supporting evidence, not just offsets. Formal control
truth is independent of the judges; natural-pair consensus is fallible, not a
gold standard or substitute for external stakeholder/methodology review.

d1-2B is an orthogonal typed-decision/extraction pilot, **not** a replacement
contest. After licence/custom-code review, pin weight/config/tokenizer/runtime
and isolate execution. Ask forward/reverse implication, co-satisfiability,
applicability, quantitative/temporal/exception changes and exact source spans,
with unknown and not-found states. Compare against best retained baseline and
the same independent pairs: baseline misses detected, overlap/Jaccard of
errors, incremental correct flags, additional false alerts, selective risk
and coverage, common-mode misses, review burden, elapsed time, peak memory and
cost. An independently useful discrepancy or grounded span justifies retaining
an optional diagnostic even if standalone accuracy is lower. It may not
override a required gate. Larger DeBERTa and ModernBERT NLI variants remain
ordered challengers. No additional weights downloaded in ordinary CI.

## Outcomes and statistical analysis

Primary directory outcome: per-stage count/proportion of all pinned entries
and of explicitly eligible sources, with missing, deferred, conflict and held
reasons; count unique artifacts and representation-scoped rows separately.
Primary comparative outcome: paired material false-equivalence/error rates
and detection coverage for reference-labelled pairs. Report confusion matrices,
five-class macro and micro precision/recall/F1, directional errors, field-level
discrepancies, coverage/abstention, false alerts, span precision/recall,
per-family/format strata and incremental fixes/introduced errors. Use family-
cluster bootstrap intervals when sufficient independent clusters exist,
exact binomial descriptive intervals for bounded control strata, paired
discordance tests where applicable; do not treat correlated generated mutations
as independent subjects. Calibration on development only; Brier/log loss,
reliability and risk-coverage curves on untouched test data. Missing/invalid
model results remain held and count toward coverage denominators. Sensitivity
analyses: reference uncertainty, alternate alignment, conservative rights
exclusions, family/format weighting, costs, common-mode dependence. Predefine
policy operating point before holdout. Existing #155 witness gates unchanged.
Release analysis scripts, safe derived tables, exact receipt and code hashes,
not rights-unclear texts or private manuscripts.

## Bias, ethics and reproducibility

Evaluate publisher/format/English and licence selection, template correlation,
training overlap and agent disagreement. No human benchmark labelling requested;
do not invent independent human reviews. Seek ethics/governance determination
before any private manuscript, participant or user study. Record funding,
conflicts, contributor roles and AI tool/model/role/prompt provenance. ICMJE
requires accountable authors and AI-use disclosure:
https://www.icmje.org/recommendations/browse/artificial-intelligence/
External standard review, authorship and submissions require accountable owner
approval. No autonomous submission or claims of EQUATOR endorsement.
