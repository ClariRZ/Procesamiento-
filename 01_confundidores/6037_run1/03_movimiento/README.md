# Verificación de movimiento y derivadas — 6037/run1

**Ejecutado en la Alienware, 14/10/2026. Resultado comunicado por la investigadora: OK.**

## Insumos, fuera del repositorio

- `~/FEAT/6037/run1.feat/mc/prefiltered_func_data_mcf.par` — 6 parámetros MCFLIRT.
- `~/TesisDoctoral/confounds_mirta/6037/run1/motion_deriv.par` — 6 primeras diferencias de dichos parámetros.

## Criterios y resultado

| Comprobación | Resultado |
|---|---|
| Movimiento | 387 filas × 6 columnas |
| Derivadas | 387 filas × 6 columnas |
| Error máximo respecto de la primera diferencia | **5.55111512313e-17** |
| Tolerancia | 1e-7 |
| Finitud | Comprobada por el bloque original |
| Estado | **OK** |

El valor inicial esperado en las seis derivadas es cero. Desde el segundo volumen, la derivada de cada columna es la diferencia entre el parámetro actual y el anterior. No hay necesidad de recalcular MCFLIRT ni las derivadas ya verificadas.

## Código reproducible

[verificar_movimiento.sh](verificar_movimiento.sh) reimplementa en Python estándar, sin `numpy`, la comprobación que se ejecutó manualmente. **Este script versionado todavía no se ha ejecutado desde GitHub:** se documenta el resultado comprobado mediante el bloque de terminal equivalente.

Desde el directorio raíz del repositorio, en la Alienware:

```bash
bash 01_confundidores/6037_run1/03_movimiento/verificar_movimiento.sh
```

**Siguiente paso:** combinar seis movimientos, seis derivadas, WM nativa y CSF nativa para formar un archivo externo `todos_confounds_nativo.txt` de **387 × 14**. Esta salida todavía no se ha producido ni validado. No incluir parámetros de movimiento por segunda vez en FEAT.
