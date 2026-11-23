# Bounded legacy PRISMA count contract

## Scope and authority

This contract qualifies count preservation for two synthetic database-only examples: one new
review and one updated review. It exercises the preserved Python CLI and the current Rust CLI,
using the [authored paired inputs](../../../contracts/examples/legacy-prisma-parity.json).
It does not select Rust as a replacement for an existing consumer.

The legacy source remains frozen at `dc51d8e392858d5cb4e653aed199563514191efb`, tree
`62d8a0e738f0255cc59822ae4e661568090a213e`, with all nine recorded revisions recoverable.
The runner verifies that [import contract](../../../conductor/tracks/03-standardflow-import/import.json)
before and after executing the cases. The two original fixtures are read directly from
`legacy/standardflow/data/prisma_data.json` and `prisma_2020_updated_data.json`; they are not rewritten.

The current Rust contract distinguishes records, reports and studies. The legacy model lacks
several of those distinctions. PRISMA's [flow templates](https://www.prisma-statement.org/prisma-2020-flow-diagram)
distinguish new and updated reviews and source streams; its
[explanation and elaboration, item 16a](https://pmc.ncbi.nlm.nih.gov/articles/PMC8005925/)
describes the selection counts and exclusion information. These sources inform the bounded mapping;
neither a synthetic example nor a successful renderer establishes the validity of a real review.

## Explicit conditions and count mapping

Every paired input supplies its Rust counts separately. The runner does not translate a legacy
file or fill absent fields. The fixture author explicitly declares database-only identification,
duplicate removal as the only removal before screening, complete retrieval of sought reports,
legacy full-text articles representing reports, one report per included study, and an exclusion
reason partition. The updated example also declares disjoint previous and new studies.
These declarations are synthetic fixture conditions, not facts inferred from the old format.

The updated legacy fields use the `new_` prefix except for the prior and total study counts.

| Legacy observation | Rust observation checked | Required condition |
| --- | --- | --- |
| Records identified | Database records and identification total | Register count explicitly zero |
| Records after duplicate removal | Records screened | No other removal before screening |
| Records screened and excluded | Matching screening counts | Identified = duplicates + screened |
| Full-text articles assessed | Reports sought and assessed | Screened = excluded records + assessed reports; none unavailable |
| Full-text articles excluded | Sum of supplied report exclusion reasons | Reasons form the supplied partition of excluded reports |
| Studies included | New included studies and reports | One report per included study; assessed = excluded reports + included reports |
| Previous and total studies | Previous and total studies and reports | One report per study in both groups; total = previous + new |

The new example checks 1,000 identified, 200 duplicates, 800 screened, 200 records excluded,
600 reports assessed, 300 reports excluded and 300 included studies/reports. The updated example
checks 500 identified, 100 duplicates, 400 screened, 100 records excluded, 300 reports assessed,
150 reports excluded, 150 new and 10 previous studies/reports, and a total of 160.

The legacy renderer repeats its inclusion count in a node labelled as quantitative synthesis.
That unsupported synthesis claim is excluded from comparison: node `H` in the new example and
node `J` in the updated example. The runner does not infer meta-analysis membership.

## Executable evidence

Use Python 3.12 with the receiving repository's
[legacy dependency profile](../../../requirements/legacy-standardflow.txt), Graphviz `dot`, and
the exact Rust toolchain in `rust-toolchain.toml`:

```sh
cargo build --locked -p standardflow-cli
python -m unittest tests.test_validate_artifacts tests.test_legacy_prisma_qualification -v
python -m scripts.qualify_legacy_prisma --rust-cli target/debug/standardflow --output qualification.json
```

The qualifier fails if a dependency, declared condition, count or expected rejection is missing.
It launches the real legacy module entry point without inherited `PYTHONPATH`, extracts counts
from its Graphviz SVG, and compares them with the authored expectations. It renders Rust scene
JSON, SVG and text, checks every expected visible and accessible node count and reading order,
checks the SVG/text projections against the scene, and verifies that the text includes every
scene stage and relationship. It compares 16 legacy nodes and 20 Rust nodes across the two cases.
Its receipt records the repository revision and working-tree status, source provenance, executable
and corpus digests, dependency versions and the hashes of all eight generated artifacts.

Two deliberately inconsistent pairs record validation differences separately from preservation:

| Counterexample | Preserved Python behavior | Required Rust behavior |
| --- | --- | --- |
| Screened count increased without changing the flow | Renders the inconsistent count | Exit 1, `SF-PRISMA-010`, no output |
| Updated total increased without changing previous/new counts | Renders the inconsistent total | Exit 1, `SF-PRISMA-040`, no output |

Those rejections are intentional improvements. They must not be counted as identical acceptance
behavior or removed to make a parity result appear broader.

## Accessibility evidence boundary

The artifact validator previously accepted nonempty but wrong accessible labels, incorrect visible
counts, a different title, an incomplete description or metadata block, and a plain-text file
containing only the review ID. Regressions now require the title, description, metadata, accessible
labels, visible lines and text export to match the scene; existing unique-reference and DOM-order
checks remain. XML attribute whitespace normalization is respected when comparing labels.

This is a check of structural fidelity. W3C's
[complex-image guidance](https://www.w3.org/WAI/tutorials/images/complex/) calls for text alternatives
that convey the essential information. A correct projection helps preserve that information, but
does not establish how a browser, embedding mode or assistive technology presents it. W3C's
[preliminary evaluation guidance](https://www.w3.org/WAI/test-evaluate/preliminary/) also separates
initial checks from comprehensive accessibility evaluation.

## Unsupported cases and remaining gates

| Case outside this qualification | Evidence still needed |
| --- | --- |
| Multiple reports per study, duplicate reports or uncertain study identity | Explicit report-to-study and deduplication evidence |
| Registers, other source streams, automation or other removal before screening | Consumer-authored source/removal counts and corresponding paired fixtures |
| Retrieval failures or unknown retrieval status | Explicit sought, unavailable and assessed report counts |
| Real exclusion reasons or synthesis membership | Author-supplied decisions and independent methodological review |
| Overlap between previous and new review populations | Defined identity/lineage rules and verified totals |
| Other PRISMA families, CONSORT, STROBE or checklists | Separate consumer contracts and executable acceptance cases |
| Layout, styling, PNG/PDF/TIFF/Typst, web or notebook behavior | Exact consumer format and interaction requirements |
| Browser and assistive-technology behavior | Independent review of inline/file/embedded SVG, discoverable long descriptions, navigation, zoom and contrast |

An independent methodological receipt must name its reviewer, source interpretation and reviewed
cases, including record/report/study identity and updated-review lineage. An accessibility receipt
must name the browser, assistive technology, versions, embedding mode and observed tasks, including
reading counts and following the exclusion and update branches. Neither receipt is supplied by
this synthetic differential run. Rights review and external-consumer acceptance remain separate
gates in the migration track.

No consumer is switched by this contract. The preserved legacy CLI remains the recovery surface;
a later cutover needs a consumer-specific acceptance and rollback receipt covering its real inputs
and outputs.
