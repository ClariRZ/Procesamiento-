#!/usr/bin/env bash
# Auditoría de SOLO LECTURA de los 21 contrastes originales de 6037/run1.
# No requiere NumPy. No genera diseños, no modifica FSF y no ejecuta FEAT.
set -euo pipefail
FSF="$HOME/Pipeline-completo-de-procesamiento-de-datos-/01_primer_nivel/automatizacion_mirta/plantilla/first_level_6037_run1_master.fsf"
python3 - "$FSF" <<'PY'
import math
import re
import sys
from pathlib import Path

fsf = Path(sys.argv[1])
if not fsf.is_file():
    raise SystemExit(f"FALTA FSF: {fsf}")

param = {}
for line in fsf.read_text(encoding="utf-8").splitlines():
    m = re.match(r'^set\s+fmri\(([^)]+)\)\s+(.+?)\s*$', line)
    if m:
        param[m.group(1)] = m.group(2).strip().strip('"')

def get(key):
    if key not in param:
        raise SystemExit(f"FALTA parámetro fmri({key})")
    return param[key]

for key, expected in (("evs_orig", 8), ("evs_real", 16),
                      ("ncon_orig", 21), ("ncon_real", 21)):
    if int(get(key)) != expected:
        raise SystemExit(f"ERROR fmri({key}): esperado {expected}")

names = ("AtencionPlena", "ExperimNeg", "ExperimNeutra", "Likert",
         "ObservaNeg", "ObservaNeutra", "Reinterpreta", "Suprime")
for index, name in enumerate(names, start=1):
    if get(f"evtitle{index}") != name or int(get(f"deriv_yn{index}")) != 1:
        raise SystemExit(f"ERROR: orden o derivada incorrecta del EV {index}")

# Numeración exacta definida por el FSF manual auditado. Todos los
# contrastes son (+1 para el primer EV, -1 para el segundo EV).
pairs = [
    (1,2), (7,2), (8,2), (1,3), (7,3), (8,3), (2,3),
    (1,5), (7,5), (8,5), (2,5), (1,6), (7,6), (8,6),
    (2,6), (7,8), (8,7), (7,1), (1,7), (8,1), (1,8)
]
assert len(pairs) == 21
for n, (positive, negative) in enumerate(pairs, 1):
    title = get(f"conname_orig.{n}")
    expected_title = f"{names[positive-1]}_vs_{names[negative-1]}"
    if title != expected_title:
        raise SystemExit(f"ERROR: contraste {n}, nombre {title!r}; se esperaba {expected_title!r}")
    vals = [float(get(f"con_orig{n}.{ev}")) for ev in range(1, 9)]
    if not all(math.isfinite(v) for v in vals):
        raise SystemExit(f"ERROR: contraste {n}, peso no finito")
    expected = [float((ev == positive) - (ev == negative)) for ev in range(1, 9)]
    if vals != expected:
        raise SystemExit(f"ERROR: contraste {n}, vector difiere del FSF auditado: {vals}")
    print(f"{n:2d}  {title}  OK")

print("CONTRASTES ORIGINALES 21/21: OK")
print("OJO: no se han validado todavía con_real ni la matriz de diseño.")
PY
