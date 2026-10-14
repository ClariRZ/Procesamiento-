# 6037/run1 — primer nivel nativo (FEAT)

## Progreso real (14/10/2026)

| Paso | Estado |
|---|---|
| BOLD funcional nativo preprocesado, máscaras y registro | Existentes; conservar el FEAT original |
| Matriz de 14 confusores del mismo run | **Validada, 387×14** |
| 8 archivos EV, amplitudes y tiempos dentro de adquisición | **Auditoría básica completada** |
| Validar secuencia de consignas, ObservaNeg=23 y descanso | **Pendiente** |
| Revisar pesos y nombres de los 21 contrastes | **Pendiente** |
| Comprobar `design.mat` y rango con `feat_model` | **Pendiente** |
| Ejecutar FILM y revisar las 21 salidas | **Pendiente** |

[**Paso 01 — eventos del paradigma**](01_eventos/README.md) incluye el script de auditoría y sus resultados. No publicar en GitHub los archivos individuales de eventos.

La plantilla original en la Alienware es:
`~/Pipeline-completo-de-procesamiento-de-datos-/01_primer_nivel/automatizacion_mirta/plantilla/first_level_6037_run1_master.fsf`.

El primer nivel a preparar será **Statistics only en espacio funcional nativo, sobre copia independiente del directorio `~/FEAT/6037/run1.feat`**, con 8 EV + 8 derivadas, 21 contrastes y 14 regresores adicionales. Sin duplicar movimiento, sin aplicar de nuevo suavizado ni transformar toda la serie 4D a MNI.

**No ejecutar FEAT antes de cerrar los puntos pendientes.**
