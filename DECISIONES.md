# Decisiones metodológicas y de seguridad

Fecha de inicio de esta bitácora: **14/10/2026**.

- **Referencia:** documento de Mirta *Pasos realizados en el FSL preprocesado más First-level run1*, especialmente la alternativa de realizar el primer nivel en espacio nativo, mencionada en la página 3. Sus comandos MNI no se copian directamente a la variante nativa.
- **Datos de entrada:** `~/FEAT/6037/run1.feat` de la Alienware. No confundir con `~/Escritorio/6037/run1_firstlevel.feat` manual de la G15 ni con los primeros niveles históricos generados desde fMRIPrep.
- **Ningún nuevo BET, FAST ni MCFLIRT** mientras sus productos existentes resulten trazables y superen QC.
- **Tejidos:** FAST sobre el T1 que utiliza el FEAT; `pve_0=CSF`, `pve_2=WM`, umbral 0,9; transformación T1→funcional con `highres2example_func.mat`, vecino más cercano; intersección con `mask.nii.gz` funcional.
- **Movimiento:** reutilizar seis parámetros de MCFLIRT y seis derivadas del mismo run. **Señales WM/CSF:** obtener de `filtered_func_data.nii.gz` nativo tras QC de las máscaras; reunir 387×14 confusores.
- **Primer nivel:** por run, con ocho EV originales, ocho derivadas de tarea y 21 contrastes del diseño validado; copiar el preprocesamiento para no tocar el original. No incluir dos veces movimiento en la GUI.
- **Segundo nivel FEAT:** efectos fijos run1+run2 del mismo sujeto, con COPE/VARCOPE y registro correcto a un espacio común; no confundir con comparación run1 vs run2.
- **Tercer nivel FEAT:** comparación entre sujetos mediante modelo adecuado para variabilidad interindividual (por ejemplo, FLAME), evaluando exclusiones y participantes con un solo run.
- **Atlas / conectividad:** identificar mapas de efectos en espacio compatible con atlas; para conectividad de tarea, emplear señales BOLD y método de conectividad definido explícitamente (p. ej., PPI), no confundir COPE con conectividad.
- **Respaldo:** `main` conserva los scripts y pruebas previas. Esta rama no es todavía la nueva `main`.

**Pendiente:** inspección visual de máscaras 6037/run1; extracción de señales; combinación de confusores; verificación EV/FSF; lanzamiento del primer nivel. No registrar como ejecutados procedimientos pendientes.
