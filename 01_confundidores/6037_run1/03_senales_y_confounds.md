# Paso 3 — Confusores de primer nivel: señales y matriz

## Parte A. Señales nativas WM/CSF — HECHA

El 14/10/2026 se extrajeron y verificaron las dos señales a partir del BOLD nativo de 6037/run1. Cada señal tiene **387 filas, 1 columna, valores finitos y variación temporal**. Resultados, comandos y scripts: [02_senales_nativas](02_senales_nativas/README.md).

| Señal | Mínimo | Máximo |
|---|---:|---:|
| WM | 10818.271690 | 11030.664290 |
| CSF | 8035.584346 | 8250.511604 |

## Parte B. Construcción del archivo de 14 confusores — PENDIENTE

Entradas ya identificadas:

- Movimiento: `~/FEAT/6037/run1.feat/mc/prefiltered_func_data_mcf.par` (6 columnas, del mismo run).
- Derivadas: `~/TesisDoctoral/confounds_mirta/6037/run1/motion_deriv.par` (6 columnas, verificar que cada fila sea la diferencia temporal del movimiento anterior, primera fila cero).
- Señal WM: `~/TesisDoctoral/confounds_nativos/6037/run1/signal_wm_nativa.txt`.
- Señal CSF: `~/TesisDoctoral/confounds_nativos/6037/run1/signal_csf_nativa.txt`.

**Movimiento y derivadas: validados** (387×6 cada uno, error máximo 5.55111512313e-17). [Procedimiento y script de verificación](03_movimiento/README.md). **Siguiente acción:** combinar. Después, crear un archivo nuevo **387 × 14** en orden: 6 movimiento + 6 derivadas + 1 WM + 1 CSF. Comprobar finitud, filas/columnas, derivadas, constancia y rango del diseño GLM. No confundir derivadas de movimiento con derivadas temporales de los EV de tarea.

No reutilizar las antiguas señales WM/CSF extraídas en MNI. No ejecutar todavía FEAT.
