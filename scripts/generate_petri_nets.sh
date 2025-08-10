#!/usr/bin/env bash
set -euo pipefail

# Check for dependencies
command -v python3 >/dev/null 2>&1 || { echo "[ERROR] python3 not found. Please install Python 3." >&2; exit 1; }

# Install Python dependencies
echo "Installing Python dependencies from requirements.txt..."
python3 -m pip install -r scripts/petri_net_generation/requirements.txt

# Find all YAML files in the source directory, excluding index.yml and templates
find source -type f -name "*.yml" ! -name "index.yml" ! -name "*template.yml" -print0 | while IFS= read -r -d '' yml_file; do
  echo "Processing $yml_file..."

  # Determine output path
  rel_path=${yml_file#source/}
  dir=$(dirname "$rel_path")
  base=$(basename "$rel_path" .yml)
  output_dir="petri-nets/$dir"
  output_pnml="$output_dir/$base.pnml"

  # Run the Python script
  python3 scripts/petri_net_generation/generate_net.py "$yml_file" "$output_pnml"
done

echo "Petri net generation complete."
