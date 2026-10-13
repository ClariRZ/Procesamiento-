# Motor estadístico parametrizable, NO ejecutar lote todavía

`primer_nivel.py`: `auditar`, `preparar`, `diseno`, `ejecutar --confirmo-ejecutar`, `verificar`. El script **no inventa ni genera EVs o contrastes**: lee el FSF del run indicado en `--fsf` y comprueba exactamente los pesos originales/reales.

Para un sujeto distinto de 6037/run1 hay que indicar el FSF de **ese sujeto/run** y su directorio de eventos. Las rutas de otros runs **no se infieren por analogía**. El esquema de segundo nivel de FSL no se ejecuta desde este motor.
