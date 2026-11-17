**Universidad Tecnológica de Bolívar**  
Ingeniería de Sistemas y Computación

# Propuesta de proyecto · Hito 1

*STREAMRETAIN-AGENT — Predicción de abandono en streaming musical*

**Presentado por:** Levis Adrian Ortiz Cano — T00083674  
**Curso:** Inteligencia Artificial · **Docente:** Edwin Alexander Puertas Del Castillo  
Cartagena de Indias, 15 de noviembre de 2026 · Modalidad individual

## 1. Problema, usuario y objetivo

El abandono de suscripciones afecta la continuidad de ingresos de las plataformas de streaming. WSDM identifica la predicción de abandono y la comprensión de la renovación como problemas de valor empresarial [1]. El usuario objetivo será un analista de retención, quien recibirá una lista priorizada de suscriptores en riesgo. Se implementará StreamRetain-Agent para estimar la probabilidad de no renovar dentro de los 30 días posteriores al vencimiento, según la definición de KKBox. Se adapta así el horizonte inicial de 28 días a la etiqueta de la fuente elegida. No se presupone colaboración con la empresa ni un proceso interno observado.

## 2. Ruta y alcance del agente

Se seguirá la **ruta C: aprendizaje automático**, con clasificación binaria supervisada. El agente leerá datos, conservará observaciones y decisiones, estimará riesgo y emitirá recomendaciones; las acciones de marketing serán simuladas. Se diseñará un ciclo semanal, cuya demostración retrospectiva utilizará únicamente cortes históricos válidos. Frente al primer corte, se incorporarán implementación reproducible, comparación de modelos y análisis de errores; no se atribuirá a las recomendaciones una reducción causal del abandono.

## 3. Fuente de datos y autorización

Se utilizará **WSDM–KKBox’s Churn Prediction Challenge**, disponible en Kaggle, sobre suscripciones de música. Sus reglas contemplan investigación y educación tras su aceptación y restringen la redistribución de datos [2]; se documentará esta autorización de uso, sin presentarla como licencia abierta. Antes del modelado se verificarán acceso, esquema, fechas, calidad y seguimiento. Se trabajará con un subconjunto reproducible compatible con recursos gratuitos. Los identificadores no serán predictores y los datos brutos no se publicarán. Las variables de actividad y suscripción dependerán de los campos efectivamente disponibles.

## 4. Línea base y comparación experimental

La línea base predecirá siempre la clase mayoritaria. Se compararán **regresión logística y árbol de decisión**, ajustando regularización y complejidad mediante validación. Se contrastan así un modelo interpretable de probabilidad y reglas no lineales. Se reservarán periodos de entrenamiento, validación y prueba; solo se empleará información disponible antes de cada predicción y etiquetas con seguimiento completo. Se ajustará el preprocesamiento únicamente con entrenamiento. La prueba final permanecerá fuera de la selección de modelos y umbrales.

## 5. Métricas y criterios de éxito

Se propone exigir simultáneamente **exactitud ≥ 0,75; F1 de abandono ≥ 0,50 y superior al de la línea base**. F1 combina precisión y sensibilidad para evaluar la detección de quienes abandonan. Se reportarán también precisión, sensibilidad, área bajo la curva precisión–sensibilidad (PR-AUC), área bajo la curva ROC (ROC-AUC) y matriz de confusión. Se comparará el desempeño por antigüedad y modalidad de renovación si los datos lo permiten, indicando tamaños de grupo. El umbral de clasificación se elegirá por F1 en validación y se congelará antes de la prueba. Se evaluará variación entre cortes temporales y al menos diez errores. Las metas se declaran antes de experimentar; cualquier cambio posterior se justificará por escrito.

## 6. Entregable y uso responsable

Se entregará un prototipo Python ejecutable, con memoria de decisiones, dependencias fijadas, semillas, resultados trazables y bitácora de IA. Se examinarán privacidad, diferencias de desempeño y limitaciones de las recomendaciones. La aprobación del alcance y de la viabilidad de los datos corresponde al docente.

## Referencias

[1] WSDM Cup 2018, “Call for Participants”, tarea 2. https://www.wsdm-conference.org/2018/call-for-participants.html  
[2] Kaggle / KKBOX, “Competition Rules”, §7. https://www.kaggle.com/c/kkbox-churn-prediction-challenge/rules
