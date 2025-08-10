#!/usr/bin/env bash
set -euo pipefail

# Check for dependencies
command -v pandoc >/dev/null 2>&1 || { echo "[ERROR] pandoc not found. Please install Pandoc." >&2; exit 1; }
command -v yq >/dev/null 2>&1 || { echo "[ERROR] yq not found. Please install yq." >&2; exit 1; }

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

    # Use yq to extract and format metadata for pandoc, mapping fields to CSL JSON
    metadata=$(yq -o=json '{
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
    }' "$yml_file")


    # Generate BibTeX (.bib)
    echo "---" > "$output_dir/$base.bib"
    echo "$metadata" >> "$output_dir/$base.bib"
    echo "---" >> "$output_dir/$base.bib"
    pandoc -f markdown -t biblatex "$output_dir/$base.bib" -o "$output_dir/$base.bib"


    # Generate RIS (.ris) if supported
    if pandoc --list-output-formats | grep -q "^ris$"; then
      echo "---" > "$output_dir/$base.ris"
      echo "$metadata" >> "$output_dir/$base.ris"
      echo "---" >> "$output_dir/$base.ris"
      pandoc -f markdown -t ris "$output_dir/$base.ris" -o "$output_dir/$base.ris"
    else
      echo "[WARNING] RIS output format not supported by this version of Pandoc. Skipping .ris generation for $yml_file."
    fi
  fi
done

echo "Citation generation complete."
