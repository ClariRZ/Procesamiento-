#!/usr/bin/env bash
# Solo lectura: audita las señales WM/CSF nativas del run1.
set -euo pipefail

PRE="$HOME/FEAT/6037/run1.feat"
OUT="${1:-$HOME/TesisDoctoral/confounds_nativos/6037/run1}"

N="$(fslval "$PRE/filtered_func_data.nii.gz" dim4)"
python3 - "$N" "$OUT/signal_wm_nativa.txt" "$OUT/signal_csf_nativa.txt" <<'PY'
import math
import sys

n = int(sys.argv[1])
for path in sys.argv[2:]:
    with open(path, encoding="utf-8") as handle:
        rows = [line.split() for line in handle if line.strip()]
    if len(rows) != n or any(len(row) != 1 for row in rows):
        raise SystemExit(f"ERROR: {path}: se esperan {n} filas y una columna")
    values = [float(row[0]) for row in rows]
    if not all(math.isfinite(x) for x in values):
        raise SystemExit(f"ERROR: {path}: valores no finitos")
    if min(values) == max(values):
        raise SystemExit(f"ERROR: {path}: señal constante")
    print(f"OK: {path}: {n} filas, mínimo {min(values):.6f}, máximo {max(values):.6f}")
PY
echo "Control numérico terminado. No se han escrito archivos."
