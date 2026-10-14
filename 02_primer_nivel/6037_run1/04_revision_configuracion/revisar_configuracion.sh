#!/usr/bin/env bash
# Diagnóstico de SOLO LECTURA: diferencias entre preproc nativo y FSF manual MNI.
set -euo pipefail
PRE="$HOME/FEAT/6037/run1.feat/design.fsf"
FSF="$HOME/Pipeline-completo-de-procesamiento-de-datos-/01_primer_nivel/automatizacion_mirta/plantilla/first_level_6037_run1_master.fsf"

for F in "$PRE" "$FSF"; do
    [[ -s "$F" ]] || { echo "FALTA: $F" >&2; exit 1; }
done

echo "=== REGISTRO NATIVO ==="
grep -E '^set fmri\((reg_yn|reginitial_highres_yn|reghighres_yn|regstandard_yn|regstandard_nonlinear_yn)\)' "$PRE" || :
echo "=== REGISTRO EN PRIMER NIVEL MANUAL MNI ==="
grep -E '^set fmri\((reg_yn|reginitial_highres_yn|reghighres_yn|regstandard_yn|regstandard_nonlinear_yn)\)' "$FSF" || :
echo "=== ENTRADAS ORIGINALES ==="
grep -E '^set (feat_files\(1\)|confoundev_files\(1\))' "$FSF"
echo "=== CUSTOM EV, CONVOLUCION Y FILTRADO DEL MODELO ==="
grep -E '^set fmri\((custom[1-8]|convolve[1-8]|tempfilt_yn[1-8])\)' "$FSF"
echo "=== CONFUSORES NATIVOS PARA MODELO NUEVO ==="
test -s "$HOME/TesisDoctoral/confounds_nativos/6037/run1/todos_confounds_nativo.txt"
echo "OK: confusores nativos existentes."
echo "La prueba no ejecuta FEAT ni modifica ninguna entrada."
