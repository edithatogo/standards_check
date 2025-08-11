#!/usr/bin/env bash
set -euo pipefail

command -v pandoc >/dev/null 2>&1 || { echo "[ERROR] pandoc not found. Please install Pandoc." >&2; exit 1; }

has_typst_writer=0
if pandoc --list-output-formats | grep -q "^typst$"; then
  has_typst_writer=1
fi

template="templates/pandoc/latex-checklist.tex"
forms_flag=()
if [[ "${FORMS:-}" == "eforms" ]]; then
  forms_flag=(-M use_eforms=true)
  echo "Using eForms package for PDF widgets."
fi
[[ -f "$template" ]] || { echo "[ERROR] Template missing: $template" >&2; exit 1; }

filter_args=()
if [[ -f filters/forms.lua ]]; then
  filter_args+=(--lua-filter=filters/forms.lua)
  echo "Using Lua filter: filters/forms.lua"
fi

shopt -s nullglob
while IFS= read -r -d '' md; do
  rel=${md#markdown/}
  dir=$(dirname "$rel")
  base=$(basename "$rel" .md)
  title=$(head -n 1 "$md" | sed 's/# //')

  mkdir -p "latex/$dir" "pdf/$dir" "docx/$dir"

  echo "Building $rel ..."

  # LaTeX
  pandoc_args=(
    "$md"
    --from=markdown+task_lists
    --to=latex
    --template="$template"
  )
  if [ ${#forms_flag[@]} -gt 0 ]; then
    pandoc_args+=("${forms_flag[@]}")
  fi
  pandoc_args+=(-o "latex/$dir/$base.tex")
  pandoc "${pandoc_args[@]}"

  # PDF (via Typst)
  if [[ $has_typst_writer -eq 1 ]]; then
    pandoc "$md" \
      --from=markdown+task_lists \
      --to=pdf \
      --pdf-engine=typst \
      --metadata title="$title" \
      -o "pdf/$dir/$base.pdf"
  else
    echo "[WARNING] Typst writer not found. Skipping PDF generation for $rel."
  fi

  # DOCX
  pandoc "$md" \
    --from=markdown+task_lists \
    --to=docx \
    -o "docx/$dir/$base.docx"

  # Typst (if writer available)
  if [[ $has_typst_writer -eq 1 ]]; then
    mkdir -p "typst/$dir"
    pandoc "$md" \
      --from=markdown+task_lists \
      --to=typst \
      -o "typst/$dir/$base.typ"
  fi

done < <(find markdown -type f -name "*.md" ! -name "_template.md" ! -name "index.md" -print0)

echo "Build complete."
