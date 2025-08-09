#!/usr/bin/env bash
set -euo pipefail

# Check for dependencies
command -v pandoc >/dev/null 2>&1 || { echo "[ERROR] pandoc not found. Please install Pandoc." >&2; exit 1; }
command -v yq >/dev/null 2>&1 || { echo "[ERROR] yq not found. Please install yq." >&2; exit 1; }

# --- Cleanup ---
TEMP_FILES=()
cleanup() {
  for file in "${TEMP_FILES[@]}"; do
    rm -f "$file"
  done
}
trap cleanup EXIT

# Pandoc needs a dummy input file, even if it's empty
DUMMY_INPUT=$(mktemp)
TEMP_FILES+=("$DUMMY_INPUT")

echo "Finding YAML files with citation metadata..."

find source -type f -name "*.yml" -print0 | while IFS= read -r -d '' yml_file; do
  # Check if the file actually contains the citation key
  if yq -e '.citation' "$yml_file" > /dev/null; then
    echo "Processing $yml_file..."

    # Determine output path
    rel_path=${yml_file#source/}
    dir=$(dirname "$rel_path")
    base=$(basename "$rel_path" .yml)
    output_dir="citations/$dir"
    mkdir -p "$output_dir"

    # Create a temporary metadata file for pandoc
    TEMP_META=$(mktemp)
    TEMP_FILES+=("$TEMP_META")

    # Use yq to extract and format metadata for pandoc, mapping fields to CSL JSON
    yq '{
      "title": .title,
      "id": .id,
      "type": .citation.type,
      "author": .citation.author,
      "DOI": .citation.doi,
      "container-title": .citation.journal,
      "volume": .citation.volume,
      "issue": .citation.issue,
      "page": .citation.pages,
      "year": .citation.year,
      "notes": .citation.notes
    }' "$yml_file" > "$TEMP_META"


    # Generate BibTeX (.bib)
    pandoc -s --metadata-file="$TEMP_META" "$DUMMY_INPUT" -t biblatex -o "$output_dir/$base.bib"

    # Generate RIS (.ris) if supported
    if pandoc --list-output-formats | grep -q "^ris$"; then
      pandoc -s --metadata-file="$TEMP_META" "$DUMMY_INPUT" -t ris -o "$output_dir/$base.ris"
    else
      echo "[WARNING] RIS output format not supported by this version of Pandoc. Skipping .ris generation for $yml_file."
    fi
  fi
done

echo "Citation generation complete."