#!/usr/bin/env bash
# Solo lectura: compara duración BOLD y cola sin eventos en los dos runs de 6037.
# No modifica BOLD, EV, FSF ni salidas FEAT.
set -euo pipefail

python3 <<'PY'
from pathlib import Path
import re
import subprocess

home = Path.home()
times = {}
for run in (1, 2):
    print(f"=== SUJETO 6037 / RUN {run} ===")
    feat = home / "FEAT" / "6037" / f"run{run}.feat"
    evdir = home / "NIFTIS_DESCOMPRIMIDOS" / "6037" / "evs" / f"run-{run}"
    bold = feat / "filtered_func_data.nii.gz"
    fsf = feat / "design.fsf"
    if not bold.is_file() or not fsf.is_file() or not evdir.is_dir():
        raise SystemExit(f"FALTAN datos del run {run}; no se puede comparar")

    n = int(subprocess.check_output(["fslval", str(bold), "dim4"], text=True).strip())
    tr = float(subprocess.check_output(["fslval", str(bold), "pixdim4"], text=True).strip())
    events = []
    for path in sorted(evdir.glob("*.txt")):
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    start, duration, amplitude = map(float, line.split())
                    events.append((start + duration, path.stem))
    if not events:
        raise SystemExit(f"ERROR: no se encontraron eventos en run{run}")

    last_time, last_name = max(events)
    fsf_text = fsf.read_text(encoding="utf-8")
    m = re.search(r"^set\s+fmri\(ndelete\)\s+(\d+)", fsf_text, re.MULTILINE)
    if m is None:
        raise SystemExit(f"ERROR: falta fmri(ndelete) en run{run}")

    nominal = n * tr
    tail = nominal - last_time
    times[run] = tail
    print(f"Volúmenes: {n}; TR: {tr:g} s; duración nominal: {nominal:.3f} s")
    print(f"Último evento: {last_name}, final: {last_time:.3f} s")
    print(f"Resto nominal sin eventos: {tail:.3f} s")
    print(f"Volúmenes descartados según FSF: {m.group(1)}")
    print()

print(f"Diferencia absoluta entre colas: {abs(times[1] - times[2]):.3f} s")
print("COMPARACIÓN COMPLETADA — SOLO LECTURA")
print("No establece si la cola estaba prevista en el protocolo.")
PY
