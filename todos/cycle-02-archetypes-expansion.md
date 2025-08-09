# TODO — Cycle 2: Expand Archetypes

- [ ] Survey EQUATOR and related bodies for additional high-level checklists.
- [ ] Add entries to `source/index.yml` with `level: archetype` and `group`.
- [ ] For each new entry:
  - [ ] Download originals to `source/archetypes/<name>.<ext>` and add sidecar metadata.
  - [ ] Create `markdown/archetypes/<name>.md` from template; include citation.
  - [ ] Create `typst/archetypes/<name>.typ` and `latex/archetypes/<name>.tex`.
  - [ ] Validate: `bash scripts/validate_md.sh` and link checks.
  - [ ] Update `source/index.yml` status fields.

