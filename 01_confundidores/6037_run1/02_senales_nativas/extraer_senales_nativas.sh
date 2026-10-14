#!/usr/bin/env bash
# Reproduce la extracción de 6037/run1 únicamente en un directorio NUEVO.
# No repite FAST, BET, registro ni preprocesamiento.
set -euo pipefail

PRE="$HOME/FEAT/6037/run1.feat"
ROOT="$HOME/TesisDoctoral/confounds_nativos/6037"
MASK="$ROOT/run1"
if [[ $# -ne 1 ]]; then
    echo "Uso: bash $0 $ROOT/run1_SENALES_REPRODUCCION_NUEVA" >&2
    exit 2
fi

OUT="$(realpath -m -- "$1")"
if [[ "$OUT" != "$ROOT/"* || -e "$OUT" || -L "$OUT" ]]; then
    echo "DETENIDO: se requiere un destino NUEVO bajo $ROOT/" >&2
    exit 2
fi

BOLD="$PRE/filtered_func_data.nii.gz"
for F in "$BOLD" "$MASK/mask_wm_func.nii.gz" "$MASK/mask_csf_func.nii.gz"; do
    [[ -s "$F" ]] || { echo "FALTA: $F" >&2; exit 1; }
done

N="$(fslval "$BOLD" dim4)"
[[ "$N" == 387 ]] || { echo "Volúmenes inesperados: $N" >&2; exit 1; }

for T in wm csf; do
    M="$MASK/mask_${T}_func.nii.gz"
    for A in 1 2 3; do
        [[ "$(fslval "$M" "dim$A")" == "$(fslval "$BOLD" "dim$A")" ]] ||
            { echo "ERROR: máscara $T, dimensión $A no coincide" >&2; exit 1; }
    done
done

mkdir -p -- "$ROOT"
mkdir -- "$OUT"
fslmeants -i "$BOLD" -m "$MASK/mask_wm_func.nii.gz" -o "$OUT/signal_wm_nativa.txt"
fslmeants -i "$BOLD" -m "$MASK/mask_csf_func.nii.gz" -o "$OUT/signal_csf_nativa.txt"

# Ejecuta el control sobre archivos nuevos; al fallar conserva la salida para auditoría.
DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
bash "$DIR/verificar_senales_nativas.sh" "$OUT"
echo "Reproducción creada en $OUT; el piloto original no se modificó."
