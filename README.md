# Tesis doctoral — procesamiento funcional FSL, registro paso a paso

**Rama de reorganización (14/10/2026).** Esta versión documenta lo **realmente realizado** en el piloto 6037/run1 en la **Alienware**. La rama `main` conserva, como respaldo, los scripts previos y sus pruebas; **no se borraron** de `main`.

## Orden de trabajo

| Carpeta | Etapa | Estado |
|---|---|---|
| [00_insumos_y_preprocesamiento](00_insumos_y_preprocesamiento/README.md) | Localizar y comprobar el preprocesamiento FSL original | Insumos confirmados; QC previo no sustituido |
| [01_confundidores/6037_run1](01_confundidores/6037_run1/README.md) | FAST existente, máscaras WM/CSF en EPI, revisión, señales, 14 columnas | **Máscaras y señales nativas correctas; matriz 387×14 pendiente** |
| [02_primer_nivel](02_primer_nivel/README.md) | GLM de cada run en espacio funcional nativo; 8 EV y 21 contrastes | Pendiente |
| [03_efectos_fijos](03_efectos_fijos/README.md) | Combinar run1 + run2 por sujeto | Pendiente |
| [04_analisis_grupal](04_analisis_grupal/README.md) | Comparaciones entre participantes | Pendiente |
| [05_atlas_y_conectividad](05_atlas_y_conectividad/README.md) | Atlas, señales regionales y conectividad funcional durante la tarea | Pendiente |
| [DECISIONES.md](DECISIONES.md) | Decisiones, advertencias y procedencia | En actualización |

## Principios

1. **Un paso a la vez.** Cada etapa registra insumos, comandos, resultados numéricos y QC; no se declara completa una operación pendiente.
2. **FSL nativo en primer nivel.** Utilizar `filtered_func_data.nii.gz` de cada `.feat` original sin normalizar todo el BOLD a MNI antes de FILM. Mantener transformaciones existentes para niveles posteriores.
3. **Ningún dato individual en Git.** Este repositorio es público: no subir NIfTI, DICOM, `.feat`, eventos de participantes, matrices de confusores, capturas de MRI ni información clínica.
4. **No escribir en los preprocesamientos originales.** Las nuevas máscaras están bajo `~/TesisDoctoral/confounds_nativos/6037/run1/`, fuera de Git.
5. **Máscara generada ≠ aprobada.** FAST, registro y máscaras requieren inspección humana.
6. **No ejecutar scripts históricos automáticamente.** Los programas de la rama `main` son material preservado, no evidencia de que se ejecutaron en este flujo.

**Siguiente acción:** revisar en FSLeyes las máscaras WM y CSF del piloto 6037/run1, documentada en [01_confundidores/6037_run1/02_qc_visual.md](01_confundidores/6037_run1/02_qc_visual.md).
