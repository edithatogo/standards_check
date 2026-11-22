# Pull request review and repository consolidation — 22 November 2026

## Decision and scope

Keep `edithatogo/standards_check` as the primary StandardFlow repository. Export this
legacy repository there with Git ancestry and Apache-2.0 notices intact. The user
explicitly requested that this source repository then become private and archived.
The retirement is an administrative consolidation after verified export; it does
not assert that the new Rust engine has replaced or matched every legacy output.
Track 03 in the primary repository owns the remaining semantic migration work.

Primary main observed during review: `1aef9b5b95582d447d9b539c94d4b5dcf4366679`.
Its tracks 01 and 02 record implementation and revision-bound hosted evidence;
Track 03 was still planned. This observation does not move either adoption pin in
`integration/standards-check-adoption.json`.

## Reviewed inputs

| Surface | Exact revision | Observed result |
| --- | --- | --- |
| Legacy main | `af299f724bcf456c131b43a143b3eabc1d81245b` | 29 local tests passed |
| PR #9 original | `41c3e174fd7932d308992c4ef96d055273dabdbd` | 41 tests: two failed web POSTs and one TIFF error; merge conflicts with main |
| PR #24 | `eb7d0703b86aaa82e3cd738a273db7c60a70f6c9` | Minimal action-hardening diff; hosted tests, privacy and adoption passed |
| PR #25 | `7d2e233217d5d3d6c4ca9c5866f64158d117099e` | Minimal setup-python alignment; hosted tests, privacy and adoption passed |

The application comparison used Python 3.12.14 and current main's dependency pins
rather than reintroducing the old Flask/Werkzeug versions from PR #9.

## PR #9 repair

- Reconcile with current main without rewriting source history; preserve adoption
  metadata, current Flask/Werkzeug pins and existing security workflows.
- Reuse existing renderers, six diagram fixtures and golden snapshots. Restore
  checklist routing, all diagram variants, styling and response types. A synthetic
  150 identified / 20 duplicate / 130 remaining case verifies the rendered counts.
- Consolidate duplicate JSON-schema keys, restore count types and non-negative
  bounds, and require multiple-choice options. Add the missing STARD fixture title.
- Use one canonical schema directory independent of the caller's working directory.
  Invalid CLI validation exits nonzero; overrides pass through validation.
- Restore the original module entry point, default PNG output, checked TIFF
  conversion without deleting a pre-existing PNG, and SVG-backed Typst diagrams.
- Parse raw JSON and typed forms correctly. Keep checklist rows after removed gaps.
  Use request-local rendering and native diagram downloads, and payload-specific
  checklist ZIPs. Escape display text and reject unsafe section filenames.
- Remove 49 duplicated/generated files, the unused cluster renderer, duplicate CARE
  schema, redundant rendering test/snapshot and unused Markdown dependency. Retain
  one executable notebook per example and clear saved outputs.
- Remove the broken, untested interactive CLI wizard; JSON input and the existing
  web forms cover input collection. Web downloads cover PNG/SVG/PDF; CLI Typst
  creates the `.typ` file together with its required sibling SVG.
- Deduplicate offline security runs by scanning PRs and main pushes, with concurrency
  cancellation. Preserve the reusable security workflow and its policy settings.

## Executed verification

```bash
python -m unittest discover -s tests -v
python scripts/check_primary_adoption.py
```

Repair result: **52 tests passed** on Python 3.12.14 with Graphviz and ImageMagick.
The suite runs all 11 notebook examples in an isolated copy; validates 29 valid
fixtures and rejects the intentionally invalid fixture; checks actual artifact
bytes, all six variant outputs, original golden snapshots, and web/CLI regressions.
Dependency consistency and `git diff --check` passed. The Markdown package was
removed from the environment before the final test run.

Independent review of the shared generation/CLI code found no remaining actionable
issue in its bounded scope. This is local Linux and legacy-renderer evidence, not
cross-platform certification, comprehensive arithmetic/methodological validation,
external accessibility acceptance, item-level rights clearance or Rust parity.

## Hosted CI evidence and remaining gate

PR #24 tests: https://github.com/edithatogo/standardflow/actions/runs/44464339747

PR #25 tests: https://github.com/edithatogo/standardflow/actions/runs/44783093490

Each inspected hosted run passed 29 host tests and 29 Docker tests. The offline
security jobs for these heads were cancelled after waiting without an assigned
runner or any executed steps. Runs `44464340646` and `44783093965` require a runner
labelled `self-hosted`, `linux`, `x64`, `ai-security-offline` and the configured
pinned offline security image. This review neither waives that gate nor claims
security execution. The repair's own hosted result must be read at its new head.

## Export and receiving requirements

1. Preserve the repaired source commit and all remaining source branch tips.
2. Import the runnable tree into `standards_check/legacy/standardflow` with source
   ancestry; retain every original licence and fixture as legacy material.
3. Verify tree identity and ancestry, run the imported 52-test suite, and record
   exact receiving commits and checks in primary Track 03.
4. Preserve unique unmerged work in history, without activating it as the runtime.
5. Complete the primary merge using a merge commit, then make this source private
   and archive it under the user's explicit instruction. Record the observed result.

Existing checklist item IDs/text and legacy diagram limitations remain migration
inputs. This review does not silently relabel requirements or promote legacy
fixtures into authoritative Standard Packs.
