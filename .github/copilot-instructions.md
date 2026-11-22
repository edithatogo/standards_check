# StandardFlow repository instructions

Follow [AGENTS.md](../AGENTS.md) and the [Conductor workflow](../conductor/workflow.md).
Read the affected track before changing code, contracts, source material, or generated outputs.

## Working boundaries

- Rust crates implement the canonical pack and diagram runtime. Legacy Markdown, document,
  and API outputs remain compatibility surfaces during migration.
- English checklist sources live under `markdown/en/{archetypes,variants}/`; generated English
  HTML lives under `html/{archetypes,variants}/`. Legacy scaffold paths remain supported.
- Keep authoritative source text, normalized interpretation, and local guidance distinct.
  Preserve item-level rights and provenance; fixture tests do not establish external acceptance.
- Use the existing validators and test commands in `AGENTS.md`. Invalid-input checks must return
  failure, and generated outputs must be reproducible.
- Install only the dependencies needed for the affected task. Rust and Python regression work
  does not require the full document toolchain. `make html` requires Pandoc and yq;
  `scripts/build_pandoc.sh` also requires Typst when the Pandoc Typst writer is available.
- Record current verification and remaining work in Conductor without overwriting historical
  receipts or promoting planned security, migration, accessibility, or publication gates.
