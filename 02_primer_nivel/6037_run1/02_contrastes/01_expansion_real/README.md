# 6037/run1 — validación de la expansión de contrastes a 16 EV

**Estado: VALIDADO en la Alienware el 14/10/2026.** La investigadora ejecutó el control numérico y compartió literalmente:

```text
Contrastes coincidentes: 21/21
EXPANSIÓN DE CONTRASTES: OK
```

## Fuente

`~/Pipeline-completo-de-procesamiento-de-datos-/01_primer_nivel/automatizacion_mirta/plantilla/first_level_6037_run1_master.fsf`

Los ocho EV originales, en orden, son `AtencionPlena`, `ExperimNeg`, `ExperimNeutra`, `Likert`, `ObservaNeg`, `ObservaNeutra`, `Reinterpreta` y `Suprime`. Los ocho tienen `deriv_yn=1`; `evs_orig=8` y `evs_real=16`.

Para cada uno de los **21 contrastes**, se comparó el vector `con_orig<contraste>.1..8` con `con_real<contraste>.1..16` en el orden principal/derivada de FEAT:

```text
[p1, 0, p2, 0, p3, 0, p4, 0, p5, 0, p6, 0, p7, 0, p8, 0]
```

Se exigió una diferencia absoluta menor que `1e-9` en cada posición. Resultado: **21/21 coincidentes**. Los pesos de las derivadas son cero; no se modificó el FSF original.

La auditoría de nombres y pesos `con_orig` figura en [02_contrastes](../README.md).

## Script versionado

[verificar_expansion_contrastes.sh](verificar_expansion_contrastes.sh) replica el control por lectura del FSF y no requiere NumPy. **El script guardado en Git se añadió después del control manual y todavía no ha sido ejecutado directamente como archivo versionado**; no confundir la auditoría completada con una segunda ejecución.

## Qué NO demuestra esta prueba

La coincidencia `con_real`/`con_orig` no prueba que los contrastes sean estimables, ni que la matriz estadística tenga rango completo; tampoco certifica la sincronización del paradigma (se documentó una cola nominal ~132 s sin eventos en ambos runs).

**Siguiente paso:** preparar la configuración de FEAT en espacio funcional nativo usando el directorio de preprocesamiento original **solo como fuente**, una copia independiente para *Statistics only*, los 14 confusores verificados y las EV correctas. Antes de lanzar FILM, comprobar `design.mat`, `design.con`, rango, registros y máscaras. No sobrescribir el FEAT original.
