#!/usr/bin/env bash
set -euo pipefail

index="source/index.yml"
out="todos/ingestion-tracker.md"

[[ -f "$index" ]] || { echo "[ERROR] Missing $index" >&2; exit 1; }

echo "# Ingestion Tracker" > "$out"
echo >> "$out"
echo "- [ ] All sidecars verified (set verified: true)" >> "$out"
echo "- [ ] All originals downloaded to source/<track>/<id>.<ext>" >> "$out"
echo >> "$out"

awk '
  $1=="-" && $2 ~ /^id:/ { id=$2; sub("id:","",id); gsub(/^[ \t]+|[ \t]+$/, "", id); level="archetypes"; next }
  $1 ~ /^level:/ { lv=$0; sub("level:","",lv); gsub(/^[ \t]+|[ \t]+$/, "", lv); if (lv=="variant") level="variants" }
  $1 ~ /^title:/ { title=$0; sub("title:","",title); gsub(/^[ \t]+|[ \t]+$/, "", title); print level "/" id "\t" title }
' "$index" | while IFS=$'\t' read -r path title; do
  id=$(basename "$path")
  printf -- "- [ ] %s — %s (%s)\n" "$id" "$title" "$path" >> "$out"
done

echo "Wrote $out"

