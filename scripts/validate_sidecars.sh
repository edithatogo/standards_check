#!/usr/bin/env bash

# This script validates the YAML sidecar files in the source/ directory.

set -uo pipefail

required=("id" "title")
optional=("group" "version" "date" "publisher" "source_url" "retrieved_at" "preferred_format" "checksum" "license")
fail=0

find source -type f -name "*.yml" -print0 | while IFS= read -r -d '' y; do
  bn=$(basename "$y")

  # Skip templates/placeholders
  if [[ "$bn" == "_meta.template.yml" ]]; then
    continue
  fi

  name=${bn%.yml}
  id_line=$(grep -m1 -E '^id:' "$y" || true)
  sid=$(echo "$id_line" | sed -E 's/^id:[[:space:]]*//')

  if [[ -z "$sid" ]] || [[ "$sid" == "<kebab-case-id>" ]]; then
    continue
  fi

  # Check required keys
  for k in "${required[@]}"; do
    if ! grep -qE "^${k}:" "$y"; then
      echo "[ERROR] $bn: missing required key '$k'" >&2
      fail=1
    fi
  done

  # Check optional keys
  for k in "${optional[@]}"; do
    if ! grep -qE "^${k}:" "$y"; then
      echo "[WARNING] $bn: missing optional key '$k'" >&2
    fi
  done

  # Check if id matches filename
  if [[ "$sid" != "$name" ]]; then
    echo "[ERROR] $bn: id '$sid' does not match filename '$name'" >&2
    fail=1
  fi
done

if (( fail == 0 )); then
  echo "Sidecar validation passed."
else
  echo "Sidecar validation failed." >&2
  exit 1
fi

exit 0