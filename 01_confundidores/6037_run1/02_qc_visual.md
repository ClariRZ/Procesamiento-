# Paso 2 — Inspeccionar máscaras y registro en FSLeyes

**Estado: PENDIENTE.** Este es **el próximo paso**, no consta aprobación.

En la Alienware, abrir sin modificar los archivos:

```bash
PRE="$HOME/FEAT/6037/run1.feat"
OUT="$HOME/TesisDoctoral/confounds_nativos/6037/run1"

fsleyes \
  "$PRE/example_func.nii.gz" \
  "$OUT/mask_wm_func.nii.gz" -cm red -a 45 \
  "$OUT/mask_csf_func.nii.gz" -cm blue -a 45
```

Recorrer cortes axiales, coronales y sagitales, y contrastar con el T1/registro original del mismo participante cuando sea necesario.

**Criterios de revisión humana:** WM predominantemente en sustancia blanca; CSF en espacios de líquido (ventrículos/cisternas); sin extensión extracerebral o invasión extensa de sustancia gris. Considerar resolución parcial del EPI. Registrar desviaciones y capturas **solo en almacenamiento privado/local**, no en Git público.

**Registro de decisión:** «aprobado», «requiere corrección» o «no evaluable» únicamente después de mirar imágenes; incluir fecha y hallazgos. **No autorizar automáticamente.**

Después de la inspección: [paso 3](03_senales_y_confounds.md).
