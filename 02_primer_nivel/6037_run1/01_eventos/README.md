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

## Dos cuestiones por resolver antes de aprobar el diseño completo

1. **ObservaNeg contiene 23 eventos.** Sin conocer la secuencia exacta de consignas, NO podemos concluir que falte un evento. Contrastar con el paradigma y `Descanso.txt` / cronología antes de editar cualquier archivo.
2. El último evento modelado finaliza a **637.806 s**, 136.194 s antes del final nominal del run (774 s). Puede corresponder a descanso u otra parte del protocolo; confirmar antes de atribuir error de sincronización.

`Descanso.txt` no se agrega automáticamente como noveno EV: es necesario verificar si funciona como referencia implícita en el diseño original.

## Scripts

[auditar_eventos.sh](auditar_eventos.sh) documenta la verificación que se hizo por terminal, sin NumPy y sin escrituras. Se agregó **después de la auditoría manual**, y aún no se ejecutó directamente desde este repositorio. No altera los eventos.

**Próxima etapa:** inspeccionar la cronología y `Descanso.txt`, luego revisar los 21 contrastes y comprobar diseño `feat_model`. No lanzar FEAT todavía.
