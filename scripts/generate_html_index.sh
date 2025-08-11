#!/bin/bash
#
# Generates the main index.html page for the web portal.
# Reads source/index.yml and creates a list of links to each checklist.

set -e

# --- Configuration ---
INDEX_YAML="source/index.yml"
TEMPLATE_FILE="templates/pandoc/html_template.html"
OUTPUT_DIR="html"
OUTPUT_FILE="${OUTPUT_DIR}/index.html"
PROJECT_TITLE="Reporting Standards Checklists"

# --- Helper Functions ---
function log() {
  echo "[INFO] $1"
}

# --- Main ---
log "Starting HTML index generation..."

# Check for input file
if [ ! -f "$INDEX_YAML" ]; then
  echo "[ERROR] Cannot find index file: $INDEX_YAML"
  exit 1
fi

# Create a temporary body file
BODY_CONTENT_TMP=$(mktemp)
trap 'rm -f "$BODY_CONTENT_TMP"' EXIT

# Generate the body of the index page
# This is a simple parser for the specific YAML structure.
# It looks for lines starting with "  - id:" to identify a checklist entry.
echo "<h2>Checklist Archetypes</h2>" >> "$BODY_CONTENT_TMP"
echo "<div class='list-group mb-4'>" >> "$BODY_CONTENT_TMP"
grep -E "^  - id:" "$INDEX_YAML" | while read -r line; do
  id=$(echo "$line" | sed 's/^  - id: //')
  title=$(grep -A 1 "id: $id" "$INDEX_YAML" | grep "title:" | sed 's/    title: //')
  html_file="${id}.html"
  echo "<a href=\"./archetypes/${html_file}\" class=\"list-group-item list-group-item-action\">${title}</a>" >> "$BODY_CONTENT_TMP"
done

# This is a placeholder for variants, assuming a similar structure
# TODO: Add logic for variants when their structure is confirmed in index.yml
# echo "<h2>Checklist Variants</h2>" >> "$BODY_CONTENT_TMP"
# echo "<div class='list-group'>" >> "$BODY_CONTENT_TMP"
# ... logic for variants ...
# echo "</div>" >> "$BODY_CONTENT_TMP"

echo "</div>" >> "$BODY_CONTENT_TMP"


# Use pandoc to apply the main template to our generated body
log "Applying HTML template..."
pandoc \
  --from=html \
  --to=html \
  --template="$TEMPLATE_FILE" \
  --metadata title="$PROJECT_TITLE" \
  --output="$OUTPUT_FILE" \
  "$BODY_CONTENT_TMP"

log "Successfully generated index page at ${OUTPUT_FILE}"
