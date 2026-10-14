#!/usr/bin/env bash
# Reproduce el procedimiento ya realizado de 6037/run1 en una carpeta NUEVA.
# No vuelve a ejecutar FAST, BET ni FEAT. Nunca sobrescribe los resultados originales.
set -euo pipefail

ROOT="$HOME/TesisDoctoral/confounds_nativos/6037"
PRE="$HOME/FEAT/6037/run1.feat"
TIS="$HOME/TesisDoctoral/confounds_mirta/6037/tissue_a24dc10f6a8e99be"

if [[ $# -ne 1 ]]; then
    echo "Uso: bash $0 $ROOT/run1_REPRODUCCION_NUEVA" >&2
    exit 2
fi
OUT="$1"
if [[ "$OUT" != "$ROOT/"* || -e "$OUT" || -L "$OUT" ]]; then
    echo "DETENIDO: indicar una salida NUEVA dentro de $ROOT; no se sobrescribe nada." >&2
    exit 2
fi

for cmd in sha256sum fslmaths flirt fslstats fslval; do
    command -v "$cmd" >/dev/null || { echo "FALTA: $cmd" >&2; exit 1; }
done

for F in \
    "$PRE/reg/highres.nii.gz" \
    "$PRE/reg/highres2example_func.mat" \
    "$PRE/example_func.nii.gz" \
    "$PRE/mask.nii.gz" \
    "$TIS/fast_6037_pve_0.nii.gz" \
    "$TIS/fast_6037_pve_2.nii.gz"; do
    [[ -s "$F" ]] || { echo "FALTA ENTRADA: $F" >&2; exit 1; }
done

HASH="$(sha256sum "$PRE/reg/highres.nii.gz")"
[[ "${HASH:0:16}" == "a24dc10f6a8e99be" ]] ||
    { echo "DETENIDO: el T1 ha cambiado con respecto al FAST reutilizado." >&2; exit 1; }

for I in 0 2; do
    for AX in 1 2 3; do
        [[ "$(fslval "$PRE/reg/highres.nii.gz" "dim$AX")" == \
           "$(fslval "$TIS/fast_6037_pve_$I.nii.gz" "dim$AX")" ]] ||
            { echo "DETENIDO: geometría del T1 y FAST no coincide." >&2; exit 1; }
    done
done

# mkdir falla sin modificar nada cuando la salida ya existe.
mkdir -- "$OUT"

for TEJIDO in csf wm; do
    if [[ "$TEJIDO" == "csf" ]]; then I=0; else I=2; fi
    fslmaths "$TIS/fast_6037_pve_$I.nii.gz" -thr 0.9 -bin \
        "$OUT/mask_${TEJIDO}_T1.nii.gz"

    flirt -in "$OUT/mask_${TEJIDO}_T1.nii.gz" \
        -ref "$PRE/example_func.nii.gz" -applyxfm \
        -init "$PRE/reg/highres2example_func.mat" \
        -interp nearestneighbour \
        -out "$OUT/mask_${TEJIDO}_func_prelim.nii.gz"

    fslmaths "$OUT/mask_${TEJIDO}_func_prelim.nii.gz" -bin \
        -mas "$PRE/mask.nii.gz" "$OUT/mask_${TEJIDO}_func.nii.gz"

    echo "MÁSCARA $TEJIDO:"
    fslstats "$OUT/mask_${TEJIDO}_func.nii.gz" -V
done

echo "Salida: $OUT"
echo "Revisar visualmente en FSLeyes antes de extraer confusores."
echo "Si una ejecución se interrumpe, dejar la carpeta para auditoría; no se borra ni se sobrescribe."
