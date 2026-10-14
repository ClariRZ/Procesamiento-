# 6037/run1 — copia independiente del preprocesamiento FEAT

**Estado: completado y comprobado en la Alienware (14/10/2026).** Este es un paso de preparación, **no** una ejecución de FEAT.

## Origen y destino

- Origen que debe permanecer intacto: `~/FEAT/6037/run1.feat/`.
- Copia creada: `~/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/entrada_run1.feat/`.
- El `du -sh` del origen indicó **638 MB**; el sistema mostró **1,6 TB** libres.
- Se empleó `rsync -a --exclude='filtered_func_data_MNI2*'` para no llevar el BOLD adicional transformado a MNI al piloto **nativo**.

La usuaria obtuvo los siguientes controles con `test -s` y `cmp -s` entre el original y la copia, todos **OK**:

1. `filtered_func_data.nii.gz`
2. `mask.nii.gz`
3. `design.fsf`
4. `example_func.nii.gz`
5. `reg/example_func2standard_warp.nii.gz`

Salida terminal: **`COPIA DEL PREPROCESAMIENTO COMPLETADA`**.

**Límites del control:** el cotejo binario se hizo para los cinco elementos listados, no constituye una auditoría binaria exhaustiva de todo el árbol de `.feat`. Tampoco ha sido lanzado todavía el GLM; el original no se modificó con este procedimiento.

## Reproducción

[crear_copia_preprocesamiento.sh](crear_copia_preprocesamiento.sh) conserva el comando usado y las comprobaciones principales. **Se versionó después de realizar la copia por terminal y NO debe ejecutarse sobre el destino existente.** Rechaza sobrescritura. Los datos y las imágenes permanecen en la Alienware, nunca en GitHub público.

## Siguiente etapa

Inspeccionar en modo lectura la configuración de *Registration* y los archivos `custom1..8` de la plantilla original de 6037, antes de generar **una nueva copia del FSF** para *Statistics only* sobre la entrada nativa. Revisar la aplicación del corte temporal 100 s al modelo sin filtrar de nuevo el BOLD y conservar los registros originales para efectos fijos y atlas. No iniciar `feat` todavía.
