# 6037/run1 — progreso real

**Equipo:** Alienware (Ubuntu/FSL). El preprocesamiento `~/FEAT/6037/run1.feat/` continúa intacto.

| Paso | Estado |
|---|---|
| Identificación de preprocesamiento, registro, T1 y FAST existente | Verificado |
| Transformación de máscaras WM/CSF a espacio funcional nativo | **Ejecutada el 14/10/2026** |
| QC visual de máscaras en FSLeyes | **Confirmado por la investigadora («todo ok»), 14/10/2026** |
| Extracción de señales medias WM/CSF del BOLD nativo | **Completada 14/10/2026; 387 filas finitas y variables por señal** |
| Movimiento y derivadas (387 × 6 cada uno) | **Verificados; error máximo 5.55e-17** |
| Matriz de 14 confusores (387 filas) | Pendiente |
| Primer nivel FEAT en nativo | Pendiente |

**Resultados existentes, fuera de Git:** `~/TesisDoctoral/confounds_nativos/6037/run1/`. CSF 4105 vóxeles, WM 9089 vóxeles.

**Máscaras:** [01_mascaras_nativas/](01_mascaras_nativas/README.md). **Señales extraídas:** [02_senales_nativas/](02_senales_nativas/README.md).

La aprobación anatómica está basada en la revisión reportada por la investigadora, no en una captura nueva visible para el asistente. No regenerar ni sobrescribir las máscaras existentes.

**Movimiento:** [03_movimiento/](03_movimiento/README.md), verificado sin repetir MCFLIRT.

**Continuación:** [03_senales_y_confounds.md](03_senales_y_confounds.md), validar movimiento y derivadas y construir la matriz de 14 confusores. No lanzar FEAT hasta validar también el diseño del GLM.
