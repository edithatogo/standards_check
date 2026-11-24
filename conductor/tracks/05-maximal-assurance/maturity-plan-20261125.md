# Repository maturity plan — 25 November 2026

Owner: [assurance issue 31](https://github.com/edithatogo/standards_check/issues/31).
Implementation follows the [track plan](plan.md); stable task identifiers and
the [issue registry](../../../contracts/project/conductor-issues.v1.json) are the
machine-readable ownership crosswalk. This document records engineering choices;
it grants no scientific acceptance, redistribution permission or external endorsement.

## Acceptance order

| Order | Work and acceptance evidence | Owner |
| --- | --- | --- |
| 1 | Required local and hosted lint, format, typing, security and prose checks reject deliberate negative probes; every owned dependency is pinned and inventoried | #31 |
| 2 | Measure the maintained production scope with unchanged exclusions; keep Python statement-plus-branch coverage above 90%, Rust line coverage above 90%, and the API's stronger native floors | #31 |
| 3 | Give every Conductor checkbox a stable task ID and canonical issue link; reconcile all repository issues, including closed history and the retained bot-dashboard comment; update both sides together | #163 |
| 4 | Require a reviewed manifest, exact files and columns, immutable source revision, export permissions, and content-bound review receipts before a metadata release can become publishable | #162 |
| 5 | Qualify native fuzzing and the independent offline security runner; close actual detector, dependency-lock and protected-updater gaps | #30, #116 |
| 6 | Qualify public release artifacts, immutable tags/assets, provenance and an independent consumer installation; expose the work in GitHub Projects | #30, #163 |
| 7 | Finish deployed interaction/accessibility and consumer semantics; freeze the evaluation before publication analyses; retain venue-specific submission restrictions | #123, #82, #161, #158 |

Steps 1–4 are implemented in this hardening change, with measured and hosted
evidence recorded separately. Later steps retain their explicit open acceptance
gates. A successful CI run qualifies the recorded revision and scope only.

## Reviewed local evidence

The sealed [coverage receipt](coverage-20261125.json) and
[source manifest](coverage-sources-20261125.json) bind the final reviewed candidate
to its source bytes. All 161 Python source/test/coverage-configuration hashes were
identical before and after the clean run. The existing coverage exclusions were
unchanged, and no excluded production lines were introduced.

| Measure | Observed local result |
| --- | --- |
| Python tests | 637 passed; three existing optional-reference tests skipped |
| Python combined | 7,730 / 8,512 statement and branch opportunities, 90.813% |
| Python statements | 5,660 / 6,122, 92.453% |
| Python branches | 2,070 / 2,390, 86.611% |
| Rust | 95 tests passed; 3,178 / 3,466 lines, 91.691%; original denominator unchanged |
| API | 41 tests passed; 143 / 143 lines and 41 / 42 branches |
| Seeded mutation campaign | Two baselines passed; ten assertion kills; no survivors, syntax failures or timeouts |

The [API receipt](api-coverage-20261125.json) and
[bounded mutation receipt](boundary-mutations-20261125.json) retain their own
source and report bindings. Static-check negative probes rejected bad lint,
formatting, types, security and prose. Crosswalk and dataset review identified and
repaired real malformed-input gaps before sealing the measurements. None of these
local receipts substitutes for the protected PR and receiving-main checks.

## Enforced quality policy

The seven existing app-bound branch checks remain required, current-base strict,
and without bypass. The `assurance` aggregate rejects failed, cancelled and
unexpectedly skipped dependencies. It contains native component coverage,
workflow policy, boundary mutation and property checks. CodeQL, privacy/secrets
and maintained dependency inventories remain independently required.

The coverage floor is Python 90.5% combined statements and branches, Rust 91%
lines, API 100% lines and 95% branches. Report the native numerator and denominator
as well as the percentage. Python branch coverage alone is a separate measure;
the combined floor does not claim that every Python branch is covered above 90%.
The retained historical import is measured through its bounded consumer contracts;
this is not a claim that every imported line is in the maintained-code denominator.

Keep pre-commit and CI checks aligned. Remote hooks and Actions use full commit
SHAs; native downloaded tools have checked archive hashes. Read-only jobs receive
no write token. The issue-reconciliation job alone needs `issues: read`, with
`GH_TOKEN` confined to its read step. Its data is parsed as data, never executed.
Issue events and a daily reconciliation detect metadata drift after code merges.
Fork PRs use their normal read-only event and do not receive publishing credentials.

The profile and protocol snapshots remain immutable. Vale does not rewrite
published technical wording, imported reporting requirements or generated evidence.
Changes to a frozen representation profile require a new version and a separate,
hash-bound approval decision. Draft 0.1.0 remains a draft.

## Tool decisions

| Tool or control | Decision | Purpose and remaining boundary |
| --- | --- | --- |
| Ruff | Required | One Python linter and formatter for maintained scripts; unused bindings, unsafe idioms and import ordering are checked |
| ty | Required in the qualified validator/receipt boundary | Warnings fail; new validators join automatically; extend coverage after optional model and report data shapes are explicitly typed |
| basedpyright | Evaluated; not added alongside ty | A second checker would duplicate enforcement without resolving the remaining untyped data contracts |
| Bandit | Required | Medium/high severity with medium/high confidence; fixes include pinned translation models and bounded shared XML ingress |
| Vale | Required on maintained author prose | Product names, descriptive links and repeated words; nine native tests ensure rules and scope are active |
| Vulture | Evaluated at 100% confidence | No distinct findings; revisit if dead-code evidence appears rather than maintaining an empty duplicate gate |
| Hypothesis and Proptest | Required tests | Generated text, shape, count and trust-boundary invariants; recorded seeds/fixtures support reproducibility |
| pytest-xdist | Deferred | First demonstrate test isolation and a measured wall-time benefit; serial coverage remains authoritative |
| cargo-mutants and seeded boundary mutations | Retained | Actual caught/surviving mutations are reported; the campaign is bounded, not whole-program mutation qualification |
| pytest-gremlins / mutmut | Choose one only when needed | Qualify a bounded Python mutation campaign against a concrete surviving-fault question before making it required |
| Native fuzzing | Open qualification | Run bounded campaigns against canonicalization, lock/artifact admission and hostile source parsers; retain crashes and minimized regressions |
| Scalene | On demand | Profile a demonstrated acquisition/rendering bottleneck; machine-dependent timings are not a deterministic merge gate |
| Gitleaks and Presidio | Retained required controls | Secrets and privacy have distinct detectors and review paths; absence of findings is not permission to publish source content |
| TruffleHog | Deferred | Add only for a demonstrated history/detector gap and an approved verification policy; do not send potential credentials to external verification services by default |
| ESLint, Rustfmt, Clippy | Retained | Native language controls remain authoritative for their components |
| actionlint, Zizmor and CodeQL | Retained | Workflow syntax, workflow security and code scanning have complementary scopes |
| Dependency review, inventories, SBOM and advisories | Retained | Exact versions and evidence of resolution are required; closing an alert without a fix is not acceptance |

The [contributor guide](../../../CONTRIBUTING.md) lists the runnable commands and
the [assurance profile](../../../requirements/assurance-tools.txt) lists exact
versions. Further tools need a distinct fault model, an exercised negative case,
an owner and an acceptable execution cost.

## Remaining robustness work

1. Qualify a native changed-line coverage gate. Codecov project/patch reports are
   supplementary: those checks are not currently among the protected seven, and
   fork/Dependabot uploads deliberately differ. A higher hosted patch target alone
   must not be represented as enforced merge protection.
   The Codecov patch target is now 90%; the local changed-line estimate is 92.565%
   for Python executable lines. That estimate is not a hosted Codecov result.
2. Complete hash-locked transitive dependency profiles where the ecosystem permits,
   verify clean installation and retain rollback/rebuild evidence. Exact versions
   alone are not content hashes. Preserve the protected updater lifecycle and
   issue 76's bot-managed body; the crosswalk uses a separate retained comment.
3. Execute the prepared native fuzz and offline security campaigns on qualified
   runners and immutable assets. A queued job, a draft PR, an unavailable scanner
   image or a skipped scan is not evidence of a passed campaign.
4. Inspect current repository security alerts and strengthen CodeQL rule severity
   thresholds after identifying the real findings. Preserve current protection while
   access is unavailable; a settings-page badge does not identify alert type or state.
5. Measure reproducible build/install behaviour and cross-platform consumers before
   issuing an alpha software release. Prepare checksums, inventories, SBOM,
   attestation, release notes, migration notes and a clean consumer smoke test.
   Keep software version, representation-profile version and dataset version distinct.

## Project, releases and website

The repository's Projects feature was disabled at the initial audit, and its
release API returned no releases. The attempted settings update timed out; a
subsequent API read still showed Projects disabled. Release immutability could
not be read back. These changes are not recorded as completed. The connector
does not expose Project/ruleset settings writes, and the alternate browser lacks
the authenticated session. Issue #163 retains the Project follow-up; issue #30
retains the release settings and security-settings readback.

The proposed Project is a projection of existing issues, using status, track,
evidence level and next acceptance gate. Conductor remains the versioned plan;
issues remain collaboration records. The project must not become a third source
of truth with independently invented completion states. Closed bounded work should
remain visible. Use one upstream EQUATOR umbrella and link implementation issues
in this repository; native parent/subissue relationships may be added when the
upstream maintainers permit them.

A deployed documentation website already exists through GitHub Pages. Astro is
an optional documentation implementation choice, not a prerequisite for strict
assurance. First qualify current interaction, import/export and accessibility under
#123. Adopt Astro only if a documented need for generated versioned reference
pages or an evidence explorer justifies migration, with URL parity, accessibility,
security headers where supported and reproducible static builds verified.

## Additional uses of the data

Prioritize uses that preserve provenance and expose uncertainty:

- **Version-change surveillance:** compare requirement identities and source hashes
  over time, separating new wording, structural movement, changed meaning and
  missing acquisition. A missing source is not evidence that a requirement vanished.
- **Reporting-obligation coverage:** query overlap and gaps by study design,
  section and reporting stage. Distinguish semantic equivalence from weaker
  relationships; a shared label alone does not justify merging obligations.
- **Format reliability research:** measure where PDF, HTML, JATS/XML, checklist
  tables and explanation documents lose identity, numbering, scope or structure.
  Report the sampling denominator and acquisition/rights failures as outcomes.
- **Orthogonal method selection:** select rules, layout parsing, classical NLP,
  discriminative models and a small generative model by their incremental error
  discoveries, not by an assumption that any one model must outperform the rest.
- **Consumer conformance suites:** derive safe synthetic fixtures and expected
  admission/hold decisions for authoring tools, journal workflows and evidence
  systems, pinned to a representation version and consumer revision.
- **Rights and availability maps:** identify which metadata can be redistributed,
  which sources require permission and which disappear or change. These are
  acquisition and review states, not automated legal conclusions.

The [dissemination policy](../../../docs/architecture/DATA_DISSEMINATION.md) governs
any Hugging Face export. The [submission plan](../../../docs/research/publication-submission-plan.v0.1.0.md)
records publication options, registration/freeze decisions, authorship and venue
rules. Neither document authorizes blanket dataset upload or manuscript submission.
