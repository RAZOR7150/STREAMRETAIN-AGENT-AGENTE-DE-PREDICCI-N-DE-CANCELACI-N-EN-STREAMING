# StreamRetain — Guion de apoyo para grabación de aproximadamente 20 minutos

Autor: Levis Adrian Ortiz Cano. Preparación:26 de noviembre de2026.

Borrador para ensayo: los tiempos son objetivos e incluyen explicación de diagramas, navegación y pausas. No se obtiene un video de20 minutos leyendo este texto rápidamente. Ensayar con cronómetro y confirmar las instrucciones definitivas del profesor. DemoV4 y enlace aún pendientes de verificación; no grabar afirmando que ya están publicados.

| Diapositiva | Tramo | Tema |
| --- | --- | --- |
| 1 | 00:00–00:30 | Presentación |
| 2 | 00:30–02:00 | Problema y objetivo |
| 3 | 02:00–03:30 | Agente y PEAS |
| 4 | 03:30–05:30 | Datos y etiqueta |
| 5 | 05:30–07:30 | Separación temporal |
| 6 | 07:30–09:00 | Modelos y selección |
| 7 | 09:00–10:30 | Aporte de características |
| 8 | 10:30–12:30 | Resultados y comparación |
| 9 | 12:30–14:00 | Limitaciones y errores |
| 10 | 14:00–18:00 | Demostración de la app |
| 11 | 18:00–18:30 | Reproducibilidad y contribución |
| 12 | 18:30–20:00 | Conclusiones |

## 1. Presentación

“Soy Levis Adrian Ortiz Cano y presento StreamRetain-Agent, un prototipo de apoyo a la detección de abandono de suscripciones usando datos históricos de KKBox. Mostraré cómo se prepararon los datos, cómo se compararon los modelos y cómo el agente convierte una predicción en una recomendación de revisión humana.”

No anunciar que el proyecto predice correctamente todos los abandonos o que alcanzó todas sus metas.

## 2. Problema y objetivo

“El usuario previsto es un analista de retención que necesita priorizar qué suscripciones revisar. El sistema recibe características calculadas con información anterior a una fecha de corte, produce un puntaje y recomienda revisar algunos casos. No hemos validado que una campaña basada en estas alertas evite cancelaciones.”

Explicar por qué el desbalance importa: en diciembre hubo557 abandonos entre8220 casos. Predecir siempre renovación consigue93,22% de exactitud, pero detecta cero abandonos. Por eso la meta incluía F1 de abandono>=0,50 además de exactitud>=0,75 y superar al baseline en F1. Precisar que F1 combina precisión y recall, no es un porcentaje de usuarios bien clasificados.

## 3. Agente y PEAS

“En PEAS, el desempeño se mide mediante métricas de clasificación y sus errores. El entorno son suscripciones históricas. Los sensores son las características de las transacciones; los actuadores de este prototipo son recomendaciones y registro local. No se envían mensajes reales a clientes.”

Recorrer: datos históricos -> características -> modelo -> umbral -> recomendación -> memoria. Explicar que la memoria registra decisiones, pero no reentrena el modelo automáticamente. El entorno es parcialmente observable: faltan motivos del usuario y otros factores que podrían anticipar el abandono.

## 4. Datos y definición de abandono

“Trabajamos con el conjunto de predicción de abandono de KKBox. El archivo original de transacciones tiene21547746 registros. Para evitar extraer todos los datos a disco, se leyó progresivamente desde el comprimido y se aplicó una selección estable de aproximadamente1% de usuarios.”

Explicar hash estable por usuario, conservando sus eventos relevantes. Las características usan90 días anteriores al corte. Los candidatos tienen un vencimiento conocido entre el corte y29 días después. La etiqueta reconstruida evalúa si hay renovación oportuna respecto al vencimiento; gap<30 corresponde a renovación y gap>=30 a abandono. No confundir esto con la propuesta inicial de exactamente28 días.

“Las etiquetas son reconstruidas y dependen de asumir cobertura suficiente del historial. Una cancelación administrativa no basta por sí sola: podría existir una renovación posterior. Tampoco se usa esa renovación futura como característica.”

## 5. Separación temporal

Mostrar los cuatro cortes. Primera ronda: entrenar marzo, validar junio. Segunda: entrenar marzo+junio, validar septiembre. Una misma configuración y umbral se comparan en ambos periodos. Posteriormente se reajusta con las tres cohortes y se evalúa diciembre.

“La primera evaluación de diciembre se hizo con V1. Después de observar sus resultados buscamos mejoras. Por eso la evaluación de V4 sobre diciembre se presenta como exploratoria y no como una prueba independiente nueva.”

Usuarios repetidos entre periodos representan suscriptores observados en distintos momentos; msno no se usa como predictor. No afirmar que se evaluaron todos los lunes o usuarios completamente nuevos.

## 6. Modelos y selección

Presentar DummyClassifier, regresión logística, árbol y ensayo adicional de bosque. La logística utiliza escalado ajustado solo con entrenamiento. Los árboles exploran límites de profundidad, tamaño mínimo de hoja y ponderación de clases; los umbrales se eligen usando validación.

“El bosque no mejoró el F1 medio respecto al árbol ampliado. Más complejidad no aseguró mejor resultado. Conservamos el criterio anunciado de F1 medio, con desempates por AP y cercanía del umbral a0,5.”

V4 elegida:depth10,hoja100,sin ponderación,umbral0,30. Mostrar diferencia entre umbral0,30 y metaF1>=0,50: uno produce alertas, la otra mide resultados.

## 7. Qué aportó la información nueva

Mostrar seis variables originales y cuatro nuevas: promedios de duración del plan, precio de lista, importe registrado y proporción de autorrenovación en los90 días previos.

“El control mantuvo configuración y umbral del árbol y pasó de F1medio0,4573 a0,5095 al añadir las variables. Después de seleccionar nuevamente parámetros con diez variables llegó a0,5398. Esto muestra el aporte del conjunto de características en validación; no identifica cuál variable lo causa individualmente.”

Son estadísticas de transacciones, incluidas cancelaciones; no ingresos netos ni prueba de que una renovación futura ocurrirá.

## 8. Resultados

Leer la tablaV1/V4 con cautela. V4:217 abandonos detectados,340 omitidos,258 falsas alertas y7405 renovadores correctamente clasificados. F1=0,4205. Precisión45,68%: de las475 alertas,217 correspondieron a abandono. Recall38,96%: se detectaron217 de557 abandonos.

“Frente a V1 detectamos28 abandonos más y generamos88 falsas alertas menos. Sin embargo, ROC-AUC bajó de0,8304 a0,6493 y AP quedó prácticamente igual, ligeramente por debajo. V4 no domina todas las métricas. La meta deF1>=0,50 no se alcanzó en diciembre.”

Explicar diferencia entre comparar modelos en un umbral y evaluar el ordenamiento de puntajes. AP es average_precision_score, no un área trapezoidal PR-AUC calculada aparte.

## 9. Errores y límites

Explicar FP como alerta innecesaria y FN como abandono omitido. No atribuir causas personales a partir de seis/diez variables. No presentar el análisis de diez casosV1 como si fueseV4: actualizar el análisis deV4 antes de completar esta sección o identificar explícitamente versión de cada caso.

“Las etiquetas dependen de cobertura, la auditoría manual no fue completa en todos los cortes, solo hay cuatro fechas separadas y el modelo usa datos históricos. El puntaje no está calibrado. La recomendación requiere revisión humana.”

No prometer equidad demográfica: los grupos históricos disponibles no incluyen un análisis validado de atributos sensibles.

## 10. Demostración (4 minutos)

Antes de grabar: verificar appV4, diez campos, umbral0,30, vínculo modelo/evidencia, selección de ejemplos y acceso público. No usar los puntajes de los antiguos perfilesV1 como expectativasV4.

- 14:00–15:00: abrir la app y explicar entradas, versión y métricas. Si se usa el enlace público, mostrarlo sin credenciales.
- 15:00–16:00: evaluar un perfil previamente comprobado que produzca alerta. Mostrar puntaje, umbral, recomendación y reglas del recorrido. No llamar al puntaje “probabilidad real”.
- 16:00–17:00: evaluar otro perfil sin alerta. Aclarar que ausencia de alerta no garantiza renovación. Cambiar un campo coherentemente para mostrar interacción, sin asegurar de antemano la dirección del efecto.
- 17:00–18:00: introducir una combinación inválida y comprobar rechazo. Mostrar historial y descarga JSON. La memoria por sesión no implica persistencia permanente en el servidor.

Si la app no está desplegada, demostrar localmente y decirlo; nunca simular que localhost es un enlace público. Para cumplir la solicitud de acceso del profesor, el enlace publicado debe comprobarse desde ventana privada antes de la entrega.

## 11. Reproducibilidad y contribución

Mostrar brevemente paquetes compartidos y scripts con main. Dependencias y semillas registradas, hashes de datos/modelos y separación entre procesamiento y demo. El modelo puede ejecutarse sin subir los comprimidos a la app.

“Implementé y ejecuté el procesamiento y los experimentos con apoyo de guías de IA. La IA ayudó en documentación, revisión y soporte; realizó una implementación puntual del módulo de preparación a petición mía. La bitácora distingue estas contribuciones.”

## 12. Conclusión

“Construimos un prototipo reproducible con comparación de técnicas, separación temporal y explicación de decisiones. Agregar información de suscripción fue más útil que continuar ajustando únicamente las seis variables iniciales. La mejora observada no permite afirmar que la meta se cumplió en una prueba independiente.”

Trabajo futuro: revisar cobertura y etiquetas, estudiar estabilidad temporal, enriquecer características y reservar una evaluación independiente. No prometer que bastará bajar el umbral. Cerrar mostrando dónde están el informe, el código y el enlace de demostración, cuando estén efectivamente disponibles.

## Lista de comprobación del video

- Confirmar formato y duración con las instrucciones definitivas del profesor.
- Ensayar y ajustar ritmo a unos20 minutos, incluyendo navegación.
- Texto legible a la resolución de grabación; probar micrófono y capturar el navegador.
- No mostrar claves, tokens ni información personal real.
- Verificar correspondencia de versión entre diapositivas, app y métricas.
- Probar la reproducción completa del archivo final y el acceso a los enlaces de entrega.
