#!/usr/bin/env bash

file="source/index.yml"
[[ -f "$file" ]] || { echo "[ERROR] $file not found" >&2; exit 1; }

required=(id title)
optional=(url version date license publisher preferred_format level group)

in_item=0
item_no=0
err=0
buffer=""

finalize_item() {
  local missing_required=()
  for k in "${required[@]}"; do
    if [[ "$k" == "id" ]]; then
      pat='^([[:space:]]*-\s*)?id:'
    else
      pat="^[[:space:]]*$k:"
    fi
    if ! printf "%b" "$buffer" | grep -qE "$pat"; then
      missing_required+=("$k")
    fi
  done
  if (( ${#missing_required[@]} > 0 )); then
    echo "[ERROR] Item #$item_no missing required keys: ${missing_required[*]}" >&2
    err=1
  fi

  local missing_optional=()
  for k in "${optional[@]}"; do
    if ! printf "%b" "$buffer" | grep -qE "^[[:space:]]*$k:"; then
      missing_optional+=("$k")
    fi
  done
  if (( ${#missing_optional[@]} > 0 )); then
    echo "[WARNING] Item #$item_no missing optional keys: ${missing_optional[*]}" >&2
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

exit 0
