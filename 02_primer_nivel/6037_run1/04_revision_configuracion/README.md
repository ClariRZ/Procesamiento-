# 6037/run1 — auditoría de configuración previa a Statistics

**Comprobación ejecutada en la Alienware el 14/10/2026; solo lectura.**

## Registros

| Parámetro | Preprocesamiento nativo de FEAT | Primer nivel manual de G15 (BOLD ya en MNI) |
|---|---:|---:|
| `reginitial_highres_yn` | 0 | 0 |
| `reghighres_yn` | **1** | 0 |
| `regstandard_yn` | **1** | 1 |
| `regstandard_nonlinear_yn` | **1** | 0 |

**Interpretación:** ambos FSF describen situaciones espaciales distintas. El primer nivel manual de G15 no se puede reutilizar copiando sus opciones de registro directamente. La ruta nativa preserva los productos `reg/` del FEAT previamente registrado (funcional→T1→MNI); antes del lanzamiento hay que comprobar cómo reutilizar esos productos sin repetir la estimación espacial. Los registros NO son confusores ni se recalculan para extraer WM/CSF; ya contamos con `highres2example_func.mat`.

## Eventos y HRF

Se encontraron `custom1` a `custom8` en la plantilla original, apuntando a los ocho archivos de eventos **de la G15**; para el modelo nuevo se deben dirigir a la carpeta equivalente **de la Alienware**, conservando el orden:

1. AtencionPlena
2. ExperimNeg
3. ExperimNeutra
4. Likert
5. ObservaNeg
6. ObservaNeutra
7. Reinterpreta
8. Suprime

En todos los EV: **`convolveN=3` (HRF doble gamma)** y **`tempfilt_ynN=1` (filtrado temporal del regresor)**. El preprocesamiento de FEAT ya aplicó high-pass 100 s al BOLD, por lo que las estadísticas deben mantener concordancia temporal del **modelo** sin aplicar por segunda vez el filtrado o suavizado a la imagen. FSL explica que los filtros de datos y modelo deben corresponder.

## Archivos y rutas del modelo

- PRE original: `~/FEAT/6037/run1.feat/` (protegido).
- Copia de entrada realizada y verificada: `~/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/entrada_run1.feat/`.
- Confusores aprobados: `~/TesisDoctoral/confounds_nativos/6037/run1/todos_confounds_nativo.txt` (387×14).
- Plantilla manual de configuración estadística: `~/Pipeline-completo-de-procesamiento-de-datos-/01_primer_nivel/automatizacion_mirta/plantilla/first_level_6037_run1_master.fsf`. **No modificarla**.
- Otros parámetros: `level=1`, `analysis=2`, `stats_yn=1`, `prewhiten_yn=1`, `motionevs=0`, `confoundevs=1`, TR=2 s, 387 volúmenes, `ndelete=0`, 8 EV, 8 derivadas, 21 contrastes.
- **`fmri(inputtype)` se documenta para entradas de nivel superior**; no utilizar su valor como interruptor mágico entre un 4D y un directorio FEAT de primer nivel.

## Qué queda pendiente

Crear un **FSF nuevo** que tome como entrada una copia del FEAT preprocesado (no el 4D MNI de G15), con eventos y confusores nativos, sin sobrescribir el FEAT original. Comprobar cuidadosamente con GUI/FEAT local el tratamiento del registro y que la entrada sea interpretada como directorio FEAT, no como 4D. Evaluar `design.mat` y `design.con` mediante `feat_model` antes de ejecutar FEAT.

La cola nominal de ~132 s sin eventos al final de ambos runs está documentada como cuestión pendiente del protocolo; **no se eliminaron volúmenes ni se desplazaron EVs**.

Fuentes: [FEAT User Guide oficial](https://fsl.fmrib.ox.ac.uk/fsl/docs/task_fmri/feat/user_guide.html) y documento de Mirta aportado para el proyecto. No iniciar FILM todavía.
