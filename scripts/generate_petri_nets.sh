#!/usr/bin/env bash
set -euo pipefail

# Check for dependencies
command -v python3 >/dev/null 2>&1 || { echo "[ERROR] python3 not found. Please install Python 3." >&2; exit 1; }

# Do not resolve or install mutable dependencies as a side effect of generating files.
python3 -c 'import pm4py' 2>/dev/null || {
  echo "[ERROR] pm4py unavailable. Install the pinned project prerequisites explicitly (scripts/petri_net_generation/requirements.txt)." >&2
  exit 1
}

# Find all YAML files in the source directory, excluding index.yml and templates
find source -type f -name "*.yml" ! -name "index.yml" ! -name "*template.yml" -print0 | while IFS= read -r -d '' yml_file; do
  echo "Processing $yml_file..."

  rel_path=${yml_file#source/}
  dir=$(dirname "$rel_path")
  base=$(basename "$rel_path" .yml)
  markdown_file="markdown/$dir/$base.md"
  output_dir="petri-nets/$dir"
  output_pnml="$output_dir/$base.pnml"

  if [ -f "$markdown_file" ]; then
    # Run the Python script
    python3 scripts/petri_net_generation/generate_net.py "$markdown_file" "$output_pnml"
  else
    echo "[WARNING] Markdown file not found for $yml_file, skipping."
  fi
done

echo "Petri net generation complete."
