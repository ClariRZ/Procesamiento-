# Auditoría comparativa de la cola temporal — 6037, run1 y run2

**Realizada el 14/10/2026 en la Alienware mediante un bloque de lectura.**

## Entradas existentes

- `~/FEAT/6037/run{1,2}.feat/filtered_func_data.nii.gz`
- `~/FEAT/6037/run{1,2}.feat/design.fsf` (preprocesamiento)
- `~/NIFTIS_DESCOMPRIMIDOS/6037/evs/run-{1,2}/*.txt`

El cálculo obtuvo duración nominal del BOLD mediante `fslval dim4` y `pixdim4`; para el último evento usó el máximo de `inicio + duración` entre **todos los archivos de eventos, incluido Descanso.txt**. El parámetro `fmri(ndelete)` se leyó del FSF guardado.

| Indicador | Run1 | Run2 |
|---|---:|---:|
| Volúmenes | 387 | 387 |
| TR (s) | 2.0 | 2.0 |
| Adquisición nominal (s) | 774.000 | 774.000 |
| Último evento | Descanso | Descanso |
| Final del último descanso (s) | 641.706 | 641.595 |
| Tiempo restante sin evento registrado (s) | **132.294** | **132.405** |
| `fmri(ndelete)` | 0 | 0 |

La diferencia entre las colas de ambos runs es **0.111 s**. Esto respalda que el tramo final sin eventos registrados es un patrón repetido, no exclusivo del run1.

## Interpretación y límites

- **No se demuestra** por estos archivos por qué se adquirieron unos 132 s adicionales ni si ese tramo era un reposo planificado, espera, demora de terminación u otra circunstancia.
- La duración `dim4 × TR` es **nominal**; la revisión no comprueba por sí sola los desencadenantes del escáner ni el sincronismo real tarea–BOLD.
- Un tramo final sin eventos no obliga automáticamente a recortar los volúmenes ni a modificar los onsets; hacerlo cambiaría filtrado, ruido y estimación estadística.
- `Descanso.txt` sigue fuera de los ocho EV de tarea del FSF original; no incorporarlo sin justificar un cambio de modelo.
- **Pendiente para validación científica:** comparar con diseño real del paradigma, registros de presentación o metadata de adquisición, y controlar los 21 contrastes antes de FILM.

## Script

[comparar_cola_runs.sh](comparar_cola_runs.sh) reproduce de forma **solo lectura** la comprobación temporal, sin NumPy. Se añadió a GitHub después de ejecutar el bloque manual; **no se ha ejecutado todavía como script versionado**.

Próxima acción: controlar los **21 contrastes** de la plantilla original en la Alienware. El GLM nativo aún no se lanza.
