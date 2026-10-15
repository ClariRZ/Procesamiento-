# Auditoría metodológica previa al lote FEAT — 14/10/2026

**Esta rama es experimental; `main` no se modificó.**

Estado comunicado desde Alienware: 76 FEAT originales, 73 preprocesamientos utilizables, 3 incompletos, 2 pilotos 6037 ya ejecutados, 71 copias estadísticas previamente preparadas y 71 FSF auditados en estructura. Estos números se han recibido por conversación; no son resultados obtenidos por la rama.

## Nueva herramienta de solo lectura

`auditar_homogeneidad_y_diseno.py` inspecciona los `design.fsf` originales por run y compara parámetros relevantes: `ndelete`, `paradigm_hp`, `smooth`, `temphp_yn`, `templp_yn`, `st`, TR y número de volúmenes. Compara runs del mismo sujeto y comprueba los FSF de estadística existentes (rutas e indicadores Stats only).

Además, si existe `~/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/entrada_run1.feat/design.mat`, compara las 14 columnas de confusores incluidas en la matriz del piloto con sus series de entrada y muestra correlaciones máximas entre confusores y EVs de tarea. La correlación **no prueba** si se aplicó exactamente el mismo filtro ni demuestra contaminación de sustancia gris. No reejecuta `feat_model` ni FEAT.

```bash
cd ~/Procesamiento-
git fetch origin auditoria-metodologica-20261014
git show origin/auditoria-metodologica-20261014:02_primer_nivel/00_automatizacion_lote/auditar_homogeneidad_y_diseno.py | python3 -B -
```

Para ejecutar pruebas sintéticas conviene trabajar en un checkout de esta rama, separadamente de cualquier ejecución real:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest \
    02_primer_nivel/00_automatizacion_lote/test_auditar_homogeneidad_y_diseno.py
```

## Por qué no lanzar todavía

- El pipeline de WM/CSF usa FAST PVE umbral 0,9, transformado con vecino más cercano, sin erosión explícita; extrae señal del BOLD ya filtrado espacial/temporalmente. Evaluar contaminación GM en vez de darla por demostrada.
- El análisis Statistics-only lleva `filtering_yn=0`. Según el manual FSL, los confusores de FEAT se filtran temporalmente cuando la opción correspondiente está activada en Pre-stats. Comprobar en el piloto cómo quedó `design.mat` y la temporalidad respecto del BOLD preprocesado.
- Existen incertidumbres abiertas: máscara de FILM 41342 frente a 43812 voxeles, visualización de cinco cortes con orientación discutida, y revisión de contrastes ampliados. No usar un estado computacional terminado como aprobación científica.
- El estado actual ya posee 71 copias; **no repetir `prepare-all` ni borrar los 71 intentos** sin identificar sus contenidos y sin respaldo.
- `6037/run1` es legado sin `finalize.json`: no debe marcarse automáticamente inválido ni recibir documentos retrospectivos inventados.

Falta decidir criterios concretos de máscara WM/CSF y filtrado a partir de resultados locales. Esta rama no cambia métodos ni genera nuevos confusores.
