# Static contract preview

The private Hugging Face Space is [StandardFlow Research Contracts](https://huggingface.co/spaces/edithatogo/standardflow-contracts).
GitHub remains authoritative; the Space is not a data repository or model deployment.

Generate the exact authored-only package from a verified checkout:

```sh
python -m scripts.render_contract_preview --output target/contracts-preview --revision "$(git rev-parse HEAD)"
```

The existing [Assurance workflow](../../.github/workflows/ci.yml) generates the same package under
`target/coverage/contracts-preview/` and retains it inside the Python coverage artifact.
The generator validates both publication contracts, the analytical plan and all declared
table, experiment, task, issue and workflow references before generating a static HTML
page and exact contract/protocol downloads. File digests and the tested revision are in
`manifest.json`. It rejects non-planned publications and writes only an explicit allowlist.
No source prose, raw ontology/citation data, benchmark labels, vectors or manuscript data
are mirrored. A future approved results view requires a new release projection, not a
relaxation of this guard.

Deploy only after checking the exact package and destination, using the authenticated
Hugging Face file interface to upload the contents of the generated directory to the
private Space root, or the native Hub CLI (already authenticated by the owner):

```sh
hf upload edithatogo/standardflow-contracts target/contracts-preview . --repo-type space
```

Verify the receiving repository commit, visibility, exact file inventory and hashes;
inspect the rendered page and links, including mobile/keyboard/accessible table navigation.
No token is needed for the offline build. Do not embed credentials or configure an
automatic remote write on pull requests.

On 26 November 2026 the authenticated Hugging Face connector reported successful creation
of the private static Space. An attempted authenticated sandbox route to populate it was
blocked by HTTP 402 Payment Required; no paid compute was used. The empty-repository
HEAD lookup was not available. This is a deployment hold, not a deployed site receipt.
Do not publish any empirical dataset until the separately reviewed #162 release contract
is approved.
