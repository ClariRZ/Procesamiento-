# Automatización de confusores nativos (72 runs pendientes)

El inventario del 14/10/2026 confirmó 38 sujetos y 76 runs; 72 tienen preprocesamiento, FAST y derivadas disponibles, 6037/run1 ya fue analizado y tres runs (5031/run1, 6025/run1, 6025/run2) tienen preprocesamiento incompleto.

Protocolo de cada run: PLAN → PREPARE → inspección visual WM/CSF → APPROVE → FINALIZE.

PREPARE: reutilizar FAST PVE0/2 correspondiente al T1, binarizar en 0.9, transformar con highres2example_func.mat y vecino más próximo, intersectar con máscara funcional, comprobar volumen/geometría y solapamiento; nunca reejecutar preprocesamiento ni FAST.

APPROVE: requiere autorización visual explícita por run; nunca automática.

FINALIZE: calcular señales medias WM/CSF con fslmeants sobre BOLD nativo, agregar seis parámetros MCFLIRT y sus seis derivadas; generar exactamente 14 columnas, verificar el número de volúmenes, finitud y variación.

No escribir nunca en ~/FEAT, ni sobrescribir confusores existentes. Ejecutar sobre el piloto 6037/run2 y después habilitar el lote de máscaras. Las carpetas incompletas deben conservarse para investigar errores, no eliminarse automáticamente. Ninguna máscara puede aprobarse solo mediante un control numérico. FEAT no forma parte de esta etapa.

Los scripts experimentales se prueban inicialmente con entradas sintéticas; la validación sobre FSL real está pendiente. Los datos de sujetos quedan fuera del repositorio público.
