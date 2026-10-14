# Máscaras WM/CSF en espacio funcional nativo — 6037/run1

## Estado del piloto (14/10/2026)

La generación de ambas máscaras se ejecutó en la Alienware sobre el FEAT original de 6037/run1. La investigadora confirmó en conversación que el control visual en FSLeyes estaba «todo ok». Esta valoración corresponde a su inspección, no a una verificación independiente del asistente.

| Máscara | Vóxeles | Volumen (mm³) |
|---|---:|---:|
| CSF | 4105 | 190858,421875 |
| WM | 9089 | 422585,187500 |

Archivos ya existentes, fuera de Git: `~/TesisDoctoral/confounds_nativos/6037/run1/mask_{csf,wm}_func.nii.gz`.

## Entradas verificadas

- `~/FEAT/6037/run1.feat/reg/highres.nii.gz`; prefijo SHA256: `a24dc10f6a8e99be`.
- FAST existente `~/TesisDoctoral/confounds_mirta/6037/tissue_a24dc10f6a8e99be/fast_6037_pve_0.nii.gz` (CSF) y `fast_6037_pve_2.nii.gz` (WM).
- `~/FEAT/6037/run1.feat/reg/highres2example_func.mat`, `example_func.nii.gz` y `mask.nii.gz`.

## Procedimiento efectivamente realizado

1. Binarizar FAST con probabilidad ≥ 0,9: `fslmaths <pve> -thr 0.9 -bin <mask_T1>`.
2. Transformar la máscara T1 al espacio funcional con `flirt -applyxfm -init reg/highres2example_func.mat -ref example_func.nii.gz -interp nearestneighbour`.
3. Binarizar el resultado e intersectar con `mask.nii.gz` funcional: `fslmaths <mask_prelim> -bin -mas <mask_funcional> <mask_final>`.
4. Comprobar vóxeles no nulos y revisar WM/CSF visualmente en FSLeyes.

No se repitieron BET, FAST, MCFLIRT ni el preprocesamiento. Un segundo intento de generación se detuvo antes de escribir porque la carpeta de resultados ya existía.

## Limitación y continuación

La primera captura compartida con el asistente ocultaba la imagen anatómica de fondo. Posteriormente la investigadora comunicó que las máscaras estaban bien. Se registra esa declaración sin atribuir al asistente una nueva inspección no documentada.

No ejecutar nuevamente las máscaras que ya existen. El paso siguiente es extraer las señales medias WM y CSF del BOLD nativo y comprobar 387 filas antes de construir 14 confusores. El script reproducible y el control numérico se guardan en esta subcarpeta, sin NIfTI ni datos individuales.
