# StreamRetain-Agent — Guion detallado de sustentación

Autor: Levis Adrian Ortiz Cano. Versión reformulada: 26 de noviembre de 2026.

Este guion acompaña `streamretain_presentacion.pdf`. Sigue la estructura: problemática → solución → PEAS → tipo de entorno → dataset → procedimiento → evolución → resultados → demostración → conclusiones. El nombre correcto del marco es **PEAS**, no PIS: Performance measure, Environment, Actuators y Sensors.

El texto hablado es una base para estudiar y ensayar. Las explicaciones adicionales al final son material de estudio, no se leen completas durante el video. El tiempo final depende de tu ritmo y de la navegación en la demo. La duración aproximada de 20 minutos procede de lo indicado por el estudiante, no de una nueva instrucción escrita del docente.

## Distribución propuesta de los 20 minutos

| Diapositiva | Tiempo | Tema |
| --- | --- | --- |
| 1 | 00:00–01:20 | Problemática |
| 2 | 01:20–02:30 | Agente y solución |
| 3 | 02:30–03:30 | PEAS: medida de desempeño |
| 4 | 03:30–04:30 | PEAS: entorno |
| 5 | 04:30–05:30 | PEAS: sensores y actuadores |
| 6 | 05:30–06:50 | Tipo de entorno |
| 7 | 06:50–08:00 | Fuente y manejo del dataset |
| 8 | 08:00–09:20 | Preparación y etiquetas |
| 9 | 09:20–10:40 | Validación temporal |
| 10 | 10:40–12:00 | Evolución de modelos |
| 11 | 12:00–13:00 | Diez características y control |
| 12 | 13:00–14:30 | Resultados |
| 13 | 14:30–18:30 | Demostración |
| 14 | 18:30–20:00 | Conclusión y contribuciones |
| 15 | Fuera del tiempo hablado | Referencias y evidencia de apoyo |

## Diapositiva 1 — ¿Cuál es la problemática?

**Idea que debe quedar clara:** el problema no es solo calcular una etiqueta; es ayudar a decidir qué suscripciones revisar ante recursos de retención limitados.

**Texto para explicar:**

“Buenos días. Soy Levis Adrian Ortiz Cano y presento StreamRetain-Agent, un proyecto de inteligencia artificial orientado a la detección de riesgo de abandono de suscripciones.

La problemática que planteamos es que un analista de retención necesita priorizar qué suscripciones revisar. Aunque exista un historial de transacciones, no es evidente cuáles usuarios podrían dejar de renovar. Además, no conocemos directamente la intención de cada persona: vemos registros de pagos y planes, pero no todos los motivos que explican su decisión.

Nuestro conjunto de diciembre contiene 557 abandonos entre 8220 casos. Esto genera un reto: un sistema que responda siempre que el usuario renovará consigue una exactitud de 93,22%, pero no detecta un solo abandono. Por tanto, una cifra alta de exactitud no basta para resolver el problema.

La pregunta del proyecto es si podemos aprovechar información histórica disponible antes de un corte para identificar casos de riesgo y apoyar la revisión humana.”

**Transición:** “Para responderla, diseñamos el siguiente agente.”

## Diapositiva 2 — ¿Cuál es la solución y qué buscamos con el agente?

**Idea central:** el modelo predictivo forma parte de un sistema que percibe, decide y comunica una recomendación.

**Texto para explicar:**

“La solución es StreamRetain-Agent. Su usuario previsto es un analista de retención. El agente recibe características históricas de una suscripción, calcula un puntaje y lo compara con un umbral. Si el puntaje alcanza el umbral, recomienda una revisión humana; si no lo alcanza, informa que no se generó alerta, sin garantizar una renovación.

La versión V4 usa un árbol aprendido mediante aprendizaje supervisado y un umbral de 0,30. La inteligencia aprendida está en el modelo; el formulario, la regla de decisión, la explicación y el registro completan el prototipo de agente.

Su objetivo es apoyar la priorización, no cancelar servicios ni decidir automáticamente una oferta. Tampoco hemos demostrado que una campaña basada en sus alertas evite abandonos. El modelo se entrena fuera de línea: consultar la página o guardar una decisión en el historial no significa que aprenda de esa consulta.”

**Transición:** “Para precisar su funcionamiento, lo formulamos mediante PEAS.”

## Diapositiva 3 — P de PEAS: Performance measure

**Idea central:** el desempeño se evalúa con resultados observables, no con que la página produzca una respuesta.

**Texto para explicar:**

“La P significa medida de desempeño: cómo evaluamos si el agente está cumpliendo su propósito. La precisión de abandono indica qué proporción de nuestras alertas correspondió a abandonos. El recall indica qué proporción de todos los abandonos logramos detectar. F1 combina ambas mediante una media armónica, de modo que una de ellas muy baja limita el resultado.

La propuesta fijó exactitud de al menos 0,75, F1 de abandono de al menos 0,50 y superar al baseline en F1. También reportamos ROC-AUC y Average Precision para describir cómo se ordenan los puntajes.

Estos criterios se distinguen del umbral 0,30: el umbral decide cuándo emitir una alerta; el F1 se calcula después, comparando predicciones con etiquetas. No evaluamos dinero recuperado ni éxito de campañas, porque no se ejecutaron intervenciones comerciales reales.”

**Transición:** “La siguiente parte de PEAS describe el entorno del agente.”

## Diapositiva 4 — E de PEAS: Environment

**Texto para explicar:**

“La E corresponde al entorno. En el uso previsto incluye suscripciones, pagos, fechas de vencimiento, cancelaciones y un analista que revisa recomendaciones. Sin embargo, debemos distinguir ese entorno objetivo del alcance implementado.

En el proyecto trabajamos con registros históricos de transacciones de KKBox. No existe una conexión actual a los usuarios de esa plataforma ni una integración real con su equipo de marketing. Tampoco utilizamos en el modelo final todos los datos de consumo que se habían considerado en el diseño inicial.

El agente conoce características de una historia transaccional, pero no conoce la intención de abandonar, los motivos personales ni todas las condiciones externas. Por eso el entorno es parcialmente observable. Nuestro experimento tampoco demuestra funcionamiento continuo cada lunes: se evaluaron cuatro fechas históricas separadas.”

**Transición:** “Dentro de ese entorno, debemos explicar cómo entra la información y cómo sale una acción.”

## Diapositiva 5 — S y A de PEAS: sensores y actuadores

**Texto para explicar:**

“Los sensores son los mecanismos de entrada. Durante la preparación leemos los registros del archivo comprimido y calculamos características anteriores al corte. En la demostración, el sensor práctico es el formulario: recibe diez características ya calculadas o introducidas como un escenario ficticio.

Los actuadores son los mecanismos con los que el sistema comunica o registra su decisión: la interfaz muestra una alerta, una recomendación de revisión o ausencia de alerta, y permite conservar el registro en el historial y exportarlo como JSON.

El árbol no es un sensor ni un actuador: es el procesamiento interno que transforma la entrada en un puntaje. Y el puntaje, por sí solo, no es una acción sobre el entorno. La acción del prototipo consiste en comunicar la recomendación y registrarla.

El historial de la web es temporal y por sesión. No debe confundirse con una base permanente de clientes ni con aprendizaje automático continuo.”

## Diapositiva 6 — ¿Qué tipo de entorno tiene el agente?

**Texto para explicar:**

“El entorno objetivo es parcialmente observable porque no tenemos todos los factores que determinan la decisión del suscriptor. Es estocástico desde nuestra perspectiva: dos usuarios con características observadas parecidas pueden actuar de manera distinta. Esto no significa que el árbol cambie aleatoriamente su respuesta ante la misma entrada; el modelo guardado produce una predicción determinista.

Es dinámico porque las transacciones, los vencimientos y las suscripciones cambian con el tiempo. En un sistema real de retención sería también secuencial, ya que observaciones e intervenciones sucesivas podrían afectar decisiones posteriores.

En cambio, nuestro prototipo no implementa esa política secuencial. Evalúa perfiles por separado y no simula los efectos de una oferta sobre el usuario. Los archivos de evaluación son capturas históricas fijas.

Las variables son mixtas: tenemos conteos e indicadores discretos, además de medias, importes y proporciones numéricas. Modelamos un solo agente; usuarios y analista se incluyen como parte del entorno, no como agentes inteligentes adicionales.”

## Diapositiva 7 — ¿De dónde salió el dataset?

**Texto para explicar:**

“La fuente es el desafío WSDM de predicción de abandono de KKBox publicado en Kaggle. Es importante distinguirlo del conjunto de recomendación musical: el problema que trabajamos es renovación o abandono de suscripciones.

El archivo original de transacciones que utilizamos contiene 21547746 registros. Por su tamaño, evitamos descomprimirlo completo al disco. Lo recorrimos progresivamente y seleccionamos aproximadamente 1% de los usuarios mediante una función hash estable.

Seleccionar usuarios de forma estable permite conservar sus eventos relevantes dentro de las ventanas de cada corte. No significa que tomemos filas al azar ni que tengamos exactamente 1% de todas las transacciones.

Construimos etiquetas propias para nuestro protocolo temporal. Por eso las llamamos etiquetas reconstruidas bajo supuesto de cobertura, y no etiquetas oficiales de Kaggle. La procedencia es Kaggle; las cifras y resultados que mostraré corresponden a nuestro experimento.”

**Transición:** “Con los registros disponibles, el siguiente problema era convertirlos en ejemplos de aprendizaje.”

## Diapositiva 8 — ¿Qué procedimiento seguimos?

**Texto para explicar:**

“Primero revisamos formatos, fechas, identificadores y coherencia de registros. Después definimos un ejemplo como un usuario observado en una fecha de corte. Para construir características utilizamos exclusivamente los 90 días anteriores al corte.

Seleccionamos candidatos cuyo vencimiento conocido estaba entre el corte y 29 días después. Reconstruimos ese estado con reglas de ordenamiento de eventos, evitando tomar simplemente el vencimiento máximo de cualquier registro.

El seguimiento posterior permitió construir la etiqueta. Gap es la diferencia entre la fecha de renovación y el vencimiento efectivo. Renovar antes de que transcurran 30 días corresponde a renovación oportuna; un gap de 30 días o más se considera tardío. Si no observamos renovación, necesitamos seguimiento suficiente y asumir que el historial publicado cubre lo necesario.

Una cancelación aislada no implica abandono: puede haber una renovación posterior. La separación fundamental es que esa información posterior se usa para establecer la etiqueta, no como característica disponible para predecir.

El protocolo ejecutado usa candidatos con vencimiento entre 0 y 29 días y tolerancia de renovación. No debemos presentarlo como si fuera exactamente el horizonte inicial de 28 días.”

## Diapositiva 9 — ¿Cómo entrenamos y validamos sin mezclar el futuro?

**Texto para explicar:**

“La primera ronda entrenó con 7443 ejemplos de marzo y validó con 7210 de junio. La segunda entrenó con marzo y junio juntos y validó con 8251 ejemplos de septiembre. Para comparar una configuración usamos su mismo umbral en ambos periodos y calculamos el F1 medio.

Después de seleccionar el candidato, lo ajustamos con 22904 ejemplos de los tres periodos de desarrollo. Diciembre contiene 8220 ejemplos posteriores. Algunos usuarios se repiten en distintos cortes, lo que representa observar suscriptores existentes en diferentes momentos. Su identificador no se introduce al modelo como predictor.

La primera versión tuvo la evaluación original de diciembre. Luego observamos sus errores e intentamos mejorar el proyecto. Por esa razón, cuando volvimos a diciembre con V4, ya no era una nueva prueba independiente. Reportamos esa comparación como exploratoria y conservamos los resultados anteriores. Esta limitación es importante para no exagerar nuestra capacidad de generalización.”

## Diapositiva 10 — ¿Cómo fue evolucionando el agente?

**Texto para explicar:**

“Empezamos con un baseline que siempre predice la clase mayoritaria. Mostró que la exactitud podía ser alta sin detectar abandonos. Después comparamos regresión logística y árbol con seis características históricas. La logística utilizó escalado ajustado solo con entrenamiento.

Seleccionamos inicialmente un árbol con F1 medio de validación cercano a 0,4490. En diciembre su F1 fue 0,3462. Al ampliar parámetros del árbol, el F1 medio subió a 0,4573: una mejora pequeña. Probamos también un bosque aleatorio, que obtuvo 0,4482 y no superó al árbol ampliado bajo el criterio elegido.

Estos resultados nos llevaron a cambiar la pregunta. En lugar de seguir aumentando la complejidad del modelo con la misma información, comprobamos si faltaban características útiles del plan. Así llegamos a V4, con diez variables.

Cada paso quedó respaldado por resultados y configuraciones guardadas. No seleccionamos solo una cifra favorable de un periodo ni cambiamos de métrica para afirmar que un experimento había ganado.”

## Diapositiva 11 — ¿Qué cambió con las diez características?

**Texto para explicar:**

“Las seis características originales eran transacciones en 90 y 30 días, cancelaciones en 90 días, días distintos con transacciones, días desde la última transacción y días hasta vencimiento.

Añadimos duración media del plan, precio de lista medio, importe pagado medio registrado y proporción histórica de autorrenovación. Todas usan registros anteriores al corte. No representan ingresos netos ni una garantía de que habrá renovación futura.

Para comprobar su aporte mantuvimos los mismos parámetros y umbral. El F1 medio pasó de 0,4573 a 0,5095. Después, seleccionando parámetros con diez variables, llegó a 0,5398. El candidato usa profundidad máxima 10, mínimo 100 ejemplos por hoja, sin ponderación de clases y umbral 0,30.

La mejora media no significa que ambos periodos superen 0,50: junio dio 0,4791 y septiembre 0,6004.”

## Diapositiva 12 — ¿Cuáles fueron los resultados?

**Texto para explicar:**

“En la comparación exploratoria de diciembre, V4 obtuvo F1 de 0,4205, frente a 0,3462 de V1. Detectó 217 de los 557 abandonos y produjo 258 falsas alertas. Quedaron 340 abandonos omitidos y 7405 renovadores correctamente clasificados.

La precisión de 45,68% significa que 217 de 475 alertas correspondieron a abandono. El recall de 38,96% significa que detectamos 217 de 557 abandonos. Frente a V1 fueron 28 abandonos detectados adicionales y 88 falsas alertas menos, usando los umbrales elegidos para cada versión.

Sin embargo, el modelo no mejoró en todas las medidas. ROC-AUC descendió de 0,8304 a 0,6493 y Average Precision quedó ligeramente por debajo. V4 mejoró el F1 en su punto de decisión, pero no podemos afirmar que ordena mejor el riesgo en general.

La meta de F1 de 0,50 no se alcanzó en diciembre. El resultado favorable de 0,5398 pertenece a validación y no debe mezclarse con este resultado.”

## Diapositiva 13 — Demostración guiada de cuatro minutos

Los escenarios de la app son **ficticios y seleccionados para mostrar decisiones distintas**. No son cinco usuarios reales con etiqueta conocida ni una muestra para medir precisión. El modelo y el umbral no se alteraron para forzar las alertas.

### 14:30–15:15 · Mostrar la página y un caso sin alerta

“Esta es la interfaz del agente V4. Las métricas de arriba describen su evaluación histórica; no cambian con cada consulta. El formulario permite introducir un perfil de suscripción.”

Selecciona A, lee su resumen y pulsa Evaluar. Puntaje esperado con sus valores originales:0,0175, por debajo de 0,30.

“Este perfil no genera alerta. Eso no garantiza que renovará: significa que no supera el umbral del modelo. El escenario B también queda por debajo, con 0,1130.”

### 15:15–16:15 · Mostrar una alerta y explicar el umbral

Selecciona C: un registro dentro de la ventana, última transacción hace 25 días, vencimiento a 5 días, sin autorrenovación. Evalúa:0,4024.

“Este puntaje supera 0,30 y activa la recomendación de revisión humana. No significa que exista una probabilidad real calibrada de 40,24% ni que sepamos que esta persona abandonará. El perfil es ficticio.”

Abre o señala el recorrido del árbol. Explica una condición con su valor real y el límite que aparece en pantalla; no memorices un recorrido que no hayas visto. Una regla del árbol describe cómo decide, no demuestra una causa del comportamiento del cliente.

### 16:15–17:15 · Contrastar otros dos escenarios

Selecciona D, evalúa y muestra 0,9333. Luego muestra E con 0,3138 si el ritmo lo permite.

“D tiene un plan de 60 días y una transacción hace 55 días. No tener transacciones recientes puede ser coherente con la duración del plan. Aun así, el modelo genera alerta. E incluye una cancelación y autorrenovación en uno de sus dos registros; también supera el umbral, por poco. No estamos afirmando que esas características causen abandono.”

No describas 0,9333 como 93,33% de certeza. Si cambias valores, los puntajes de esta guía dejan de ser expectativas obligatorias: son los valores de los perfiles originales.

### 17:15–18:30 · Control de entrada e historial

En E cambia transacciones en 30 días a 3, manteniendo transacciones en 90 días en 2. Pulsa Evaluar. Debe aparecer un error y no añadirse una decisión al historial.

“Este control rechaza una entrada incoherente. El historial conserva las decisiones válidas de la sesión y puede descargarse. No contiene nombres ni ejecuta acciones comerciales.”

Restaura la entrada. Muestra el enlace público si está comprobado desde ventana privada. Si grabas localmente, dilo: localhost no es un enlace que el profesor pueda abrir desde su equipo. Verifica antes de grabar que el despliegue recibió la actualización con los cinco escenarios.

## Diapositiva 14 — Conclusión, límites y contribuciones

**Texto para explicar:**

“El proyecto permitió construir un prototipo reproducible que transforma historia transaccional en recomendaciones de revisión. La evolución mostró que añadir información del plan aportó más que seguir cambiando parámetros con las seis variables originales.

El F1 medio de validación fue 0,5398 y el F1 exploratorio de diciembre 0,4205. La meta no se alcanzó en diciembre, y la reutilización de ese periodo impide presentarlo como una nueva prueba independiente. Además, las etiquetas dependen de cobertura suficiente y la auditoría manual no fue completa en todos los cortes. La demo no demuestra eficacia de campañas, equidad demográfica ni desempeño con clientes actuales.

Como trabajo futuro proponemos revisar etiquetas y cobertura, estudiar la estabilidad temporal y reservar una nueva evaluación independiente antes de afirmar mejoras generales.

El desarrollo se realizó con apoyo de IA para guía, documentación, revisión y soporte. Implementé y ejecuté los experimentos; la IA también realizó, por solicitudes puntuales, el módulo de preparación y ajustes de la interfaz. Mi responsabilidad es comprender y defender el funcionamiento y las limitaciones presentadas.

Con esto concluyo la presentación de StreamRetain-Agent.”

## Diapositiva 15 — Referencias y trazabilidad

Es una diapositiva de apoyo. La formulación del agente se apoya en el material del curso y el diseño inicial. El dataset se identifica mediante el desafío de Kaggle. Los resultados propios proceden de los JSON de experimentos indicados; no son métricas obtenidas por Kaggle.

Fuente del dataset: https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/overview

Material local: Context/docs/AI_Lecture02_Intelligent_Agents.pdf y diseño inicial. Evidencias: experiments/comparacion_caracteristicas_v4/resultados.json, experiments/prueba_final/resultados.json y experiments/modelo_v4/evaluacion_diciembre.json.

---

# Apoyo de estudio: preguntas que debes poder responder

## ¿Por qué es un agente y no solamente un árbol?

El árbol es el componente predictivo. El prototipo además recibe información, aplica una política de alerta, comunica una recomendación y registra decisiones. Es un agente de apoyo acotado; no un sistema autónomo de marketing completo.

## ¿Qué significa cada letra de PEAS en una frase?

- P: evaluar desempeño con precisión, recall, F1, exactitud y métricas complementarias.
- E: suscripciones, transacciones y revisión de retención; observados aquí mediante datos históricos.
- A: mostrar recomendaciones y escribir/exportar registros de decisiones.
- S: leer transacciones o recibir características mediante el formulario.

## ¿Por qué el entorno es estocástico si siempre responde igual?

La incertidumbre describe el comportamiento de los suscriptores y lo que desconocemos del entorno. El modelo entrenado es determinista para una misma entrada. Son niveles distintos.

## ¿Por qué llamamos secuencial al entorno previsto pero no al modelo?

En retención real, una intervención puede influir en el estado y decisiones futuras. Aquí no modelamos ni optimizamos ese efecto: clasificamos capturas históricas y perfiles individuales. Tener variables históricas no convierte un árbol en un modelo de planificación secuencial.

## ¿Qué diferencia hay entre 90 días, 29 días y 30 días?

90 días delimitan la historia usada para características.0..29 días delimitan el vencimiento conocido que hace elegible a un candidato.30 días es el límite de tolerancia de renovación aplicado a la etiqueta: gap exactamente 30 ya es tardío. No son tres maneras de expresar el mismo horizonte.

## ¿Qué son precisión, recall y F1 con los números de V4?

Precisión=217/(217+258)=45,68%. Recall=217/(217+340)=38,96%. F1=2×217/(2×217+258+340)=0,4205. Precisión pregunta por la fiabilidad de las alertas; recall por los abandonos detectados. F1 exige atender ambas.

## ¿Qué es una fuga de información?

Introducir como predictor un dato que no estaría disponible al momento de predecir. Por ejemplo, la primera renovación después del corte. Sí podemos usarla para construir la etiqueta retrospectiva, pero no para representar lo que el agente sabía al corte.

## ¿Qué aporta el control de seis frente a diez variables?

Mantener parámetros y umbral reduce cambios simultáneos: permite medir el aporte del conjunto de cuatro características bajo esa configuración. No identifica por sí solo el aporte individual de cada variable ni demuestra causalidad sobre el usuario.

## ¿Por qué la meta no se declara cumplida si 0,5398 es mayor que 0,50?

Porque 0,5398 es la media de validaciones usadas para seleccionar. En diciembre V4 obtuvo 0,4205. Además, diciembre ya era conocido y su nueva evaluación es exploratoria. No basta con encontrar una cifra favorable en alguna etapa.

## ¿Por qué no bajar el umbral hasta que mejore diciembre?

Eso utilizaría diciembre para seleccionar y lo alejaría aún más de una evaluación independiente. Bajar el umbral puede detectar más abandonos y generar más falsas alertas; no garantiza mejorar F1. El umbral 0,30 se seleccionó en desarrollo.

## ¿Los cinco escenarios prueban que funciona bien?

Prueban que la interfaz procesa entradas y aplica el modelo correctamente. Se eligieron para mostrar tres alertas y dos ausencias de alerta. No tienen etiquetas reales y no permiten calcular precisión ni afirmar eficacia predictiva.

## ¿Por qué no subimos todos los CSV al despliegue?

La inferencia necesita el modelo, el contrato de características, sus metadatos y las dependencias. El dataset fue necesario para preparar, entrenar y evaluar, pero no para calcular el puntaje de una entrada ya resumida. La reproducibilidad se documenta por separado.

## ¿Cómo explicar ROC-AUC y AP sin prometer demasiado?

Describen la calidad del ordenamiento de puntajes, considerando distintos puntos de decisión. F1 se calcula con un umbral concreto. Por eso mejorar F1 al umbral elegido no obliga a mejorar ROC-AUC o AP. AP aquí corresponde a average_precision_score, no a otra integración de la curva PR.

## ¿Qué debo comprobar antes de grabar?

- La app desplegada identificaV4, diez características y umbral 0,30.
- Los cinco perfiles originales reproducen los puntajes de la diapositiva 13.
- El video usa los archivos reformulados, no el PDF anterior llamado borrador.
- La letra y la voz se entienden; se ensayó el tiempo con navegación real.
- El enlace funciona desde una ventana privada. No exponer credenciales al grabar.
- No presentar como cerrados el informeIEEE o análisisV4 que aún estén pendientes.
- No atribuir el análisis de errores/subgrupos deV1 aV4. En estas diapositivas solo se muestran cifras globales verificadas deV4.
