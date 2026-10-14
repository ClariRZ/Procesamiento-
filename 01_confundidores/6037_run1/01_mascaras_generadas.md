# Paso 1 — Crear máscaras WM/CSF en espacio funcional nativo

**Estado: HECHO, 14/10/2026 ~06:36, Alienware.** Esto documenta operaciones ya realizadas; **no ejecutarlas nuevamente**.

## Insumos confirmados

```text
PRE=~/FEAT/6037/run1.feat
TIS=~/TesisDoctoral/confounds_mirta/6037/tissue_a24dc10f6a8e99be
OUT=~/TesisDoctoral/confounds_nativos/6037/run1
```

La huella SHA256 de `PRE/reg/highres.nii.gz` comienza por `a24dc10f6a8e99be`, coincidente con FAST almacenado. Se reutilizaron `fast_6037_pve_0.nii.gz` (CSF) y `fast_6037_pve_2.nii.gz` (WM). No se ejecutó FAST ni BET de nuevo.

## Operaciones realizadas

1. `fslmaths fast_6037_pve_0 -thr 0.9 -bin mask_csf_T1.nii.gz` y el equivalente `pve_2` para WM, con rutas completas reales.
2. `flirt -applyxfm -init PRE/reg/highres2example_func.mat -ref PRE/example_func.nii.gz -interp nearestneighbour` de cada máscara T1 hacia la grilla funcional.
3. `fslmaths <mascara_func_prelim> -bin -mas PRE/mask.nii.gz <mascara_func>` para restringir ambas al dominio funcional original.

**Resultados devueltos por `fslstats -V`:**

| Salida | Vóxeles | Volumen |
|---|---:|---:|
| `mask_csf_func.nii.gz` | **4105** | 190858,421875 mm³ |
| `mask_wm_func.nii.gz` | **9089** | 422585,1875 mm³ |

**Archivos generados** en `OUT`: `mask_csf_T1.nii.gz`, `mask_csf_func_prelim.nii.gz`, `mask_csf_func.nii.gz`, `mask_wm_T1.nii.gz`, `mask_wm_func_prelim.nii.gz`, `mask_wm_func.nii.gz`.

El segundo intento encontró el directorio `OUT` existente y se detuvo: «DETENIDO: ya existe ... No se sobrescribió nada».

**Interpretación:** la generación y las comprobaciones de no-vacío se completaron; **la investigadora informó el 14/10/2026 que el control visual en FSLeyes estaba «todo ok»** (esta confirmación no equivale a una revisión independiente del asistente).. Volumen válido no implica pureza WM/CSF. No calcular señales hasta completar [QC visual](02_qc_visual.md).
