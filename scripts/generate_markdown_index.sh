#!/usr/bin/env bash
set -euo pipefail

out="markdown/index.md"
echo "# Checklists" > "$out"
echo >> "$out"

for track in archetypes variants; do
  # Capitalize track name (portable)
  cap=$(printf '%s' "$track" | awk '{print toupper(substr($0,1,1)) substr($0,2)}')
  echo "## $cap" >> "$out"
  echo >> "$out"
  while IFS= read -r -d '' f; do
    rel=${f#markdown/}
    name=$(basename "$f" .md)
    title=$(grep -m1 -E '^# ' "$f" | sed 's/^# //')
    echo "- [${title:-$name}]($rel)" >> "$out"
  done < <(find "markdown/$track" -type f -name "*.md" -print0)
  echo >> "$out"
done

echo "Wrote $out"
