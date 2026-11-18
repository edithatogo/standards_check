# Conductor tracks

Status, implementation completeness and evidence are separate. These tracks are **planned** and **contracted** until implementation and verification receipts say otherwise.

| ID | Track | Horizon | Depends on | Outcome |
| --- | --- | --- | --- | --- |
| 00 | [Platform foundation](tracks/00-platform-foundation/spec.md) | short | none | Conductor, Rust workspace, evidence model and baseline CI |
| 01 | Canonical Standard Pack | short | 00 | One authoritative versioned semantic filesystem and lockfile |
| 02 | Checklist, document and diagram engines | short | 01 | Generic accessible renderers, including complete PRISMA 2020 flows |
| 03 | History-preserving standardflow import | short | 00, 01, 02 | Import useful legacy code/tests and cut over only after parity |
| 04 | Research ecosystem contracts | medium | 01, 02 | Exact-pinned evidence exchange with SearchRight, SourceRight and AuthenText |
| 05 | Maximal assurance, release and external validation | short→long | 00–04 | Deep quality/security engineering and evidence-gated maturity |

The detailed sequencing and later capabilities are in [`roadmap.md`](./roadmap.md). Tracks 01–05 are roadmap entries pending creation through `conductor-new-track`; Track 00 is the active implementation track.
