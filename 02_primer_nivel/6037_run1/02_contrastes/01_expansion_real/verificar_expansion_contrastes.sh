#!/usr/bin/env bash
# 6037/run1: control de con_real en 16 EV frente a con_orig en 8 EV.
# Modo lectura; no necesita NumPy; no modifica FSF ni ejecuta FSL.
set -euo pipefail
FSF="$HOME/Pipeline-completo-de-procesamiento-de-datos-/01_primer_nivel/automatizacion_mirta/plantilla/first_level_6037_run1_master.fsf"

python3 - "$FSF" <<'PY'
import math
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.is_file():
    raise SystemExit(f"FALTA archivo: {path}")
params = {}
for line in path.read_text(encoding="utf-8").splitlines():
    m = re.match(r'^set\s+fmri\(([^)]+)\)\s+(.+?)\s*$', line)
    if m:
        params[m.group(1)] = m.group(2).strip().strip('"')

def get(key):
    if key not in params:
        raise SystemExit(f"FALTA fmri({key})")
    return params[key]

for k, v in (("evs_orig", 8), ("evs_real", 16),
             ("ncon_orig", 21), ("ncon_real", 21)):
    if int(get(k)) != v:
        raise SystemExit(f"ERROR fmri({k}); se esperaba {v}")
for ev in range(1, 9):
    if int(get(f"deriv_yn{ev}")) != 1:
        raise SystemExit(f"ERROR: falta derivada de tarea en EV{ev}")

ok = 0
for c in range(1, 22):
    original = [float(get(f"con_orig{c}.{ev}")) for ev in range(1, 9)]
    real = [float(get(f"con_real{c}.{ev}")) for ev in range(1, 17)]
    if not all(math.isfinite(v) for v in original + real):
        raise SystemExit(f"ERROR: peso no finito en contraste {c}")
    expected = [v for weight in original for v in (weight, 0.)]
    error = max(abs(a - b) for a, b in zip(real, expected))
    if error >= 1e-9:
        raise SystemExit(f"ERROR contraste {c}: expansión diferente, error={error:.12g}")
    ok += 1
    print(f"Contraste {c:02d}: OK")
print(f"Contrastes coincidentes: {ok}/21")
print("EXPANSIÓN DE CONTRASTES: OK")
PY
