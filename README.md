# Procesamiento de fMRI — primer nivel FSL en espacio funcional nativo

**Piloto: 6037/run1 en la G15.** Código y procedimientos preparados; **NO se ha ejecutado todavía FAST, FLIRT, `fslmeants`, `feat_model` ni FEAT con las imágenes reales de 6037 desde este repositorio**. Las pruebas locales son sintéticas con llamadas FSL simuladas. La validación real se hace en la G15, donde están los datos.

## Empezar por aquí

1. [`01_confundidores/6037/README.md`](01_confundidores/6037/README.md): auditoría → FAST → máscaras T1→funcional → QC humano → 14 regresores nativos.
2. [`02_primer_nivel/6037/README.md`](02_primer_nivel/6037/README.md): reutilizar `.fsf` histórico 8 EV + 21 contrastes; FEAT Statistics sobre una **copia del `.feat` nativo**; comprobar `feat_model`; ejecutar solo tras revisión.
3. [`REFERENCIAS_Y_DECISIONES.md`](REFERENCIAS_Y_DECISIONES.md): comparativa precisa con el Word de Mirta y documentación oficial de FSL.
4. [`tests/test_workflow.py`](tests/test_workflow.py): validaciones sintéticas repetibles de máscaras, movimientos, EV/contrastes, procedencia y seguridad.

```text
01_confundidores/
  6037/README.md + ejecutar.sh               # piloto manual y pasos individuales
  automatizacion/confundidores.py              # mismo procedimiento parametrizable por sujeto/run
02_primer_nivel/
  6037/README.md + ejecutar.sh                 # piloto 6037/run1, guiado
  automatizacion/primer_nivel.py               # reutiliza el FSF DE CADA RUN
REFERENCIAS_Y_DECISIONES.md
requirements.txt
.gitignore
```

## Reglas no negociables

- BOLD del primer nivel: `run1.feat/filtered_func_data.nii.gz` (**64×64×44×387, TR 2 s** según revisión de cabeceras del 13/10/2026), no `filtered_func_data_MNI2`. Ningún `applywarp` del BOLD a MNI.
- El T1/FAST vive en espacio anatómico; las **máscaras WM/CSF sí se transforman** T1→funcional nativo con `highres2example_func.mat`, vecino más cercano e intersección con `mask.nii.gz` funcional.
- Regresores: 6 movimientos + 6 diferencias temporales (fila inicial 0) + WM + CSF = **14 columnas**. Los tiempos de eventos y las estadísticas se verifican para el run concreto.
- El modelo de tarea **no se reescribe**: el generador lee el `.fsf` real de la G15 y preserva los ocho EV con sus derivadas y los 21 contrastes, verificando originales y reales. **No se suben a GitHub archivos de eventos**, matrices, imágenes ni tablas individuales.
- El repositorio es **público** (verificado el 13/10/2026): jamás cargar NIfTI, DICOM, `.feat`, datos clínicos o salidas de pacientes. Los archivos de trabajo se guardan fuera de Git, en `~/TesisDoctoral/fsl_nativo/`.
- La revisión humana es un paso obligatorio. Una comprobación numérica no significa que FAST, BET o el registro sean correctos.
- Nunca escribir dentro de la fuente `~/Escritorio/6037/run1.feat`. Se bloquean resultados preexistentes y duplicación de corridas. Todo paso de ejecución estadística exige confirmación explícita.
- Sujetos/runs pendientes conocidos (5017/1, 6010/2, 6032/2, 5031/1, 6025/1 y 6025/2) no se procesan con este código hasta resolver su situación; no equivalen a exclusión científica definitiva.

## Instalación en la G15, después de publicar los archivos

```bash
cd ~
git clone https://github.com/ClariRZ/Procesamiento-.git
cd Procesamiento-
python3 -c 'import numpy, nibabel; print("dependencias Python: OK")'
command -v fast flirt fslmaths fslmeants feat feat_model
python3 -m unittest discover -s tests -v
```

Si faltan las dependencias, preparar un entorno Python compatible con FSL; no alterar la instalación de FSL a ciegas. Los lanzadores prefieren `$FSLDIR/bin/python` cuando existe; `PYTHON_NATIVO` permite seleccionar otro intérprete compatible. Una falla de dependencias **detiene** la ejecución.

**No ejecutar un lote todavía**: primero completar y verificar el piloto 6037/run1 en la G15.
