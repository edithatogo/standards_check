# Orthogonal qualification increment — 26 November 2026

Base: receiving main `06d88189f4015bbefd3ff0ca595a1f9107477599` from PR #177.
All seven required check contexts on this base passed, including
[receiving Assurance 45767621591](https://github.com/edithatogo/standards_check/actions/runs/45767621591),
[CodeQL 45767621198](https://github.com/edithatogo/standards_check/actions/runs/45767621198),
[dependency inventories 45767621706](https://github.com/edithatogo/standards_check/actions/runs/45767621706)
and [privacy 45767621668](https://github.com/edithatogo/standards_check/actions/runs/45767621668).
The earlier failed checks remain in [the historical receipt](orthogonal-verification-20261126.md).
This increment reuses the same eight tasks and issue owners, not a parallel registry.

## Implementation and evidence boundaries

| Existing task | New executable increment | Remaining gate |
| --- | --- | --- |
| T01.060 | Calibration-only threshold selection, disjoint case/family checks and simultaneous one-sided family-level risk bounds in selective_risk.py | Actual independently adjudicated source families, independent score/reference freeze, sampling/shift qualification |
| T01.061 | Signed finite ground-Horn closure, explicit precedence and conflict taint; byte and line-locator binding; bounded SciPy/HiGHS transitive equivalence optimization; actual costing scope audit | Source-qualified rule corpus, real typed equivalence and hierarchy constraints, larger solver or full Datalog only for a measured gap |
| T01.062 | Exact reference and final package path/hash matching before restricted overlap scan | Authorized private corpus and independent extraction coverage |
| T02.060 | PM4Py comparison of maintained PNML corpus and weighted concurrent/loop/deadlock/limit controls; Markdown parser-backed typed unit/DOI normalization with byte preservation | Actual hosted corpus results; native CST/WFST and Typst/LaTeX projections, broader notation and citation identity resolution |
| T03.060 | Generic pack boundary differential across eight supported kinds; 64 generated PRISMA partition/mutation cases | Native non-PRISMA renderer/consumer semantics and retained mismatch qualification |
| T05.060 | Single prospective publication retains E1–E14 and formal/statistical ablations; independent family risk and costing results kept distinct from topical ranking | Independent freeze, prespecified comparative endpoints, real held-out runs |
| T05.061 | Final metadata promotion CLI now requires a private exact overlap manifest, with synthetic wrong-inventory/incomplete/leak controls | Actual authorized runner/reference corpus and release approval; no upload |
| T05.062 | Independent enumeration vs HiGHS, PM4Py marking semantics, property-based arithmetic and shared-boundary Rust CLI qualification | Exact-head/receiving results, deeper fuzz and wider semantic domain |

All tasks remain open. The ordinary Python assurance lane now generates
`target/coverage/petri-net-qualification.json`, `pack-differential.json` and
`costing-scope-audit.json` alongside the existing legacy PRISMA receipt. These
are generated on the actual tested checkout and retained with Python coverage;
a new configured command is not a successful run. Any mismatch must be retained
and resolved, not ignored. No new workflow, runtime dependency or model download.

## Rule contract

The version `dev.standardflow.applicability-rules.v1` defines facts
(id, signed literal, anchor), ground Horn rules (id, head, conjunctive body, anchor)
and decision rows (id, obligation, require/exclude action, explicit integer priority,
body and anchor). Anchors contain source ID, SHA-256, locator. The bounded reference
evaluator validates unique identities and inventory limits, computes a least
fixed point over signed literals, identifies both signs and removes derivations
that rely on conflicting atoms. Cycles without a supporting fact do not create
knowledge. At the highest potentially applicable priority, unknown or conflict
holds the decision; equal-priority opposing actions hold. A lower priority applies
only after all higher conditions are explicitly false. No default exclusion.
The result retains the obligation, selected rule IDs and proof supports.
The byte-binding entry verifies exact source inventory, UTF-8 bytes, digest and
valid line locators. It does not establish that a rule accurately interprets a
source. This is a finite ground fragment, not a general-purpose variable Datalog,
ASP or source admission engine. No real guideline rules are inferred from prose.

## Costing and statistical boundaries

The existing costing metadata contains 26 records, 106 mapped item identifiers,
31 domains and 125 editorial covers_topic associations. The full 3,286-pair
candidate audit conserves all IDs, labels pairs as topical candidates, records
lexical rank and flags 11 item rows whose editorial domains fall outside their
instrument-level scope summaries. These summaries are not independently verified
hard exclusion constraints. No topical edge is promoted to equivalence, no
semantic merges, and the actual typed solver run remains held for appropriate
reference constraints. The bounded optimizer instead uses the already locked
SciPy/HiGHS implementation on explicitly typed synthetic equivalence candidates.
Triangle inequalities enforce equivalence closure; incompatible pairs are fixed
to zero. A second solve excludes the selected candidate set at the same score
to detect ties. Verify integer solution and objective, hold solver limits/ties.
No universal one-to-one rule and no unconditional ontology hierarchy claims.

Selective risk estimates the probability of at least one false equivalence
conditional on a guideline family containing an accepted equivalence. Exact
one-sided binomial bounds are adjusted across a prespecified threshold grid;
selection uses calibration only, then evaluates disjoint families at the chosen
threshold. This requires independent sampled families and eligible reference
labels; it is not a pair-level precision or conformal coverage guarantee.
Keep the earlier negative synthetic conformal shift result. The new synthetic
control deliberately contains a held-out error family after selecting a threshold;
report that error rather than changing the threshold. No independent calibration
dataset or empirical model superiority claim.

## Format and release

The bounded Markdown increment uses the locked markdown-it-py parser to locate
explicit inline code markers for units and DOI strings; accepts only its small
finite unit lexicon and conservative DOI syntax, rejects ambiguous spans and
unknown terms, compares parsed token structure after the byte-preserving edit
and retains comments, links, prose, and unedited bytes. The finite lexicon is a
deterministic special case, not a general WFST or native multi-language lossless
CST. No fabricated citation ID, automatic quantity conversion or standard text
rewrite. Native Typst/LaTeX CST and weighted transducers remain separate gates.

The existing promotion CLI requires a private overlap manifest binding the exact
staged artifact paths and hashes. Private references and extracted fragments
must remain outside the export package. The checker never echoes match excerpts
on the promotion path. Structural dataset validation still does not establish
rights, extraction completeness or reviewer authenticity. Actual restricted
corpus qualification and any Hub upload remain held.

## Local evidence and pending checks

Tests-first import failures were observed locally before the initial rule,
HiGHS and selective-risk implementations. Six initial rule tests, three solver
tests (including 12 seeded exact-enumeration cases), and three risk tests passed
in isolation with Python 3.13.5 and local SciPy 1.17.0, NumPy 2.3.5. Exact
tested blobs were verified at their corresponding commits; subsequent source
binding and formatting changes require fresh checks. Full clone DNS was
unavailable, no local Rust or PM4Py installation; no local full-suite or
all-corpus pass claimed. Hosted CI uses the repository's existing locked
PM4Py 2.7.23.15, SciPy 1.18.1 and markdown-it-py 4.3.0 profile. Record
exact-head and receiving-main outcomes after successful execution, and preserve
all eight broader acceptance gates. No new research result, pack, model or
restricted-data admission. One publication, issue #158.

### First hosted run and follow-up

[Assurance 45781269198](https://github.com/edithatogo/standards_check/actions/runs/45781269198)
at `fa60d57aa9e4eb7bff3ddc43e4adabd12324adcb` reported one Ruff formatting
finding in the release CLI and one type-check finding for the decoded private
manifest before Python regression execution. Require an explicit dictionary
check and simplify the formatting; no suppression or coverage change.
Later isolated verification passed the additional source binding test and
three Markdown parser tests (local markdown-it-py 4.2.0, copied unchanged
rewrite function). Remote rule and Markdown code/test blobs match the locally
executed files. Total local isolated tests: 16. Locked full-suite and actual
corpus acceptance remain pending, not inferred from these results.

### Hosted qualification and direct-script review finding

[Assurance 45781577197](https://github.com/edithatogo/standards_check/actions/runs/45781577197),
head `49b2de63c201d81dace91e9a8b68c56a80312468`, tested merge
`2f0912dc82d30412de65cb0fcff695f37a3dfa94`: the Python job
[139778104144](https://github.com/edithatogo/standards_check/actions/runs/45781577197/job/139778104144)
passed 831 tests, three skipped, two warnings, 91.67 percent combined coverage.
The actual PNML, pack differential and costing audit commands completed. All
ordinary component tests and the workflow-policy job passed. The Python coverage
archive [15097964757](https://github.com/edithatogo/standards_check/actions/runs/45781577197/artifacts/15097964757)
has API-reported SHA-256 `5326bc303bce429279a29ba7561e4e139a48b08403213a083a5404b17c289946`.
This is revision-bound historical evidence, not a verified download or final
integration result. An independent inline review reproduced a direct-script
import failure in the new promotion path; add a real subprocess regression
for ready and leaking manifests from outside the repository, and make direct
script execution resolve the same trusted package-relative import as module
execution. Do not merge until the review finding and fresh protected checks pass.
