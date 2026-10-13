# Automatización preparada, NO habilitada en lote

`confundidores.py` acepta `--sujeto`, `--run`, `--feat` y `--trabajo`. Cada fase es deliberadamente un comando independiente. No recorre sujetos ni interpreta marcadores existentes como aprobaciones nuevas.

Para pilotar exactamente 6037/run1 usar `../6037/ejecutar.sh` y seguir su README.

Cuando se complete el piloto, el mismo script podrá aplicarse **uno por uno** a otros runs aprobados. No se admite un loop que saltee revisión humana; `aprobar` exige dos confirmaciones y nota específica. `finalizar` valida la procedencia de esa aprobación y detiene inconsistencias.
