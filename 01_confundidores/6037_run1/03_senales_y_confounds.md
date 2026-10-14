# Paso 3 — Extraer WM/CSF y preparar la matriz de confusores

**Estado: PENDIENTE. No se ha ejecutado.** No extraer señales antes de aprobar el QC visual.

Una vez aprobadas las dos máscaras, las entradas previstas serán:

- BOLD: `~/FEAT/6037/run1.feat/filtered_func_data.nii.gz` (387 volúmenes, **nativo**).
- WM: `~/TesisDoctoral/confounds_nativos/6037/run1/mask_wm_func.nii.gz`.
- CSF: `~/TesisDoctoral/confounds_nativos/6037/run1/mask_csf_func.nii.gz`.
- Movimiento: `~/FEAT/6037/run1.feat/mc/prefiltered_func_data_mcf.par`.
- Derivadas existentes: `~/TesisDoctoral/confounds_mirta/6037/run1/motion_deriv.par` (revalidar procedencia y valores contra el movimiento).

**Pendiente de construir**, en nuevo destino bajo `~/TesisDoctoral/confounds_nativos/6037/run1/`:

1. `fslmeants` sobre BOLD nativo para las dos señales.
2. Verificar exactamente 387 muestras por señal, que sean finitas y no constantes.
3. Verificar `motion_deriv.par` frente a las primeras diferencias del `.par` original.
4. Combinar en orden **6 movimiento + 6 derivadas + 1 WM + 1 CSF**, sin borrar filas: 387×14; comprobar finitud y rango, guardar procedencia.

No se incluye aún un lanzador ejecutable porque falta la decisión QC del paso anterior. No reciclar por defecto las señales WM/CSF extraídas previamente en MNI.
