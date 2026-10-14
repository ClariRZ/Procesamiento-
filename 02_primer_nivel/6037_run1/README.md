# 6037/run1 — primer nivel nativo (FEAT)

## Progreso real (14/10/2026)

| Paso | Estado |
|---|---|
| BOLD funcional nativo preprocesado, máscaras y registro | Existentes; conservar el FEAT original |
| Matriz de 14 confusores del mismo run | **Validada, 387×14** |
| 8 archivos EV, amplitudes y tiempos dentro de adquisición | **Auditoría básica completada** |
| Comparar secuencias y cola temporal de run1/run2 | **Realizado: 132.294 s vs 132.405 s; causa por confirmar** |
| Validar secuencia completa y causa de la cola con protocolo de tarea | **Pendiente** |
| Revisar pesos y nombres de los 21 contrastes originales | **Completado: 21/21, todos finitos y con ±1 correctos** |
| Comprobar expansión a 16 regresores de tarea (`con_real`) | **VALIDADO: 21/21 correctos** |
| Comprobar `design.mat` y rango con `feat_model` | **Pendiente** |
| Ejecutar FILM y revisar las 21 salidas | **Pendiente** |

[**Paso 01 — eventos del paradigma**](01_eventos/README.md) incluye la auditoría básica, la cronología y la [comparación temporal de ambos runs](01_eventos/02_comparacion_runs/README.md). [**Paso 02 — contrastes**](02_contrastes/README.md) documenta nombres, pesos y la [expansión 21/21 a 16 EV](02_contrastes/01_expansion_real/README.md), con scripts auditores. No publicar en GitHub los archivos individuales de eventos.

La plantilla original en la Alienware es:
`~/Pipeline-completo-de-procesamiento-de-datos-/01_primer_nivel/automatizacion_mirta/plantilla/first_level_6037_run1_master.fsf`.

El primer nivel a preparar será **Statistics only en espacio funcional nativo, sobre copia independiente del directorio `~/FEAT/6037/run1.feat`**, con 8 EV + 8 derivadas, 21 contrastes y 14 regresores adicionales. Sin duplicar movimiento, sin aplicar de nuevo suavizado ni transformar toda la serie 4D a MNI.

**Copia independiente ya creada y comprobada:** [03_copia_preprocesamiento](03_copia_preprocesamiento/README.md) (`~/TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/entrada_run1.feat/`). Se cotejaron cinco archivos esenciales con `cmp`; no se ejecutó FEAT. Siguiente: auditar configuración de registros y EVs del FSF manual antes de generar un diseño nuevo.

**No ejecutar FEAT antes de cerrar los puntos pendientes.**
