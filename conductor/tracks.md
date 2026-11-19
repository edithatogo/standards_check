# Conductor tracks

Status, implementation completeness and evidence are separate. Hosted receipts apply only to
their recorded commit. PR #60's hosted integration acceptance is recorded at
`bfe2255fda85b891c2f68044676c0b777d92c38c`; later revisions require their own checks. Compiler and synthetic-fixture checks do not establish methodological
validity, source reconciliation, external accessibility certification, rights or publication.

| ID | Track | Horizon | Depends on | Status | Implementation | Evidence | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 00 | [Platform foundation](tracks/00-platform-foundation/spec.md) | short | none | in progress | source implemented; PR #59 and #79 merged | compiler verified at PR #79 reviewed head | Conductor/Rust baseline; brownfield inventory and gitlink checks integrated; profile reconciliation remains open |
| 01 | [Canonical Standard Pack runtime](tracks/01-canonical-standard-pack/spec.md) | short | 00 | implementation complete | source implemented; hosted integration accepted | fixture proven at recorded PR #60 revision | Strict packs, rights, canonicalization, locks and CLI; source, rights, migration and external gates remain open |
| 02 | [Semantic diagram engine and PRISMA 2020 flows](tracks/02-semantic-diagram-prisma/spec.md) | short | 01 | implementation complete | source implemented; hosted integration accepted | fixture proven at recorded PR #60 revision | Four PRISMA families and 12 golden outputs; independent source, rights, accessibility, methodology and publication gates remain open |
| 03 | History-preserving standardflow import | short | 00, 01, 02 | planned | contracted | contracted | Import useful legacy code/tests and cut over only after parity |
| 04 | Research ecosystem contracts | medium | 01, 02 | planned | contracted | contracted | Exact-pinned evidence exchange with SearchRight, SourceRight and AuthenText |
| 05 | Maximal assurance, release and external validation | short to long | 00 through 04 | planned | contracted | contracted | Deep quality/security engineering and evidence-gated maturity |

Revision-bound receipts and open gates are retained in each active track's metadata, plan and
evidence file. PR #60 is now based on `main`; PR #59 is no longer an open merge dependency.
The detailed sequencing and later capabilities remain in [`roadmap.md`](./roadmap.md).

## Current reconciliation

Track 00 brownfield audit and Conductor integrity checks merged through [PR #79](https://github.com/edithatogo/standards_check/pull/79) at receiving-main commit `840b8431403035be7e5dec5f22b64ad3ddb20d2b`. Exact-head PR checks passed at `baab246e62f3585237b987f87647eba743f2818e`; receiving-main checks must be recorded separately. The distinct legacy rights, profile and migration gates remain open. See [quality frontier reconciliation](quality-frontier-20261119.md).
