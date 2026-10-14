# 01 — Confusores funcionales nativos

Para cada run: seis parámetros MCFLIRT + seis derivadas temporales del movimiento + señal media WM + señal media CSF. En 6037/run1 habrá 387 filas y 14 columnas.

**Piloto:** las máscaras WM/CSF fueron generadas y la investigadora confirmó su revisión en FSLeyes el 14/10/2026. Se documentan junto con los scripts reproducibles en [6037_run1/01_mascaras_nativas](6037_run1/01_mascaras_nativas/README.md).

**Ejecutado el 14/10/2026:** extracción de ambas señales nativas WM/CSF, cada una con 387 valores, finitos y variables. [Procedimiento y scripts](6037_run1/02_senales_nativas/README.md). **Pendiente:** validación del movimiento y derivadas y construcción/verificación del fichero 387×14. No se recalcula FAST ni el preprocesamiento original. No añadir de nuevo los parámetros de movimiento en FEAT cuando estén incluidos en los 14 confusores.

[Siguiente paso: señales y confusores](6037_run1/03_senales_y_confounds.md).
