# Preguntas de repaso y respuestas corregidas

Material de estudio de StreamRetain-Agent. Última actualización: 15 de noviembre de 2026.

Este archivo reúne las preguntas de comprensión revisadas durante el proyecto. Complementa el [Glosario](Glosario.md): aquí se practica cómo explicar los conceptos y justificar las decisiones. Las respuestas son explicaciones de referencia; no es necesario memorizarlas literalmente.

## Ejercicio 1: lectura progresiva de etiquetas

Referencia: `docs/guias/02_lectura_etiquetas.md`.

### 1. ¿Por qué la clave del contador es el texto "1" y no el entero 1?

**Respuesta corregida:** porque `csv.DictReader` entrega el contenido de los campos como texto. La etiqueta leída es `"1"`, por lo que el contador utiliza claves del mismo tipo:

```python
conteos = {"0": 0, "1": 0}
etiqueta = "1"
conteos[etiqueta] += 1
```

Los diccionarios de Python sí admiten claves enteras. No es obligatorio ni siempre mejor utilizar texto. Podríamos usar `{0: 0, 1: 0}`, pero tendríamos que convertir y validar la etiqueta antes de acceder al contador.

**Ejemplo de la diferencia:**

```python
# Este diccionario tiene dos claves distintas.
ejemplo = {"1": "clave de texto", 1: "clave entera"}
```

**Corrección de la idea inicial:** no usamos texto simplemente por estar trabajando con un diccionario, sino para que el tipo de la clave coincida con el tipo de la etiqueta que leemos.

**Respuesta breve para explicar oralmente:** “La etiqueta llega del CSV como texto. Por eso uso claves de texto; si quisiera claves enteras, tendría que convertirla”.

### 2. ¿Por qué el programa no necesita guardar el CSV descomprimido completo?

**Respuesta corregida:** el descompresor envía el contenido a un canal que Python lee progresivamente. El programa procesa cada fila y actualiza sus contadores sin escribir el CSV completo en el disco ni reunir todas las filas en una lista.

Flujo del ejercicio:

`Archivo .7z → descompresor → canal de texto → lector CSV → contadores`

Tu explicación de que Python consume los datos conforme se descomprimen era correcta.

**Matiz importante:** lectura progresiva no significa que no se utilice memoria. El descompresor y los canales necesitan memoria; además, cualquier estructura que guardemos puede crecer. Por ejemplo, conservar un registro por usuario para comprobar unicidad requiere más memoria que mantener únicamente dos contadores.

**Respuesta breve para explicar oralmente:** “Procesamos el contenido mientras se descomprime y conservamos el resumen, por lo que no necesitamos almacenar el CSV completo”.

### 3. ¿Por qué el porcentaje de abandono no es la exactitud de un modelo?

**Respuesta corregida:** el porcentaje de abandono describe las etiquetas reales del conjunto. La exactitud compara predicciones con etiquetas reales para contar aciertos.

| Medida | Cálculo | Qué responde |
| --- | --- | --- |
| Porcentaje de abandono | Filas etiquetadas como abandono / filas evaluadas × 100 | ¿Qué proporción de casos corresponde a abandono? |
| Exactitud | Predicciones correctas / predicciones evaluadas × 100 | ¿Qué proporción de casos acertó el modelo? |

En la ejecución comunicada por el estudiante:

- Filas leídas: **970.960**.
- Renovación: **883.630**.
- Abandono: **87.330**.
- Porcentaje de abandono: `87.330 / 970.960 × 100 ≈ 8,99 %`.

El 8,99 % se puede obtener sin entrenar un modelo. En ese ejercicio no se generaron predicciones, por lo que no se midió exactitud.

**Ejemplo ilustrativo con esos conteos:** si una regla predijera renovación para todas las filas, acertaría 883.630 casos y fallaría 87.330. Su exactitud sobre ese mismo conjunto sería aproximadamente 91,01 %, pero detectaría cero abandonos.

Ese 91,01 % es un cálculo ilustrativo, **no una evaluación experimental de la línea base en validación o prueba**. Muestra por qué superar el 75 % de exactitud no basta para demostrar utilidad cuando predominan las renovaciones.

**Respuesta breve para explicar oralmente:** “El porcentaje de abandono describe los datos; la exactitud mide los aciertos de las predicciones. Puedo conocer el primero aunque todavía no exista un modelo”.

### 4. ¿Qué diferencia hay entre contar filas y contar usuarios únicos?

**Respuesta corregida:** contar filas indica cuántos registros existen. Contar usuarios únicos indica cuántos identificadores diferentes aparecen, sin importar cuántas veces se repita cada uno.

**Ejemplo hipotético:**

| Fila | Usuario | Evento |
| --- | --- | --- |
| 1 | A | Transacción 1 |
| 2 | A | Transacción 2 |
| 3 | A | Transacción 3 |
| 4 | B | Transacción 1 |

Hay **4 filas y 2 usuarios únicos**.

Tu explicación sobre varias filas que pueden pertenecer a una misma persona era correcta. El ajuste es que contar usuarios únicos **no elimina filas ni demuestra que las repeticiones sean errores**. Varias transacciones o fechas del mismo usuario pueden ser válidas.

En una tabla de etiquetas de una misma cohorte debemos comprobar si existen usuarios repetidos y si sus etiquetas coinciden. Si una persona aparece con 0 y 1, corresponde investigar el contexto; no borrar registros ni elegir una etiqueta automáticamente.

**Respuesta breve para explicar oralmente:** “Las filas cuentan observaciones; los usuarios únicos cuentan identificadores distintos. Un usuario puede tener varias observaciones legítimas”.

## Cómo estudiar estas preguntas

1. Lee la pregunta e intenta responder sin consultar la explicación.
2. Compara tu respuesta con la versión corregida y explica el ejemplo con tus propias palabras.
3. Identifica qué supuesto necesita cada afirmación: tipo de dato, clase positiva, periodo o unidad de observación.
4. Evita presentar ejemplos hipotéticos o cálculos ilustrativos como resultados de un modelo entrenado.

Las nuevas preguntas se incorporarán con sus respuestas revisadas a medida que avance el proyecto. Los ejercicios aún no ejecutados no se presentarán como verificados.

## Ejercicio 2: interpretación del resultado de unicidad

### ¿Qué significa obtener 970.960 filas y 970.960 usuarios únicos, sin repeticiones?

Según la salida comunicada por el estudiante, cada fila de train_v2 tiene un identificador distinto y una etiqueta válida. No hay que eliminar duplicados de usuario en esa tabla. Esto no demuestra que cada identificador corresponda a una persona física diferente ni verifica el historial de otros archivos.

### ¿Cero contradicciones significa que las etiquetas son necesariamente correctas?

No. Significa que no se detectó un mismo identificador con etiquetas 0 y 1 dentro del archivo revisado. Todavía hay que contrastar la definición, la versión y los periodos de observación. Si cada usuario solo aparece una vez, no puede haber contradicción entre dos filas de ese usuario dentro de esa tabla.

### ¿Ya se puede entrenar después de esta comprobación?

La comprobación resuelve una parte de la calidad de las etiquetas. Aún falta decidir la evaluación, evitar información futura y preparar las entradas. Los conteos no son una línea base evaluada.

## Ejercicio 3: comparación entre versiones

### ¿Cómo puede haber cero contradicciones en v2 y 45.990 etiquetas diferentes entre archivos?

Son controles distintos. Dentro de v2 cada usuario aparece una vez. Entre archivos, las etiquetas pueden corresponder a periodos diferentes o revisiones. No son necesariamente errores: hay que consultar la definición temporal.

### ¿Qué significa ('0', '1')?

Es una tupla ordenada: etiqueta 0 en original y 1 en v2. Los 40.721 casos son usuarios compartidos; no son falsos positivos, porque no hay predicciones.

### ¿Esta tabla es una matriz de confusión de un modelo?

No. Compara etiquetas de dos archivos. La evaluación de un modelo compara predicciones y etiquetas reales para los mismos casos y objetivo temporal.

### ¿El aumento de 6,39 % a 8,99 % demuestra que los mismos clientes abandonan más?

No. Son poblaciones parcialmente distintas y hay que verificar sus periodos. Es una descripción, no una explicación causal.

### ¿Basta con entrenar en un mes y evaluar en el siguiente?

No. Las características y etiquetas usadas para entrenar deben estar disponibles al predecir. Una etiqueta que requiere observar 30 días después del vencimiento puede conocerse después del siguiente corte. Hay que comprobarlo para evitar información futura.

## Ejercicio 4: fechas y corte temporal (guía preparada, ejecución pendiente)

### ¿Por qué comprobar ocho dígitos y también construir una fecha?

El formato no garantiza que el día exista. 20170230 tiene ocho dígitos pero febrero no tiene 30 días. La forma y la validez de calendario son comprobaciones diferentes; ninguna demuestra por sí sola que la fecha refleje correctamente el evento real.

### ¿Por qué agrupar por transaction_date y no membership_expire_date?

Queremos saber cuándo ocurrieron las transacciones observadas. El vencimiento describe hasta cuándo se extiende una suscripción, no cuándo se registró el pago o cambio.

### ¿Un vencimiento futuro es siempre fuga de información?

No. Si el vencimiento ya se conocía por una transacción anterior al corte, puede utilizarse. Lo que no puede incorporarse es una renovación o modificación registrada después del momento de predicción.

### ¿El máximo del archivo basta para evaluar todos los lunes?

No. No garantiza cobertura continua, seguimiento suficiente de cada suscripción ni etiquetas vinculadas a cada corte. Para determinar abandono necesitamos observar el plazo que corresponde al vencimiento; no basta con que el archivo tenga alguna fecha posterior al lunes.

## Revisión de las respuestas del estudiante a la guía 05

Revisadas el 2026-11-16 tras comunicar la ejecución.

1. **Ocho dígitos y calendario:** la explicación del formato es correcta; precisar el orden YYYYMMDD (año, mes, día). Faltaba explicar la segunda comprobación: 20170230 tiene ocho dígitos pero no es un día real.
2. **Fecha de transacción frente a vencimiento:** la idea es correcta. transaction_date sitúa el pago o cambio; membership_expire_date indica el vencimiento registrado en esa transacción, que puede ser futuro. No demuestra por sí misma que el cliente abandonó.
3. **Vencimiento futuro conocido:** el razonamiento es correcto si el vencimiento estaba registrado antes del corte. No asumir que todos los planes duran 30 días; usar el vencimiento informado. La duración del plan y el plazo de 30 días para determinar abandono son conceptos diferentes.
4. **El máximo no basta:** faltaba la respuesta. Tener una transacción el 31 de marzo no garantiza seguimiento suficiente de todos los usuarios. Una suscripción que vence el 20 de marzo necesita observación hasta abril para determinar si renovó dentro del plazo. Tampoco el rango demuestra ausencia de huecos ni etiquetas para cada lunes.

## Guía 06: revisión de comprensión del piloto temporal

Fecha: 2026-11-16. El estudiante comunicó 40.503 transacciones guardadas (25.054 históricas y 15.449 de seguimiento). Todavía no son usuarios etiquetados.

### 1. ¿Por qué seleccionar usuarios con una función estable y no filas al azar?

La respuesta sobre controlar la selección va en la dirección correcta. Hay dos razones concretas: repetir exactamente la selección y conservar juntas las transacciones de cada usuario dentro de la ventana. Si se seleccionaran filas al azar, podría conservarse un pago y perderse la renovación posterior del mismo usuario, distorsionando su historia y su etiqueta. La regla depende del identificador, no del abandono ni de que exista una renovación futura. No garantiza cobertura fuera de la ventana ni que la fuente tenga todos los eventos.

Respuesta breve: seleccionamos usuarios de forma reproducible y conservamos sus eventos dentro de la ventana, evitando romper sus historias con un muestreo de filas.

### 2. ¿Qué uso tienen los eventos anteriores y posteriores al 7 de marzo?

No corresponden directamente a entrenamiento y validación. Para la cohorte de marzo, los anteriores permiten reconstruir el estado del usuario y las características X disponibles al predecir. Los posteriores permiten construir la respuesta real y: renovó o abandonó según el vencimiento y las reglas. Solo cuando se conoce y se dispone de un ejemplo etiquetado (X, y). La cohorte de marzo podrá usarse para entrenar un modelo que se evalúe en una cohorte posterior, como junio, con sus propias características y etiquetas.

Respuesta breve: antes del corte construimos la información de entrada; después observamos el resultado. Entrenamiento y validación se separarán por cohortes, no confundiendo historia y seguimiento de una misma cohorte.

### 3. ¿Por qué una renovación futura sirve para la etiqueta, pero no como característica?

No se debe a falta de certeza. En el archivo histórico podemos saber con certeza que ocurrió una renovación después del corte. Sin embargo, esa información no estaba disponible al predecir. Usarla como entrada sería fuga de información. Ejemplo hipotético: al 7 de marzo sabemos que una suscripción vence el 20; una renovación del 25 permite después determinar el resultado, pero el día 7 todavía no podíamos observarla. Una renovación anterior al corte sí puede aportar información histórica.

Respuesta breve: el resultado posterior sirve para enseñar o comprobar la respuesta; las entradas deben limitarse a lo que se sabía al hacer la predicción.

### 4. ¿Por qué la muestra todavía no es una cohorte etiquetada?

El nombre piloto no es la razón. Actualmente cada fila es una transacción; un usuario puede tener muchas. Falta reconstruir su estado al corte, decidir si su vencimiento lo hace elegible, comprobar seguimiento y calcular su etiqueta, además de resumir sus características. No todos los usuarios seleccionados serán candidatos. El objetivo posterior es una fila por usuario y corte con sus entradas y su etiqueta. Un mismo usuario puede aportar otra fila en un corte posterior.

Respuesta breve: tenemos eventos seleccionados, pero aún no los hemos convertido en ejemplos por usuario y corte con una etiqueta de abandono válida.

## Guía 07: candidatos frente a etiquetas

### 1. ¿Por qué no elegir el mayor vencimiento de cada usuario?

La respuesta del estudiante señaló que se ignorarían datos; la razón concreta es que el vencimiento máximo no siempre describe el estado más reciente. Ejemplo hipotético: un pago fija vencimiento el 5 de abril, pero una cancelación posterior, conocida antes del corte, lo adelanta al 10 de marzo. El máximo conserva abril e ignora la modificación. Debe reconstruirse el estado con eventos anteriores al corte y reglas de orden/desempate. Fecha máxima de vencimiento y fecha de última transacción son conceptos diferentes.

### 2. ¿Estar fuera de la ventana significa abandono?

No. La respuesta del estudiante es correcta en esencia. La ventana 7 de marzo–5 de abril selecciona a quién evaluar en este corte. Estar fuera significa no cumplir esa condición, no haber abandonado. Un usuario que vence el 20 de abril queda fuera aunque pudiera renovar normalmente. Tampoco un vencimiento anterior al corte demuestra abandono: debe revisarse la renovación y su plazo.

### 3. ¿Por qué no exigir eventos futuros para admitir un candidato?

El estudiante identificó correctamente el problema de usar información futura. Exigir eventos posteriores seleccionaría usuarios por algo desconocido al predecir y podría excluir a quienes abandonan: sesgo de selección basado en el futuro. No tener eventos posteriores no demuestra por sí solo una cancelación; se requiere seguimiento suficiente y considerar las limitaciones de cobertura. is_cancel de una transacción no equivale automáticamente a is_churn.

### 4. ¿Qué diferencia hay entre candidato y ejemplo etiquetado?

Candidato: usuario que cumple las condiciones para evaluar su riesgo en una fecha, usando lo conocido entonces. Ejemplo etiquetado: caso para el que además se determinó el resultado real según la definición y el seguimiento necesario. La etiqueta es el resultado observado, no una predicción del modelo.

Ejemplo hipotético sin cancelaciones que modifiquen el vencimiento: al 7 de marzo, un usuario tiene vencimiento conocido el 20 de marzo y cumple las condiciones, así que es candidato. Si se observa su renovación el 25 de marzo, su etiqueta es 0 porque la brecha es menor de 30 días. Si no renueva antes del límite de 30 días, y se dispone de seguimiento suficiente y cobertura justificada, su etiqueta es 1. Si no hay seguimiento suficiente, no se debe forzar 0 o 1: el resultado queda sin determinar para este análisis.

Los 7.443 candidatos todavía no tienen esa etiqueta calculada. Después de etiquetarlos, también habrá que preparar las características para obtener ejemplos utilizables por el modelo. Un candidato no es necesariamente alguien de alto riesgo: aún no se ha estimado su probabilidad.

## Guía 08: respuestas revisadas y definición de gap

El estudiante pidió definir gap antes de usarlo. Se añadió explicación y ejemplos al glosario y a la guía 08.

1. **Renovar exactamente 30 días después:** corregir la confusión con duración del plan. Primero vence la suscripción; después se cuentan los días hasta la renovación. El Scala define renovación para gap < 30 y abandono para gap >= 30. Por tanto, exactamente 30 ya es abandono bajo esta definición, aunque exista una renovación tardía. No afirmar que todos los planes duran 30 días.
2. **Gap negativo:** gap = fecha de primera renovación desde el corte menos vencimiento efectivo. Si renueva el 15 de marzo y vencía el 20, gap = -5: renovó cinco días antes. No es un error ni debe reemplazarse por cero. Sin renovación el gap es desconocido, no negativo ni cero.
3. **Cancelación:** la respuesta es correcta en esencia. Puede haber una renovación posterior a tiempo. La condición precisa se refiere al vencimiento efectivo, posiblemente adelantado por la cancelación, y al límite de 30 días; no basta con estar en el mismo mes o ventana de candidatos.
4. **Ausencia con seguimiento suficiente frente a insuficiente:** la distinción del estudiante es correcta, manteniendo el supuesto de cobertura. Con historial suficientemente observado y cobertura asumida puede asignarse 1 si no hubo renovación oportuna. Si el archivo termina antes, no se conoce aún el resultado y no se debe forzar una etiqueta. La completitud del proveedor no se demuestra solo con una fecha máxima.
5. **Por qué gap y motivo no son características:** ambos se obtienen al observar el futuro para construir la etiqueta. Al predecir el 7 de marzo aún no sabemos la fecha de una renovación del 25 de marzo ni su distancia al vencimiento. Usarlos daría al modelo la respuesta o información que la revela: fuga de información. Sirven para auditoría, no como entradas. Ejemplos de entradas históricas posibles: número de pagos anteriores y días hasta el vencimiento conocido al corte.

## Guía 09: qué episodio estamos etiquetando

### ¿Observado hasta el 5 de mayo significa que necesito conocer el pago habitual de mayo?

No. Observado hasta describe el final del historial disponible. La etiqueta corresponde al vencimiento conocido en el corte del 7 de marzo, no al último vencimiento que aparezca después ni a la permanencia indefinida del usuario. Si ya observamos la primera renovación oportuna de ese episodio, podemos asignar 0 sin esperar todos los ciclos posteriores.

En los casos revisados del informe: Caso 01 vence 23 de marzo y renueva 22 de marzo (gap -1); Caso 02 vence y renueva 10 de marzo (gap 0); Caso 03 vence 12 de marzo y renueva 16 de marzo (gap 4). Los tres reciben 0 para el episodio de marzo. No sabemos con ello qué harán en mayo ni necesitamos saberlo para esa etiqueta.

### ¿Qué significa primera renovación?

En esta implementación es la primera transacción de renovación desde el corte, no la primera transacción de toda la historia. En el Caso 01 es el 22 de marzo, no el 22 de enero. Las fechas anteriores al corte sirven para reconstruir el vencimiento conocido y características históricas.

### ¿Qué fecha de vencimiento uso para calcular el gap?

El vencimiento efectivo del episodio en evaluación, partiendo del conocido al corte y considerando cancelaciones anteriores a la primera renovación. No restar a la fecha de renovación el nuevo vencimiento que esa misma renovación concede para el ciclo siguiente. En el Caso 03: 16 de marzo menos 12 de marzo = 4 días; el nuevo vencimiento del 15 de abril pertenece al ciclo renovado.

### ¿is_cancel=0 e is_churn=0 son lo mismo?

No. is_cancel describe el tipo de transacción; is_churn clasifica el resultado del episodio según el plazo. Una transacción de renovación (is_cancel=0) puede llegar 30 días o más después del vencimiento efectivo y producir is_churn=1. No fundamentar la etiqueta solo en que la columna Cancelación vale cero.

### ¿Cómo escribir la reconstrucción al corte?

Debe escribirse una fecha concreta, no solo bueno o correcto. Para el Caso 01, la transacción histórica del 22 de febrero deja un vencimiento conocido del 23 de marzo. Después se identifica la renovación desde el corte y se calcula su distancia a ese vencimiento.

## Auditoría: casos 04 y 05 y límite de 30 días

El estudiante calculó finalmente 29 días para el Caso 04 (2016-03-08 a 2016-04-06) y 30 para el Caso 05 (2016-03-17 a 2016-04-16). Los días reales del calendario importan: marzo tiene 31 días. No se aproxima cada mes a 30 días. Se resta la fecha inicial de la final, sin contar ambas fechas como días completos adicionales.

Caso 04: del 8 al 31 de marzo transcurren 23 días y hasta el 6 de abril otros 6: gap 29. Etiqueta esperada 0, renovación oportuna. La renovación histórica del 4 de febrero sirve para reconstruir el vencimiento de marzo; no es la renovación que determina esta etiqueta.

Caso 05: del 17 al 31 de marzo transcurren 14 días y hasta el 16 de abril otros 16: gap 30. Etiqueta esperada 1, renovación tardía. El estudiante propuso 0 porque interpretó el plazo como inclusivo. Se aclaró que la implementación de referencia usa gap < 30 para 0 y gap >= 30 para 1, no gap <= 30. La redacción coloquial dentro de 30 días puede ser ambigua; usar la desigualdad exacta para defender el criterio.

La etiqueta 1 no significa que jamás renovó: puede haber renovación tardía que no cumple el plazo definido. Cambiar a <=30 sería un cambio de definición del objetivo, no una corrección de un error de código. No se modificaron etiquetas. La comprensión de esta distinción debe confirmarse antes de continuar la auditoría restante.

## Auditoría guiada: casos 06–09

### Caso 06: renovación tardía

La conclusión del estudiante es correcta. Vencimiento 2016-03-15, renovación 2016-04-20: 16 días restantes de marzo más 20 de abril = 36. Como gap >= 30, is_churn=1. No es necesario calcular la duración del plan ni usar febrero.

### Caso 07: sin eventos futuros

La etiqueta 1 coincide, pero debe corregirse la justificación: no se asigna porque el gap esté vacío ni por estimar un plan de 60 días. Vencimiento 2016-03-26; el límite de 30 días es 2016-04-25. Observación hasta 2016-05-05, sin renovación y bajo cobertura asumida, permite asignar 1. Un gap vacío con seguimiento insuficiente dejaría el resultado desconocido. No es necesario calcular enero-febrero para evaluar este episodio.

### Caso 08: vencimiento adelantado

El estudiante identificó correctamente que cancelar no basta para etiquetar abandono. El vencimiento conocido era 2016-03-18; la cancelación del 2016-03-14 lo adelanta a esa fecha. El límite queda en 2016-04-13. No se observa renovación hasta el 2016-05-05: etiqueta 1 bajo cobertura asumida. Gap vacío porque no hay renovación que permita una resta. No mezclar los gaps de ciclos históricos con este resultado.

### Caso 09: cambio anterior al corte y abandono posterior

El estudiante interpretó los eventos del 2016-02-25 como posible cambio de plan. Es una interpretación plausible, no una intención demostrada por los registros. Hay una cancelación con firma 1493041 y una transacción no cancelada con firma 0735. Según el orden de firmas descendente como texto del Scala, la primera queda antes de la segunda. El vencimiento reconstruido al corte 2016-03-07 es 2016-03-25.

Ambos eventos son ANTERIORES al corte. La transacción no cancelada de febrero no es una renovación posterior para resolver este episodio de marzo. No hay eventos en seguimiento, y el límite de 30 días desde 2016-03-25 es 2016-04-24. El historial llega a 2016-05-05: corresponde is_churn=1 bajo cobertura asumida. Cambiar de plan en febrero y no renovar el vencimiento de marzo son hechos compatibles.

### Regla para revisar cualquier caso

1. Identificar el corte.
2. Reconstruir el vencimiento conocido con historia anterior al corte.
3. Revisar solo el seguimiento desde el corte para determinar este resultado.
4. Aplicar cancelaciones previas a la primera renovación, si existen.
5. Con renovación, calcular gap exacto. Sin renovación, comparar vencimiento efectivo + 30 días con el final de observación; no sustituir gap vacío por cero ni por duración del plan.

Los nueve casos han recibido revisión guiada. No es una certificación global de etiquetas ni una auditoría independiente del estudiante. Antes de avanzar, confirmar que puede explicar el Caso 09 distinguiendo historia y seguimiento.

## Guía 10: respuestas corregidas

### ¿Por qué días hasta vencimiento sí, pero gap no?

La explicación del estudiante sobre días restantes es correcta; falta precisar disponibilidad temporal. Al corte sabemos el vencimiento registrado y podemos restarle la fecha del corte. Gap no es una fecha ni un rango: es la diferencia exacta entre la primera renovación posterior al corte y el vencimiento efectivo. Esa renovación aún no era observable al predecir. Ejemplo: al 7 de marzo, un vencimiento conocido del 23 da 16 días restantes; solo al observar la renovación del 22 sabemos que el gap fue -1. Usar ese gap para predecir el 7 sería fuga de información.

### ¿Por qué transacciones_90d y dias_con_transacciones_90d difieren?

La respuesta del estudiante es correcta. Tres transacciones el mismo día suman tres al primer contador y uno al segundo. Días con transacciones cuenta fechas distintas, no días de escucha ni duración de suscripción.

### ¿Por qué unir por identificador?

La respuesta es correcta: el orden de las filas puede diferir entre archivos. El identificador enlaza características y respuesta del mismo usuario. Además se comprueba el corte para no unir su historia de marzo con una etiqueta de junio. Cuando haya varias cohortes, la identidad de un ejemplo será usuario y corte.

### ¿Por qué la cohorte lista no demuestra que el modelo funciona?

Correcto: preparar entradas y etiquetas no equivale a entrenar, predecir ni medir resultados. Incluso entrenar no bastará: habrá que evaluar en la cohorte posterior reservada para validación, comparando con la línea base y manteniendo la prueba final fuera de los ajustes.

## Guía 11: respuestas revisadas

### ¿Por qué misma selección de usuarios pero distintos candidatos posibles?

No buscamos obligatoriamente usuarios nuevos ni excluimos los de marzo. La regla estable de muestreo hace comparable la selección. La elegibilidad se recalcula con el estado y vencimiento conocido en cada corte: alguien puede cumplir en marzo, junio, ambos o ninguno. Se evalúa el futuro de suscriptores, que pueden repetirse; no es una prueba exclusiva de usuarios nuevos. El cambio relevante es el tiempo de observación, no forzar identidades diferentes.

### ¿Por qué marzo puede entrenar y junio sirve para validar?

Marzo es una cohorte de datos, no una línea base. Línea base significa un predictor sencillo de referencia; aquí predecirá la clase mayoritaria aprendida en entrenamiento. Los resultados de marzo se observaron hasta el 5 de mayo, antes del corte de junio (6 de junio). Las respuestas de junio dependen de acontecimientos posteriores, con seguimiento hasta agosto. Usarlas para entrenar antes de predecir junio introduciría información futura. Después sí se usan para medir las predicciones y validar modelos. En una ronda posterior, una vez conocidas, pueden entrar al entrenamiento para predecir septiembre según el protocolo.

### ¿Por qué no forzar conteos iguales?

Los conteos son resultados observados, no metas. Forzarlos podría eliminar o añadir registros arbitrariamente y alterar la población de validación. Se mantienen reglas y comprobaciones de coherencia, no necesariamente cantidades. Si los conteos coincidieran por casualidad tampoco sería un problema ni significaría que no aprendemos. Repetimos el mismo procedimiento sobre otro periodo; no buscamos artificialmente un resultado diferente.

## Guía 12: elegibilidad y usuarios compartidos

La respuesta del estudiante acierta en que aparecer en marzo no obliga a aparecer en junio. Debe precisarse que no basta con tener cualquier registro: en este piloto se exige historia en los 90 días anteriores al 6 de junio y que el vencimiento reconstruido con esa historia esté entre el 6 de junio y el 5 de julio, inclusive. Se mantiene además el muestreo determinista ya aplicado. No se exige actividad posterior al corte.

No excluir usuarios de marzo tiene una razón metodológica: se evalúa riesgo futuro de suscriptores que pueden ser conocidos. La separación es temporal y exige características disponibles al corte y etiquetas de entrenamiento conocidas antes de validar. Excluir todos los usuarios compartidos cambiaría la pregunta a generalización a usuarios no vistos. Compartir usuarios no garantiza por sí solo ausencia de fuga: seguimos controlando tiempos y no usamos el identificador como predictor.

## Guía 13: ejemplos sintéticos y proporción de abandono

### ¿Por qué los ejemplos inventados conservan fechas de marzo?

No representan la actividad de los usuarios de junio ni se mezclan con el dataset. Son casos sintéticos independientes que comprueban reglas de una función: gap 29 debe dar 0, gap 30 debe dar 1, una cancelación puede adelantar vencimiento, etc. Cada prueba aporta sus propias fechas y resultado esperado. La regla es la misma en ambos periodos; cambiar la cohorte no obliga a cambiar los ejemplos. Las fechas absolutas no deciden el resultado: importan las diferencias temporales y el orden de los eventos.

### ¿El descenso de 14,71 % a 5,70 % prueba una mejora del modelo?

No. Son proporciones de etiquetas reconstruidas de dos cohortes. El etiquetador aplica reglas, no es un modelo entrenado que esté tomando decisiones distintas. Todavía no hemos entrenado ni evaluado un predictor. No confundir la frecuencia del fenómeno con nuestra capacidad para predecirlo. Más adelante compararemos predicciones con etiquetas mediante F1, precisión, sensibilidad y otras métricas, frente a una línea base.

Investigar la diferencia de proporciones puede ser útil para calidad de datos y contexto, pero no permite llamarla mejora o empeoramiento predictivo. Las causas posibles requieren evidencia; no se deben cambiar reglas para forzar la misma tasa.
