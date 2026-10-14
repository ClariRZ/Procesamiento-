#!/usr/bin/env bash
# Solo lectura. Auditoría numérica de eventos para el primer nivel nativo 6037/run1.
# No modifica los EV, el FSF ni los resultados FEAT. No requiere numpy.
set -euo pipefail

EV="$HOME/NIFTIS_DESCOMPRIMIDOS/6037/evs/run-1"
FSF="$HOME/Pipeline-completo-de-procesamiento-de-datos-/01_primer_nivel/automatizacion_mirta/plantilla/first_level_6037_run1_master.fsf"

python3 - "$EV" "$FSF" <<'PY'
import math
import re
import sys
from pathlib import Path

evdir = Path(sys.argv[1])
fsf = Path(sys.argv[2])
names = (
    "AtencionPlena", "ExperimNeg", "ExperimNeutra", "Likert",
    "ObservaNeg", "ObservaNeutra", "Reinterpreta", "Suprime",
)

if not fsf.is_file():
    raise SystemExit("ERROR: falta plantilla FSF")
text = fsf.read_text(encoding="utf-8")
def setting(key):
    match = re.search(r"^set\s+fmri\(" + re.escape(key) + r"\)\s+(.+?)\s*$",
                      text, re.MULTILINE)
    if not match:
        raise SystemExit(f"ERROR: falta campo fmri({key})")
    return match.group(1).strip('"')

tr = float(setting("tr"))
npts = int(setting("npts"))
if tr != 2.0 or npts != 387:
    raise SystemExit(f"ERROR: TR/NPTS inesperados: {tr}/{npts}")
if [int(setting(x)) for x in ("evs_orig", "evs_real", "ncon_orig", "ncon_real")] != [8, 16, 21, 21]:
    raise SystemExit("ERROR: número de EV/contrastes distinto del piloto")
for i, name in enumerate(names, 1):
    if setting(f"evtitle{i}") != name or int(setting(f"deriv_yn{i}")) != 1:
        raise SystemExit(f"ERROR: plantilla inconsistente con EV {i}: {name}")

print(f"Run 6037/1: {npts} volúmenes, TR={tr:g}s, duración nominal={npts*tr:g}s")
print("Plantilla: 8 EV + 8 derivadas temporales + 21 contrastes")
for name in names:
    p = evdir / (name + ".txt")
    if not p.is_file():
        raise SystemExit(f"FALTA: {p}")
    raw = [line.split() for line in p.read_text(encoding="utf-8").splitlines()
           if line.strip()]
    if not raw or any(len(row) != 3 for row in raw):
        raise SystemExit(f"ERROR: {name}: archivo vacío o no contiene 3 columnas por fila")
    rows = [[float(value) for value in row] for row in raw]
    if any(not math.isfinite(value) for row in rows for value in row):
        raise SystemExit(f"ERROR: {name}: NaN/Inf")
    if any(start < 0 or duration < 0 or start+duration > npts*tr
           for start, duration, amplitude in rows):
        raise SystemExit(f"ERROR: {name}: inicio/duración/final fuera de adquisición")
    warning = " (ADVERTENCIA: inicios no ordenados)" if [r[0] for r in rows] != sorted(r[0] for r in rows) else ""
    final = max(row[0] + row[1] for row in rows)
    print(f"{name:15s} {len(rows):3d} eventos | último final {final:9.3f}s{warning}")
print("Descanso.txt:", "existe (no es EV del FSF)" if (evdir/"Descanso.txt").is_file() else "no encontrado")
print("AUDITORÍA BÁSICA DE EVENTOS: OK")
print("Pendiente: verificar la cronología del paradigma y los 21 contrastes.")
PY
