# 01 — Confusores nativos (Mirta adaptado)

Piloto documentado: [`6037/README.md`](6037/README.md). Motor reutilizable: [`automatizacion/confundidores.py`](automatizacion/confundidores.py).

Operaciones separadas: `auditar` (lectura), `mascaras` (FAST + FLIRT, salida nueva), `aprobar` (marcador de revisión humana), `finalizar` (señales y matriz 14 columnas), `estado` (lectura).

Para otros sujetos/runs, **primero deben verificarse** su preprocesamiento, registro, identidad anatómica, archivos de movimiento y revisión visual. Ejemplo de invocación **no automática**:

```bash
python3 01_confundidores/automatizacion/confundidores.py auditar \
  --sujeto 6037 --run 1 --feat "$HOME/Escritorio/6037/run1.feat"
```

No hay ejecución masiva ni aprobación visual automática. Cada corrida usa un destino por sujeto/run fuera de Git.
