# 01 — Confusores del GLM

Para el primer nivel **nativo** de cada run:

- 6 parámetros MCFLIRT del propio run.
- 6 primeras diferencias de esos parámetros (primera fila cero).
- 1 serie temporal media de sustancia blanca (WM) del BOLD nativo.
- 1 serie temporal media de líquido cefalorraquídeo (CSF) del BOLD nativo.

Se construirá un único archivo **387 filas × 14 columnas** para 6037/run1, después de verificar las señales. No agregar además `Add Motion Parameters` en FEAT, porque duplicaría regresores.

**Estado real:** en [6037_run1](6037_run1/README.md) las máscaras nativas se generaron el 14/10/2026; el QC visual y las señales aún están pendientes. No son válidas automáticamente por superar controles numéricos.
