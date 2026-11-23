# StandardFlow

> **Transition status:** this repository is the primary adoption home for StandardFlow. The existing
> standards corpus and document pipeline remain operational legacy surfaces while the canonical pack,
> Rust execution core and generic artefact engines are implemented through the evidence-aware
> [Conductor programme](conductor/index.md).

StandardFlow is being developed as a machine-actionable research-standards platform: versioned
standards and provenance, deterministic applicability and evidence assessment, plus accessible
checklists, forms, PRISMA/CONSORT/STROBE diagrams and publication artefacts.

## Current repository surface

The established pipeline collects original files and provenance under `source/`, maintains cleaned
Markdown and generated Typst/LaTeX/HTML/PDF/DOCX outputs, and exposes static/API views. These files
are not yet all Canonical Standard Packs. Existing status must not be interpreted as implementation
of the future Rust architecture.

## Costing and valuation reconciliation

The source-aware [costing and valuation reconciliation](reconciliations/costing/README.md) remains
separate from canonical checklists. It classifies 26 sources and provides 106 verified
item/principle mappings, with explicit applicability and coverage limits.

Run `python3 scripts/validate_costing_reconciliation.py` to check catalogue references, status
distinctions and verified-coverage counts. This metadata check also runs through `make validate`;
it does not assess scientific validity.

## Target architecture

```text
authoritative source + rights + anchors
  → Canonical Standard Pack + content lock
  → deterministic Rust resolver and artefact engines
  → checklist / diagram / document / API / MCP / research-object projections
```

Presentation formats become generated views rather than competing sources of truth. The generic
diagram engine will use validated recipes and an accessible semantic scene graph; PRISMA 2020 is the
first complete reference pack.

Read:

- [`conductor/index.md`](conductor/index.md) for the project handshake;
- [`conductor/roadmap.md`](conductor/roadmap.md) for short-, medium- and long-horizon work;
- [`docs/architecture/STANDARDFLOW_ARCHITECTURE.md`](docs/architecture/STANDARDFLOW_ARCHITECTURE.md);
- [`docs/architecture/RESEARCH_ECOSYSTEM.md`](docs/architecture/RESEARCH_ECOSYSTEM.md).

## Conductor

The official `gemini-cli-extensions/conductor` plugin is installed as an exact gitlink at
`.agents/plugins/conductor`. The expected revision is recorded in
[`metadata.revision` in the local router](.agents/skills/conductor/SKILL.md) and checked
against the gitlink by `scripts/audit_foundation.py`.

Initialise submodules after cloning:

```bash
git submodule update --init --recursive
```

## Foundation validation

```bash
python scripts/validate_foundation.py
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
cargo test --workspace --all-targets --all-features --locked
```

## Imported legacy renderer

The Python/Graphviz reference application is retained under
[`legacy/standardflow`](legacy/standardflow). This repository is its maintained
home; use the [Track 03 runbook](conductor/tracks/03-standardflow-import/spec.md)
for CLI, web, notebooks and Docker commands. The import preserves the repaired
source tree and all recorded branch histories. Legacy checklist text and diagrams
remain reference material, separate from the Rust engine and canonical packs.

Use the [isolated receiving environment](legacy/README.md) for pinned dependencies
and source-to-subtree parity checks, which work without access to the old remote.

The old `edithatogo/standardflow` remote is private and archived. This repository
remains the active home, with the exact imported tree and all nine source histories
preserved. The [Track 03 verification record](conductor/tracks/03-standardflow-import/verification.md)
records consolidation and retirement; full legacy-to-Rust semantic parity remains
tracked here.

## Legacy corpus workflow

Until the canonical migration is complete:

- originals and sidecars remain under `source/{archetypes,variants}/`;
- cleaned checklist views remain under `markdown/`;
- `make validate`, `make build`, `make scaffold` and `make index` retain their existing meanings;
- generated API/document artefacts are compatibility outputs, not the future semantic authority.

Do not ingest or reproduce third-party standard text unless item-level rights and provenance are
recorded. Where reuse is restricted, retain canonical links, hashes, citations and normalized local
requirements without redistributing the source.

## Ecosystem boundaries

SearchRight remains authoritative for systematic-search and review state, including PRISMA counts.
SourceRight remains authoritative for CSL and citation verification. AuthenText supplies bounded
text-pattern findings. StandardFlow owns standards identity, applicability, evidence expectations and
standards-derived artefact generation. The projects integrate through exact-pinned contracts rather
than being merged into one codebase.

## Licensing

Repository-authored Rust code is dual licensed under MIT or Apache-2.0. Existing documentation and
imported source material retain their stated licences. The history-preserving `standardflow`
migration must retain Apache-2.0 notices and item-level rights. See `LICENSE.md` and source sidecars
for the current corpus rules.
