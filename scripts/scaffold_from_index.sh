#!/usr/bin/env bash

tpl="markdown/_template.md"
index="source/index.yml"

[[ -f "$tpl" ]] || { echo "[ERROR] Missing template: $tpl" >&2; exit 1; }
[[ -f "$index" ]] || { echo "[ERROR] Missing index: $index" >&2; exit 1; }

created=0

# Extract id, level, title per item (best-effort parsing)
awk '
  $1=="-" && $2 ~ /^id:/ {
    if (id!="") print id "\t" level "\t" title
    id=$2; sub("id:","",id); gsub(/^[ \t]+|[ \t]+$/,"",id)
    level=""; title=""
  }
  $1 ~ /^level:/ { level=$0; sub("level:","",level); gsub(/^[ \t]+|[ \t]+$/,"",level) }
  $1 ~ /^title:/ { title=$0; sub("title:","",title); gsub(/^[ \t]+|[ \t]+$/,"",title) }
  END { if (id!="") print id "\t" level "\t" title }
' "$index" | while IFS=$'\t' read -r id level title; do
  track=archetypes; [[ "$level" == "variant" ]] && track=variants
  out="markdown/$track/$id.md"
  [[ -f "$out" ]] && continue
  mkdir -p "markdown/$track"
  { printf '# %s\n' "$title"; sed '1d' "$tpl"; } > "$out"
  echo "Scaffolded: $out"
  created=$((created+1))
done

echo "Scaffold complete. New files: $created"
