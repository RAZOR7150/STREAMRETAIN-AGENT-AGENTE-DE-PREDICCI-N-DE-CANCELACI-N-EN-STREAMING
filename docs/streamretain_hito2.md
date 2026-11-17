**Universidad Tecnológica de Bolívar**  
Ingeniería de Sistemas y Computación

# Avance del proyecto · Hito 2

*STREAMRETAIN-AGENT — Predicción de abandono en streaming musical*

**Presentado por:** Levis Adrian Ortiz Cano — T00083674  
**Curso:** Inteligencia Artificial · **Docente:** Edwin Alexander Puertas Del Castillo  
Cartagena de Indias, 16 de noviembre de 2026 · Modalidad individual

## 1. Objetivo y avance alcanzado

Se busca identificar suscriptores en riesgo de abandono para apoyar la priorización de acciones de retención. Se completó la preparación de dos cohortes históricas de KKBox y se ejecutó una línea base temporal reproducible. El estudiante escribió y ejecutó el procesamiento y la evaluación con guías comentadas de IA; la asistencia se registra en docs/bitacora_ia.md.

## 2. Datos y preparación

Se utilizó transactions.csv.7z del desafío WSDM–KKBox Churn Prediction [1], con 21.547.746 transacciones entre enero de 2015 y febrero de 2017; la auditoría no reportó filas mal formadas ni fechas inválidas en las dos columnas revisadas. Se leyó el comprimido progresivamente y se seleccionó aproximadamente el 1 % de identificadores mediante SHA-256, conservando sus eventos dentro de cada ventana. Los datos brutos y derivados permanecen locales, sujetos a las reglas de acceso de la fuente.

Cada ejemplo corresponde a un usuario y un corte. Se reconstruyó el vencimiento conocido con 90 días de historia y se eligieron vencimientos entre el corte y 29 días después. Las etiquetas adaptan las reglas del código Scala publicado: primera renovación desde el corte, cancelaciones que pueden adelantar el vencimiento y abandono si la brecha es ≥30 días, o si no se observa renovación con seguimiento suficiente. Son etiquetas reconstruidas, no oficiales. Las seis entradas describen transacciones en 90/30 días, cancelaciones, fechas distintas con transacciones, días desde la última transacción y días hasta el vencimiento conocido. Se excluyeron identificadores y datos futuros de las entradas.

## 3. Evaluación temporal y primer resultado

Se entrenó con el corte del 7 de marzo de 2016: 7.443 usuarios y 1.095 abandonos, observados hasta el 5 de mayo. Se validó en el corte del 6 de junio: 7.210 usuarios y 411 abandonos, observados hasta el 4 de agosto. Hay 5.875 usuarios compartidos: se evalúa el futuro de suscriptores potencialmente conocidos. Las etiquetas de entrenamiento ya estaban disponibles antes del corte de validación. Diciembre permanece reservado para prueba final.

DummyClassifier con estrategia most_frequent aprendió la clase mayoritaria de marzo y predijo renovación para todos los casos de junio. Resultado: **exactitud 94,30 %; precisión, sensibilidad y F1 de abandono 0; ROC-AUC 0,50; Average Precision (AP) 0,0570**. La matriz, con filas reales y columnas predichas [0,1], es [[6799,0],[411,0]]. AP resume precisión–recall y se distingue del área trapezoidal PR-AUC. La exactitud supera 0,75 por el desbalance, pero no se detectó ningún abandono ni se alcanzó la meta de F1 ≥0,50. El resultado constituye una referencia que los modelos posteriores deberán superar.

## 4. Evidencia, limitaciones y próximos pasos

El script scripts/14_linea_base_temporal.py y experiments/baseline_marzo_junio.json conservan ejecución, métricas, semilla 42, versiones y huellas de las cohortes; README.md describe la reproducción. Se usa Python 3.11.16 y scikit-learn 1.9.1. La fuente editable, los scripts y la bitácora acompañan esta entrega; la creación y publicación del repositorio remoto corresponde al estudiante.

La cobertura de transacciones se asume a partir del historial publicado y no se verifica por usuario. Se revisaron nueve casos de marzo y dos de nueve de junio; los siete restantes se pospusieron por tiempo. No es una auditoría exhaustiva ni validación cruzada completa. La selección exige historia reciente y limita la representación de planes largos. Se continuará con regresión logística y árbol de decisión, ajuste en validación, cortes adicionales, análisis de errores e impacto por subgrupos, manteniendo la prueba final separada.

## Referencia

[1] KKBox, WSDM Churn Prediction Challenge: datos, reglas y WSDMChurnLabeller.scala. https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data
