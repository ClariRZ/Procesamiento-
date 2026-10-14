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

## Qué sigue tras obtener el inventario

Resolver faltantes de máscaras y confusores **en espacio funcional nativo**, auditar la calidad visual, generar un FSF individual con 8 EV, 8 derivadas, 21 contrastes y 14 confusores; preparar una **copia independiente** por run, validar el diseño y lanzar FILM solamente sobre runs aprobados. En modo *Statistics only* con entrada `.feat`, FSL agrega las estadísticas a esa misma copia.

**Importante:** esta etapa NO es un lanzador de lote. Se probó con fixtures sintéticas; aún falta comprobarla sobre los datos reales de la Alienware. No subir NIfTI, EVs individuales, confusores ni informes por sujeto al repositorio público.

Ver [piloto 6037/run1](../6037_run1/06_piloto_estadistico/README.md) y [código del inventario](inventariar_primer_nivel.py).
