#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Searching for 'TBD' values in source/ directory..."
grep -r --color=always "TBD" source/ || echo "[INFO] No 'TBD' values found."
