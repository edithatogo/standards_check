#!/usr/bin/env bash
set -euo pipefail

pandoc markdown/archetypes/care-2013.md \
  --from=markdown+task_lists \
  --to=pdf \
  --template=templates/pandoc/latex-checklist.tex \
  --pdf-engine=xelatex \
  --lua-filter=filters/forms.lua \
  -o test.pdf
