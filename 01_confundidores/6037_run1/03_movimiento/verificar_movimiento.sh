#!/usr/bin/env bash
# Solo lectura. Verifica el movimiento MCFLIRT y sus derivadas del run1 de 6037.
# Python estándar: no requiere numpy y no crea archivos.
set -euo pipefail

PRE="$HOME/FEAT/6037/run1.feat"
BASE="$HOME/TesisDoctoral/confounds_mirta/6037/run1"

python3 - "$PRE/mc/prefiltered_func_data_mcf.par" "$BASE/motion_deriv.par" <<'PY'
import math
import sys

def read_matrix(path):
    with open(path, encoding="utf-8") as f:
        rows = [line.split() for line in f]
    if len(rows) != 387 or any(len(row) != 6 for row in rows):
        raise SystemExit(f"Dimensiones incorrectas: {path} (esperadas: 387×6)")
    vals = [[float(v) for v in row] for row in rows]
    if not all(math.isfinite(v) for row in vals for v in row):
        raise SystemExit(f"Valores no finitos en {path}")
    return vals

motion = read_matrix(sys.argv[1])
derivatives = read_matrix(sys.argv[2])

error_max = max(
    abs(derivatives[t][j] - (0.0 if t == 0 else motion[t][j] - motion[t-1][j]))
    for t in range(387) for j in range(6)
)
print("Movimiento: 387 × 6")
print("Derivadas: 387 × 6")
print(f"Error máximo de derivadas: {error_max:.14g}")
if error_max >= 1e-7:
    raise SystemExit("ERROR: derivadas incorrectas")
print("MOVIMIENTO Y DERIVADAS: OK")
PY
