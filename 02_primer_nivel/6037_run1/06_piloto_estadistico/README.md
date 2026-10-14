# 6037/run1 — piloto FEAT Stats only sobre copia nativa

**Fecha:** 14/10/2026 (Alienware). **Estado:** ejecución estadística completada; QC de geometría/máscara y revisión científica todavía pendientes.

## Arquitectura y precauciones

- Preprocesamiento original **protegido**: `~/FEAT/6037/run1.feat/`.
- Copia independiente **destino efectivo de estadísticas**: `~/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/entrada_run1.feat/`.
- `Statistics only` con **`fmri(inputtype)=1`** significa *Input is a FEAT directory*. FEAT **agrega estadísticas dentro de la carpeta .feat de entrada** y no creó el nuevo directorio `run1_firstlevel_nativo_piloto02.feat/` pese al campo `fmri(outputdir)`. Esta semántica debe reflejarse en cualquier automatización futura: **siempre trabajar sobre copia fresca y controlada**.
- El piloto original con `fmri(inputtype)=2` falló al intentar interpretar la carpeta `.feat` como una imagen (error 63). No usar ese FSF para relanzar.
- En la segunda versión del FSF se cambió únicamente `fmri(inputtype) 2 → 1` y `fmri(outputdir)` para distinguir intentos. Los 8 EV, 8 derivadas, 14 confusores y 21 contrastes se mantuvieron.

## Evidencia de la ejecución exitosa

- Registro FEAT iniciado **11:32:34**; informe final `Finished at mié 14 oct 2026 11:35:00 -03`, sin mensaje de error en la salida de estado examinada.
- `film_gls` alcanzó **`Saving results... Completed`**: 387 puntos temporales y 30 columnas del modelo; **21 contrastes** en post-stats.
- En `entrada_run1.feat/stats/`: **COPE 21/21, VARCOPE 21/21, ZSTAT 21/21**, comprobados con archivos no vacíos.
- Comparación binaria `cmp` del BOLD `filtered_func_data.nii.gz` y `mask.nii.gz` de la copia frente a los originales: **ambos idénticos** al terminar. Esto no equivale a una auditoría exhaustiva de todos los archivos del original ni a una validación espacial.
- Los cuatro archivos de registro `reg/example_func2highres.mat`, `reg/highres2standard_warp.nii.gz`, `reg/example_func2standard_warp.nii.gz`, `reg/standard.nii.gz` **ya se habían verificado idénticos** entre copia y original antes de ejecutar el piloto.

## QC geométrico dimensional (14/10/2026)

Comprobado en Alienware mediante `fslinfo` y `fslstats -V` en `entrada_run1.feat/`:

| Imagen | Dimensiones (x,y,z,t) | Tamaño de vóxel espacial (mm) |
|---|---|---|
| `filtered_func_data` | 64,64,44,387 | 3.593800,3.593800,3.599899 |
| `mask` | 64,64,44,1 | igual |
| `stats/cope1` | 64,64,44,1 | igual |
| `stats/varcope1` | 64,64,44,1 | igual |
| `stats/zstat1` | 64,64,44,1 | igual |

TR (BOLD): 2.000000 s. `fslstats mask -V` = **43812 vóxeles** (2 037 001 mm³). Coincide con la máscara original registrada anteriormente. Dimensiones y tamaño de vóxel coincidentes **no certifican por sí solos la matriz afín/orientación**.

**Observación por resolver:** en el log de `film_gls` y `smoothest` se utiliza el volumen de **41342 vóxeles**, menor que los 43812 de la máscara guardada. Probablemente el umbral de intensidad `--thr=1000` deja menos vóxeles efectivos, pero la explicación no está confirmada. Auditar la máscara efectiva sin relanzar FEAT antes de considerar aprobado el control espacial.

## Próxima y única fase de QC antes del segundo run

Comprobar las geometrías del BOLD/máscara/COPE y la máscara efectiva del análisis, e inspeccionar las imágenes estadísticas en FSLeyes. Luego revisar que la carpeta `.feat` con estadísticas contenga las transformaciones esperadas para el segundo nivel de efectos fijos. **No volver a lanzar FEAT sobre esta copia**, no repetir los controles de diseño ya completados.

Conservar este registro como evidencia de un piloto **computacionalmente terminado**, sin equipararlo todavía a una aprobación científica ni a un análisis de conectividad funcional. No subir imágenes, confusores, mapas individuales ni identificadores sensibles a un repositorio público.
