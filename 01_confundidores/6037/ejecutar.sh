#!/usr/bin/env bash
set -euo pipefail
THIS="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "${FSLDIR:-}" && -x "$FSLDIR/bin/python" ]]; then
    PYTHON="${PYTHON_NATIVO:-$FSLDIR/bin/python}"
else
    PYTHON="${PYTHON_NATIVO:-python3}"
fi
[[ $# -ge 1 ]] || { echo 'Uso: ejecutar.sh auditar|mascaras|aprobar|finalizar|estado [opciones]' >&2; exit 2; }
ACCION="$1"; shift
exec "$PYTHON" "$THIS/../automatizacion/confundidores.py" "$ACCION" \
    --sujeto 6037 --run 1 "$@"
