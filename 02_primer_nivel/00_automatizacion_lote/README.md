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

## Qué sigue tras obtener el inventario

Resolver faltantes de máscaras y confusores **en espacio funcional nativo**, auditar la calidad visual, generar un FSF individual con 8 EV, 8 derivadas, 21 contrastes y 14 confusores; preparar una **copia independiente** por run, validar el diseño y lanzar FILM solamente sobre runs aprobados. En modo *Statistics only* con entrada `.feat`, FSL agrega las estadísticas a esa misma copia.

**Importante:** esta etapa NO es un lanzador de lote. Se probó con fixtures sintéticas; aún falta comprobarla sobre los datos reales de la Alienware. No subir NIfTI, EVs individuales, confusores ni informes por sujeto al repositorio público.

Ver [piloto 6037/run1](../6037_run1/06_piloto_estadistico/README.md) y [código del inventario](inventariar_primer_nivel.py).
