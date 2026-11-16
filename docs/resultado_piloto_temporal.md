# Resultado del piloto temporal: extracción

Fecha: 2026-11-16. Fuente: resumen comunicado por el estudiante al ejecutar scripts/04_piloto_temporal.py. Codex revisó el bloque de controles y salida y las sumas, sin ejecutar procesamiento de filas.

| Medida | Resultado comunicado |
| --- | ---: |
| Filas originales recorridas | 21.547.746 |
| Transacciones históricas guardadas | 25.054 |
| Transacciones de seguimiento guardadas | 15.449 |
| Total guardado | 40.503 |
| Tamaño en MiB | 3,14 |

Historia: 2015-12-08 a 2016-03-06. Corte: 2016-03-07. Seguimiento: 2016-03-07 a 2016-05-05. Salida local: data/derived/piloto_2016-03-07.csv. El archivo previo se conservó como piloto_2016-03-07.previo-299ec0e5.csv; no usarlo como muestra validada.

| Mes | Transacciones |
| --- | ---: |
| 2015-12 | 6553 |
| 2016-01 | 8717 |
| 2016-02 | 8355 |
| 2016-03 | 7865 |
| 2016-04 | 7806 |
| 2016-05 | 1207 |

La suma mensual y la suma de fases coinciden con 40.503. Marzo incluye ambas fases: no separar por mes completo. Estas son transacciones, no usuarios únicos ni ejemplos etiquetados. La selección aproximada del 1 % se aplica a identificadores, no al porcentaje de filas conservadas del archivo completo; además hay un filtro temporal.

La salida indica que la extracción llegó al resumen después de los controles del script. No demuestra que cada usuario tenga historia suficiente ni etiquetas construidas. Próximo paso: agrupar y ordenar los eventos por usuario, reconstruir estado al corte, seleccionar vencimientos elegibles, verificar seguimiento y construir etiquetas con las reglas documentadas, antes de características agregadas y línea base. No volver a recorrer el original para este paso: trabajar sobre el CSV reducido ya obtenido.

## Guía 07 completada: candidatos

Fuente: resumen comunicado por el estudiante; Codex leyó el bloque de selección/salida y comprobó las sumas, sin ejecutar el procesamiento.

| Medida | Resultado |
| --- | ---: |
| Filas históricas / seguimiento | 25.054 / 15.449 |
| Usuarios con historia | 10.447 |
| Usuarios con seguimiento | 8.385 |
| Usuarios solo con seguimiento | 1.100 |
| Usuarios con varios eventos en último día histórico | 383 |
| Vencimiento anterior al corte | 2.120 |
| Vencimiento posterior a ventana | 884 |
| Candidatos | 7.443 |

2.120 + 884 + 7.443 = 10.447. Las filas siguen sumando 40.503. Por diferencia, 7.285 usuarios tienen historia y seguimiento; este número no es el número de candidatos con seguimiento. Los 383 empates se refieren a usuarios históricos con varios eventos el último día, no necesariamente a candidatos ni a duplicados incorrectos. Los 1.100 usuarios solo observados en seguimiento no son necesariamente altas nuevas; solo carecen de eventos en la ventana histórica del piloto.

Salida reportada: data/derived/candidatos_2016-03-07.csv. Son candidatos por vencimiento conocido al corte, todavía sin is_churn. Próximo paso: construir y revisar etiquetas usando seguimiento y reglas de renovación/cancelación, con casos de frontera y comprobación de cobertura. No entrenar todavía ni asignar abandono por exclusión de la ventana.

## Guía 08 completada: etiquetas reconstruidas

Fuente: salida comunicada por el estudiante. Codex revisó el bloque de resumen del script y las sumas, sin procesar filas.

| Medida | Resultado |
| --- | ---: |
| Casos ilustrativos correctos reportados | 9 |
| Candidatos procesados | 7.443 |
| Sin eventos de seguimiento | 895 |
| Vencimientos adelantados antes de primera renovación | 103 |
| Renovación (0) | 6.348 |
| Abandono (1) | 1.095 |
| Sin etiqueta | 0 |
| Renovación oportuna | 6.348 |
| Renovación tardía | 34 |
| Sin renovación en plazo | 1.061 |

6.348 + 1.095 = 7.443; 34 + 1.061 = 1.095; prevalencia reconstruida 14,71 %. Los 895 sin eventos no equivalen a los 1.061 sin renovación: según el algoritmo, la diferencia de 166 corresponde a usuarios con eventos pero sin una transacción de renovación en el seguimiento (solo cancelaciones). Es una deducción de los conteos y la lógica, no una inspección adicional de sus filas.

Seguimiento declarado hasta 2016-05-05. Salida: data/derived/etiquetas_piloto_2016-03-07.csv. Etiquetas reconstruidas bajo el supuesto de cobertura del historial publicado, no oficiales. Cero sin etiqueta significa que la lógica asignó un resultado a todos con ese horizonte y supuesto; no prueba cobertura perfecta ni precisión del etiquetado. El 14,71 % no es exactitud ni resultado de modelo; no exigir igualdad con 8,99 % de otra cohorte.

Próximo paso: auditar ejemplos reales y reglas del etiquetado antes de preparar características y línea base. Excluir de características los datos posteriores al corte (gap, motivo, renovación futura y vencimiento ajustado con seguimiento).

## Guía 09: primera revisión de casos 01–03

Fuente: resumen y razonamiento comunicados por el estudiante, contrastados por Codex con el informe Markdown generado por el estudiante. No se releyeron ni procesaron CSV. La coherencia interna de 7.443 etiquetas fue reportada; no equivale a validación independiente del resultado real.

Conteos reportados: anticipadas 852, mismo día 4.234, de 1 a 28 días 1.260, gap 29: 2, gap 30: 3, gap mayor de 30: 31, sin eventos 895, solo cancelaciones 166, vencimiento adelantado 103, empate último día histórico 187. Nueve casos distintos para revisión. 852+4.234+1.260+2=6.348 renovaciones; 3+31=34 tardías; 895+166=1.061 sin renovación. Categorías de vencimiento adelantado y empates se superponen con otras, no se suman al total.

El informe muestra:

| Caso | Vencimiento conocido al corte | Primera renovación desde corte | Gap | Etiqueta guardada / esperada |
| --- | --- | --- | ---: | --- |
| 01 | 2016-03-23 | 2016-03-22 | -1 | 0 / 0 |
| 02 | 2016-03-10 | 2016-03-10 | 0 | 0 / 0 |
| 03 | 2016-03-12 | 2016-03-16 | 4 | 0 / 0 |

Los tres coinciden bajo las reglas documentadas y los eventos del informe. La explicación del estudiante confundía primera renovación desde el corte con una transacción histórica de enero y con posibles renovaciones de mayo. Codex aclaró que se evalúa el episodio asociado al vencimiento conocido el 7 de marzo; las renovaciones posteriores de otros ciclos no cambian esta etiqueta. No se necesita esperar un pago de mayo para resolver un episodio de marzo ya renovado a tiempo. No se afirmó revisión independiente del estudiante completada: debe incorporar y explicar la corrección. Permanecen por revisar los demás casos, especialmente límites, ausencia y cancelación.

## Revisión guiada de casos 04–05

El estudiante identificó gap 29 y 30 considerando marzo de 31 días. Propuso cambiar el Caso 05 a renovación por interpretar el límite inclusivamente. Se explicó que bajo las reglas Scala gap < 30 -> 0 y gap >= 30 -> 1: Caso 04 coincide con 0 y Caso 05 con 1. Es una diferencia de interpretación del objetivo, no evidencia de error del etiquetador. No se alteraron datos ni se considera terminada la auditoría. Resto de casos pendiente.

## Revisión guiada de casos 06–09

Resultados esperados según los eventos del informe y cobertura asumida: Caso 06 gap 36 -> 1; Caso 07 vencimiento 2016-03-26, límite 2016-04-25, sin renovación -> 1; Caso 08 vencimiento efectivo 2016-03-14, límite 2016-04-13, sin renovación -> 1; Caso 09 vencimiento al corte 2016-03-25, límite 2016-04-24, sin seguimiento -> 1. Observación hasta 2016-05-05.

Se corrigieron dos razonamientos: gap vacío no demuestra abandono, y un posible cambio de plan de febrero no resuelve la etiqueta del vencimiento posterior de marzo. Los nueve casos están comentados en revisión guiada; no hay discrepancia identificada con las etiquetas según el informe. No se declara validación exhaustiva ni comprensión independiente final. Falta confirmar explicación del Caso 09 antes de pasar a características. No se modificaron etiquetas ni se procesaron CSV.

## Guía 10 ejecutada: cohorte histórica preparada

Fuente: resumen comunicado por el estudiante. Script local encontrado con nombre scripts/08_caracterustucas_historicas.py (distinto del nombre propuesto en la guía); no se renombró. Codex leyó el bloque de unión/salida y contrastó la aritmética, sin ejecutar ni recorrer los CSV.

Corte 2016-03-07; 40.503 filas recorridas; 15.449 futuras excluidas; 19.656 transacciones históricas de candidatos utilizadas. Cohorte: 7.443 filas, seis características, 6.348 renovaciones y 1.095 abandonos. Salida reportada: data/derived/cohorte_2016-03-07.csv.

| Característica | Mínimo | Máximo | Promedio reportado |
| --- | ---: | ---: | ---: |
| transacciones_90d | 1 | 7 | 2,64 |
| transacciones_30d | 0 | 5 | 0,97 |
| cancelaciones_90d | 0 | 3 | 0,07 |
| dias_con_transacciones_90d | 1 | 5 | 2,59 |
| dias_desde_ultima_transaccion | 1 | 90 | 16,33 |
| dias_hasta_vencimiento | 0 | 29 | 14,95 |

19.656 / 7.443 = aproximadamente 2,64 transacciones por candidato; etiquetas conservadas. De las 25.054 transacciones históricas del piloto, 5.398 pertenecían a usuarios fuera de los candidatos. Los rangos son compatibles con las ventanas; los resúmenes no prueban por sí solos ausencia de fuga ni exactitud fila a fila.

Respuestas conceptuales revisadas: distinción entre transacciones y días correcta; enlace por identificador correcto con verificación de corte; tabla preparada no demuestra rendimiento. Se precisó que gap es una diferencia exacta de días y no una fecha ni un rango, y que la prohibición como característica se debe a su disponibilidad posterior al corte.

Siguiente paso: preparar cohorte de 2016-06-06 con mismas reglas y muestreo estable para primera validación temporal; marzo será entrenamiento, disponible tras seguimiento hasta 2016-05-05. Aún no se entrenó ni evaluó línea base.
