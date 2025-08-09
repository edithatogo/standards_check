#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <file> [sidecar.yml]" >&2
  exit 2
}

[[ ${1:-} ]] || usage
file="$1"
[[ -f "$file" ]] || { echo "[ERROR] File not found: $file" >&2; exit 1; }

hash=""
if command -v shasum >/dev/null 2>&1; then
  hash=$(shasum -a 256 "$file" | awk '{print $1}')
elif command -v openssl >/dev/null 2>&1; then
  hash=$(openssl dgst -sha256 "$file" | awk '{print $2}')
else
  echo "[ERROR] Need shasum or openssl to compute checksum" >&2
  exit 1
fi

if [[ -n ${2:-} ]]; then
  sidecar="$2"
  [[ -f "$sidecar" ]] || { echo "[ERROR] Sidecar not found: $sidecar" >&2; exit 1; }
  if grep -qE '^checksum:' "$sidecar"; then
    sed -i'' -E "s/^checksum:.*/checksum: $hash/" "$sidecar"
  else
    printf '\nchecksum: %s\n' "$hash" >> "$sidecar"
  fi
  echo "Updated checksum in $sidecar: $hash"
else
  echo "$hash"
fi

