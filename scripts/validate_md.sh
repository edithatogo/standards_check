#!/usr/bin/env bash
set -euo pipefail

fail=0
while IFS= read -r -d '' f; do
  bn=$(basename "$f")
  if [[ ! $bn =~ ^[a-z0-9]+(-[a-z0-9]+)*\.md$ ]]; then
    echo "[ERROR] Invalid filename (kebab-case expected): $bn" >&2
    fail=1
  fi
  # Check first non-empty line starts with '# '
  first_line=$(grep -m1 -E "\S" "$f" || true)
  if [[ ! $first_line =~ ^#\  ]]; then
    echo "[ERROR] $bn: first non-empty line must be an H1 ('# Title')." >&2
    fail=1
  fi
done < <(find markdown -type f -name "*.md" ! -name "_template.md" -print0)

if [[ $fail -eq 0 ]]; then
  echo "Markdown validation passed."
else
  echo "Markdown validation failed." >&2
fi

exit $fail
