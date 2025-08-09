#!/usr/bin/env bash
set -euo pipefail

index="source/index.yml"
[[ -f "$index" ]] || { echo "[ERROR] Missing $index" >&2; exit 1; }

echo "== Index Summary =="
total=$(grep -cE '^[[:space:]]*-[[:space:]]id:' "$index" || true)
echo "Items: $total"

echo
echo "== Sidecar Verification =="
verify_count=0
verify_true=0
while IFS= read -r -d '' y; do
  bn=$(basename "$y")
  [[ $bn == _meta.template.yml ]] && continue
  verify_count=$((verify_count+1))
  if grep -qE '^verified:[[:space:]]*true' "$y"; then
    verify_true=$((verify_true+1))
  fi
done < <(find source -type f -name '*.yml' -path 'source/*/*.yml' -print0)
echo "Sidecars: $verify_true verified / $verify_count total"

echo
echo "== TBD Fields (sidecars) =="
grep -Rn --line-number -E '\bTBD\b' source/*/*.yml || echo "None"

echo
echo "== TBD Fields (markdown) =="
grep -Rns --line-number '\[TBD\]' markdown || echo "None"

