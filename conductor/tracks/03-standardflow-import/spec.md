# Track 03: History-preserving StandardFlow import

## Objective and authority

Keep `edithatogo/standards_check` as the primary StandardFlow repository. Preserve the
repaired Python/Graphviz application under `legacy/standardflow`, its exact Git tree,
licence notices and every source branch history. On 22 November 2026 the user directed
export followed by making `edithatogo/standardflow` private and archived. That is
repository consolidation; replacement of legacy behavior by Rust remains separate.

The canonical import manifest is [import.json](import.json). The manifest inside the
imported application is historical source material and does not override this receipt.
The legacy files are compatibility/reference inputs; they do not become Canonical
Standard Packs, acquire new rights or supply authoritative counts.

## Acceptance

- Imported subtree OID equals the pinned repaired source tree OID.
- The repaired commit and all recorded source branch heads are reachable ancestors.
- The imported 52-test suite, including all 11 notebooks, passes from its new location.
- Root CI checks provenance and runs host/container legacy tests; nested workflows stay inert.
- Preserve the primary canonical contracts. The separate Ponytail review fixes validation,
  HTML builds and SVG reading order/identifier bounds; its two changed SVGs retain the same
  geometry and labels. See [the review receipt](../../ponytail-review-20261122.md).
- A normal merge commit preserves source ancestry; squash/rebase merging is inappropriate.
- Primary merge and a recoverable source export precede the requested private archival.

## Use the imported application

Clone this primary repository. All legacy commands run from the imported directory:

```bash
cd legacy/standardflow
python -m pip install -r requirements.txt
python -m src.cli validate data/prisma_data.json
python -m src.cli generate data/prisma_data.json -o prisma-example.svg
python -m unittest discover -s tests -v
python -m web.app
```

Install Graphviz and ImageMagick for the legacy formats. From the primary repository
root, the container build must use the subtree as its context:

```bash
docker build --tag standardflow-legacy legacy/standardflow
docker run --rm standardflow-legacy python -m unittest discover -s tests -v
docker compose -f legacy/standardflow/docker-compose.yml up --build
python scripts/check_standardflow_import.py
```

The original imported README's source-clone instructions are retained as historical
bytes; this runbook supersedes them. No network call or private-source checkout is
needed to run the imported application after cloning the primary repository.

## Preserved unmerged work

The extra `feature/implement-guidelines` branch is retained only in Git history. Its
ten newly labelled guideline arrays exactly duplicate the STARD checklist; its copied
schemas and self-generating snapshots do not prove guideline support. Do not promote
that branch's data into active code or standards packs.

The source CI PRs #24 and #25 are retained in history. The root receiving workflow uses
their audited Harden Runner and setup-python pins. Renovate PRs #26 through #29 appeared
during export; their Click, graphviz, ipykernel and jsonschema requirement updates are also preserved only
in history, without claiming those upgrades were tested. The final inventory has
nine branch heads and no tags.

The following source issues remain assurance work under primary Track 05. Archival
does not mark their underlying tasks complete; their historical inventory claims
must be reconciled against the receiving repository before implementation.

| Source issue | Remaining work carried forward |
| --- | --- |
| #12 | Assess property-based, mutation and contract testing and applicable CI gates. |
| #13 | Reconcile maintainer guidance, rulesets, dependency coverage and Codecov needs. |
| #14 | Parent of #12 and #13; retain the unresolved assurance work. |
| #23 | Historical Renovate dashboard; future dependency management belongs here. |

## Recovery and ongoing work

Every source ref name and exact SHA is recorded in import.json. A temporary recovery
clone can recreate those branch refs from the reachable commits, without accessing
the old remote. After verified retirement, the private archived original is an additional
owner-accessible copy. Never delete original source history or replace the exact subtree silently.

If changing legacy behavior later, first preserve this receipt, advance the source/tree
contract deliberately and rerun the receiving tests. Full legacy-to-Rust semantic
parity, source rights, independent method/accessibility review and release qualification
remain open. Source retirement is an explicit user-directed administrative action;
it does not mark those gates complete.

The maintained host dependency profile is separate from the exact source snapshot and
historical Docker requirements. The [23 November dependency qualification](../../../docs/migration/standardflow/dependency-qualification-20261123.json)
records independent and combined Click, graphviz and jsonschema upgrades with unchanged
application artefacts. The optional interactive ipykernel update is not admitted to
that profile. Follow the [receiving runtime instructions](../../../legacy/README.md)
for the maintained host setup; the original commands above retain the historical setup.
