# Estado de revisión del hito 1

Actualizado el 15 de noviembre de 2026.

## Decisiones actuales

- Fuente elegida por el usuario: KKBox, WSDM Churn Prediction Challenge.
- Modalidad ratificada por el usuario: individual, Levis Adrian Ortiz Cano.
- La propuesta adopta la etiqueta de no renovación durante los 30 días posteriores al vencimiento; se documenta la diferencia con los 28 días del diseño inicial.
- PDF vigente: `Entregables/streamretain_hito1.pdf`. Fuente: `docs/streamretain_hito1.md`. Generador visual: `docs/generar_hito1.py`.
- Estilo adaptado de `context/docs/Plantilla_Diseño_Agente.docx`: Times New Roman, encabezado centrado, títulos numerados azules y pie de página. Se condensó la portada para respetar una página.

## Verificaciones pendientes antes del modelado

1. Descargar por el mecanismo permitido, comprobar esquema, fechas, seguimiento, tamaño y posibilidad de formar cortes de evaluación. No se ha descargado ni auditado el dataset.
2. Documentar aceptación de reglas y acceso autorizado; no publicar datos brutos. Las reglas contemplan educación e investigación, con restricciones de distribución.
3. Las metas del borrador son accuracy >= 0,75 y F1 de abandono >= 0,50 y superior al mayoritario. El valor 0,50 sigue siendo una meta propuesta, no un rendimiento observado ni garantía de viabilidad.
4. Precisar cálculo de PR-AUC: usar área trapezoidal de la curva precisión–sensibilidad y nombrarla así; si se reporta average precision (AP), identificarla por separado, pues no es exactamente el mismo cálculo.
5. El destinatario es un analista de retención; no hay empresa colaboradora ni entrevista acreditadas.

## Fuentes consultadas

- https://www.wsdm-conference.org/2018/call-for-participants.html : definición oficial y relevancia del problema.
- https://www.kaggle.com/c/kkbox-churn-prediction-challenge/rules : reglas, sección 7, recuperadas mediante búsqueda.
- https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data : ficha original; la apertura directa no permitió auditar el esquema.
- https://scikit-learn.org/stable/modules/model_evaluation.html : documentación de métricas.

No se entrenaron modelos ni se obtuvieron resultados experimentales. La decisión individual del usuario se registra sin atribuir una aprobación al docente que no se ha acreditado.
