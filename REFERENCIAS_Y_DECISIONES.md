# Protocolo Mirta vs. primer nivel funcional nativo — decisiones verificables

## Fuente de supervisión

Documento aportado: **«Pasos realizados en el FSL preprocesado más First-level run1»**, ocho páginas, ejemplo 6037. No se modificó el original.

| Página del Word | Parte que se conserva | Adaptación nativa |
|---|---|---|
| 1–2 | BET T1, preprocesamiento FEAT ya realizado y revisado; 387 volúmenes, TR 2 s, suavizado 8 mm y HP 100 s en nuestro run1. | No repetirlos automáticamente: reutilizar `run1.feat` tras QC. |
| 3 | MCFLIRT `.par`, seis rotaciones/traslaciones, seis diferencias temporales de primer orden con ceros iniciales. | Se conserva idéntico movimiento del mismo run; las derivadas se recalculan fuera de `.feat`. |
| 3–4 | FAST T1 3 clases; CSF `pve_0`, WM `pve_2`, umbral 0,9 y binarización. | Se ejecuta sobre **el mismo `reg/highres.nii.gz`** usado por FEAT. |
| 4 | Transformar las máscaras al mismo espacio que el BOLD y revisarlas con FSLeyes; usar NN para máscaras. | **No MNI**. `flirt -applyxfm -init highres2example_func.mat -ref example_func.nii.gz -interp nearestneighbour`; intersección con la máscara EPI nativa. |
| 5 | `fslmeants` WM y CSF + combinación de hasta 14 columnas. | Extraer de `filtered_func_data.nii.gz` **nativo**, usando las máscaras funcionales, sin normalizar la serie. |
| 6–8 | FEAT First-level → Statistics; confound EVs; ocho eventos y 21 contrastes. | `Input is a FEAT directory` sobre una copia del preprocesado **nativo**, reutilizando el `.fsf` auténtico de 6037 y las EV de run1. |

**Cuidado con una ambigüedad del Word:** crea máscaras MNI `*_clean` pero sus comandos de extracción utilizan las máscaras MNI **sin** `_clean`. Aquí se adopta explícitamente **intersección con máscara funcional nativa** antes de `fslmeants`. Es una decisión de adaptación, **no** una transcripción literal de esos comandos MNI.

Mirta aclara en página 3 que también es posible seguir en espacio nativo y transformar solamente los contrastes para niveles superiores. **Los mapas estadísticos no se han transformado aquí**: primero se verificará el primer nivel por run.

## Fuentes oficiales de FSL consultadas

1. [FEAT User Guide](https://fsl.fmrib.ox.ac.uk/fsl/docs/task_fmri/feat/user_guide.html). Statistics permite FEAT directories, pero **seleccionar la carpeta FEAT en la GUI restablece otros ajustes**; seleccionar esa entrada ANTES de confirmar EV/contrastes. `feat <design.fsf>` y `feat_model` son comandos oficiales.
2. [FEAT FAQ](https://fsl.fmrib.ox.ac.uk/fsl/docs/task_fmri/feat/faq.html). Primer nivel habitualmente en espacio EPI nativo, grupo en estándar.
3. [FEAT output directory](https://fsl.fmrib.ox.ac.uk/fsl/docs/task_fmri/feat/feat_output.html). `filtered_func_data`, `mask`, `mc/*.par`, `reg/highres2example_func.mat`, `stats/cope*` y `varcope*`.
4. [FAST](https://fsl.fmrib.ox.ac.uk/fsl/docs/structural/fast.html). T1 cerebral como entrada, clases y mapas de volumen parcial.
5. [FLIRT User Guide](https://fsl.fmrib.ox.ac.uk/fsl/docs/registration/flirt/user_guide.html) y [FLIRT FAQ](https://fsl.fmrib.ox.ac.uk/fsl/docs/registration/flirt/faq.html). Aplicación de transformaciones guardadas y geometría determinada por imagen de referencia.
6. [FSL utilities](https://fsl.fmrib.ox.ac.uk/fsl/docs/utilities/fslutils.html) y [Registration Practical](https://fsl.fmrib.ox.ac.uk/fslcourse/graduate/lectures/practicals/registration/index.html). `fslmeants` extrae la media temporal en una máscara que esté en la grilla adecuada.

## Control de rigor

- Este código no declara que FSL imponga **14** confounds; es una elección del protocolo de Mirta. `Add additional confound EVs` admite una columna por confusor.
- Se usa `feat_model <raiz> <archivo_confounds>` para comprobar el diseño incluyendo la matriz externa (si no, se pueden omitir 14 columnas en el *preflight*).
- La comprobación `matriz 387 × 30, rango 30, 21 contrastes` **requiere el `feat_model` real de la G15**, no basta con pruebas simuladas.
- Umbrales de seguridad que detectan máscaras excesivas (>80% del FOV, WM >80% y CSF >50% del cerebro funcional) **no son criterios universales de aceptabilidad anatómica**; ninguna máscara queda aprobada automáticamente.
- Los runs se combinan **después**, con COPE/VARCOPE y transformaciones de registro apropiadas. No promediar Z ni asumir espacios nativos equivalentes entre runs.
