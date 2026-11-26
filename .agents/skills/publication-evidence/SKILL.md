---
name: publication-evidence
description: Plan and execute StandardFlow publication experiments, blinded model-agent adjudication, reproducible analysis and evidence-grounded manuscript development. Use for publication protocols, experiment freezes, claim review or research handoffs in this repository.
---

# Publication evidence

Read `AGENTS.md`, `conductor/index.md`, the affected track and
`docs/research/publication-protocol.v0.1.0.md`. Reuse existing source, relation,
model and projection commands. Do not create another model executor or canonical schema.

1. Inspect `contracts/publication/programme.v1.json` and run
   `python scripts/validate_publication_contract.py`. Identify the question,
   primary endpoint, input pins, split, review budget, stop rule and current
   evidence. A planned contract permits planning, not a claim of execution.
2. Before confirmatory runs, resolve the listed freeze blockers and preserve
   the approved protocol/contract revision. Record exact source/edition and
   family partitions, model/runtime integrity, rubric and prompt hashes.
   Freeze the design and decision record before viewing held-out outputs.
3. Delegate source curation, blinded adjudication, execution and review as
   separate tasks using the role table in the protocol. Start adjudicators in
   fresh contexts with source-only packets; withhold predictions, expected
   answers and peer labels. Record actual agent/model/run identity. Separate
   initial labels from later discrepancy resolution. Hold unsupported labels;
   same-model agreement is not independent truth.
4. Execute the smallest predeclared experiment with the existing harness.
   Preserve commands, failed runs, implementation/model revisions, timestamps,
   resource use and hashed outputs. Do not run remote model code or modify
   source rights/admission to make an experiment pass.
5. Compare paired baseline and augmented results at the same review budget.
   Measure unique catches, shared misses, spurious flags, abstention and
   domain calibration. A candidate can help triangulation without winning
   standalone accuracy; disagreement alone is not a corrected error.
6. Ask a separate reviewer to check source support, arithmetic, falsifying
   controls, uncertainty, correlated errors and citation accuracy. Record
   claims as observed only when linked runs and review evidence support them.
   The integrity validator cannot certify scientific truth or authenticity.
7. Draft from the verified ledger. Bind each result/table/figure to retained
   outputs. Distinguish development, natural held-out and synthetic evidence;
   preserve null results and limits. Disclose AI assistance and preserve
   accountable author approval under the selected journal's policy.
8. Update the owning Conductor track and existing issues with actual receipts
   and the next gate. Keep specification approval, implementation conformance,
   model utility, EQUATOR feedback and publication acceptance distinct.

Do not contact stakeholders, submit manuscripts, upload unpublished material
or install a new service merely because this skill is invoked. Follow the
user's existing authorization for any such action. Never label a run, claim,
source, model or manuscript accepted solely because a local check passes.

## Model lifecycle and value

At each new experiment design or material model/runtime release, inspect the dated
[frontier evaluation record](../../../docs/research/frontier-evaluation-20261125.md).
Record the current role, incumbent and challenger; compare primary risk, incremental
supported detections, resource cost and review burden on the same locked inputs.
Keep failed, null and unqualified observations; do not change a frozen protocol or
select a model using held-out results. A new design or cohort is required for a
new confirmatory claim. Do not name a provider/model version that cannot be verified.

## Optional human review

Use independent fresh-context agents and a separate resolver/reviewer by default
for model-relative development and feasibility outputs. Human review is an optional
additional evidence tier for that work, not a start gate. Preserve actual agent
identity, evidence limits and disagreements. The E4–E8 planned design has a joint
freeze; keep its human/external-evidence claims held and record exploratory work
separately until a versioned model-relative design can be frozen independently of
E8. Never mislabel model-relative results as expert reference or human consensus.
See [operational policy](../../../docs/development/optional-human-review.md).
