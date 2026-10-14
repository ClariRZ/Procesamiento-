#!/usr/bin/env bash
# Solo lectura. No crea ni modifica imágenes.
set -euo pipefail

PRE="$HOME/FEAT/6037/run1.feat"
OUT="${1:-$HOME/TesisDoctoral/confounds_nativos/6037/run1}"

for T in csf wm; do
    M="$OUT/mask_${T}_func.nii.gz"
    [[ -s "$M" ]] || { echo "FALTA: $M" >&2; exit 1; }

    for A in 1 2 3; do
        [[ "$(fslval "$M" "dim$A")" == "$(fslval "$PRE/example_func.nii.gz" "dim$A")" ]] ||
            { echo "ERROR: dimensión $A incompatible para $T" >&2; exit 1; }
        [[ "$(fslval "$M" "pixdim$A")" == "$(fslval "$PRE/example_func.nii.gz" "pixdim$A")" ]] ||
            { echo "ERROR: resolución $A incompatible para $T" >&2; exit 1; }
    done

    TOTAL="$(fslstats "$M" -V | awk '{print $1}')"
    DENTRO="$(fslstats "$M" -k "$PRE/mask.nii.gz" -V | awk '{print $1}')"
    [[ "$TOTAL" -gt 0 && "$TOTAL" -eq "$DENTRO" ]] ||
        { echo "ERROR: $T vacía o no limitada al cerebro funcional" >&2; exit 1; }
    echo "$T: $TOTAL vóxeles, todos dentro de la máscara funcional original."
done

SOLAPE="$(fslstats "$OUT/mask_csf_func.nii.gz" -k "$OUT/mask_wm_func.nii.gz" -V | awk '{print $1}')"
[[ "$SOLAPE" -eq 0 ]] || { echo "ERROR: hay $SOLAPE vóxeles compartidos entre CSF y WM" >&2; exit 1; }
echo "Control numérico correcto. El control anatómico visual es independiente."
