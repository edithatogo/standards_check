# Ponytail review — 22 November 2026

## Reviewed and repaired

Baseline: `1aef9b5b95582d447d9b539c94d4b5dcf4366679`.
Published implementation: `c64c61a0a978b4b50f8d525fc76d6548d2e75718`.

- Markdown/index validators printed errors but returned success; the sidecar validator lost
  failures in a pipeline subshell. Invalid input now fails the aggregate gate. Explicit legacy
  placeholders and optional-field warnings retain their existing meanings.
- The TBD warning examined log text rather than source content. It now searches text files,
  ignores binary data and distinguishes no matches from search errors.
- `make html` did not discover the current English corpus and split Pandoc arguments across
  shell commands. It now builds both supported layouts, uses real H1 titles, respects template
  dependencies and generates citations once.
- Two mixed-source PRISMA SVGs emitted node groups in storage order instead of scene reading
  order. Rendering now follows the validated order. XML comparison confirms unchanged node
  geometry, labels, edges and styling; only group order changed.
- Isolated scene nodes could exceed the schema's 256-character identifier bound. Rust now
  applies the existing bound directly to every node.
- The SVG gate now resolves ARIA title/description IDs uniquely, checks every node label and
  compares DOM order with the validated scene. CI invokes the negative regressions.
- Agent guidance now identifies the Rust/canonical surface and the actual legacy paths;
  stale duplicate Copilot instructions have been replaced with references to current guidance.

## Local evidence

Linux, Rust 1.98.1 and Python 3.12.14:

- Rust formatting and Clippy with warnings denied: passed.
- All Rust targets: 64 tests passed; documentation-test command passed with zero examples.
- Offline Python suite: 197 tests and 38 subtests passed.
- Final Makefile title regression: 2 methods passed after the H1 metadata correction.
- Real Pandoc/yq HTML build: 56 checklist pages plus index, without missing-title warnings.
- Foundation, Conductor inventory, canonical pack and four diagram-family validators: passed.
- All 12 reference diagram outputs regenerated and matched committed bytes.
- Real corpus gate: 56 index entries; costing metadata 26 sources, 31 domains, 106 mappings.
- Independent review found no blocker in validators, Rust changes, SVGs or CI integration.

The reviewed primary changes were first tested locally at `065efd6efd64246d67bfe0a095f418b9018da457`;
the published implementation contains the same 19-file changes and also preserves the concurrent
repaired StandardFlow import as a parent. These are local receipts. Hosted checks must be read for
their actual final commit; historical
success, a configured job, a neutral check or a cancelled offline-security job is not acceptance.

## Remaining work

1. Track 02: carry generic recipe padding and line-height through the scene/rendering contract.
   Recipes accept custom metrics while the SVG renderer currently uses 18/20. Built-in recipes
   use those defaults; nondefault metrics can overflow. Add a small-metrics multiline fixture,
   define backwards-compatible scene fields, then regenerate and validate all projections.
2. Track 00 / issues #29–31: repository-standards profile, branch enforcement, coverage and
   managed-file reconciliation remain separate. The cancelled offline security pipeline still
   needs a qualified runner and an execution receipt.
3. Issue #82: the existing 42-item PRISMA source transcription is retained. Normalized
   interpretation, evidence expectations and semantic migration acceptance remain open.
4. Track 03: both live repositories agree that standards_check is retained and standardflow
   is the legacy import source. The user's later instruction explicitly requests import, then
   private archival; the receiving track records that work separately from this code review.
