# Conductor tracks

Status, implementation completeness and evidence are separate. Historical hosted receipts apply
to their recorded commit. Local repair evidence does not mark the final merged head's hosted
acceptance complete. Compiler and synthetic-fixture checks do not establish methodological
validity, source reconciliation, external accessibility certification, rights or publication.

| ID | Track | Horizon | Depends on | Status | Implementation | Evidence | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 00 | [Platform foundation](tracks/00-platform-foundation/spec.md) | short | none | in progress | source implemented; PR #59 merged | compiler verified at reviewed foundation head | Conductor, Rust workspace and baseline CI; brownfield audit remains open |
| 01 | [Canonical Standard Pack runtime](tracks/01-canonical-standard-pack/spec.md) | short | 00 | implementation complete | source implemented; integration acceptance pending | original-head hosted fixtures and local repair fixtures proven | Strict packs, rights, canonicalization, locks and CLI; final-head hosted checks pending |
| 02 | [Semantic diagram engine and PRISMA 2020 flows](tracks/02-semantic-diagram-prisma/spec.md) | short | 01 | implementation complete | source implemented; integration acceptance pending | original-head hosted fixtures and local repair fixtures proven | Four PRISMA families, accessible scene structure and 12 golden outputs; final-head hosted checks pending |
| 03 | History-preserving standardflow import | short | 00, 01, 02 | planned | contracted | contracted | Import useful legacy code/tests and cut over only after parity |
| 04 | Research ecosystem contracts | medium | 01, 02 | planned | contracted | contracted | Exact-pinned evidence exchange with SearchRight, SourceRight and AuthenText |
| 05 | Maximal assurance, release and external validation | short to long | 00 through 04 | planned | contracted | contracted | Deep quality/security engineering and evidence-gated maturity |

Revision-bound receipts and open gates are retained in each active track's metadata, plan and
evidence file. PR #60 is now based on `main`; PR #59 is no longer an open merge dependency.
The detailed sequencing and later capabilities remain in [`roadmap.md`](./roadmap.md).
