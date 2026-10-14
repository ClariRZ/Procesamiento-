# 01 — Confusores funcionales nativos

Para cada run: seis parámetros MCFLIRT + seis derivadas temporales del movimiento + señal media WM + señal media CSF. En 6037/run1 habrá 387 filas y 14 columnas.

**Piloto:** las máscaras WM/CSF fueron generadas y la investigadora confirmó su revisión en FSLeyes el 14/10/2026. Se documentan junto con los scripts reproducibles en [6037_run1/01_mascaras_nativas](6037_run1/01_mascaras_nativas/README.md).

**Pendiente:** extracción de las señales y creación/verificación del fichero 387×14. No se recalcula FAST ni el preprocesamiento original. No añadir de nuevo los parámetros de movimiento en FEAT cuando estén incluidos en los 14 confusores.

[Siguiente paso: señales y confusores](6037_run1/03_senales_y_confounds.md).
