#!/usr/bin/env bash
set +e

# Minimal offline repo validation: run existing checks and exit.

errors=0

echo "[INFO] Running markdown validation"
bash scripts/validate_md.sh || errors=$((errors+1))

echo "[INFO] Running index validation"
bash scripts/validate_index.sh || errors=$((errors+1))

echo "[INFO] Running sidecar validation"
bash scripts/validate_sidecars.sh || errors=$((errors+1))

echo "[INFO] Running costing reconciliation validation"
python3 scripts/validate_costing_reconciliation.py || errors=$((errors+1))

if (( errors > 0 )); then
  echo "Repo validation failed with $errors error(s)." >&2
  exit 1
fi

echo "[INFO] Checking for TBD values"
grep -rI -- "TBD" source/ > /dev/null
case $? in
  0) echo "[WARNING] TBD values found. Please complete them." ;;
  1) echo "[INFO] No TBD values found." ;;
  *) echo "[ERROR] Could not search source for TBD values." >&2; exit 1 ;;
esac

echo "Repo validation passed."
exit 0
