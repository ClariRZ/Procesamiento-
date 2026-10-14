# 02 — Primer nivel FEAT por run en espacio funcional nativo

**Piloto: [6037/run1](6037_run1/README.md).**

## Estado actual (14/10/2026)

- **14 confusores nativos 387×14 ya verificados** para el run1.
- **8 EV originales y 8 derivadas temporales** presentes en la plantilla; auditoría temporal básica de los ocho archivos EV realizada. [Ver resultados y pendientes](6037_run1/01_eventos/README.md).
- **21 contrastes originales y expandidos validados**; `feat_model` generó diseño 387×30 (rango 30/30).
- **Piloto 6037/run1 ejecutado** con `inputtype=1` sobre copia FEAT; 21 COPE, VARCOPE y ZSTAT; ver [registro detallado](6037_run1/06_piloto_estadistico/README.md).
- **Pendiente:** QC espacial/máscara, inspección de mapas, interpretación del tramo final ~132 s de la tarea.
- **FILM completado únicamente en la copia del run1 6037**. No extender a run2 u otros sujetos sin cerrar QC.

## Configuración que se comprobará antes de ejecutar

En la Alienware, copiar **sin modificar el original** `~/FEAT/6037/run1.feat`; escoger FEAT *First-level → Statistics → Input is a FEAT directory* apuntando a esa copia. Mantener `filtered_func_data.nii.gz` funcional nativo, máscara funcional y registros originales. No renombrar `filtered_func_data_MNI2`, no volver a suavizar ni volver a procesar movimiento.

Tomar los pesos y títulos de los 21 contrastes del FSF original de 6037/run1 importado de G15; no inventar contrastes. Cargar en FEAT un único archivo `~/TesisDoctoral/confounds_nativos/6037/run1/todos_confounds_nativo.txt` en *Add additional confound EVs*, y elegir *Don't Add Motion Parameters* (ya incluido).

**6037/run1 ya se ejecutó como piloto**, con resultados en `entrada_run1.feat/` (la carpeta de entrada se actualiza en modo Stats only). No relanzarlo; antes de correr el lote o run2, completar QC de geometría, máscara y registros. El segundo nivel de efectos fijos viene **después**, con `COPE` y `VARCOPE` de run1/run2 y registros apropiados.
