# Plan

## Phase 1: Link Corrections
- [ ] Task 1: Run `validate_links.py` (if present, or implement it/use existing scripts) to identify broken links.
- [ ] Task 2: Correct links in source `YAML` and `MD` files.

## Phase 2: Schema Validation
- [ ] Task 1: Review current JSON schemas in `schemas/`.
- [ ] Task 2: Ensure `validate_repo.sh` or related validation scripts check all `source/**/*.yml` against `schemas/sidecar.schema.json`. Fix validation errors in existing YAMLs.