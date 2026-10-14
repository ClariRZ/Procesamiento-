# Histórico de pasos — señales y confusores de 6037/run1

Los pasos descritos aquí ya se ejecutaron y tienen subcarpetas independientes con scripts, explicación y comprobaciones.

- **Señales WM/CSF en espacio EPI:** 387 valores por señal; verificadas. [02_senales_nativas](02_senales_nativas/README.md).
- **Movimiento MCFLIRT y derivadas:** 387×6 por componente, diferencia máxima de derivadas 5.55111512313e-17. [03_movimiento](03_movimiento/README.md).
- **Archivo final 387×14:** generado en `~/TesisDoctoral/confounds_nativos/6037/run1/todos_confounds_nativo.txt` y verificado frente a las cuatro fuentes; usuaria informó «confounds nativos ok». [04_confounds_finales](04_confounds_finales/README.md).

Los scripts que se añadieron a Git después del piloto documentan el procedimiento; no se han ejecutado como programas versionados en la Alienware. El material MRI y las matrices individuales permanecen fuera del Git público.

**El rango y condicionamiento del diseño GLM completo aún no se han comprobado.** El siguiente paso consiste en inspeccionar los ocho archivos EV del propio run, el FSF real y los 21 contrastes antes de construir el diseño.
