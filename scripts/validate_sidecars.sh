#!/usr/bin/env bash
set -euo pipefail

required=(id title)
optional=(group version date publisher source_url retrieved_at preferred_format checksum license)

fail=0

while IFS= read -r -d '' y; do
  bn=$(basename "$y")
  # Skip templates/placeholders
  if [[ $bn == _meta.template.yml ]]; then
    continue
  fi
  name=${bn%.yml}
  sid=$(grep -m1 -E '^id:' "$y" | sed -E 's/^id:[[:space:]]*//')

  if [[ "$sid" != "<kebab-case-id>" ]]; then
    # Check required keys are present
    for k in "${required[@]}"; do
      if ! grep -qE "^${k}:" "$y"; then
        echo "[ERROR] $bn: missing key '$k'" >&2
        fail=1
      fi
    done
    # Check optional keys are present
    for k in "${optional[@]}"; do
      if ! grep -qE "^${k}:" "$y"; then
        echo "[WARNING] $bn: missing key '$k'" >&2
      fi
    done
    # Check id matches filename
    if [[ "$sid" != "$name" ]]; then
      echo "[ERROR] $bn: id '$sid' does not match filename '$name'" >&2
      fail=1
    fi
  fi
done < <(find source -type f -path 'source/*/*.yml' -print0)

if (( fail == 0 )); then
  echo "Sidecar validation passed."
else
  echo "Sidecar validation failed." >&2
fi

exit $fail
