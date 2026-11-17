# Conceptos clave de StreamRetain-Agent

Guía de consulta y preparación para la sustentación. Última actualización: 15 de noviembre de 2026.

Los ejemplos numéricos son inventados para explicar los conceptos: **no son resultados del proyecto**. Las variables mencionadas como ejemplos solo podrán utilizarse si existen en los datos y están disponibles en el momento de la predicción.

Para practicar explicaciones, consultar [Preguntas de repaso y respuestas corregidas](Preguntas%20de%20repaso.md).

## Índice

- [Problema y datos](#problema-y-datos)
- [Ejemplo de evaluación](#ejemplo-de-evaluación)
- [Métricas](#métricas)
- [Entrenamiento y evaluación experimental](#entrenamiento-y-evaluación-experimental)
- [Modelos y explicaciones](#modelos-y-explicaciones)
- [El agente y su funcionamiento](#el-agente-y-su-funcionamiento)
- [Diferencias que conviene recordar](#diferencias-que-conviene-recordar)

## Problema y datos

### Abandono o churn

Es el evento que representa la pérdida de un suscriptor, según una definición explícita. No siempre significa pulsar un botón de cancelación.

**En este proyecto:** se adopta la definición de KKBox: no renovar dentro de los 30 días posteriores al vencimiento de la suscripción. No equivale a cancelar durante los próximos 30 días contados desde cualquier fecha de predicción. El diseño inicial hablaba de 28 días; la propuesta documenta su adaptación a KKBox.

### KKBox

Plataforma de streaming de música por suscripción y fuente elegida para el proyecto, mediante el conjunto de datos del desafío WSDM de predicción de abandono. Usar sus datos no implica trabajar para la empresa ni conectarse a sus sistemas reales.

### Conjunto de datos o dataset

Colección organizada de observaciones. Puede estar distribuida en varias tablas: suscriptores, transacciones y actividad, por ejemplo. Su **esquema** describe las columnas, sus tipos y cómo se relacionan las tablas.

**Misma empresa no significa misma tarea:** KKBox publicó desafíos de recomendación y de abandono. En los archivos de recomendación recibidos, `target` significa reescucha de una canción, no cancelación. Los detalles de esta diferencia están en `docs/analisis_datos_kkbox.md`.

### Clave primaria, relación entre tablas e integridad referencial

Una clave primaria identifica de forma única una fila de una tabla. Una columna de otra tabla puede referirse a ella: por ejemplo, el `song_id` de una interacción apunta a la ficha de una canción. Comprobar integridad referencial consiste en verificar que existan esas fichas. Que un identificador no se repita en la tabla de canciones no impide que aparezca muchas veces en la tabla de interacciones.

### Valor faltante, código especial y dato anómalo

Un campo vacío es información ausente. Un código como `-1` o el texto `Unknown` puede tener un significado especial que requiere consultar la documentación. Un dato anómalo puede estar presente pero ser poco plausible, como una edad de 1.051 años. No se deben tratar los tres casos de la misma forma sin justificación.

### Huella de archivo — SHA-256

Resumen calculado a partir de los bytes de un archivo. Permite comparar si se está utilizando exactamente la misma versión de datos que se auditó. No prueba que los datos sean correctos ni que exista permiso para utilizarlos.

### Plantilla de envío — sample submission

Archivo de ejemplo que indica cómo presentar predicciones a una competencia. Sus valores no son resultados reales de prueba. En la descarga de recomendación recibida, todos los valores de ejemplo son `0.5`; no pueden utilizarse como etiquetas para evaluar el modelo.

### Observación y unidad de análisis

Una observación es un caso registrado. La unidad de análisis indica exactamente qué representa ese caso: un usuario, una transacción o un usuario en una fecha determinada.

**Ejemplo:** una fila por usuario y semana no es lo mismo que una fila por usuario para todo el estudio. Las observaciones repetidas de una persona están relacionadas.

### Variable predictora o característica — feature

Información que el modelo utiliza para estimar el resultado. Por ejemplo, actividad reciente o antigüedad de la suscripción.

Debe estar disponible **antes de predecir**. Un identificador permite vincular registros, pero no debe tratarse como una señal arbitraria de riesgo.

### Etiqueta o variable objetivo — target

Resultado real que se pretende predecir. Se propone representar abandono con `1` y permanencia con `0`, siguiendo la definición y el seguimiento correspondientes.

Una persona cuyo resultado aún se desconoce no debe recibir automáticamente la etiqueta `0`.

### Clasificación binaria supervisada

Aprendizaje a partir de ejemplos que incluyen sus características y su etiqueta, para distinguir entre dos clases. En StreamRetain: abandono y permanencia.

### Clase positiva y clase negativa

La clase positiva es el evento que se busca detectar: **abandono**. La negativa es **permanencia**. “Positivo” no significa que el evento sea bueno.

### Desbalance de clases

Ocurre cuando una clase tiene muchos más casos que otra. Si 90 de cada 100 suscriptores permanecen, un modelo que siempre prediga permanencia consigue 90 % de exactitud sin detectar ningún abandono.

### Ventana de observación, predicción y seguimiento

- **Observación:** periodo pasado del que se obtienen las características.
- **Predicción:** resultado futuro y periodo al que se refiere la estimación.
- **Seguimiento:** información posterior necesaria para saber qué ocurrió realmente.

En KKBox, confirmar la falta de renovación requiere observar el periodo posterior al vencimiento. Ejecutar el agente semanalmente no significa conocer el resultado de cada predicción al terminar esa semana.

### Cohorte y corte temporal

Una cohorte reúne casos con un criterio común, por ejemplo suscripciones que vencen en un mismo mes. Un corte temporal fija hasta qué fecha se permite usar información para generar una predicción.

### Captura de estado o snapshot

Registro del estado observable de un usuario en una fecha. Varias capturas pueden formar un historial si contienen observaciones reales nuevas. Copiar el mismo archivo cada semana no crea evolución del comportamiento.

## Ejemplo de evaluación

Supongamos 100 suscriptores: 20 abandonan y 80 permanecen. El modelo detecta 12 abandonos y genera 6 falsas alarmas.

| Lo que realmente ocurrió | Predice abandono | Predice permanencia | Total |
| --- | ---: | ---: | ---: |
| Abandona | 12 verdaderos positivos | 8 falsos negativos | 20 |
| Permanece | 6 falsos positivos | 74 verdaderos negativos | 80 |
| Total | 18 | 82 | 100 |

Esta tabla es la **matriz de confusión**. Las filas muestran la realidad y las columnas la predicción; siempre hay que comprobar ese orden cuando se lee una matriz.

| Abreviatura | Significado | Interpretación en StreamRetain |
| --- | --- | --- |
| VP / TP | Verdadero positivo | Se alertó sobre un suscriptor que abandonó |
| FP | Falso positivo | Se alertó sobre alguien que permaneció |
| FN | Falso negativo | No se detectó a alguien que abandonó |
| VN / TN | Verdadero negativo | Se predijo correctamente la permanencia |

Un falso positivo puede consumir recursos de retención innecesarios. Un falso negativo puede representar una oportunidad de intervención perdida. Estos efectos son posibles consecuencias; no demuestran que una oferta hubiera evitado el abandono.

## Métricas

### Exactitud — accuracy

Proporción de predicciones correctas sobre el total.

`Exactitud = (VP + VN) / (VP + VN + FP + FN)`

**Ejemplo:** `(12 + 74) / 100 = 0,86 = 86 %`.

Responde: **¿qué proporción de todos los casos clasificó correctamente el modelo?** Puede ser alta aunque detecte pocos abandonos cuando las clases están desbalanceadas.

### Precisión — precision

Proporción de abandonos reales entre las alertas de abandono.

`Precisión = VP / (VP + FP)`

**Ejemplo:** `12 / (12 + 6) = 0,667`, aproximadamente 66,7 %.

Responde: **de todas las alertas que emitimos, ¿cuántas correspondían a abandonos reales?** No es sinónimo de exactitud.

### Sensibilidad o exhaustividad — recall

Proporción de abandonos reales que el modelo detectó. También se denomina tasa de verdaderos positivos o TPR.

`Sensibilidad = VP / (VP + FN)`

**Ejemplo:** `12 / (12 + 8) = 0,60 = 60 %`.

Responde: **de todos los que abandonaron, ¿a cuántos detectamos?**

### F1

Media armónica de precisión y sensibilidad. Combina la calidad de las alertas con la capacidad de detectar los abandonos y penaliza que una de esas dos medidas sea baja.

`F1 = 2 × precisión × sensibilidad / (precisión + sensibilidad)`

Forma equivalente: `F1 = 2 × VP / (2 × VP + FP + FN)`.

**Ejemplo:** `24 / (24 + 6 + 8) = 0,632`, aproximadamente.

F1 va de 0 a 1; un valor mayor es mejor para esta medida. **F1 de 0,50 no significa que se acertó el 50 % de todos los clientes.** No incorpora directamente los verdaderos negativos ni sustituye una evaluación de costos de las intervenciones.

Si alguna fórmula tiene denominador cero, hay que informar y definir cómo se trata el caso, no interpretar una división imposible como un resultado normal. También hay que especificar si se reporta F1 de abandono, macro o ponderado; en la propuesta se utiliza **F1 de abandono**.

### Umbral de clasificación

Valor a partir del cual el modelo convierte una puntuación o probabilidad estimada en una alerta. Por ejemplo, con umbral `0,60`, un riesgo de `0,72` genera alerta y uno de `0,45` no.

Al bajar el umbral suelen aumentar los casos detectados y las falsas alarmas; la precisión no está garantizada a subir o bajar de forma estrictamente monótona. El umbral se selecciona con validación, no buscando el mejor resultado en la prueba final.

### Curva y área bajo la curva — AUC

Una curva muestra cómo cambian dos medidas al variar el umbral. AUC significa **área bajo la curva** y resume esa relación en un número. Hay que indicar de qué curva se trata: PR y ROC evalúan relaciones diferentes.

### PR-AUC

Área bajo la curva de **precisión y sensibilidad**. La curva coloca sensibilidad en el eje horizontal y precisión en el vertical. Ayuda a evaluar cómo se mantienen la calidad de las alertas y la detección al cambiar el umbral.

Es útil cuando interesa una clase poco frecuente, como el abandono. El valor de referencia depende de la proporción de positivos: con 20 % de abandonos, una ordenación sin información tiene como referencia una precisión cercana a 0,20. Esa referencia no es una garantía exacta para una muestra finita.

Un PR-AUC mayor es preferible al comparar sobre el mismo conjunto y definición de clase. **No significa porcentaje de aciertos.** No puede calcularse a partir de una sola matriz de confusión: requiere puntuaciones y etiquetas para recorrer umbrales.

### Precisión promedio — average precision o AP

Resumen de la relación precisión–sensibilidad que pondera la precisión por los incrementos de sensibilidad. Se suele utilizar junto con las curvas PR, pero **no es idéntico al área trapezoidal de esa curva**.

En los experimentos deberá indicarse el cálculo utilizado. Si se calcula AP, se reportará como AP; no se intercambiarán ambos nombres sin aclaración.

### Tasa de falsos positivos — FPR

Proporción de personas que permanecieron pero recibieron una alerta de abandono.

`FPR = FP / (FP + VN)`

**Ejemplo:** `6 / (6 + 74) = 0,075 = 7,5 %`.

No es lo mismo que la proporción de alertas equivocadas: tienen denominadores diferentes.

### ROC-AUC

Área bajo la curva que relaciona **tasa de falsos positivos** en el eje horizontal y **sensibilidad** en el vertical, variando el umbral.

También puede interpretarse como la probabilidad de que un abandono elegido al azar reciba una puntuación mayor que una permanencia elegida al azar, contando los empates con peso de la mitad.

- `1`: separación perfecta entre las dos clases.
- `0,5`: ordenación equivalente al azar como referencia.
- Menor que `0,5`: ordenación peor que esa referencia; conviene revisar, entre otras cosas, si se invirtió la clase o el sentido del puntaje.

Un ROC-AUC de 0,90 **no significa 90 % de exactitud**. No determina por sí solo cuántas alertas serán correctas al elegir un umbral. También requiere puntuaciones de riesgo; no se obtiene de la matriz del ejemplo sin información adicional.

### Calibración

Concordancia entre las probabilidades estimadas y las frecuencias observadas. Si muchos casos reciben un riesgo cercano al 70 %, se espera que aproximadamente el 70 % de ellos presente el evento cuando el modelo está bien calibrado para esa población.

Un modelo puede ordenar bien a los usuarios y, aun así, exagerar sus probabilidades. Tener ROC-AUC alto no garantiza buena calibración ni certeza sobre una persona concreta.

### Resultados por subgrupos

Consiste en calcular las métricas por separado para grupos relevantes, como antigüedad o modalidad de renovación, cuando los datos lo permitan.

**Ejemplo hipotético:** el modelo puede detectar el 80 % de los abandonos de usuarios antiguos y solo el 35 % de los recientes. Un promedio global podría ocultar esa diferencia.

Se deben informar cantidad de casos, cantidad de abandonos y limitaciones de cada grupo. Una diferencia observada en un grupo pequeño puede ser inestable; tampoco prueba por sí sola discriminación o una causa determinada. Los grupos se definirán con justificación, no para buscar únicamente comparaciones favorables.

### Meta o umbral de éxito

Condición declarada antes de experimentar para evaluar el proyecto. En la propuesta se plantea exactitud ≥ 0,75 y F1 de abandono ≥ 0,50 y superior al mayoritario.

Estos valores son **metas propuestas, no resultados obtenidos**. Un umbral de éxito, como F1 ≥ 0,50, no es el umbral de riesgo usado para emitir alertas.

## Entrenamiento y evaluación experimental

### Línea base — baseline

Solución sencilla que sirve como referencia. El clasificador mayoritario predice siempre la clase más frecuente aprendida en entrenamiento.

En el ejemplo de 100 usuarios, si esa clase es permanencia, obtiene 80 % de exactitud y F1 de abandono igual a 0. Un modelo más complejo debe justificar su utilidad frente a esa referencia.

### Entrenamiento, validación y prueba

| Conjunto | Para qué sirve | Qué no debe hacerse |
| --- | --- | --- |
| Entrenamiento | Aprender parámetros y transformaciones de datos | Ajustar transformaciones con datos futuros |
| Validación | Elegir modelo, hiperparámetros y umbral | Presentarlo como prueba final independiente |
| Prueba | Evaluar la configuración ya fijada | Usarlo repetidamente para escoger la mejor configuración |

### Separación temporal

Organización de los datos respetando el tiempo: aprender del pasado y evaluar en periodos posteriores. Las etiquetas de entrenamiento deben haber podido conocerse en la fecha correspondiente; ordenar las filas por fecha no basta si sus resultados utilizan información futura.

### Fuga de información — data leakage

Ocurre cuando el entrenamiento o la predicción aprovecha información que no estaría disponible en el uso real o que pertenece a la evaluación reservada.

**Ejemplos:** usar una cancelación futura como característica, calcular transformaciones con todo el dataset o elegir el umbral con la prueba final. Produce resultados artificialmente favorables.

### Preprocesamiento y pipeline

El preprocesamiento prepara los datos: tratar faltantes, codificar categorías o escalar valores. Un pipeline encadena esas transformaciones con el modelo para aplicarlas de manera consistente.

Las transformaciones que aprenden valores, como medias o escalas, se ajustan solo con entrenamiento y después se aplican a validación y prueba.

### Parámetro e hiperparámetro

- **Parámetro:** valor aprendido durante el entrenamiento; por ejemplo, un coeficiente de regresión logística.
- **Hiperparámetro:** configuración elegida para controlar el aprendizaje; por ejemplo, profundidad máxima de un árbol o intensidad de regularización.

El ajuste de hiperparámetros compara configuraciones mediante validación.

### Sobreajuste — overfitting

El modelo aprende peculiaridades o ruido del entrenamiento y pierde desempeño en datos nuevos. Un árbol que memoriza los ejemplos puede acertar casi todo en entrenamiento y fallar después.

### Regularización

Mecanismo que limita la complejidad del modelo para reducir sobreajuste. En regresión logística puede penalizar coeficientes grandes; en árboles se controla la complejidad mediante profundidad, tamaño mínimo de hojas o poda.

### Validación cruzada

Evaluación con varias divisiones de entrenamiento y validación. Para datos temporales, las divisiones deben respetar la disponibilidad de información y el orden temporal; no se deben mezclar pasado y futuro indiscriminadamente.

### Reproducibilidad y semilla

Reproducibilidad significa poder repetir el procedimiento con datos, código, versiones y configuración documentados. Una semilla fija controla ciertas operaciones aleatorias. **Fijar la semilla por sí solo no garantiza reproducibilidad completa.**

### Análisis de errores

Estudio de casos en los que el modelo falla para identificar patrones e hipótesis: datos incompletos, usuarios recientes o comportamientos poco representados, por ejemplo. Una hipótesis sobre la causa del error no es un hecho demostrado.

## Modelos y explicaciones

### Regresión logística

Modelo de clasificación que transforma una combinación de características en una probabilidad mediante una función logística. Aunque su nombre incluya “regresión”, puede utilizarse para clasificar abandono frente a permanencia.

### Árbol de decisión

Modelo que realiza preguntas sucesivas sobre las características hasta llegar a una decisión o estimación. Sus reglas pueden ser fáciles de interpretar si el árbol es pequeño. Un árbol demasiado complejo puede memorizar el entrenamiento.

### Explicabilidad y SHAP

La explicabilidad busca comprender qué información influye en las predicciones. SHAP es un método que atribuye contribuciones de características respecto de una referencia.

**Ejemplo:** una explicación podría indicar que la baja actividad elevó la estimación de riesgo del modelo. Eso describe el modelo; **no demuestra que la baja actividad causó el abandono**. SHAP sigue siendo una posibilidad, no un componente confirmado del proyecto.

### Asociación y causalidad

Asociación significa que dos fenómenos están relacionados en los datos. Causalidad significa que intervenir sobre uno modifica el otro, bajo condiciones determinadas.

Que un usuario permanezca después de recibir una oferta no prueba que permaneció gracias a ella. Podría haber renovado sin intervención.

## El agente y su funcionamiento

### Modelo predictivo y agente

El modelo recibe características y estima un resultado. El agente integra ese modelo con percepción de datos, memoria, decisiones, acciones y seguimiento.

**En StreamRetain:** leer registros → conservar historial → estimar riesgo → priorizar → emitir una recomendación → registrar lo ocurrido. Las acciones de marketing del prototipo se plantean como simuladas.

### PEAS

Marco para describir la tarea de un agente:

| Componente | Significado | Ejemplo en StreamRetain |
| --- | --- | --- |
| P | Medida de desempeño | Métricas y metas de evaluación |
| E | Entorno | Suscripciones, actividad, pagos y retención |
| A | Actuadores | Escritura de decisiones o envío de recomendaciones |
| S | Sensores | Lectura de registros disponibles |

El modelo predictivo es procesamiento interno, no un actuador por sí solo.

### Inferencia y reentrenamiento

- **Inferencia:** utilizar un modelo ya entrenado para generar predicciones.
- **Reentrenamiento:** volver a aprender parámetros con datos de entrenamiento actualizados.

Ejecutar el agente cada semana no obliga a reentrenarlo cada semana. Una nueva versión debe evaluarse antes de reemplazar a la anterior.

### Sesgo y deriva

El **sesgo** puede aparecer si los datos, las etiquetas o las decisiones representan inadecuadamente ciertos grupos. La **deriva** es un cambio a lo largo del tiempo en los datos o en la relación entre características y abandono. Ambos pueden reducir la utilidad del modelo y requieren evaluación.

## Diferencias que conviene recordar

| No confundir | Diferencia principal |
| --- | --- |
| Exactitud y precisión | Aciertos totales frente a aciertos entre las alertas |
| Precisión y sensibilidad | Calidad de las alertas frente a cobertura de abandonos |
| F1 y porcentaje de aciertos | F1 combina precisión y sensibilidad; no es exactitud |
| PR-AUC y ROC-AUC | Usan ejes distintos y no tienen el mismo valor de referencia |
| PR-AUC trapezoidal y AP | Son resúmenes relacionados con cálculos diferentes |
| Umbral de clasificación y meta de éxito | Regla para alertar frente a criterio para evaluar el proyecto |
| Ciclo semanal y periodo de seguimiento | Frecuencia de ejecución frente a tiempo necesario para conocer el resultado |
| Datos sintéticos y datos reales | Los primeros se generan; no deben presentarse como observaciones reales |
| Predicción de abandono y efecto de una oferta | Estimar riesgo no demuestra que una intervención lo reduzca |

## Fuentes de consulta

- Material docente local: `context/docs/AI_Lecture07c_MachineLearning.pdf`, secciones de preparación, evaluación, explicabilidad y operación de modelos.
- Material docente local: `context/docs/AI_LectureML02_LogisticRegression_ES.pdf`, `AI_LectureML05_DecisionTree_ES.pdf` y `AI_Lecture02_Intelligent_Agents.pdf`.
- [Convocatoria oficial WSDM: definición de la tarea de KKBox](https://www.wsdm-conference.org/2018/call-for-participants.html).
- [Documentación de métricas de scikit-learn](https://scikit-learn.org/stable/modules/model_evaluation.html).

Esta guía se ampliará conforme aparezcan conceptos nuevos. Definir un concepto no significa que su técnica haya sido seleccionada para implementarse.

## Aclaraciones del primer ejercicio de etiquetas

### Claves de diccionario: texto frente a entero

Un diccionario de Python admite claves enteras y de texto; no es obligatorio ni siempre mejor usar texto. En el ejercicio se usa `"1"` porque `csv.DictReader` devuelve el contenido del campo como texto. La clave `"1"` y la clave `1` son distintas. Sería posible convertir las etiquetas con `int()` y utilizar claves enteras, validando la conversión.

### Proporción de abandono frente a exactitud

La proporción de abandono describe las etiquetas reales: filas con abandono / filas evaluadas. La exactitud compara una predicción con su etiqueta: predicciones correctas / predicciones evaluadas. Puede conocerse la proporción de abandono sin tener un modelo.

El estudiante comunicó 87.330 abandonos de 970.960 filas, aproximadamente 8,99 %. Predecir renovación en todas esas filas daría aproximadamente 91,01 % de exactitud sobre ese mismo conjunto y detectaría cero abandonos. Este último es un cálculo ilustrativo, no una evaluación experimental de una línea base.

### Usuarios únicos no significa eliminación de duplicados

Contar usuarios únicos mide cuántos identificadores diferentes existen. No borra filas. Las observaciones repetidas de un usuario pueden representar eventos o fechas distintos y ser válidas. Una etiqueta contradictoria dentro de una misma cohorte requiere investigación; no se debe elegir automáticamente la primera etiqueta.

## Gap de renovación (diferencia en días)

En inglés, gap significa separación o intervalo. En este proyecto, `gap_dias` es la diferencia entre la fecha de la primera renovación observada desde el corte y el vencimiento efectivo:

**gap = fecha de renovación − fecha de vencimiento efectivo.**

El vencimiento efectivo parte del conocido al corte y puede adelantarse por cancelaciones previas a esa primera renovación, según las reglas Scala. No es la duración del plan ni la cantidad de días desde la predicción.

Ejemplos hipotéticos sin cancelaciones, con vencimiento el 20 de marzo de 2016:

| Renovación | Gap en días | Interpretación y etiqueta según el código |
| --- | ---: | --- |
| 15 de marzo | -5 | Renovación anticipada; 0 |
| 20 de marzo | 0 | Renovación el mismo día; 0 |
| 25 de marzo | 5 | Renovación cinco días después; 0 |
| 18 de abril | 29 | Antes del límite; 0 |
| 19 de abril | 30 | Alcanza el límite; 1 |

La condición exacta del código de referencia es gap < 30 para renovación y gap >= 30 para abandono. El plan ya venció en la fecha base; los 30 días son el plazo posterior usado para clasificar. Una renovación tardía puede existir y, aun así, la etiqueta ser abandono según esta definición.

Si no se observa renovación, no existe un gap calculable: se guarda vacío/None, nunca cero. Con seguimiento suficiente y cobertura asumida, puede asignarse abandono sin tener un gap numérico. Sin seguimiento suficiente, el resultado se deja sin determinar.

`gap_dias`, `motivo`, `primera_renovacion` y el vencimiento efectivo ajustado usando eventos posteriores son campos para auditar la etiqueta. No pueden alimentar una predicción realizada al corte porque contienen información futura. Esto es distinto de calcular, por ejemplo, días restantes hasta el vencimiento conocido al corte, que sí usa información disponible entonces.
