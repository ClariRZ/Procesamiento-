# Procesamiento funcional FSL — tesis doctoral

**Piloto actual: 6037/run1 en la Alienware, espacio funcional nativo.** Este repositorio documenta las operaciones realmente ejecutadas, los controles reportados por la investigadora y los scripts reproducibles incorporados después de cada paso. La documentación de la antigua organización se conserva en el historial de Git, no en los archivos vigentes.

| Etapa | Ubicación | Estado |
|---|---|---|
| 00. Insumos y preprocesamiento existente | [00_insumos_y_preprocesamiento](00_insumos_y_preprocesamiento/README.md) | Identificados y conservados |
| 01. Confusores de 6037/run1 | [01_confundidores/6037_run1](01_confundidores/6037_run1/README.md) | **387×14 construido y validado** |
| 02. Primer nivel FEAT por run | [02_primer_nivel](02_primer_nivel/README.md) | **Siguiente: revisar EV, derivadas y 21 contrastes** |
| 03. Efectos fijos run1 + run2 | [03_efectos_fijos](03_efectos_fijos/README.md) | Pendiente |
| 04. Comparación entre sujetos | [04_analisis_grupal](04_analisis_grupal/README.md) | Pendiente |
| 05. Atlas y conectividad funcional de tarea | [05_atlas_y_conectividad](05_atlas_y_conectividad/README.md) | Pendiente |

## Reglas de trabajo

- Un paso a la vez: ejecutar → verificar → documentar → pasar al siguiente.
- Primer nivel en **espacio funcional nativo**; combinar resultados estadísticos con registros apropiados antes de comparaciones superiores y atlas.
- No repetir BET, FAST, MCFLIRT ni etapas ya resueltas; no modificar ni sobrescribir `~/FEAT/6037/run1.feat/`.
- Guardar imágenes NIfTI, datos individuales, eventos y matrices de confusores **solo en almacenamiento local/privado**. Este GitHub es público.
- No atribuir a una captura inicial una aprobación que no pueda verificarse; conservar la procedencia de la valoración anatómica.
- Los nuevos scripts de Git aún **no fueron ejecutados directamente** como versiones independientes en la Alienware, salvo que se indique lo contrario. Los pasos manuales que reproducen sí fueron verificados.

**Archivo de confusores verificado:** `~/TesisDoctoral/confounds_nativos/6037/run1/todos_confounds_nativo.txt`, 387 filas × 14 columnas. [Script, verificación y detalles](01_confundidores/6037_run1/04_confounds_finales/README.md).
