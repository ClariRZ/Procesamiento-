#!/usr/bin/env bash
# Solo lectura. Valida dimensiones, finitud, rango aproximado y contrastes no nulos.
# No requiere NumPy. No ejecuta feat_model ni feat.
set -euo pipefail
BASE="${1:-$HOME/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/VALIDACION_DISENO_6037_RUN1}"
python3 - "$BASE" <<'PY'
import math
import sys
from pathlib import Path

root = Path(sys.argv[1])
def read_fsl_matrix(path, expected_rows, expected_cols, rows_key):
    lines = path.read_text(encoding="utf-8").splitlines()
    meta = {}
    for line in lines:
        if line.startswith("/") and line.split()[0] != "/Matrix":
            chunks = line.split()
            if len(chunks) > 1:
                meta[chunks[0]] = chunks[1]
    if int(meta.get("/NumWaves", -1)) != expected_cols or int(meta.get(rows_key, -1)) != expected_rows:
        raise SystemExit(f"ERROR: cabecera no coincide: {path}")
    try:
        start = lines.index("/Matrix") + 1
    except ValueError as exc:
        raise SystemExit(f"ERROR: no existe /Matrix en {path}") from exc
    rows = [[float(v) for v in line.split()] for line in lines[start:] if line.strip()]
    if len(rows) != expected_rows or any(len(row) != expected_cols for row in rows):
        raise SystemExit(f"ERROR: dimensiones de datos incorrectas: {path}")
    if not all(math.isfinite(v) for row in rows for v in row):
        raise SystemExit(f"ERROR: valores no finitos: {path}")
    return rows

X = read_fsl_matrix(root/"design.mat", 387, 30, "/NumPoints")
C = read_fsl_matrix(root/"design.con", 21, 30, "/NumContrasts")
basis = []
residuals = []
for col in zip(*X):
    norm = math.sqrt(math.fsum(x*x for x in col))
    if norm == 0:
        raise SystemExit("ERROR: columna nula")
    v = [x/norm for x in col]
    for _ in range(2):
        for q in basis:
            proj = math.fsum(a*b for a,b in zip(v,q))
            v = [a-proj*b for a,b in zip(v,q)]
    residual = math.sqrt(math.fsum(x*x for x in v))
    residuals.append(residual)
    if residual > 1e-8:
        basis.append([x/residual for x in v])

print("Matriz: 387 filas × 30 columnas")
print("Rango numérico:", len(basis), "/30")
print(f"Residuo mínimo normalizado: {min(residuals):.12g}")
print("Contrastes: 21 × 30")
if len(basis) != 30:
    raise SystemExit("REVISAR: rango numérico incompleto")
if any(all(abs(value) < 1e-12 for value in row) for row in C):
    raise SystemExit("REVISAR: existe contraste nulo")
print("RANGO COMPLETO Y CONTRASTES NO NULOS: OK")
print("Este control no mide el número de condición ni comprueba pesos de contrastes.")
PY
