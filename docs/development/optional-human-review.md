# Optional human review and unattended assurance

Status: proposed operational policy, based on live repository readback on
26 November 2026. Scope: StandardFlow only. Owners: Track 05 / #31, #30, #116
and research issue #158.

## Native review path

The protected main ruleset has zero required approving reviews, no required
reviewers or code-owner approval, required review-thread resolution, seven
app-bound required checks with strict base freshness, CodeQL alert thresholds,
no bypass actors, and deletion/force-push protection. Repository auto-merge
and automatic merged-head deletion are enabled. Keep these controls: an
absence of human review is allowed, but an unresolved finding is not an
approval. CODEOWNERS remains accountable ownership, not a required signature.

Use ordinary pull requests for changes from agents, humans and dependency bots.
An authorized automation may prepare a PR, review its diff and evidence,
enable native auto-merge or merge the exact verified head using the normal
protected API. It must not mark a failed, held or unqualified change ready.
Inspect the tested base and head, actual required results, review threads,
and receiving revision. Merge sequentially and retain failed runs.

A human may inspect the PR and job artifacts, comment, request changes,
disable auto-merge, convert a PR to draft, cancel/rerun a workflow or close
a proposal. An intentional hold is effective until its reason is resolved;
do not re-arm auto-merge or resolve a human objection merely to get green.
No reviewer response, approval checkbox, or arbitrary waiting period is
required for normal automated work. Do not create synthetic human approvals
or a privileged workflow to bypass branch rules.

## Workflow inventory and changes

All 18 checked-in workflow files have automatic event triggers; the foundation
workflow alone lacked explicit workflow dispatch. Add it and test automatic
triggers and dispatch availability for the maintained workflow inventory.
The GitHub Actions run/job logs, annotations, artifacts and step summaries are
the native optional review surface. A manual dispatch is also an API entrypoint
for authorized automation, not a requirement that a person clicks a button.
Keep existing event scopes, permissions, protected status names, coverage
floors, failure behavior and expensive experiment budgets.

The only deployment environment found in workflow YAML is `github-pages`.
The preceding receiving main deployed successfully. Environment protection,
organization Actions policy and first-time external-fork execution permissions
are server-side; this connector cannot inspect or change environment rules.
For owner review: verify Environments > `github-pages` has no mandatory reviewers
for this routine approved Pages projection, while retaining deployment branch
restrictions. Do not remove security restrictions on untrusted forks.
Offline security is still queued for its qualified runner; optional review
cannot substitute for an unavailable detector.

## Dependency proposals

The shared Renovate preset requires dashboard approval for major changes.
Override it locally: all ordinary and major proposals may be created without
a dashboard checkbox, with major and security changes still separated and
one routine PR at a time. The dashboard remains a convenient optional
intervention and visibility surface. Preserve Dependabot until a real
protected Renovate update and receiving lock/inventory/security receipt is
observed. The existing disabled unattended Renovate merge settings remain
during that handover; agents may qualify and merge individual updates via
native protected PRs without human approval. After the updater is qualified,
prefer routine PR-based native auto-merge, retain explicit holds for breakage
or evidence loss, and never set ignoreTests or bypass protected checks.
This change does not prove the remote updater has picked up the new config.

## Research and evidence

Use the existing publication-evidence skill. Automated deterministic checks,
independent source-only agent reviews, separate discrepancy resolution,
and revision/hash-bound machine receipts are the ordinary review path.
Human expert review or audit is an optional additional evidence tier for
model-relative development and feasibility work. Never stop acquisition,
source diagnostics, synthetic controls, candidate retrieval, ontology
linking or model-relative comparative work merely because no human
reviewer is available. Unresolved cases remain held; no inferred permission,
automatic equivalence closure or claimed human consensus.

For research claims whose endpoint actually requires human participants,
issuer decisions, verified external permissions or an expert reference,
the missing evidence is a scientific or authorization hold, not a mandatory
routine workflow approval. Preserve the existing E1–E3 and E4–E8 contracts,
including their freeze rules; do not remove a blocker to register a run
with a different estimand. Continue separately recorded exploratory
model-relative experiments using the same source and claim boundaries.
Before a confirmatory freeze, split the model-relative E4–E7 design from
the human-dependent E8 evaluation if needed, with explicit version,
reference type and separate claims, keeping original planned records.
Humans can optionally review or correct any machine receipt. Where a
claim requires a human audit or external determination, keep that claim
unqualified until that evidence actually exists. Rights, privacy, paid
compute, disclosure, publication and external release permissions remain
independent; no automated review fabricates them.

## Acceptance and rollback

Required regression suite checks the native event path and the local
Renovate overrides. Verify all seven required checks on candidate and
receiving main, and observe a real updater proposal without dashboard
approval before closing its operational hold. Use a protected revert PR
if dispatch or update behavior regresses. No new token, scheduler,
approval bot, external service or workflow bypass is introduced.

Primary references: [GitHub auto-merge](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/automatically-merging-a-pull-request),
[GitHub deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments),
and [Renovate configuration options](https://docs.renovatebot.com/configuration-options/#dependencydashboardapproval).
