# 01 — Confusores del GLM en espacio funcional nativo

**Piloto 6037/run1 completado y validado (14/10/2026).** Un único fichero `todos_confounds_nativo.txt` de **387 filas × 14 columnas**: seis parámetros MCFLIRT, seis primeras diferencias del movimiento, señal WM nativa y señal CSF nativa.

Todos los productos individuales se conservan en la Alienware; no en este repositorio público.

La cadena documentada, con scripts por subetapa, se encuentra en [6037_run1](6037_run1/README.md): máscaras → señales tisulares → movimiento/derivadas → matriz final.

**Estado:** el contenido y la procedencia de la matriz final se verificaron con las cuatro fuentes; **aún falta validar la matriz completa de diseño FEAT** y sus eventos. Al configurar FEAT, seleccionar *Don't Add Motion Parameters* porque el fichero adicional ya incluye el movimiento.

**Continuación:** [02 — primer nivel nativo](../02_primer_nivel/README.md).
