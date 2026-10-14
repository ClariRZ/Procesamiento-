#!/usr/bin/env bash
# Reproduce la matriz nativa de 14 columnas SOLO si el archivo destino no existe.
# No vuelve a ejecutar MCFLIRT, FAST, FLIRT ni fslmeants.
# Datos siempre fuera del repositorio público.
set -euo pipefail

PRE="$HOME/FEAT/6037/run1.feat"
BASE="$HOME/TesisDoctoral/confounds_mirta/6037/run1"
OUT="$HOME/TesisDoctoral/confounds_nativos/6037/run1"
DEST="${1:-$OUT/todos_confounds_nativo.txt}"

# No admitir destinos fuera de la carpeta de resultados dedicada.
DEST="$(realpath -m -- "$DEST")"
[[ "$DEST" == "$OUT/"* ]] || {
    echo "DETENIDO: destino fuera del directorio $OUT" >&2
    exit 2
}
[[ ! -e "$DEST" && ! -L "$DEST" ]] || {
    echo "DETENIDO: el archivo ya existe; no lo reescribimos: $DEST" >&2
    exit 2
}
[[ -d "$OUT" && -d "$(dirname -- "$DEST")" ]] || {
    echo "DETENIDO: falta la carpeta de resultados" >&2
    exit 2
}

N="$(fslval "$PRE/filtered_func_data.nii.gz" dim4)"
[[ "$N" == 387 ]] || { echo "DETENIDO: dimensión temporal distinta de 387" >&2; exit 1; }

python3 - "$N" \
    "$PRE/mc/prefiltered_func_data_mcf.par" \
    "$BASE/motion_deriv.par" \
    "$OUT/signal_wm_nativa.txt" \
    "$OUT/signal_csf_nativa.txt" \
    "$DEST" <<'PY'
import math, os, sys, tempfile
from pathlib import Path

n = int(sys.argv[1])
motion, deriv, wm, csf, dest = map(Path, sys.argv[2:])

def read_rows(path, cols):
    with path.open(encoding="utf-8") as f:
        cells = [line.split() for line in f]
    if len(cells) != n or any(len(row) != cols for row in cells):
        raise SystemExit(f"ERROR: {path}: no contiene {n} filas x {cols} columnas")
    x = [[float(value) for value in row] for row in cells]
    if not all(math.isfinite(value) for row in x for value in row):
        raise SystemExit(f"ERROR: {path}: valores no finitos")
    return x

m = read_rows(motion, 6)
d = read_rows(deriv, 6)
w = read_rows(wm, 1)
c = read_rows(csf, 1)
err = max(abs(d[t][j] - (0. if t == 0 else m[t][j] - m[t-1][j]))
          for t in range(n) for j in range(6))
if err >= 1e-7:
    raise SystemExit(f"ERROR: derivadas no corresponden al movimiento (error={err})")
rows = [m[t] + d[t] + w[t] + c[t] for t in range(n)]
if any(len(row) != 14 for row in rows):
    raise SystemExit("ERROR: 14 columnas incorrectas")
const = [j + 1 for j in range(14)
         if min(row[j] for row in rows) == max(row[j] for row in rows)]
if const:
    raise SystemExit(f"ERROR: columnas constantes: {const}")

tmp = None
try:
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=dest.parent,
        prefix=".confounds_nativos_", suffix=".tmp", delete=False
    ) as f:
        tmp = Path(f.name)
        for row in rows:
            f.write(" ".join(format(v, ".17g") for v in row) + "\n")
    # os.link publica atómicamente y falla si el destino ya existe.
    os.link(tmp, dest)
finally:
    if tmp is not None:
        tmp.unlink(missing_ok=True)

print(f"OK: archivo NUEVO {dest}, {n} filas x 14 columnas; error derivadas={err:.12g}")
PY
