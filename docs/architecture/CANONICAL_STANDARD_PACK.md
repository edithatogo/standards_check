# Canonical Standard Pack v1

A pack is a portable, versioned directory whose integrity and rights can be evaluated without a network connection.

```text
packs/<namespace>/<family>/<edition>/
├── pack.json
├── requirements.json
├── relationships.json
├── applicability.json
├── artefacts/
├── sources/
│   ├── manifest.json
│   └── anchors.json
├── rights.json
├── citations.csl.json
├── translations/
├── tests/
└── standardflow.lock.json
```

## Required distinctions

- authoritative verbatim text, where redistribution is permitted;
- normalized machine requirement;
- explanatory guidance;
- local interpretation or implementation note;
- source anchor and retrieval evidence;
- item-level rights and redistribution status.

Every requirement has a stable identifier independent of display numbering. A pack release is content-addressed. Supersession, extension, companion, conflict, mapping and translation relations are explicit. Lockfiles pin pack IDs, versions, hashes, rule engines and artefact recipes.
