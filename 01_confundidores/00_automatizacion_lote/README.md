# Automatización de confusores nativos — 72 runs pendientes

**Estado: código publicado en GitHub, probado con FSL simulado y con la etapa PREPARE real de 6037/run2.**
El inventario real del 14/10/2026 halló 76 runs: 72 pendientes con insumos FAST y derivadas existentes, 6037/run1 terminado y 3 preprocesamientos incompletos (5031/run1, 6025/run1 y 6025/run2).

## Código
[automatizar_confounds_nativos.py](automatizar_confounds_nativos.py)

**Los únicos cambios permitidos están en** `~/TesisDoctoral/confounds_nativos/<ID>/<run>/`. No se reejecutan BET, FAST, MCFLIRT, FEAT ni se escribe dentro de `~/FEAT`.

La preparación usa PVE0 (CSF) y PVE2 (WM) de la carpeta `confounds_mirta/<ID>/tissue_<SHA256_T1_16>`. Umbral 0.9, `flirt -applyxfm` con `highres2example_func.mat` y vecino más cercano, intersección con máscara funcional, rechazo de máscaras vacías y solapamiento WM/CSF. Las señales se extraen con `fslmeants` en el espacio funcional nativo.

## Etapas

1. **prepare**: genera máscaras e informe `prepare.json`; NO extrae señales ni aprueba QC.
2. **approve**: exige observador, declaración `HE_REVISADO_AMBAS_MASCARAS` y hashes de máscaras intactos después de inspección visual en FSLeyes.
3. **finalize**: exclusivamente después de approve, genera las dos señales y la tabla `Nvol × 14`: 6 MCFLIRT, 6 derivadas, WM, CSF. Comprueba nvol, finitud, variabilidad y derivadas respecto de movimiento.
4. **prepare-all --execute**: prepara todos los runs elegibles sin tocar los existentes. Omite el piloto de 6037/run1, 6037/run2 ya preparado y los tres incompletos.
5. **finalize-all --execute**: finaliza solamente los runs **individualmente aprobados**.
6. **plan** y **status**: solo lectura; permiten identificar faltantes y estados.

Ejemplos (ajustar la ruta al clon o al archivo local descargado):

```bash
SCRIPT="$HOME/TesisDoctoral/CODIGO_AUTOMATIZACION/automatizacion_confounds_72/automatizar_confounds_nativos.py"
python3 "$SCRIPT" status
python3 "$SCRIPT" approve --id 6037 --run run2 --observer "Investigadora principal" --confirm HE_REVISADO_AMBAS_MASCARAS
python3 "$SCRIPT" finalize --id 6037 --run run2
python3 "$SCRIPT" prepare-all --execute
python3 "$SCRIPT" status
```

**Recomendación de ejecución:** terminar y controlar el run2 piloto, luego lanzar `prepare-all`. Escribir los logs fuera del repositorio público. La automatización **nunca aprueba QC visual de manera masiva**. Si falla una carpeta, se conserva para auditoría y queda fuera de `finalize-all`; el lote continúa con las restantes. No ejecutar `prepare-all` en dos terminales al mismo tiempo.

## Resultados de la verificación estructural real del lote (14/10/2026)

La investigadora ejecutó el auditor independiente de lectura tras completar `prepare-all`. Resultados recibidos:

```text
runs=76 OK_TECNICO=72 LEGADO_COTEJADO=1 FUERA_DE_PREPARE=3 REVISAR=0
FASES: CONFOUNDS_COTEJADOS=2 MASCARAS_PREPARADAS=71 PREPROC_INCOMPLETO=3
QC: PENDIENTE_VISUAL=71 PILOTO_MANUAL_SIN_JSON=1 REGISTRADO_POR_HUMANO=1 NO_APLICA=3
```

Se verificó 6037/run2 con 387 volúmenes, máscara funcional 43 832 vóxeles, WM 8 953, CSF 4 058, fase `CONFOUNDS_COTEJADOS` y QC humano registrado. 6037/run1 consta como piloto manual sin JSON retrospectivo. No hubo errores estructurales detectados por este auditor. **Los 71 runs restantes NO están visualmente aprobados y NO tienen confusores finales**; siguen bloqueados para FINALIZE hasta su revisión. Los tres incompletos siguen fuera del lote.

El auditor fue aportado como archivo descargable a la investigadora, **no está incorporado aquí como script Git**. La salida privada permanece local en `~/TesisDoctoral/`.

## Revisión visual por lotes sin aprobar automáticamente

[generar_laminas_qc.py](generar_laminas_qc.py) crea un directorio **nuevo** con imágenes PNG de cinco cortes por run, superposición de WM/CSF sobre `example_func`, y un `index.html` privado para revisar los 71 runs pendientes. **No crea ni altera NIfTI, aprobaciones ni confusores**. Compara las huellas del `prepare.json`, las geometrías y matrices afines, y rechaza máscaras fuera de la máscara cerebral o solapadas.

Ejemplo desde un clon local del repositorio (es necesaria la Python de FSL con `numpy`, `nibabel` y `matplotlib`):

```bash
"$FSLDIR/bin/python" 01_confundidores/00_automatizacion_lote/generar_laminas_qc.py
```

El resultado previsto es `~/TesisDoctoral/QC_LAMINAS_CONFUNDS_20261014/index.html`. El script **se detiene si esa carpeta existe**; no la sobrescribe. Abrir el HTML localmente; no publicarlo en GitHub. Es una previsualización de cinco cortes, **no sustituye revisar todos los cortes y tres planos cuando haya dudas**. Aprobación solo individual de máscaras efectivamente inspeccionadas.

**Ejecución real verificada por salida de terminal, 14/10/2026:** `LAMINAS=71 ERRORES=0`, carpeta local `~/TesisDoctoral/QC_LAMINAS_CONFUNDS_20261014/`. Esto confirma que se generaron las 71 visualizaciones sin errores reportados. **Todavía no se han aprobado visualmente las 71 máscaras**: las cinco secciones por run son un cribado inicial, que debe complementarse con inspección en FSLeyes cuando sea necesario. No interpretar una PNG sin errores como QC humano superado.

## Pruebas y límites

El 14/10/2026 se comprobó `py_compile` y se realizó una prueba sintética completa: `plan`, `prepare`, rechazo de `finalize` sin aprobar, `approve`, `finalize` 387×14, rechazo de segundo `finalize`, rechazo de segundo `prepare`, y omisión en `prepare-all`. El usuario ejecutó `prepare` con FSL real en 6037/run2: máscara cerebro 43832, WM 8953, CSF 4058; indicó que las máscaras eran correctas visualmente. **La finalización real de run2 y el lote de 71 restantes todavía no constan ejecutados.**

La igualdad de dimensiones y pixdim no verifica orientación, matriz afín ni calidad anatómica. Cada run queda sujeto a QC visual y revisión adicional de la señal; no atribuir aprobación a runs no inspeccionados. La huella del T1 se utiliza para ubicar la segmentación FAST, pero no sustituye auditoría exhaustiva de procedencia. Los datos individuales no se suben al Git público.

**Primer nivel posterior:** ver [automatización del primer nivel](../../02_primer_nivel/00_automatizacion_lote/README.md). FEAT Stats only (`inputtype=1`) se debe ejecutar únicamente **sobre copias nuevas** de los directorios `.feat` porque escribe las estadísticas dentro de su entrada.
