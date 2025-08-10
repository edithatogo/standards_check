# Copilot Instructions for Standards Check Repository

## Repository Overview

This repository processes academic publication checklists through a multi-stage pipeline: `source/` → `markdown/` → `typst/` → `latex/`. It maintains two tracks in each stage:
- **archetypes/**: High-level checklists (e.g., `prisma-2020`, `consort-2010`)
- **variants/**: Discipline-specific extensions (e.g., `prisma-scr-2018`, `prisma-nma`)

**Size**: ~50 files across pipeline stages | **Type**: Documentation processing | **Languages**: Bash scripts, Markdown, YAML, LaTeX templates | **Target**: Multi-format academic checklist generation (PDF, LaTeX, DOCX, Typst)

## Environment Setup & Dependencies

**CRITICAL**: Always install required dependencies before any build operations:
```bash
sudo apt-get update
sudo apt-get install -y pandoc texlive-xetex texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended
```

**Validation**: Verify Pandoc installation: `pandoc --version` (should show 3.1.3+)

## Build, Test & Validation Commands

### Essential Command Sequence
**ALWAYS** run validation before making changes:
```bash
make validate          # Run all validators (may initially fail - see Known Issues)
```

**Build Commands** (require dependencies above):
```bash
make build             # Generate PDF/LaTeX/DOCX from markdown using Pandoc
FORMS=eforms make build # Enhanced build with interactive PDF widgets
```

**Utility Commands**:
```bash
make scaffold          # Create missing markdown files from source/index.yml
make index             # Generate markdown/index.md with all checklist links
make list-tbd          # Find placeholder "TBD" values needing completion
make clean             # Remove generated artifacts (pdf/, latex/, docx/)

### Known Issues & Workarounds
- **Validation Failure**: `make validate` currently fails because many markdown files have YAML frontmatter before H1 titles. The validator expects first non-empty line to be `# Title`. This is a known repository state.
- **Build Timing**: Full builds take 30-60 seconds due to LaTeX processing
- **Missing Dependencies**: Build will fail without Pandoc + LaTeX tools
- **TBD Values**: Many YAML files contain "TBD" placeholders for metadata (use `make list-tbd` to find them)
- **Enhanced Forms**: `FORMS=eforms` build requires additional LaTeX packages not available in standard setup

## Project Architecture & File Layout

### Directory Structure
```
├── source/{archetypes,variants}/    # Raw checklists + YAML metadata
├── markdown/{archetypes,variants}/  # Canonical markdown format
├── typst/{archetypes,variants}/     # Typst format output
├── latex/{archetypes,variants}/     # LaTeX format output
├── scripts/                         # Validation and build helpers
├── templates/pandoc/                # Pandoc conversion templates
├── schemas/                         # JSON schemas for validation
├── .github/workflows/               # CI/CD automation
└── pdf/, docx/                      # Generated output directories
```

### Key Configuration Files
- `pandoc.yaml`: Pandoc build settings (template, PDF engine, metadata)
- `source/index.yml`: Master checklist registry with required metadata
- `templates/pandoc/latex-checklist.tex`: LaTeX template for PDF generation
- `Makefile`: Primary build interface

### CI/CD Pipeline
**GitHub Actions**: `.github/workflows/build-docs.yml`
- **Triggers**: Changes to `markdown/**`, templates, or build scripts
- **Process**: Validates → Installs dependencies → Builds → Uploads artifacts
- **Artifacts**: PDF, LaTeX, and DOCX files downloadable from Actions tab

### Validation Requirements
**File Naming**: All files must use kebab-case (e.g., `prisma-2020.md`)
**Structure**: Each checklist requires triplet files across stages:
- `source/{track}/<name>.{yml,pdf,html,etc}`
- `markdown/{track}/<name>.md`
- `typst/{track}/<name>.typ`
- `latex/{track}/<name>.tex`

**Markdown Format**:
- One H1 (`# Title`) per file as first non-empty line
- Consistent sections: Title, Scope, Items, Reference
- Task lists (`- [ ]`) for checkboxes in PDF output
- Text fields: `[Notes]{.textfield name=field_name width=12cm}`

## Content Pipeline Workflow

### Adding New Checklists
1. **Source**: Add raw file to `source/{archetypes|variants}/` with sidecar YAML
2. **Markdown**: Create clean `.md` in `markdown/` using template structure
3. **Convert**: Run `make build` to generate typst/latex outputs
4. **Validate**: Run `make validate` to check formatting compliance

### Interactive PDF Features
- **Basic**: Use `make build` for standard PDF checkboxes (recommended)
- **Enhanced**: Use `FORMS=eforms make build` for rich form widgets (requires additional LaTeX packages not in standard install)
- **Authoring**: Use task lists (`- [ ]`) and `.textfield` spans in markdown
- **Lua Filter**: `filters/forms.lua` automatically converts task lists to form fields

## Dependencies & Architecture Notes

**External Dependencies**:
- **Pandoc 3.1.3+**: Core conversion engine
- **LaTeX (XeLaTeX)**: PDF generation via texlive packages
- **Optional**: Typst writer for .typ output

**Internal Dependencies**:
- Lua filters in `filters/` directory automatically loaded if present
- Template system in `templates/pandoc/`
- JSON schemas in `schemas/` for validation

## Quick Reference: Root Directory Files
```
.editorconfig          # Editor configuration
.gitignore            # Git ignore patterns
AGENTS.md             # Coding style and PR guidelines
CHANGELOG.md          # Version history
CONTRIBUTING.md       # Contribution guidelines
HANDOFF.md           # Next-agent instructions
LICENSE.md           # Licensing (CC BY 4.0 docs, MIT code)
Makefile             # Build interface
README.md            # Project overview and quickstart
ROADMAP.md           # Development phases and planning
pandoc.yaml          # Pandoc build configuration
```

## Agent Instructions

**TRUST THESE INSTRUCTIONS**: Only search/explore if information here is incomplete or incorrect. This repository has consistent patterns - use them rather than reinventing.

**For Build Issues**: Always check dependency installation first, then validate file naming conventions.
**For Validation Failures**: Check YAML frontmatter vs H1 header requirements in affected files.
**For New Features**: Follow existing patterns in similar files; maintain cross-stage consistency.
**For Testing Changes**: Use `make validate` and spot-check generated PDF outputs to verify formatting.

### Common Agent Tasks & Patterns
**Adding a new checklist**: Follow the pipeline `source/` → `markdown/` → run `make build`
**Fixing validation errors**: Check kebab-case naming and H1 header placement
**Updating metadata**: Edit YAML sidecars in `source/`, not just markdown
**Converting formats**: Always use `make build` rather than manual Pandoc commands
**Debugging builds**: Check `pandoc --version` and LaTeX installation first