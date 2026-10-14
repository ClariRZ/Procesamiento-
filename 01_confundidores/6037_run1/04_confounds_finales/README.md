# 6037/run1 — matriz final de 14 confusores nativos

**Estado: REALIZADO y VALIDADO por la investigadora el 14/10/2026 en la Alienware.**
El archivo ya existe en su computadora; no es necesario regenerarlo.

## Entrada del primer nivel

```text
~/TesisDoctoral/confounds_nativos/6037/run1/todos_confounds_nativo.txt
```

Procede exclusivamente del mismo run de 6037 y está alineado temporalmente con `~/FEAT/6037/run1.feat/filtered_func_data.nii.gz` (387 volúmenes). No proviene del BOLD MNI.

| Columnas | Contenido | Archivo de origen |
|---|---|---|
| 1–6 | 6 parámetros MCFLIRT | `~/FEAT/6037/run1.feat/mc/prefiltered_func_data_mcf.par` |
| 7–12 | 6 derivadas temporales del movimiento | `~/TesisDoctoral/confounds_mirta/6037/run1/motion_deriv.par` |
| 13 | Media BOLD WM nativa | `~/TesisDoctoral/confounds_nativos/6037/run1/signal_wm_nativa.txt` |
| 14 | Media BOLD CSF nativa | `~/TesisDoctoral/confounds_nativos/6037/run1/signal_csf_nativa.txt` |

## Comprobación realizada

Se ejecutó un bloque de Python estándar (sin NumPy) que leyó los cuatro archivos, revisó filas/columnas, finitud, verificó las derivadas, concatenó en orden las 14 columnas, comprobó ausencia de columnas constantes y escribió el resultado evitando sobrescribir destinos preexistentes. Luego se realizó una **verificación independiente de lectura**, que cotejó la matriz de salida con las cuatro fuentes originales y confirmó sus 387 filas, 14 columnas, finitud y variación. La investigadora comunicó: **«confounds nativos ok»**.

El error máximo previo de movimiento-derivadas fue `5.55111512313e-17`; la comprobación independiente de la matriz completa resultó **OK**, sin que conste un valor numérico exacto adicional de error máximo en la conversación.

**No se ha verificado todavía el rango de la matriz de diseño completa de FEAT** (EV de tarea y sus derivadas, más confusores). Ese control pertenece al próximo paso, antes de ejecutar FILM.

## Scripts, añadidos después de validar el paso manual

- [generar_confounds_nativos.sh](generar_confounds_nativos.sh): crea la matriz únicamente si NO existe el destino (no volver a ejecutarlo sobre el archivo actual).
- [verificar_confounds_nativos.sh](verificar_confounds_nativos.sh): solo lectura, compara la salida con los cuatro insumos y comprueba derivadas.

**Estos scripts versionados aún no se han ejecutado desde GitHub sobre el caso real**: los resultados informados proceden de los bloques equivalentes de terminal. No se suben a este repositorio público las señales individuales, matrices numéricas ni datos MRI.

## Para usarlo en FEAT (más adelante)

Seleccionar *Add additional confound EVs*, con el archivo `todos_confounds_nativo.txt`. Usar **Don't Add Motion Parameters**: los seis movimientos y seis derivadas ya forman parte de esas 14 columnas. Comprobar antes el modelo: 8 EV de tarea, 8 derivadas temporales de tarea, 21 contrastes, FILM prewhitening, TR=2 s, 387 volúmenes; evitar doble preprocesamiento.

**Siguiente tarea:** auditar archivos de eventos y FSF real del run1 en el equipo correcto, construir/inspeccionar `design.mat` con `feat_model`, sin lanzar FEAT prematuramente.
