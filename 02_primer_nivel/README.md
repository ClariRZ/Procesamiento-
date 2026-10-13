# 02 — Primer nivel FEAT Statistics, funcional nativo

Piloto y GUI: [`6037/README.md`](6037/README.md). Motor reutilizable: [`automatizacion/primer_nivel.py`](automatizacion/primer_nivel.py).

El `.fsf` se obtiene **del diseño real del run**, no de un contraste inventado. Para otros runs es obligatorio pasar `--fsf /ruta/del/runX/design.fsf`. La etapa `diseno` ejecuta FSL `feat_model` con los 14 confusores; la etapa `ejecutar` exige confirmación explícita. No hay lote habilitado.

**Advertencia:** No utilizar `filtered_func_data_MNI2`; no reemplazar ni renombrar imágenes en el FEAT original. FEAT Statistics recibe la **copia de un directorio FEAT preprocesado**, `inputtype=1`, con el BOLD nativo intacto y los registros existentes. No repetir smoothing, MCFLIRT ni filtrado del BOLD. Cualquier transformación a MNI de COPE/VARCOPE corresponde al nivel posterior.
