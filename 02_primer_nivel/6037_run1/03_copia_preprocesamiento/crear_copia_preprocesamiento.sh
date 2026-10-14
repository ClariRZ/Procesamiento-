#!/usr/bin/env bash
# Copia NO destructiva para piloto 6037/run1.
# No ejecuta FEAT ni modifica ~/FEAT/6037/run1.feat.
# Este script reproduce el paso manual ya realizado: NO ejecutarlo de nuevo
# sobre la carpeta de destino existente.
set -euo pipefail

PRE="$HOME/FEAT/6037/run1.feat"
BASE="$HOME/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037"
COPIA="$BASE/entrada_run1.feat"

[[ -d "$PRE" ]] || { echo "FALTA FEAT original: $PRE" >&2; exit 1; }
[[ ! -e "$COPIA" && ! -L "$COPIA" ]] || {
    echo "DETENIDO: la copia ya existe: $COPIA; no se sobrescribe." >&2
    exit 2
}
for prog in rsync cmp du df awk; do
    command -v "$prog" >/dev/null || { echo "FALTA programa: $prog" >&2; exit 1; }
done
for F in filtered_func_data.nii.gz mask.nii.gz design.fsf example_func.nii.gz \
         reg/example_func2standard_warp.nii.gz; do
    [[ -s "$PRE/$F" ]] || { echo "FALTA: $PRE/$F" >&2; exit 1; }
done

NECESARIO="$(du -sb --exclude='filtered_func_data_MNI2*' "$PRE" | awk '{print $1}')"
DISPONIBLE="$(df -B1 --output=avail "$HOME" | tail -1)"
(( DISPONIBLE > NECESARIO + 1073741824 )) || {
    echo "DETENIDO: espacio insuficiente con margen de 1 GiB." >&2
    exit 1
}

mkdir -p -- "$BASE"
rsync -a --exclude='filtered_func_data_MNI2*' "$PRE/" "$COPIA/"

for F in filtered_func_data.nii.gz mask.nii.gz design.fsf example_func.nii.gz \
         reg/example_func2standard_warp.nii.gz; do
    [[ -s "$COPIA/$F" ]] && cmp -s -- "$PRE/$F" "$COPIA/$F" || {
        echo "ERROR: falta o difiere $F; conservar la copia para auditoría" >&2
        exit 1
    }
    echo "OK: $F"
done

echo "COPIA DEL PREPROCESAMIENTO COMPLETADA"
echo "NO inicia Statistics, no calcula mapas y no modifica los originales."
