#!/usr/bin/env bash
set -euo pipefail

file="source/index.yml"
[[ -f "$file" ]] || { echo "[ERROR] $file not found" >&2; exit 1; }

required=(id title url version date license publisher preferred_format level group)

in_item=0
item_no=0
err=0
buffer=""

finalize_item() {
  local missing=()
  for k in "${required[@]}"; do
    if [[ "$k" == "id" ]]; then
      pat='^([[:space:]]*-\s*)?id:'
    else
      pat="^[[:space:]]*$k:"
    fi
    if ! printf "%b" "$buffer" | grep -qE "$pat"; then
      missing+=("$k")
    fi
  done
  if (( ${#missing[@]} > 0 )); then
    echo "[ERROR] Item #$item_no missing keys: ${missing[*]}" >&2
    err=1
  fi
  buffer=""
}

while IFS= read -r line; do
  if [[ $line =~ ^[[:space:]]*-[[:space:]]id:[[:space:]] ]]; then
    if (( in_item == 1 )); then finalize_item; fi
    ((item_no++))
    in_item=1
    buffer+=$line$'\n'
  else
    if (( in_item == 1 )); then
      buffer+=$line$'\n'
    fi
  fi
done < "$file"

if (( in_item == 1 )); then finalize_item; fi

if (( item_no == 0 )); then
  echo "[ERROR] No items found in $file" >&2
  exit 1
fi

if (( err == 0 )); then
  echo "Index validation passed for $item_no item(s)."
else
  echo "Index validation failed." >&2
fi

exit $err
