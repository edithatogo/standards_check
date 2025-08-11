#!/usr/bin/env bash
#
# Creates placeholder files for a new checklist to begin ingestion.
#
# Usage: ./scripts/scaffold_from_index.sh [id]
#
# If an id is provided, only that item is processed. Otherwise, all items
# in the index are checked and any missing files are created.

set -euo pipefail

# Configuration
index_file="source/index.yml"
tpl_md="markdown/_template.md"
tpl_bib="citations/archetypes/.gitkeep" # Empty file
tpl_yml="source/archetypes/_meta.template.yml"

# Check for yq
if ! command -v yq &> /dev/null;
then
    echo "[ERROR] yq is not installed. Please install it to continue."
    exit 1
fi

# File checks
[[ -f "$index_file" ]] || { echo "[ERROR] Missing index: $index_file" >&2; exit 1; }
[[ -f "$tpl_md" ]] || { echo "[ERROR] Missing markdown template: $tpl_md" >&2; exit 1; }
[[ -f "$tpl_bib" ]] || { echo "[ERROR] Missing bib template: $tpl_bib" >&2; exit 1; }
[[ -f "$tpl_yml" ]] || { echo "[ERROR] Missing yml template: $tpl_yml" >&2; exit 1; }

# Target ID from argument
target_id=${1:-}
created_count=0

# Read and process the index file
while IFS= read -r item; do
  read -r id level title <<<"$item"

  # Skip if a target is specified and this is not it
  if [[ -n "$target_id" && "$id" != "$target_id" ]]; then
    continue
  fi

  # Determine track (archetypes/variants)
  track="archetypes"
  if [[ "$level" == "variant" ]]; then
    track="variants"
  fi

  # File paths
  file_md="markdown/$track/$id.md"
  file_bib="citations/$track/$id.bib"
  file_yml="source/$track/$id.yml"

  # Create markdown file if it doesn't exist
  if [[ ! -f "$file_md" ]]; then
    mkdir -p "$(dirname "$file_md")"
    { printf '# %s\n\n' "$title"; cat "$tpl_md"; } > "$file_md"
    echo "Created: $file_md"
    created_count=$((created_count + 1))
  fi

  # Create bib file if it doesn't exist
  if [[ ! -f "$file_bib" ]]; then
    mkdir -p "$(dirname "$file_bib")"
    cp "$tpl_bib" "$file_bib"
    echo "Created: $file_bib"
    created_count=$((created_count + 1))
  fi

  # Create yml file if it doesn't exist
  if [[ ! -f "$file_yml" ]]; then
    mkdir -p "$(dirname "$file_yml")"
    cp "$tpl_yml" "$file_yml"
    echo "Created: $file_yml"
    created_count=$((created_count + 1))
  fi
done < <(yq -r '.items[] | .id + " " + .level + " " + .title' "$index_file")

echo "Scaffold complete. New files: $created_count"
