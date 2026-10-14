# 6037/run1 — auditoría de eventos de tarea

**Estado: control básico de archivos y tiempos REALIZADO (14/10/2026). Coherencia del paradigma PENDIENTE.**

## Insumos en la Alienware (fuera de Git)

- Carpeta: `~/NIFTIS_DESCOMPRIMIDOS/6037/evs/run-1/`.
- Plantilla original importada desde la G15: `~/Pipeline-completo-de-procesamiento-de-datos-/01_primer_nivel/automatizacion_mirta/plantilla/first_level_6037_run1_master.fsf`.
- Parámetros de plantilla: TR=2 s, 387 volúmenes, **8 EV originales, 16 EV reales (8 derivadas temporales), 21 contrastes**.
- Los ocho archivos de eventos existen con los nombres declarados; `Descanso.txt` existe, pero no figura entre esos ocho EV.

## Resultados del control ejecutado

Todos los archivos de los ocho EV fueron leídos en la Alienware y superaron los controles básicos del bloque manual: no vacíos, exactamente tres columnas numéricas finitas por fila; tiempos iniciales no negativos y duraciones no negativas; finales de los eventos dentro de los **774 s** nominales del run.

| EV | Nombre | Eventos | Último final (s) |
|---:|---|---:|---:|
| 1 | AtencionPlena | 6 | 109.893 |
| 2 | ExperimNeg | 6 | 629.717 |
| 3 | ExperimNeutra | 6 | 369.944 |
| 4 | Likert | 30 | 637.806 |
| 5 | ObservaNeg | 23 | 623.714 |
| 6 | ObservaNeutra | 6 | 363.941 |
| 7 | Reinterpreta | 6 | 239.928 |
| 8 | Suprime | 6 | 499.862 |

La auditoría no emitió advertencias por finales fuera de duración, duraciones cero ni inicio desordenado para estos ocho archivos.

## Auditoría de cronología realizada (14/10/2026)

Se leyó **también `Descanso.txt`**, que tiene **30 eventos**, desde 12.193 s hasta 641.706 s. La secuencia observada al principio es:

| Intervalo (s) | Evento |
|---|---|
| 0.000–4.031 | AtencionPlena |
| 4.031–12.214 | Likert |
| 12.193–16.218 | Descanso |
| 16.218–19.229 | ObservaNeg |
| 19.229–25.233 | AtencionPlena |

El primer ensayo comienza con `AtencionPlena` directamente en 0 s, sin instrucción `ObservaNeg` previa: **esto ofrece una explicación plausible de los 23 eventos `ObservaNeg`**, pero todavía NO verifica que cada uno de los demás ensayos tenga su instrucción correcta. No añadir eventos artificialmente.

Los últimos eventos observados son:

| Intervalo (s) | Evento |
|---|---|
| 620.706–623.714 | ObservaNeg |
| 623.714–629.717 | ExperimNeg |
| 629.717–637.806 | Likert |
| 637.806–641.706 | Descanso |

**Diferencia temporal pendiente de aclarar:** adquisición nominal 387×2 = **774 s**, fin del último descanso **641.706 s**, tramo restante **132.294 s** (unos 66 TR). El fin del último EV de tarea modelado es 637.806 s (136.194 s antes del fin nominal). Ambos números son correctos, pero hacen referencia a finales distintos.

Podría existir un tramo final de adquisición sin tareas, o un desfase en el protocolo/recorte de volúmenes. **No hay evidencia suficiente para decidirlo**; verificar con metadatos reales de adquisición, diseño de la tarea, parámetros `ndelete` y cronología de otros runs. No recortar series, desplazar onsets ni agregar `Descanso` como noveno EV sin justificación.

**Estado:** formato y tiempos dentro de adquisición aprobados; **coherencia completa del paradigma y tramo final por confirmar**, y también quedan pendientes los 21 contrastes.

## Scripts

[auditar_eventos.sh](auditar_eventos.sh) documenta la verificación que se hizo por terminal, sin NumPy y sin escrituras. Se agregó **después de la auditoría manual**, y aún no se ejecutó directamente desde este repositorio. No altera los eventos.

**Próxima etapa:** inspeccionar la cronología y `Descanso.txt`, luego revisar los 21 contrastes y comprobar diseño `feat_model`. No lanzar FEAT todavía.
