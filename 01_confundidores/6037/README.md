# 6037/run1 — confusores primero

**Equipo:** G15 `clara@claraubuntu`, desde terminal SSH. El BOLD nativo que verificamos mide **64×64×44×387, TR=2 segundos**; FSL `run1.feat` incluye T1, `.mat` T1→funcional y MCFLIRT. La existencia de esos archivos no certifica registro ni BET.

Desde la raíz del repositorio `~/Procesamiento-`:

### 1. Auditar (solo lectura)
```bash
bash 01_confundidores/6037/ejecutar.sh auditar
```

### 2. Crear máscaras nuevas fuera del FEAT original
```bash
bash 01_confundidores/6037/ejecutar.sh mascaras
```

FAST segmenta `~/Escritorio/6037/run1.feat/reg/highres.nii.gz` (T1 cerebral usado en ese FEAT); produce `pve_0`/`pve_2` y umbraliza 0,9. FLIRT usa **`reg/highres2example_func.mat`** y `example_func.nii.gz` con vecino más cercano. La máscara transformada se intersecta con `mask.nii.gz` del FEAT (criterio **nativo** explícito), no con un atlas MNI. **Ningún `applywarp` sobre el BOLD.** Las máscaras se escriben en `~/TesisDoctoral/fsl_nativo/6037/run1/01_confundidores/mascaras/`.

### 3. Revisar visualmente, sin aprobar automáticamente

```bash
PRE="$HOME/Escritorio/6037/run1.feat"
MASK="$HOME/TesisDoctoral/fsl_nativo/6037/run1/01_confundidores/mascaras"
fsleyes "$PRE/example_func.nii.gz" \
  "$MASK/mask_wm_func.nii.gz" \
  "$MASK/mask_csf_func.nii.gz"
```

Comprobar **T1 completo**, registro funcional↔T1, ventrículos, límites WM/CSF y máscaras no ampliadas. El registro y máscaras requieren juicio humano, no solo vóxeles finitos y tamaños razonables. Si hay recorte frontal/registro dudoso: **detenerse; no aprobar**.

Solo tras revisión real:

```bash
bash 01_confundidores/6037/ejecutar.sh aprobar \
  --confirmo-registro --confirmo-mascaras \
  --nota 'Describir en términos concretos lo que efectivamente se revisó en FSLeyes'
```

### 4. Extraer señales y construir confusores
```bash
bash 01_confundidores/6037/ejecutar.sh finalizar
bash 01_confundidores/6037/ejecutar.sh estado
```

Salida esperada: `~/TesisDoctoral/fsl_nativo/6037/run1/01_confundidores/finales/todos_confounds_nativo.txt` de **387 × 14**, solo si las cabeceras confirman 387. Guarda seis parámetros MCFLIRT, seis diferencias de primer orden (primera fila 0), señal WM y CSF. Verifica finitud, espacio, hashes y señales no constantes. Nunca escribe dentro de `~/Escritorio/6037/run1.feat`.

**No poner esta matriz todavía en un GLM**: el paso siguiente comprueba por separado el `.fsf` histórico y sus eventos.
