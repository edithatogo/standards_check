# Contributing

Thank you for contributing. This repository is documents-first and pipeline-driven.

- Start with `AGENTS.md` for coding style, naming, and PR requirements.
- Use `ROADMAP.md` and `todos/` to pick the next task.
- If you have internet access, follow `HANDOFF.md` to verify sources, ingest originals, and transcribe items.

## Core Workflow

This project uses a data-driven approach to manage checklists. All checklist information is stored in YAML files under the `source/` directory. The primary file is `source/index.yml`, which contains a master list of all checklists and their metadata.

To add a new checklist, you must first add a new entry to `source/index.yml`. Then, run the following command to generate the necessary files:

`make scaffold`

This will create the markdown file, citation file, and other necessary assets based on the information in `source/index.yml`. **Do not create these files manually.**

## Quick Commands
- `make validate`: Run all local validators.
- `make build`: Generate PDF/LaTeX/DOCX from Markdown.
- `make scaffold`: Create missing Markdown stubs from the index.
- `make list-tbd`: Find all placeholder "TBD" values.
- `make index`: Regenerate `markdown/index.md`.
- `make clean`: Remove generated artifacts.

## PR Checklist
- Use the provided PR template and complete all boxes.
- Keep PRs focused (one checklist or a small batch).
- Include artifacts (PDF/DOCX) via CI run links when helpful.
