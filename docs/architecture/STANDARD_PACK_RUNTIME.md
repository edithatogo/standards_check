# Canonical Standard Pack runtime

Track 01 turns the pack contract into executable Rust behaviour.

## Runtime guarantees

- Strict Serde decoding rejects unknown fields.
- Stable pack and requirement identifiers reject traversal and non-portable characters.
- Semantic validation keeps pack text, normalized requirements, guidance, rights and evidence expectations distinct.
- Verbatim text is prohibited unless effective item-level rights are `cleared`.
- Imported transcriptions remain usable but emit a stable warning until source reconciliation is recorded.
- Canonical JSON sorts keys, omits insignificant whitespace and rejects floating-point values.
- A deterministic SHA-256 identifies canonical `pack.json` semantics.
- `standardflow.lock.json` records every raw pack file, byte count, SHA-256 and a tree digest.
- Lock generation rejects symbolic links, non-UTF-8 paths, excessive depth, oversized files and aggregate-size overflow.
- Lock writes use a same-directory temporary file and atomic rename.

## CLI

```bash
standardflow --json pack validate packs/org.prisma/prisma/2020/pack.json
standardflow pack canonicalize packs/org.prisma/prisma/2020/pack.json /tmp/prisma.canonical.json
standardflow pack digest packs/org.prisma/prisma/2020/pack.json
standardflow pack lock packs/org.prisma/prisma/2020 --check
```

`--json` returns stable machine-readable success and diagnostic envelopes. Canonical JSON can be written to `-` only in text mode.

## PRISMA reference pack

The first real pack contains the 27 PRISMA 2020 reporting items already present in the repository. It retains the recorded source checksum and CC BY 4.0 attribution, but its verification status is deliberately `imported_unverified`. This distinguishes schema/compiler validity from item-by-item reconciliation with the authoritative source.

The reference pack does not yet implement PRISMA flow diagrams. Diagram recipes, arithmetic invariants and the accessible semantic scene graph remain Track 02 work.
