# 6037/run1 — progreso real

**Equipo:** Alienware (Ubuntu / FSL). Se conserva intacto el preprocesamiento `~/FEAT/6037/run1.feat/`.

| Paso | Estado |
|---|---|
| Insumos y FAST existente sobre T1 identificado | Verificados, 14/10/2026 |
| Máscaras WM/CSF transformadas a EPI nativo | Realizado, 14/10/2026 |
| QC visual de máscaras | Confirmado por la investigadora («todo ok») |
| Señales nativas WM/CSF, 387 valores cada una | Verificadas |
| Movimiento y sus derivadas, 387×6 cada uno | Verificados, error 5.55111512313e-17 |
| **Matriz de confusores nativos 387×14** | **Creada y verificada; «confounds nativos ok»** |
| Matriz de diseño FEAT y primer nivel | **PENDIENTES** |

**Resultados reales en la Alienware, fuera de Git:** `~/TesisDoctoral/confounds_nativos/6037/run1/`.

## Procedimientos realizados y documentados

- [01_mascaras_nativas](01_mascaras_nativas/README.md): FAST existente → T1→funcional → WM/CSF; CSF 4105, WM 9089 vóxeles.
- [02_senales_nativas](02_senales_nativas/README.md): extracción de señales medias WM/CSF, controles numéricos.
- [03_movimiento](03_movimiento/README.md): parámetros MCFLIRT y derivadas verificados.
- [04_confounds_finales](04_confounds_finales/README.md): matriz 387×14, procedencia, script seguro y verificación independiente.

La valoración anatómica de las máscaras corresponde a la confirmación de la investigadora; la captura inicial no permitió una inspección independiente completa.

**Próxima etapa:** [02_primer_nivel](../../02_primer_nivel/README.md), verificar los ocho EV, sus derivadas temporales y los 21 contrastes del FSF antes de preparar el modelo y sin lanzar FEAT prematuramente.
