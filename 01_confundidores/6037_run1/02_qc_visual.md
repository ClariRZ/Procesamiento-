# Paso 2 — Inspección visual en FSLeyes

**Estado: confirmado por la investigadora el 14/10/2026 («esta todo ok»).**

La revisión corresponde a las máscaras funcionales nativas de 6037/run1: `mask_wm_func.nii.gz` y `mask_csf_func.nii.gz`, superpuestas a `example_func.nii.gz`.

La primera captura recibida en la conversación tenía oculto el fondo anatómico. Se pidió activarlo para revisar registro y pureza tisular; posteriormente la investigadora comunicó que estaba todo correcto. **No se afirma que el asistente haya examinado una segunda captura ni que haya certificado la anatomía por su cuenta.**

Comando de visualización (lectura; ya utilizado):

```bash
PRE="$HOME/FEAT/6037/run1.feat"
OUT="$HOME/TesisDoctoral/confounds_nativos/6037/run1"
fsleyes "$PRE/example_func.nii.gz" \
        "$OUT/mask_wm_func.nii.gz" -cm red -a 45 \
        "$OUT/mask_csf_func.nii.gz" -cm blue -a 45
```

Criterios para repetir QC en otros sujetos: ubicación predominante de WM en sustancia blanca y CSF en espacios de líquido, alineación en tres planos, contaminación de sustancia gris y regiones extracerebrales, cobertura y resolución parcial de EPI.

**Próxima etapa:** extraer señales nativas WM/CSF, comprobar sus 387 muestras y combinar regresores. Si aparece nueva evidencia de mala localización, suspender y revisar.
