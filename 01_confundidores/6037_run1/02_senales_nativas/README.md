# 6037/run1 — extracción de señales WM y CSF nativas

**Ejecutado en la Alienware el 14/10/2026. Verificación numérica OK.** El QC anatómico previo de las máscaras fue confirmado por la investigadora.

## Entradas existentes

- BOLD: `~/FEAT/6037/run1.feat/filtered_func_data.nii.gz` (387 volúmenes, espacio funcional nativo).
- WM: `~/TesisDoctoral/confounds_nativos/6037/run1/mask_wm_func.nii.gz` (9089 vóxeles).
- CSF: `~/TesisDoctoral/confounds_nativos/6037/run1/mask_csf_func.nii.gz` (4105 vóxeles).

## Comandos realmente ejecutados

```bash
PRE="$HOME/FEAT/6037/run1.feat"
OUT="$HOME/TesisDoctoral/confounds_nativos/6037/run1"
fslmeants -i "$PRE/filtered_func_data.nii.gz" -m "$OUT/mask_wm_func.nii.gz" -o "$OUT/signal_wm_nativa.txt"
fslmeants -i "$PRE/filtered_func_data.nii.gz" -m "$OUT/mask_csf_func.nii.gz" -o "$OUT/signal_csf_nativa.txt"
```

## Validación documentada

Se comprobaron 387 filas y una columna por señal, todos los valores finitos y rango distinto de cero.

| Salida | Filas | Mínimo | Máximo |
|---|---:|---:|---:|
| `signal_wm_nativa.txt` | 387 | 10818.271690 | 11030.664290 |
| `signal_csf_nativa.txt` | 387 | 8035.584346 | 8250.511604 |

Las señales individuales permanecen **solo en la computadora**, fuera de GitHub.

## Scripts

- `extraer_senales_nativas.sh`: para reproducir la extracción posteriormente en un directorio nuevo; no repetir sobre los archivos ya existentes.
- `verificar_senales_nativas.sh`: comprobación de solo lectura.

Los scripts versionados no se han ejecutado todavía como tal en la Alienware; lo validado es el bloque manual anterior. Esta diferencia queda documentada.

**Siguiente paso:** validar los 6 parámetros de movimiento y 6 derivadas frente a los archivos fuente, combinar con estas dos señales y comprobar `todos_confounds_nativo.txt` de 387 filas × 14 columnas. El primer nivel FEAT sigue pendiente.
