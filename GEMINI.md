# Project Overview

This repository is a pipeline for processing and converting academic publication checklists. It takes source files in various formats (PDF, DOCX, etc.), converts them into a canonical Markdown format, and then further processes them into Typst, LaTeX, PDF, and DOCX formats.

The project is organized into a clear directory structure, with separate folders for source files, Markdown, Typst, LaTeX, and generated outputs. The workflow is heavily automated using shell scripts and a GitHub Actions CI/CD pipeline.

## Key Directories

-   `source/`: Contains the original checklist files and YAML sidecar files with metadata.
-   `markdown/`: The canonical version of the checklists in Markdown format.
-   `typst/`: Typst versions of the checklists.
-   `latex/`: LaTeX versions of the checklists.
-   `pdf/`, `docx/`, `html/`: Generated output files.
-   `scripts/`: Automation scripts for building, validation, and other tasks.
-   `schemas/`: JSON schemas for metadata validation.
-   `.github/workflows/`: GitHub Actions workflow for CI/CD.

## Building and Running

The project uses a combination of shell scripts and a `Makefile` to automate tasks.

### Key Commands

-   `make validate`: Run all validation scripts.
-   `make build`: Build all output formats (PDF, DOCX, LaTeX, etc.).
-   `make scaffold`: Create placeholder Markdown files from the `source/index.yml`.
-   `make index`: Generate the main `index.md` file for the Markdown checklists.
-   `make clean`: Remove all generated files.

### Individual Scripts

-   `scripts/build_pandoc.sh`: The core script for converting Markdown files to other formats using Pandoc.
-   `scripts/validate_repo.sh`: A comprehensive script that runs all validation checks.
-   `scripts/ingest_source.sh`: A helper script to download source files and update metadata.

## Development Conventions

-   **Workflow:** The primary workflow is to add new checklists to the `source/` directory, create a corresponding Markdown file in `markdown/`, and then use the build scripts to generate the other formats.
-   **Metadata:** Metadata for each checklist is stored in YAML sidecar files in the `source/` directory, which are validated against the `schemas/sidecar.schema.json` schema.
-   **CI/CD:** The GitHub Actions workflow in `.github/workflows/build-docs.yml` automatically validates and builds the checklists on every push and pull request.
-   **Contribution:** The `AGENTS.md` and `HANDOFF.md` files provide detailed instructions for contributing to the project.
