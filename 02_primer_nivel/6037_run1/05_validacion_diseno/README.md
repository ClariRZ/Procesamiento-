# 6037/run1 — validación de la matriz del GLM nativo

**Estado: GENERACIÓN Y RANGO NUMÉRICO COMPROBADOS, 14/10/2026, Alienware. FILM no se ha ejecutado.**

## Entradas existentes (no publicar en Git)

- Candidato FSF: `~/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/6037_run1_nativo_CANDIDATO_NO_EJECUTAR.fsf`; huella SHA256 confirmada en la terminal: `43207c8265c1041dd8796947ac5f1a45e90ead44711fcdabebdb63a94ddd6034`.
- Confusores nativos: `~/TesisDoctoral/confounds_nativos/6037/run1/todos_confounds_nativo.txt`; 387×14, validados previamente.
- Carpeta de preprocesamiento COPIADA: `~/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/entrada_run1.feat/`, con BOLD funcional nativo y archivos de registro conservados.

## Generación ejecutada

Se preparó una carpeta independiente:
`~/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/VALIDACION_DISENO_6037_RUN1/`

En ella se guardó `design.fsf` (copia del candidato) y se ejecutó solamente:

```bash
feat_model "$HOME/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/VALIDACION_DISENO_6037_RUN1/design" \
  "$HOME/TesisDoctoral/confounds_nativos/6037/run1/todos_confounds_nativo.txt"
```

Se generaron `design.mat`, `design.con`, `design.frf`, `design.trg` y visualizaciones de diseño. **No se ejecutó `feat`, FILM ni se generaron mapas de activación.**

## Resultados objetivos

| Control | Resultado |
|---|---|
| `design.mat /NumPoints` | **387** |
| `design.mat /NumWaves` | **30** |
| `design.con /NumContrasts` | **21** |
| `design.con /NumWaves` | **30** |
| Finitud de `design.mat` y `design.con` | OK |
| Rango numérico de `design.mat` | **30/30** |
| Residuo mínimo normalizado por Gram-Schmidt reortogonalizado | **0.256212410175** |
| Contrastes con vector íntegramente cero | **0** |

El control de rango se ejecutó con **Gram–Schmidt modificado y dos pasadas**, aplicando el umbral de residuo normalizado **1e-8**. [verificar_rango_diseno.sh](verificar_rango_diseno.sh) reproduce esa comprobación en modo lectura y sin NumPy. **El script Git aún no se ha ejecutado como tal**; la validación anterior proviene del bloque manual de terminal que se utilizó antes de documentarla.

**Precaución estadística:** rango completo no es sinónimo de ausencia de multicolinealidad elevada, buen número de condición ni estimabilidad comprobada de todas las comparaciones. El residuo mínimo citado NO es un valor singular.

## Pendiente antes de lanzar FEAT

1. Comparar filas reales de `design.con` con los pesos esperados de los 21 contrastes del FSF (incluidos ceros en los 14 confusores).
2. Inspeccionar las visualizaciones de diseño y covarianzas y evaluar colinealidad/eficiencia de los contrastes.
3. Confirmar que *Statistics only* realmente utilizará el BOLD nativo de la carpeta `.feat` copiada sin repetir preprocesamiento y que los registros relevantes estarán disponibles para efectos fijos y grupo.
4. Mantener documentada la incertidumbre sobre los ~132 s nominales finales sin eventos.

No subir matrices de diseño particulares, confusores o imágenes del sujeto a este repositorio público. No ejecutar FEAT todavía.
