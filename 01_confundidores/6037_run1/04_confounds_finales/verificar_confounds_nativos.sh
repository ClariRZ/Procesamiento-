#!/usr/bin/env bash
# Auditoría de SOLO LECTURA de los 14 confusores del primer nivel nativo 6037/run1.
set -euo pipefail
PRE="$HOME/FEAT/6037/run1.feat"
BASE="$HOME/TesisDoctoral/confounds_mirta/6037/run1"
OUT="$HOME/TesisDoctoral/confounds_nativos/6037/run1"
DEST="${1:-$OUT/todos_confounds_nativo.txt}"
N="$(fslval "$PRE/filtered_func_data.nii.gz" dim4)"
[[ "$N" == 387 ]] || { echo "ERROR: BOLD no tiene 387 volúmenes" >&2; exit 1; }

python3 - "$N" \
    "$PRE/mc/prefiltered_func_data_mcf.par" \
    "$BASE/motion_deriv.par" \
    "$OUT/signal_wm_nativa.txt" \
    "$OUT/signal_csf_nativa.txt" \
    "$DEST" <<'PY'
import math, sys
from pathlib import Path
n = int(sys.argv[1])
paths = [Path(x) for x in sys.argv[2:]]
def load(path, cols):
    with open(path, encoding="utf-8") as f:
        r = [line.split() for line in f]
    if len(r) != n or any(len(row) != cols for row in r):
        raise SystemExit(f"ERROR: dimensiones inválidas: {path}; esperado {n} x {cols}")
    arr = [[float(v) for v in row] for row in r]
    if not all(math.isfinite(v) for row in arr for v in row):
        raise SystemExit(f"ERROR: valores no finitos: {path}")
    return arr

mov, deriv, wm, csf, data = (
    load(paths[0], 6), load(paths[1], 6), load(paths[2], 1),
    load(paths[3], 1), load(paths[4], 14)
)
deriv_error = max(abs(deriv[t][j] -
                      (0. if t == 0 else mov[t][j] - mov[t - 1][j]))
                  for t in range(n) for j in range(6))
if deriv_error >= 1e-7:
    raise SystemExit(f"ERROR: derivadas incorrectas ({deriv_error:.12g})")

err = 0.0
for t in range(n):
    expected = mov[t] + deriv[t] + wm[t] + csf[t]
    for j, value in enumerate(expected):
        difference = abs(data[t][j] - value)
        err = max(err, difference)
        if not math.isclose(data[t][j], value, rel_tol=1e-12, abs_tol=1e-9):
            raise SystemExit(f"ERROR: fila {t+1}, columna {j+1} no coincide con fuente")

constant = [j+1 for j in range(14)
            if min(row[j] for row in data) == max(row[j] for row in data)]
if constant:
    raise SystemExit(f"ERROR: columnas constantes: {constant}")

print(f"Filas: {n}")
print("Columnas: 14")
print("Correspondencia con cuatro fuentes: OK")
print(f"Error máximo de correspondencia: {err:.12g}")
print(f"Error máximo en derivadas: {deriv_error:.12g}")
print("Valores finitos; columnas constantes: 0")
print("CONFOUNDS NATIVOS: OK (solo lectura)")
PY
