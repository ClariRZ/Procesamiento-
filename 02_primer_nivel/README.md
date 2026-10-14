# 02 — Primer nivel FEAT por run, en espacio funcional nativo

**Estado: PENDIENTE**, condicionado a confusores nativos revisados y completos.

Para 6037/run1, usar una **copia independiente** de `~/FEAT/6037/run1.feat`; FEAT **First-level analysis → Statistics → Input is a FEAT directory**. No reemplazar `filtered_func_data.nii.gz` por la imagen normalizada. Conservar los productos `reg/` originales y verificar qué máscara utiliza efectivamente FILM.

Modelo a auditar antes de ejecutar: FSF manual original G15 `/home/clara/Escritorio/6037/run1_firstlevel.feat/design.fsf` (8 EV con derivadas temporales, 21 contrastes, 387 volúmenes, TR 2 s, FILM). Cambiar **solo en una copia** las rutas de eventos, confusores, FEAT de entrada y salida; comprobar diseño y confusores sin duplicar movimiento. Los archivos de eventos de 6037/run1 deben verificarse en la Alienware; no asumir su existencia por el FSF de la G15.

El procedimiento completo y su ejecución se documentarán **después** de cerrar el control visual y la matriz 14×387. No lanzar el GLM ni el lote todavía.

**Importante:** la combinación de dos runs no forma parte del primer nivel; se realiza en [03_efectos_fijos](../03_efectos_fijos/README.md).
