#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <archetypes|variants> <id> <title> <group> <version> [preferred_format]" >&2
  exit 2
}

track=${1:-}
id=${2:-}
title=${3:-}
group=${4:-}
version=${5:-}
pref=${6:-pdf}

[[ "$track" =~ ^(archetypes|variants)$ ]] || usage
[[ -n "$id" && -n "$title" && -n "$group" && -n "$version" ]] || usage

out="source/$track/$id.yml"
[[ -e "$out" ]] && { echo "[ERROR] Sidecar already exists: $out" >&2; exit 1; }

cat > "$out" <<YAML
id: $id
title: $title
group: $group
version: "$version"
date: TBD
publisher: TBD
source_url: TBD
retrieved_at: TBD
preferred_format: $pref
checksum: TBD
license: TBD
notes: |
  Add citation, canonical URL, and licensing once verified.
YAML

echo "Created $out"

