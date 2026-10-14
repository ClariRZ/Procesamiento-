# Automatización primer nivel — Etapa 00

Se incorporó el inventario de elegibilidad **de solo lectura** para todos los runs preprocesados.

## Ejecutar el inventario en Ubuntu

Desde un clon local del repositorio:

```bash
python3 02_primer_nivel/00_automatizacion_lote/inventariar_primer_nivel.py
```

No ejecuta FEAT, no modifica los directorios originales y no crea imágenes. Requiere FSL (`fslval`) disponible. Busca `~/FEAT/<id>/run1.feat` y `run2.feat`, sin inventar un número de runs.

El reporte tabulado contiene identificador, run, nvol, TR, estado y motivos. Comprueba BOLD/máscara, preprocesamiento, registros, 8 EV por run, máscaras WM y CSF nativas, matriz de 14 confusores, movimiento MCFLIRT y sus derivadas, y que el destino esté libre.

- `REVISAR`: hay prerrequisitos ausentes o incorrectos.
- `APTO_TECNICO_PENDIENTE_QC_VISUAL`: las verificaciones del script pasaron, **no equivale a aprobación humana**.
- `YA_ANALIZADO_PILOTO`: protege la ejecución terminada de 6037/run1.

## Inventario real de la Alienware (14/10/2026)

**Confirmado a partir de la salida compartida por la investigadora:** 38 sujetos, 76 carpetas run detectadas; 73 con BOLD/máscara/registros suficientes para avanzar, incluidas las estadísticas ya calculadas de 6037/run1; **72 adicionales requieren máscaras WM/CSF y confounds nativos**; **3 preprocesamientos incompletos** quedan fuera del lote. Las etiquetas originales del inventario fueron 75 `REVISAR` y 1 `YA_ANALIZADO_PILOTO` (las 75 incluyen los 72 faltantes y los 3 incompletos). No asumir que las máscaras y confounds faltantes ya fueron creados.

## Siguiente comprobación, solo lectura

Antes de generar las máscaras faltantes debemos saber si FAST (PVE0 LCR y PVE2 WM) está disponible y corresponde al **mismo T1 registrado para cada run**, y si las derivadas MCFLIRT que ya preparó el pipeline anterior están disponibles. Ejecutar:

```bash
python3 02_primer_nivel/00_automatizacion_lote/auditar_insumos_confounds.py
```

El auditor calcula la huella SHA256 de `reg/highres.nii.gz`, busca su carpeta FAST `tissue_<16 caracteres>` dentro de `~/TesisDoctoral/confounds_mirta/<id>/`, comprueba `fast_<id>_pve_0.nii.gz`, `fast_<id>_pve_2.nii.gz`, y `motion_deriv.par` por run. No genera ni modifica NIfTI. **Una coincidencia de nombre basada en huella y archivos presentes no sustituye la inspección geométrica, los hashes de procedencia completos ni el QC visual de WM/CSF.** El script se probó con casos sintéticos positivo y con PVE faltante; no fue ejecutado aún sobre la muestra real.

## Primer nivel: inventario final y generación segura de FSF (14/10/2026)

**Resultado recibido de la Alienware:** `CONFOUNDS_COTEJADOS=73`, `PREPROC_INCOMPLETO=3`, `REVISAR=0`, `REGISTRADO_POR_HUMANO=72` y el piloto 6037/run1 registrado por separado. Se cierra la etapa de confusores para los preprocesamientos completos.

El nuevo script [preparar_fsf_nativos.py](preparar_fsf_nativos.py) tiene **dos acciones**:

- `plan`: solo lectura, detecta 6037/run1 ya calculado, exige un confound final 14-columnas con manifiesto/hashes y QC humano, verifica la existencia de los ocho EV y de los archivos FEAT esenciales, y comprueba que no haya destino del primer nivel ocupado. Debe arrojar idealmente 72 candidatos, pero es necesario comprobarlo sobre la Alienware.
- `generar --id 6037 --run run2`: tras pasar el plan, utiliza **la plantilla local realmente ejecutada** `~/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/6037_run1_nativo_INPUTTYPE1.fsf`, conserva los 8 EV, 8 derivadas, 21 contrastes y 14 confusores, y actualiza exclusivamente las rutas y los números de volúmenes, TR y total de vóxeles. Escribe un único FSF nuevo en `~/TesisDoctoral/PRIMER_NIVEL_LOTE_NATIVO/6037/run2_stats_only.fsf`. **NO copia todavía ningún FEAT ni ejecuta FILM.**

```bash
python3 preparar_fsf_nativos.py plan
python3 preparar_fsf_nativos.py generar --id 6037 --run run2
```

El modo `inputtype=1` de FEAT escribe las estadísticas dentro de la **carpeta `.feat` de entrada**, por lo que el siguiente módulo deberá copiar cada preprocesamiento a una ubicación independiente, **excluyendo estadísticas antiguas** y verificando hash/registro antes de lanzar una sola ejecución piloto. No usar `feat` sobre `~/FEAT`.

**Estado:** el script está publicado, pero no ha sido ejecutado todavía sobre el dataset real; no considerar listos los 72 FSF hasta inspeccionar el resultado del plan y probar un caso. `plan` no ejecuta FEAT ni prepara archivos; la generación individual no ejecuta FEAT.

## Qué sigue tras obtener el inventario

Resolver faltantes de máscaras y confusores **en espacio funcional nativo**, auditar la calidad visual, generar un FSF individual con 8 EV, 8 derivadas, 21 contrastes y 14 confusores; preparar una **copia independiente** por run, validar el diseño y lanzar FILM solamente sobre runs aprobados. En modo *Statistics only* con entrada `.feat`, FSL agrega las estadísticas a esa misma copia.

**Importante:** esta etapa NO es un lanzador de lote. Se probó con fixtures sintéticas; aún falta comprobarla sobre los datos reales de la Alienware. No subir NIfTI, EVs individuales, confusores ni informes por sujeto al repositorio público.

Ver [piloto 6037/run1](../6037_run1/06_piloto_estadistico/README.md) y [código del inventario](inventariar_primer_nivel.py).

## Actualización confirmada: confusores completos (14/10/2026)

La auditoría final comunicada por la investigadora fue:

```text
RESUMEN runs=76 OK_TECNICO=72 LEGADO_COTEJADO=1 FUERA_DE_PREPARE=3 REVISAR=0
FASES CONFOUNDS_COTEJADOS=73 PREPROC_INCOMPLETO=3
QC NO_APLICA=3 PILOTO_MANUAL_SIN_JSON=1 REGISTRADO_POR_HUMANO=72
```

**Cerrada la etapa de confusores:** 73 runs completos (72 automatizados + piloto manual 6037/run1); 3 runs incompletos excluidos. El control visual de 72 runs está registrado por humano, principalmente mediante 71 láminas de cinco cortes; ese alcance no equivale a inspección exhaustiva de cada vóxel. Ahora corresponde generar y validar los FSF nativos por run antes de ejecutar FILM. Evitar modificar `~/FEAT` y nunca repetir el primer nivel de 6037/run1.
