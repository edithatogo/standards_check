# Representation and publication programme — 24 November 2026

Owners: Track 01 representation/source, Track 04 receiving interoperability,
Track 05 software/scientific assurance. Programme issue [#158](https://github.com/edithatogo/standards_check/issues/158);
source census [#111](https://github.com/edithatogo/standards_check/issues/111),
EQUATOR engagement [#118](https://github.com/edithatogo/standards_check/issues/118),
quality [#31](https://github.com/edithatogo/standards_check/issues/31).
Starting main: `675fc9afeaf3dc17c8ddef793b553e2f44b401a7`.

## Decisions and implemented increment

1. StandardFlow's product is a machine-readable reporting-standard representation,
   reconciliation and assurance system. Existing packs and validators remain canonical.
2. [Profile 0.1.0](../../../docs/specifications/reporting-guideline-representation/0.1.0.md)
   is an immutable **draft** with RGI-01–14, explicit five-class directional semantics,
   applicability, rights and evidence boundaries. The [registry](../../../contracts/representation/releases.json)
   binds source bytes and implementation schemas. Version integrity and approval
   references are checked separately from scientific acceptance; `approved_version`
   is null. Published amendments require another version.
3. Reuse #142's directory-wide workflow, `scripts/survey_projections.py` and the
   existing Parquet writer. Do not implement a competing census or database.
4. d1-2B is a conditional complementary-evidence experiment. Its useful test is
   additional supported errors at the same review budget, with harmful changes,
   shared misses, calibration, coverage and cost reported. Standalone superiority
   is not required; independent errors must still be measured.
5. The [publication protocol](../../../docs/research/publication-protocol.v0.1.0.md),
   [experiment/claim contract](../../../contracts/publication/programme.v1.json) and
   [agent skill](../../../.agents/skills/publication-evidence/SKILL.md) define E1 census,
   E2 blinded five-class reference and E3 incremental decision-model utility. All
   three are **planned**; there is no experimental freeze or observed claim.
6. The existing required CI aggregate now includes the existing ESLint hook and
   Rust fmt/strict Clippy. Local pre-commit and required Python CI validate the
   specification and publication records. No branch policy or threshold is weakened.

## Directory integration and inspected evidence

[PR #142](https://github.com/edithatogo/standards_check/pull/142) merged normally at
`15f8470a440c946eebfe0421ae0a4cb8d55a9aaa` after all seven app-bound protected
checks passed on `0af95961c14bba78a5c9aec4b5e0708b64b3eb98` and the addressed
identity-conflict review thread was resolved. Actual artifact inspection verified
ZIP and table hashes, typed schemas, sorted unique keys, exact input joins,
held-status invariants and live row-level regeneration with Polars 1.44.2.

| Snapshot | Directory identities | Acquisition records | Item fingerprints | Review findings |
| --- | ---: | ---: | ---: | ---: |
| Current observation, artifact 14925482519 | 720 | 193 | 0 | 2,338 |
| Historical replay, artifact 14926570626 | 720 | 145 | 95 | 2,241 |

Both came from [run 45405885030](https://github.com/edithatogo/standards_check/actions/runs/45405885030),
tested merge `78f437e6a8c2821bcadd8d12abd53fc250cc3882`, upstream revision
`d74413b15d266334067e1e5c104957601be3ba6c`. Current source-survey artifact
14926436388 has ZIP SHA-256
`f336eeac08d5c3e9081d3864959c2b266bf96e16fd478d14b7eb337ea45a1cd5`;
current projection ZIP: `01a03905363b0d4602b9b5f6699e59d7e76558f0b7098be13151ba70cda4f1ad`;
historical replay ZIP: `fdbadf2ce4dae0893683fd3c6e4b5eb448230819715933f2a700455d51884b7b`.

The current zero-item outcome reflects six held priority acquisitions after provider
timeouts/held alternatives, one bulk article inventory, two held bulk attempts and
184 deferred records. It reused 362 metadata observations. This is faithful coverage
of failures and holds, not successful item-level acquisition. Historical replay's 95
fingerprints are preserved separately; its original input regeneration was not repeated
because those inputs are not included in the replay artifact. No canonical packs promoted.

On receiving main, [Assurance 45407700819](https://github.com/edithatogo/standards_check/actions/runs/45407700819),
privacy, dependency inventory, foundation and Canonical Pack passed. The fresh catalogue
and remaining checks were still running at this observation. Scorecard's container pull
failed and Build Documents built successfully but Pages deployment failed; neither is
silently described as green. Preserve existing #116/#123 operational ownership.

## Format integration and scientific holds

[PR #153](https://github.com/edithatogo/standards_check/pull/153) is the existing
fourteen-cohort comparison. Exact-head actual artifacts were inspected at tested merge
`2fbfdfd7bef6722f242c5d910c0c0fec21f6624a`: both PDF readers recovered all 89 EcoEvo
IDs in order; 88/89 strict fingerprints and 89/89 after explicit layout normalization.
The PDF versus office formats gave 83/89 strict and 89/89 normalized; derivative CSV
item 8.3 remains different. Same-head official-byte receipts confirmed the PDF/DOCX/XLSX
hashes. Source-family holds, missing denominators and non-body content limitations remain.
The known EcoEvo header issue was fixed and independently verified; its review thread
was resolved. The branch was synchronized with #142 receiving main, with 30 focused
merged-tree tests passing; all seven protected checks then passed on `a5b39cc41cf0faf1721da9c5f057caf56464f4b0`.
The PR merged normally at `e2797940a9f46ee0412a4783506a4c36a85372a1`; receiving-main
checks are recorded separately. Both merged feature branches were automatically pruned.

[PR #155](https://github.com/edithatogo/standards_check/pull/155) owns the active
five-class agent/model experiments. The witness-v2 artifact explicitly failed scientific
qualification despite workflow success (6/17 correct consensuses, only one correctly
covered class). A later experiment is separate evidence; never turn green CI or formal
control accuracy into natural-language or production qualification. No competing model
harness or premature model admission is introduced here.

## Prior art and publication contribution

[Batista et al. (2022)](https://doi.org/10.1038/s41597-022-01707-6) already covers
machine-actionable reporting models, JSON-ScheeLD, MIRcat/FAIRsharing and CEDAR export.
The protocol's initial prior-art matrix therefore requires interoperability/reuse
evaluation before a novelty claim. The proposed contribution to test is source/edition
reconstruction, rights-aware provenance, directional obligations and measured multi-method
assurance at directory scale. A technical profile, empirical methods paper and conditional
software paper have separate acceptance criteria. EQUATOR should be asked about the
specification and optional implementation; its endorsement is not assumed.

## Verification and remaining sequence

The final pre-integration working-tree verification passed 452 Python tests with three optional model
skips, 218 subtests, and all 73 Rust tests on the exact maintained Rust 1.100.0 toolchain.
Strict Clippy, Rustfmt, existing schema/pack/recipe validation, foundation audit, Markdown
and index checks also passed. The 22 focused integrity regressions include historical-pin, coordinated-rehash,
failed-run deletion and held-reference denominator corrections. Final PR checks
remain required for the synchronized candidate. Required workflow-policy consumes the existing ESLint pin;
all maintained JS passed and a direct-eval negative probe was rejected. Zizmor reported
no unsuppressed findings; 42 pre-existing suppressions were not changed.

1. Complete current-base integration and receiving evidence for #153 and this increment.
2. Refine #118 with the immutable profile and prior-art framing, attempt the authorized
   GitHub issue once and record the actual result; keep any permission failure explicit.
3. Complete source acquisition/reconstruction by measured failure family, retaining every
   directory identity, exact source bytes and held next action. Qualify rights/interpretation
   before admitting additional packs; #82/#95 remain open.
4. Freeze the prospective publication design, untouched families and decision thresholds;
   preserve historical failed experiments and finish the existing #155 scientific gate.
5. Qualify and execute d1-2B only in the existing isolated model lane, testing complementarity.
6. Complete a real consumer canary, external feedback and release/author acceptance before
   submission. Native fuzz, offline runner, updater handover, provenance/signing and deployed
   accessibility retain their existing issues and require actual execution receipts.

Rollback: revert this additive specification/contract/lint increment. Preserve published
versions and historical experiment receipts; no source, pack rights or consumer state changes.
