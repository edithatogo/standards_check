# Track 05 verification

## Accepted implementation, 23 November 2026

The bounded assurance implementation is qualified on actual main
`dd3f995c473db0cc1cd6dad9d392b3744166958b`, tree
`3bdbebf0bb72a7f7edf9c90a7c4fc10412d98200`. [PR #107](https://github.com/edithatogo/standards_check/pull/107)
head `4e8e13a632777f2916b183101774cf2ff5389823` and its tested synthetic merge
`f8d86bcf61ba9f22b8a1bebd2bae078ae9e19b9b` have the same tree. The PR merged normally
after the valid review finding was corrected and its thread resolved. Protection remained active.

The [exact-revision record](hosted-status-20261123.json) retains source/report/artifact hashes,
job identities, settings observations and earlier failures. The
[portable receipt](verification-receipt-20261123.json) is validated against the central
verification-receipt schema and deliberately reports **partial**: accepted software controls
do not complete updater, offline-security, release or independent programme obligations.
This receipt names the implementation revision; a later documentation-only commit records it.

## Actual main measurements

[Assurance run 45106620582](https://github.com/edithatogo/standards_check/actions/runs/45106620582)
passed all four measurement jobs and the aggregate. All four downloaded artifact digests,
three native report checksums, checkout identities and 83 boundary-source bindings were
independently verified against actual main.

| Component | Observed result | Enforced floor and scope |
| --- | --- | --- |
| Maintained Python | 265 tests; 1,700/2,151 statements and 520/744 branches; **76.6839378238342% combined** across 28 modules. | 75% combined; zero exclusions. The denominator retains `simple_extract.py` at zero coverage. |
| Rust workspace | 72 tests; 2,742/3,430 lines; **79.94169096209912%**. | 79% lines. Source-file coverage includes embedded unit tests; no branch measurement is claimed. |
| Maintained API | 41 tests; 143/143 lines; 41/42 branches; **100% lines and 97.61904761904762% branches**. | 98% lines and 90% branches. Static generation and browser JavaScript are outside this component. |
| Schema/API mutations | Two clean baselines; ten assertion kills; zero survivors, unviable mutations or timeouts. | Ten hand-selected operators, with source drift and invalid syntax rejected; no global mutation percentage. |
| Existing validators and PRISMA contract | All six validators, two authored count-preservation pairs and two intentional validation differences passed. | Real CLI qualification ran inside Python coverage on clean main. No new dedicated diagrams-workflow run is claimed for this API/receipt change. |

The [coverage receipt](coverage-20261123.json) retains local measurement inputs and the
corrected historical API object. Native main report hashes are recorded separately in the
revision record. Floors, denominators and exclusions were not weakened to obtain acceptance.

### Dependency inventories

[Run 45106620577](https://github.com/edithatogo/standards_check/actions/runs/45106620577/job/137469275648)
produced artifact `14787249909`. Independent readback verified all nine inventories, all
48 retained-file checksums, all 15 dependency source inputs plus the generator, clean main
checkout binding, complete package identity sets and dependency references. Archive SHA-256:
`5b331712f3ed9248adf713043e79e431f377fe28c7a89b88ea81a0ea97a204f9`.

| Inventory | Components | Source scope |
| --- | ---: | --- |
| Rust | 89 | Cargo lock; 86 registry identities plus three workspace components. |
| Root Node | 3 | Root npm lock. |
| API | 72 | API npm lock; 73 locked records, including rate-limiter and address dependencies. |
| Foundation Python | 6 | Exact active pins on Python 3.14, including bootstrap pip. |
| Legacy Python | 31 | Maintained exact legacy-host profile on Python 3.12. |
| Python tests | 45 | Observed isolated resolution; transitives are not a frozen source lock. |
| Assurance tools | 3 | Exact maintained tool profile on Python 3.12. |
| Kernel baseline / candidate | 43 each | Maintained legacy host plus qualification overlay and workflow-owned ipykernel 6.25.0 / 6.31.0. |

Dependency inputs, generator and workflow are unchanged from accepted main8029; the new
hosted artifact nevertheless binds every inventory to actual main `dd3f995`. No costly local
imports were repeated. [Scope and procedure](sbom-20261123.md) distinguish native lock-derived
inventories from installed Python environments. The conditional foundation pin supports only
the deliberately narrow numeric `python_version <` marker; unsupported syntax fails before
installation. Inventories exclude release binaries/images, operating-system packages,
toolchain binaries, bundled native libraries and build downloads. They establish neither
vulnerability freedom nor source/content licence approval.

### Codecov and Pages observations

All three main OIDC upload jobs verified their native reports, used explicit component files
and returned processing URLs naming `dd3f995`. Push jobs correctly derived the SHA from the
checkout; they did not use an explicit `--sha` override. At 03:37:59 UTC, legacy patch status
`59621115216` succeeded; no Codecov App 254 check-run or project status was observed for main.
The final PR's actual App patch check
[`137468737189`](https://github.com/edithatogo/standards_check/runs/137468737189)
passed at 100% against 80%. Uploader jobs and provider checks are distinct evidence.

Trusted upload jobs alone request OIDC, verify native artifact identity and use pinned
Codecov action 7.1.1/CLI 11.3.2. Fork PRs do not receive that upload permission. Component
floors remain enforced independently of external provider processing.

Pages recovery was observed on earlier receiving main8029 in
[run 45103418503](https://github.com/edithatogo/standards_check/actions/runs/45103418503/job/137460173154):
exact artifact `14786298400`, `github-pages-1`, passed the bounded metadata probe and native
deployment. PR #106's eleven regressions exercise visibility, ambiguity, identity and expiry.
The native deployment supplies the separate Actions Results observation; a new Pages
deployment on `dd3f995` is not inferred.

## API security correction and evidence integrity

Main8029 marked rate-limit alert #1 and format-string alert #2 **Fixed via PR #100**, then
exposed two new High path findings, #5/#6. PR #107 makes both endpoints enumerate fixed corpus
directories and select only regular file entries. A validated request ID is compared with
entry names; it does not supply the filesystem path. The failure-first symlink test served
200 before the repair and returned 404 afterward. Invalid identifiers return 400,
absent/non-file entries return 404, and enumeration/I/O failures return sanitized 500s.

Independent review used actual symlinks in both directories, a dangling link, a Markdown-named
directory, invalid aliases and injected enumeration errors. It found no publication blocker.
The deployment-controlled corpus remains a limit: enumeration/read is not atomic against a
local writer replacing files; hostile mounts or local races are not qualified by this fix.
See [the path-selection receipt](api-path-selection-20261123.json).

Two evidence corrections were necessary and remain visible:

1. Initial head `5a5d0eb` failed privacy because a public LCOV checksum stored under the key
   `api.lcov` matched `generic-api-key`. Exact b30-pinned tooling and Gitleaks 8.30.1 reproduced
   the one finding. Head `19b17bf` replaced that mapping with explicit `path`/`sha256` records,
   preserving all values and production/test bytes. The corrected scan found zero findings
   and zero reviewed exceptions; scanner configuration and suppressions were unchanged.
2. A valid Codex review then found that a Python object alias had copied current API hashes
   and coverage into an old record retaining 40 tests and the old report. The only semantic
   correction restored the historical API object from main8029. Independent deep comparison
   proved the old API/tests/report equal that parent and all other current fields equal
   `19b17bf`; both old/new reports were rehashed. Final head `4e8e13a` published the correction,
   then thread `PRRT_kwDOPbFwGs66rmvp` was resolved before normal merge. No code rerun was
   needed for this metadata-only proof; final hosted API and mutation checks still passed.

The historical API result remains **40 tests, 146/146 lines and 36/38 branches**; the current
result is **41 tests, 143/143 lines and 41/42 branches**. Neither is relabelled as the other.

After normal merge, the live main inventory explicitly showed **0 open and 4 closed** CodeQL
alerts. #5/#6 each read **Fixed via PR #107**, not dismissed; #6's activity linked actual
`dd3f995`. Main privacy job `137469276069` passed with zero Gitleaks findings and reviewed
exceptions, zero Presidio blocking findings and seven advisory checksum-looking matches.
These observed controls do not certify full privacy coverage or vulnerability freedom.

## Technique applicability

| Technique | Application | Limit |
| --- | --- | --- |
| Properties | Eight Rust properties, 256 cases under each of seeds 0, 721114987 and 20261123: 6,144 examples. [Bounds/replay](rust-qualification-20261123.md). | Finite generators. Direct Python/API rejection contracts cover the bounded interfaces without another property framework. |
| Metamorphic relations | Canonical key-order/whitespace invariance and idempotence; lock order and reversible content/rename changes; count redistribution; renderer reading order; API list/item equality. | Identifier splitting and authored pairs do not establish reversible semantic migration or general legacy-renderer equivalence. |
| Native mutation | Six Rust functions, 26 selected; initial misses repaired; 25 viable caught and one unviable excluded. Hosted [first-head campaign](rust-hosted-first-head-20261123.md) at `12b7b007` verified the same outcomes. | Historical campaign, not a final-head rerun or global score. Native selected-package baseline 61 differs from workspace 72. |
| Schema/API mutation and contracts | [Ten operators](boundary-mutation-20261123.md), schema/pack guards, CLI errors, actual HTTP/CORS behavior, source-PDF checks, locks and 12 diagram reference outputs. | Imported legacy 52-test runtime/parity qualification is separate from Rust semantics and scientific content acceptance. |
| Deterministic simulation | Mocked API clock checks exhaustion, rejection before parsing/I/O and recovery after expiry. | Process-local counter only. No distributed scheduler, replica or shared-store claim; synchronous Rust filesystem failure/race tests remain applicable. |

## Historical failures and revision boundaries

| Observation | Disposition retained |
| --- | --- |
| `12b7b007` first head | Component/provider checks passed; boundary setup failed under the wrong Python profile and the aggregate correctly failed. [Original receipt](hosted-first-head-20261123.json). |
| `d67d9e9` | Native coverage, ten boundary kills, nine inventories and OIDC passed. Separate PRISMA failed during rustfmt installation before qualification; retry cancelled without steps. The same CLI contract passed inside coverage. |
| `b615279` | Superseded by PR #106 integration; SBOM/native work cancelled without execution. |
| `92e61459` / main8029 | Initial queued/passkey-blocked snapshots superseded by verified execution and active protection. PR: 41 successes, two expected skips and two offline jobs queued. Native assurance, dedicated two-pair PRISMA, SBOM and Pages qualified; later main path alerts required PR #107. |
| `5a5d0eb` / `19b17bf` | Privacy presentation failure, then clean representation repair; the valid historical-API review still blocked merge. Neither head was accepted as main. |
| `4e8e13a` / main `dd3f995` | Corrected history, addressed review, normal protected merge, native/SBOM/OIDC qualification and actual alert closure. Final PR: 22 successes/two offline jobs queued. Main: 19 successes, one PR-only skip and one offline job queued. |

PR #104/#105 explicitly request `rustfmt,clippy` at pinned Rust setup sites, retaining
`llvm-tools-preview` for coverage. New Python modules initially reduced combined coverage
to 71.47%; the existing real PRISMA CLI contract raised it above the unchanged 75% floor with
no exclusions. Earlier `not_run` observations remain separate from later successful execution.

## Policy, protection and remaining gates

The [managed-file receipt](managed-file-drift-20261123.json) records the original exact central
comparison, local extensions and Unicode triage. Later semantic review against
[`repository-standards@2efdbd9`](https://github.com/edithatogo/repository-standards/tree/2efdbd988064f6857795b9fa9ed4e1d08d18791d)
confirms registered `node`/`baseline` requires dependency review and SBOM. Both are implemented;
no missing native test type was identified. Scorecard, Security Insights and SLSA are not
selected baseline controls, without waiving future release requirements.

[Issue #30](https://github.com/edithatogo/standards_check/issues/30) records the local `ci.yml`
specialization through the existing [semantic-conflict route](https://github.com/edithatogo/repository-standards/blob/2efdbd988064f6857795b9fa9ed4e1d08d18791d/docs/continuous-conformance-standard.md).
The [managed-file contract](https://github.com/edithatogo/repository-standards/blob/2efdbd988064f6857795b9fa9ed4e1d08d18791d/managed-files/manifest.json)
preserves local additions, and enforcement policy preserves stronger controls. Local
Python/Rust/API jobs and separate trusted explicit-report uploads therefore remain. The
manifest still describes a thin immutable reusable call; this review does not claim that call
exists or that local files equal the template. No profile migration, new waiver or extra
approval is required. Future central reusable-workflow adaptation must preserve these boundaries.
A single quick-profile command remains an optional improvement, not an added acceptance gate.

[Ruleset 27871801](https://github.com/edithatogo/standards_check/rules/27871801) is active on the
default branch: PRs, resolved conversations, strict checks, zero human approvals, no force
push/deletion and no bypass actors. All seven contexts are bound to GitHub Actions app 15368:
privacy, four CodeQL analyses, `assurance` and `Maintained dependency inventories`. Native
CodeQL thresholds are High-or-higher security and errors. Post-merge readback confirmed the
same settings and `current_user_can_bypass: never`.

The original Confirm access/passkey block and empty API inventory remain historical. After
owner authentication, activation and normal protected merges were observed. Recovery is the
authenticated [named ruleset edit path](https://github.com/edithatogo/standards_check/settings/rules/27871801):
reauthenticate when requested, correct a renamed/misconfigured check, restore and verify
protections. Edit access was observed; no standing bypass exists and no recovery change was
rehearsed. A destructive drill is not a new acceptance requirement.

Renovate installation/discovery and prior bot merges do not prove the protected updater
lifecycle; Dependabot remains until the existing handover is qualified. Offline-security is
still unexecuted. The observed runner inventory had no configured runners; #30 retains the
qualified image/assets, matching isolated runner, consumer-pin and execution prerequisites.
Ordinary hosted checks, CodeQL or a queued job do not substitute for them.

The [plan](plan.md) keeps independent interpretation/evidence review (#82), held guideline
rights/provenance (#95), broader legacy consumer semantics, Track 04 contracts, release/offline
reproducibility, provenance/signatures, downstream cutover/rollback and independent
methodology/accessibility/publication open. Optional kernels (#94/#101), held-source identity
rejection (#102) and bounded PRISMA parity (#103) retain their recorded limits. Track status
remains in progress; accepted implementation is not completion of the whole programme.

## Repository health, accessibility and advisory supply-chain reconciliation — 23 November 2026

At [main `f4d8b3e`](https://github.com/edithatogo/standards_check/commit/f4d8b3e159e442950bcd888b611121d065197501),
[RepoHealth run 45121828831](https://github.com/edithatogo/standards_check/actions/runs/45121828831)
reported **93/100 (A)**: CI/CD 15/15, Testing 16/20, Documentation 13/15 and Security 9/10.
Its test-framework recommendation is not sufficient grounds to add a second runner or
uninformative configuration: Rust, Python and Node tests already run under `Assurance`.
ALint passed with 74 nonblocking notices (one missing code of conduct; the others
missing terminal newlines). Preserve immutable original/archival source bytes rather
than mass-normalising them to chase a hygiene score. The separate actionlint/Zizmor
workflow-policy job passed; Zizmor reported **zero active findings and 39 suppressed**,
not zero underlying diagnostic observations. Suppression categorisation needs an
explicit audit if it becomes a security gate.

[OpenSSF Scorecard run 45121828713](https://github.com/edithatogo/standards_check/actions/runs/45121828713)
published [SARIF artifact 14794255855](https://github.com/edithatogo/standards_check/actions/runs/45121828713/artifacts/14794255855)
with actionable advisory **RUSTSEC-2026-0486**: `Cargo.lock` held `rustix 1.1.4`,
fixed upstream in **1.1.6**. This increment updates only the exact `rustix` lock entry
using the published `1.1.6` registry checksum; hosted `cargo --locked` verification and
a subsequent Scorecard rescan are required before declaring the finding resolved.
Other diagnostic checks: PinnedDependencies 8 (pip install commands without hashes);
SAST 7 (23/30 observed historical commits); Fuzzing 0 (no detected recognised integration);
BranchProtection 4 / CodeReview 0 (deliberate zero-human-approval solo-maintainer policy);
BestPractices 0 (self-attestation not attempted). These scores are not release gates.
Any full pip hash migration or native fuzzing programme requires a focused dependency-
and use-case-qualified increment; none is inferred from the current property/mutation tests.

This commit adds a repository-specific accessibility statement, reporting template,
community conduct and support routes, an introductory run example and local credential
ignores. It does not claim independent WCAG compliance, release provenance, external
methodology acceptance or rights to redistribute third-party reporting guidelines.
See [quality frontier #31](https://github.com/edithatogo/standards_check/issues/31)
and [security #30](https://github.com/edithatogo/standards_check/issues/30).
