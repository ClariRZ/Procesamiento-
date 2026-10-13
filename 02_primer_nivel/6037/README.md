# 6037/run1 — primer nivel individual nativo, después de confusores

**Requisitos**: confusores de [`01_confundidores/6037`](../../01_confundidores/6037/README.md) FINALIZADOS y máscaras revisadas en FSLeyes. Usaremos el **FSF realmente guardado en la G15**:

```text
~/Escritorio/6037/run1_firstlevel.feat/design.fsf
```

Su lectura previa mostró: 8 EV (`AtencionPlena`, `ExperimNeg`, `ExperimNeutra`, `Likert`, `ObservaNeg`, `ObservaNeutra`, `Reinterpreta`, `Suprime`), cada una con derivada temporal, **21 contrastes**, TR=2, 387 volúmenes. La entrada MNI y los confusores MNI antiguos **se reemplazan solamente en la copia del diseño**, sin cambiar pesos/títulos de los contrastes.

### 1. Auditoría previa (solo lectura)
```bash
cd "$HOME/Procesamiento-"
bash 02_primer_nivel/6037/ejecutar.sh auditar
```

Valida el FSF original y real, las ocho EV en `~/NIFTIS_DESCOMPRIMIDOS/6037/evs/run-1/`, el BOLD nativo y la matriz nueva de 14 regresores.

### 2. Preparar copia independiente (NO corre FEAT)
```bash
bash 02_primer_nivel/6037/ejecutar.sh preparar
```

Copia el preprocesado a `~/TesisDoctoral/fsl_nativo/6037/run1/02_primer_nivel/entrada_nativa.feat` y genera `diseno_run_nativo.fsf` con `Statistics`, entrada FEAT, **sin recomputar preprocesamiento**. Se excluyen series MNI adicionales. El original sigue intacto. Exige espacio para una copia independiente; no pisa destinos existentes.

### 3. Comprobar diseño con el ejecutable real de FSL
```bash
bash 02_primer_nivel/6037/ejecutar.sh diseno
```

Esperado **387 filas × 30 columnas** (8 EV + 8 derivadas de tarea + 14 confusores), rango 30, 21 contrastes. Detenerse si `feat_model` reporta diferencias, errores o rango deficiente. No usar un diseño si solo se calcularon 16 columnas sin confounds.

### 4. Revisar en FEAT GUI (sin iniciar todavía)

Desde una sesión gráfica de G15, o SSH `-X` desde Alienware:

```bash
Feat
```

En la GUI: pulsar **Load**, abrir:

```text
~/TesisDoctoral/fsl_nativo/6037/run1/02_primer_nivel/diseno_run_nativo.fsf
```

Verificar que el selector esté en **First-level analysis → Statistics**; **Input is a FEAT directory** apuntando a `entrada_nativa.feat`; salida nueva `run_firstlevel_nativo.feat`; **no elegir** `filtered_func_data_MNI2` ni `Select 4D data` en esta variante. Comprobar `Stats → Add additional confound EVs` con `todos_confounds_nativo.txt`, `Don't Add Motion Parameters` (ya incluidos), FILM prewhitening, ocho EV, sus derivadas, pesos y nombres de los 21 contrastes. **No pulsar GO todavía** si cambiaste algo o hay errores.

**FSL advierte**: seleccionar otro directorio FEAT en GUI puede restaurar ajustes y contrastes. Si se cambia la entrada, volver a comprobar todas las opciones y rehacer `diseno`; no asumir que el `preflight` anterior sigue válido.

### 5. Ejecutar una sola vez, por GUI O terminal

Una vez revisado el diseño, se puede pulsar **GO en la GUI** O, usando el FSF generado sin modificar, ejecutar en la terminal:

```bash
bash 02_primer_nivel/6037/ejecutar.sh ejecutar --confirmo-ejecutar
```

**No usar ambos métodos**. El lanzador CLI exige manifest de integridad y prueba real de `feat_model`; si se altera manualmente el `.fsf` desde GUI, hay que volver a preparar/validar una versión nueva en otra carpeta de trabajo. Conservar siempre los originales.

### 6. Verificar las 21 salidas
```bash
bash 02_primer_nivel/6037/ejecutar.sh verificar
```

Comprueba COPE/VARCOPE 1–21 en la grilla **64×64×44 nativa** y la máscara estadística (no vacía ni todo el FOV). Además revisar `report.html`, `report_log.html`, movimiento, registro, señal y mapas en FSLeyes. Que existan 21 COPE **no** equivale a aprobación de la calidad científica.

**Después de 6037/run1:** 6037/run2 necesita su propio `.fsf` y ocho eventos del run2; las máscaras y señales de run1 **no** se trasladan al segundo run. Fixed effects viene después.
