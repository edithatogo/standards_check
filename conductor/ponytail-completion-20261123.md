# Ponytail implementation follow-up — 23 November 2026

This receipt covers the remaining implementation from the
[22 November review](ponytail-review-20261122.md), the five open receiving
dependency PRs and the source-import bookkeeping. It does not close the broader
repository quality, methodology or rights programme.

The integration starts from receiving main
`cf7d14da7bfb4d32c2c8746ec1111a6643c4a716`. The older prepared retirement receipt
`f7dde8955c06cc614f30484824bde83c9ba290a3` was reconciled with PR #96's stronger
actual-main evidence rather than replacing it. Publication must preserve that
receipt and the dependency heads below as ancestors, with the reviewed tree.

## Implemented work

| Work | Result |
| --- | --- |
| Generic recipe text metrics | Scene JSON retains nondefault padding/line height; SVG consumes them. Omitted defaults retain existing serialized behavior. |
| Narrow labels | Wrapping uses each node's checked inner width and column span. Invalid widths fail before layout with `SF-RECIPE-022`. |
| Conductor updates | Router metadata provides the expected exact pin; the audit rejects mismatched or ambiguous pins. Gitlink-only changes now trigger foundation checks. |
| Receiving dependency PRs | The five heads below are integrated together and validated as one working tree. |
| Source issues | Source #12–14 are closed as relocated, with original bodies retained and live obligations in receiving #29–31. |
| Source inventory | Records actual-main acceptance at `cf7d14da`, nine preserved export tips, four remaining live source refs and no open source PRs. |

| Receiving PR | Change | Preserved head |
| --- | --- | --- |
| [#87](https://github.com/edithatogo/standards_check/pull/87) | Pinned setup-node 7.1.0 | `22f6d81069bfe14a4d0d985af31425cb717b6dd3` |
| [#89](https://github.com/edithatogo/standards_check/pull/89) | url 2.5.9 and form_urlencoded 1.2.3 | `fc9e99b3a81359211c876a5d979a56a560b2cd56` |
| [#90](https://github.com/edithatogo/standards_check/pull/90) | Conductor gitlink `6e8f9a8` | `e803d2e7ee74c3d4119326dc49523f160b498b77` |
| [#91](https://github.com/edithatogo/standards_check/pull/91) | cors 2.8.6 | `866974ddd7ffe47dc2e784aec9847386472bdb3f` |
| [#93](https://github.com/edithatogo/standards_check/pull/93) | serde_json 1.0.154 | `080f01ad3aeb585c57ce3f80918e3c28b48cdde2` |

The exact legacy subtree remains
`62d8a0e738f0255cc59822ae4e661568090a213e`, from source commit
`dc51d8e392858d5cb4e653aed199563514191efb`. All nine exported histories remain
ancestors. No held legacy dependency or guideline candidate was promoted.

## Local integration evidence

Linux, Rust 1.98.1, Python 3.12.14 and Node 24.22.3:

- `cargo fmt --all -- --check`: passed.
- Workspace Clippy, all targets and features, locked dependencies, warnings denied: passed.
- Workspace tests, all targets and features, locked dependencies: **69 passed**.
- Workspace documentation tests: passed; zero examples were present.
- Offline Python suite: **204 passed**.
- Root Node suite: **7 passed**; API Node suite: **34 passed**.
- Root and API lockfile vulnerability audits: **zero reported vulnerabilities**.
- Foundation, Conductor, canonical-pack and four diagram-family validators: passed.
- Legacy exact-tree and nine-history checks: passed.
- Markdown and 56-entry index validation: passed.
- All 12 built-in PRISMA SVG, text and scene-JSON projections: byte-identical.

The [metrics receipt](tracks/02-semantic-diagram-prisma/recipe-text-metrics-20261123.md)
binds the rendering changes to file hashes and records the five new regressions.
The Conductor audit adds three regressions covering synchronized pin changes,
gitlink/file mismatches and invalid router metadata. The final pull request must
record its published head and actual hosted check results; these local results do
not substitute for an unexecuted hosted job.

## Open boundaries

The owner completed the authorized privacy/archive changes to
`edithatogo/standardflow`. An independent repository API read at
`2026-11-22T22:55:19Z` returned `private: true` and `archived: true`; the
[retirement record](../docs/migration/standardflow/retirement.md) preserves the
evidence. The earlier 21:00 UTC public/unarchived observation, GitHub account
reauthentication blocker and unavailable browser are historical.

[Repository-standards PR #172](https://github.com/edithatogo/repository-standards/pull/172)
has merged at `a3cc8dccdb67e6f122c71cec713194cdec792d07`, with the same tree as
its tested candidate. It removes only the retired source entry and retains
`standards_check`. Nine PR checks succeeded, two expected checks skipped, and local
qualification recorded 311 passes with 38 capability skips. Voiage's link PR #1394
remains open at verified signed, current-base head
`3bc04fdc1df6f30981765eee49c0c9dbce490cde`; its hosted and required local checks
must complete before merge.

The latest accepted receiving runtime is main
`2b0c579454a1dd469cd12cfb9538d23c96785370`. Its
[actual-main job](https://github.com/edithatogo/standards_check/actions/runs/45070791156/job/137357038355)
passed provenance, parity, container and default-startup HTTP checks; the
[parity artifact](https://github.com/edithatogo/standards_check/actions/runs/45070791156/artifacts/14773685812)
retains the result. At that main revision, 26 observed checks succeeded, including
deployment. The separate
[offline security run](https://github.com/edithatogo/standards_check/actions/runs/45070791434)
was still queued when re-read at approximately 22:58 UTC on 22 November.

Receiving #29–31, #82, #94 and #95 remain open for their documented obligations.
Queued offline security work has no execution receipt. Branch enforcement,
coverage, legacy-to-Rust semantic parity, item-level rights, methodology and
independent accessibility acceptance are not established by these implementation
checks. The API generator also exposed stale static snapshots; the
[brownfield audit](tracks/00-platform-foundation/brownfield-audit.md) records that
reconciliation without publishing unqualified content changes.

The receiving repository remains the active public home. See the
[retirement record](../docs/migration/standardflow/retirement.md) for recovery and
the completed source settings and remaining downstream reconciliation.
