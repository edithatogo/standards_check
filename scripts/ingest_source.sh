#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<USAGE
Usage: $0 <archetypes|variants> <id> <url> [ext]

Downloads the source file into source/<track>/<id>.<ext>, computes checksum,
and updates sidecar fields (source_url, retrieved_at, preferred_format, checksum).
USAGE
  exit 2
}

track=${1:-}
id=${2:-}
url=${3:-}
ext=${4:-}

[[ "$track" =~ ^(archetypes|variants)$ ]] || usage
[[ -n "$id" && -n "$url" ]] || usage

sidecar="source/$track/$id.yml"
[[ -f "$sidecar" ]] || { echo "[ERROR] Sidecar not found: $sidecar" >&2; exit 1; }

if [[ -z "$ext" ]]; then
  # try to detect ext from URL path
  path_part=${url%%\?*}
  ext=${path_part##*.}
  [[ "$ext" =~ ^[A-Za-z0-9]{2,5}$ ]] || ext=pdf
  ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
fi

out="source/$track/$id.$ext"
mkdir -p "source/$track"

echo "Downloading: $url -> $out"
if command -v curl >/dev/null 2>&1; then
  curl -L --fail -o "$out" "$url"
elif command -v wget >/dev/null 2>&1; then
  wget -O "$out" "$url"
else
  echo "[ERROR] Need curl or wget to download" >&2
  exit 1
fi

# Compute checksum and write into sidecar
scripts/checksum.sh "$out" "$sidecar"

# Update sidecar metadata (source_url, retrieved_at, preferred_format)
today=$(date +%F)
sed -i'' -E "s|^source_url:.*$|source_url: $url|" "$sidecar"
sed -i'' -E "s|^retrieved_at:.*$|retrieved_at: $today|" "$sidecar"
sed -i'' -E "s|^preferred_format:.*$|preferred_format: $ext|" "$sidecar"

echo "Ingested $id ($ext). Sidecar updated: $sidecar"

