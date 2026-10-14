# 6037/run1 — Auditoría de los 21 contrastes originales

**Estado:** auditados el 14/10/2026 en la Alienware utilizando el FSF original importado desde la G15. **Los 21 contrastes originales tienen los pesos esperados, finitos y no nulos**. Este paso NO ha validado todavía las 16 columnas de `con_real` ni la matriz `design.mat`.

## Fuente y orden de los ocho EV

Plantilla local: `~/Pipeline-completo-de-procesamiento-de-datos-/01_primer_nivel/automatizacion_mirta/plantilla/first_level_6037_run1_master.fsf`.

Orden: **1 AtencionPlena, 2 ExperimNeg, 3 ExperimNeutra, 4 Likert, 5 ObservaNeg, 6 ObservaNeutra, 7 Reinterpreta, 8 Suprime**. Cada EV declara derivada temporal activada. El archivo declara `evs_orig=8`, `evs_real=16`, `ncon_orig=21`, `ncon_real=21`.

## Contrastes originales comprobados

| Nº | Nombre literal | EV +1 | EV −1 |
|---:|---|---|---|
| 1 | AtencionPlena_vs_ExperimNeg | AtencionPlena | ExperimNeg |
| 2 | Reinterpreta_vs_ExperimNeg | Reinterpreta | ExperimNeg |
| 3 | Suprime_vs_ExperimNeg | Suprime | ExperimNeg |
| 4 | AtencionPlena_vs_ExperimNeutra | AtencionPlena | ExperimNeutra |
| 5 | Reinterpreta_vs_ExperimNeutra | Reinterpreta | ExperimNeutra |
| 6 | Suprime_vs_ExperimNeutra | Suprime | ExperimNeutra |
| 7 | ExperimNeg_vs_ExperimNeutra | ExperimNeg | ExperimNeutra |
| 8 | AtencionPlena_vs_ObservaNeg | AtencionPlena | ObservaNeg |
| 9 | Reinterpreta_vs_ObservaNeg | Reinterpreta | ObservaNeg |
| 10 | Suprime_vs_ObservaNeg | Suprime | ObservaNeg |
| 11 | ExperimNeg_vs_ObservaNeg | ExperimNeg | ObservaNeg |
| 12 | AtencionPlena_vs_ObservaNeutra | AtencionPlena | ObservaNeutra |
| 13 | Reinterpreta_vs_ObservaNeutra | Reinterpreta | ObservaNeutra |
| 14 | Suprime_vs_ObservaNeutra | Suprime | ObservaNeutra |
| 15 | ExperimNeg_vs_ObservaNeutra | ExperimNeg | ObservaNeutra |
| 16 | Reinterpreta_vs_Suprime | Reinterpreta | Suprime |
| 17 | Suprime_vs_Reinterpreta | Suprime | Reinterpreta |
| 18 | Reinterpreta_vs_AtencionPlena | Reinterpreta | AtencionPlena |
| 19 | AtencionPlena_vs_Reinterpreta | AtencionPlena | Reinterpreta |
| 20 | Suprime_vs_AtencionPlena | Suprime | AtencionPlena |
| 21 | AtencionPlena_vs_Suprime | AtencionPlena | Suprime |

El reporte de la terminal confirma que cada vector `con_origN.1…con_origN.8` consta de un único **+1**, un único **−1** y seis ceros. **Likert** no participa de ningún contraste (coeficiente 0), pero permanece en el diseño como EV para explicar su señal. Los pares **16/17**, **18/19** y **20/21** son inversos matemáticos, no 6 comparaciones independientes.

## Precauciones científicas

- En los contrastes 8–15 se comparan condiciones con `ObservaNeg`/`ObservaNeutra`, que podrían corresponder a instrucciones de otra duración/fase del ensayo. **No cambiar el diseño original**; evaluar cómo interpretar esas comparaciones antes de las conclusiones científicas.
- Un contraste original bien definido no garantiza que el diseño sea identificable ni que el contraste sea estimable después de incluir todas las derivadas y los 14 confusores.
- El extremo final del protocolo sigue pendiente de cotejar con registros de adquisición: ambos runs muestran ~132 s nominales sin eventos registrados tras el último descanso.

## Reproducción

[verificar_contrastes_originales.sh](verificar_contrastes_originales.sh) realiza una auditoría de solo lectura, sin NumPy. **El script fue incorporado después de la comprobación manual, y todavía no ha sido ejecutado como archivo versionado en la Alienware**.

**Expansión a 16 EV completada:** los 21/21 contrastes `con_real` coinciden con los ocho pesos originales intercalados con cero para la derivada de cada EV. [Ver auditoría y script reproducible](01_expansion_real/README.md). **Siguiente paso:** verificar configuración exacta del primer nivel nativo y generar/controlar `design.mat` con `feat_model` en una salida nueva; todavía no ejecutar FEAT.
