#!/bin/bash

# Checklist Comparison Tool
#
# Compares two checklist markdown files.
#
# Usage:
#   bash scripts/compare_checklists.sh <checklist1.md> <checklist2.md>
#
# Example:
#   bash scripts/compare_checklists.sh consort-2010.md consort-2025.md

set -euo pipefail

# --- Configuration ---
# Base directory where checklists are stored
CHECKLIST_DIR="markdown"

# --- Functions ---
function print_usage() {
  echo "Usage: $(basename "$0") <checklist1.md> <checklist2.md>"
  echo "Compares two checklist files from the '${CHECKLIST_DIR}' directory."
  echo
  echo "Example:"
  echo "  bash $(basename "$0") consort-2010.md consort-2025.md"
}

function list_available_checklists() {
  echo
  echo "Available checklists:"
  find "${CHECKLIST_DIR}" -type f -name "*.md" -exec basename {} \; | sort
}

function find_checklist_path() {
  local checklist_name="$1"
  local file_path
  file_path=$(find "${CHECKLIST_DIR}" -type f -name "${checklist_name}" | head -n 1)

  if [[ -z "${file_path}" ]]; then
    echo "Error: Checklist '${checklist_name}' not found in '${CHECKLIST_DIR}'." >&2
    list_available_checklists >&2
    return 1
  fi
  echo "${file_path}"
}

# --- Main Script ---
if [[ "$#" -ne 2 ]]; then
  print_usage
  list_available_checklists
  exit 1
fi

FILE1_NAME="$1"
FILE2_NAME="$2"

FILE1_PATH=$(find_checklist_path "${FILE1_NAME}")
if [[ $? -ne 0 ]]; then
  exit 1
fi

FILE2_PATH=$(find_checklist_path "${FILE2_NAME}")
if [[ $? -ne 0 ]]; then
  exit 1
fi

echo "---"
echo "Comparing:"
echo "  (1) ${FILE1_PATH}"
echo "  (2) ${FILE2_PATH}"
echo "---"

# Use diff with the --unified format.
# The `|| true` ensures the script doesn't exit with an error code if diff finds differences.
diff --unified=3 "${FILE1_PATH}" "${FILE2_PATH}" || true
