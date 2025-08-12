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
echo "<h2>Implemented Checklists</h2>" >> "$BODY_CONTENT_TMP"
echo "<div class='list-group mb-4'>" >> "$BODY_CONTENT_TMP"
yq -r '.items[] | select(.status == "mapped") | .id' "$INDEX_YAML" | while read -r id;
do
  title=$(yq -r ".items[] | select(.id == \"$id\") | .title" "$INDEX_YAML")
  level=$(yq -r ".items[] | select(.id == \"$id\") | .level" "$INDEX_YAML")
  html_file="${id}.html"
  if [ "$level" == "archetype" ]; then
    echo "<a href=\"./archetypes/${html_file}\" class=\"list-group-item list-group-item-action\">${title}</a>" >> "$BODY_CONTENT_TMP"
  else
    echo "<a href=\"./variants/${html_file}\" class=\"list-group-item list-group-item-action\">${title}</a>" >> "$BODY_CONTENT_TMP"
  fi
done
echo "</div>" >> "$BODY_CONTENT_TMP"

echo "<h2>Placeholder Checklists</h2>" >> "$BODY_CONTENT_TMP"
echo "<div class='list-group mb-4'>" >> "$BODY_CONTENT_TMP"
yq -r '.items[] | select(.status != "mapped") | .id' "$INDEX_YAML" | while read -r id;
do
  title=$(yq -r ".items[] | select(.id == \"$id\") | .title" "$INDEX_YAML")
  level=$(yq -r ".items[] | select(.id == \"$id\") | .level" "$INDEX_YAML")
  html_file="${id}.html"
  if [ "$level" == "archetype" ]; then
    echo "<a href=\"./archetypes/${html_file}\" class=\"list-group-item list-group-item-action\">${title}</a>" >> "$BODY_CONTENT_TMP"
  else
    echo "<a href=\"./variants/${html_file}\" class=\"list-group-item list-group-item-action\">${title}</a>" >> "$BODY_CONTENT_TMP"
  fi
done
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