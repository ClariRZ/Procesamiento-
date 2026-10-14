# 00 — Insumos y preprocesamiento existente: 6037/run1

**Estado: identificados en la Alienware.** No volvemos a preprocesar el BOLD.

| Propósito | Ruta |
|---|---|
| Carpeta FEAT original | `~/FEAT/6037/run1.feat/` |
| BOLD ya procesado, espacio funcional nativo | `filtered_func_data.nii.gz` |
| Máscara cerebral funcional original | `mask.nii.gz` |
| Referencia funcional para FLIRT | `example_func.nii.gz` |
| T1 utilizado por FEAT | `reg/highres.nii.gz` |
| Transformación T1→EPI | `reg/highres2example_func.mat` |
| Movimiento 6 columnas | `mc/prefiltered_func_data_mcf.par` |
| Derivadas de movimiento existentes | `~/TesisDoctoral/confounds_mirta/6037/run1/motion_deriv.par` |
| FAST ya calculado sobre ese T1 | `~/TesisDoctoral/confounds_mirta/6037/tissue_a24dc10f6a8e99be/fast_6037_pve_{0,1,2}.nii.gz` |

**Resultado constatado en terminal el 14/10/2026:** BOLD 387 volúmenes; T1 y `pve_0/1/2` con dimensiones 256×256×160 y vóxel 0,9375×0,9375×1,1 mm. El prefijo SHA256 de `reg/highres.nii.gz` es `a24dc10f6a8e99be`, correspondiente al nombre de la carpeta FAST; así evitamos repetir FAST.

**Límite de la comprobación:** que existan archivos y coincidan sus identificadores/geometrías no aprueba anatómicamente el T1, la segmentación ni el registro.

**NO utilizar** el BOLD MNI `filtered_func_data_MNI2.nii.gz` en el primer nivel nativo. Tampoco mezclar con salidas previas de fMRIPrep.

Siguiente etapa: [01_confundidores/6037_run1](../01_confundidores/6037_run1/README.md).
