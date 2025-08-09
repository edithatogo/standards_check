#!/usr/bin/env bash

# Minimal offline repo validation: run existing checks and exit.

errors=0

echo "[INFO] Running markdown validation"
bash scripts/validate_md.sh || errors=$((errors+1))

echo "[INFO] Running index validation"
bash scripts/validate_index.sh || errors=$((errors+1))

echo "[INFO] Running sidecar validation"
bash scripts/validate_sidecars.sh || errors=$((errors+1))

if (( errors > 0 )); then
  echo "Repo validation failed with $errors error(s)." >&2
  exit 1
fi

echo "Repo validation passed."
exit 0
