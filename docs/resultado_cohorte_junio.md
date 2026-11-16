# Cohorte de junio — resultados comunicados

Fuente: ejecuciones del estudiante. Codex comprueba resúmenes y código indicado; no reejecuta procesamiento.

## Extracción completada

- Origen transactions.csv.7z: 21.547.746 filas recorridas.
- Historia desde 2016-03-08, corte 2016-06-06, seguimiento hasta 2016-08-04.
- Historia guardada: 23.165 transacciones.
- Seguimiento guardado: 17.447 transacciones.
- Total: 40.612 transacciones; tamaño comunicado 3,15 MiB.
- Salida: data/derived/piloto_2016-06-06.csv.

| Mes | Transacciones |
| --- | ---: |
| 2016-03 | 6176 |
| 2016-04 | 7806 |
| 2016-05 | 7973 |
| 2016-06 | 8130 |
| 2016-07 | 9410 |
| 2016-08 | 1117 |

Suma mensual y suma de fases: 40.612. Codex revisó corte/rutas del extractor y aritmética, sin recorrer CSV. No hay todavía candidatos, etiquetas ni características de junio. La fuente, el muestreo y la definición se mantienen; no imponer el tamaño ni los usuarios candidatos de marzo. Próximo paso: guía 12.

## Candidatos de junio completados

Salida comunicada por el estudiante: 23.165 filas históricas, 17.447 de seguimiento, 40.612 total. Usuarios con historia: 9.038; con seguimiento: 9.891; solo seguimiento: 2.261; varios eventos en último día histórico: 113. Vencimiento anterior: 1.318; posterior: 510; candidatos: 7.210. Las tres categorías de vencimiento suman 9.038. Archivo reportado: data/derived/candidatos_2016-06-06.csv. Codex revisó rutas/corte del script y aritmética, sin procesar CSV.

Tener historia no basta: el vencimiento conocido al corte debe estar entre 2016-06-06 y 2016-07-05. Usuarios repetidos entre cohortes son compatibles con el objetivo de evaluar el futuro de suscriptores conocidos, no una evaluación exclusiva de usuarios nuevos. No se midió todavía la intersección de candidatos entre meses. Etiquetas y características de junio pendientes; siguiente guía 13.

## Etiquetas de junio completadas

Resumen comunicado por el estudiante: nueve casos ilustrativos correctos; 7.210 candidatos; 206 sin eventos de seguimiento; 78 vencimientos adelantados; 6.799 renovaciones; 411 abandonos; cero sin etiqueta. Motivos: 6.799 oportunas, 85 tardías, 326 sin renovación en plazo. Seguimiento hasta 2016-08-04. Salida etiquetas_piloto_2016-06-06.csv.

Sumas verificadas por Codex: 6.799 + 411 = 7.210; 85 + 326 = 411; proporción de abandono 5,70 %. Revisión de rutas/corte del script, sin ejecución de filas. Bajo la lógica aplicada, 326 - 206 = 120 usuarios tuvieron eventos pero ninguna renovación en seguimiento; es deducción de conteos, pendiente de auditoría.

Marzo tenía 14,71 % y junio 5,70 % de abandono reconstruido. Esta diferencia descriptiva no mide mejora ni deterioro de un modelo: todavía no hay predicciones. No atribuir causas a comportamiento, población, muestreo o cobertura sin investigarlas. Mantener reglas y auditar ejemplos; no ajustar etiquetas para igualar porcentajes. Próximo paso guía 14 de auditoría de junio.

## Auditoría de junio generada; revisión manual pendiente

El estudiante comunicó 7.210 etiquetas coherentes internamente y nueve ejemplos distintos. Categorías: anticipada 907, mismo día 4.635, entre 1 y 28 días 1.257, gap29 cero, gap30 nueve, gap>30 76, sin eventos 206, solo cancelaciones 120, vencimiento adelantado 78, empate último día histórico 20.

907+4.635+1.257=6.799; 9+76=85; 206+120=326; 85+326=411. Los grupos de vencimiento adelantado y empate se superponen con otros. Ausencia de gap29 en esta cohorte no es un error; la frontera está cubierta por los ejemplos sintéticos, sin afirmar que haya ejemplo real.

Codex leyó docs/auditorias/piloto_2016-06-06.md, sin procesar CSV. Para la primera revisión del estudiante se proponen Caso 03 (vencimiento conocido 2016-06-17, renovación 2016-06-18) y Caso 08 (vencimiento conocido 2016-06-21; cancelación registrada 2016-06-14 con vencimiento efectivo 2016-06-15; sin renovación). No confundir fecha de cancelación con vencimiento efectivo. Observación hasta 2016-08-04. Las etiquetas guardadas no se consideran revisadas independientemente por el estudiante hasta recibir su razonamiento. Resto de ejemplos pendientes.

## Priorización del hito 2 por solicitud del estudiante

El estudiante pidió omitir por ahora los demás casos de junio para avanzar hacia la entrega. Auditoría de junio: coherencia interna reportada de 7.210 etiquetas; revisión guiada manual de casos 03 y 08 completada; siete casos restantes pendientes. Caso 03 gap 1 -> 0; Caso 08 vencimiento efectivo 2016-06-15, límite 2016-07-15, sin renovación -> 1 bajo cobertura asumida. Se aclaró que renovar exactamente en el límite también sería tardío. No presentar auditoría completa.

Esta omisión está autorizada por el usuario; se permite continuar a características y línea base con la limitación declarada, sin reabrir una solicitud de permiso. No se autoriza ejecución autónoma por Codex del procesamiento o entrenamiento. Guías 15 y 16 permiten al estudiante realizar ambas ejecuciones seguidas si todos los controles pasan y compartir las salidas juntas para revisión.

## Características y primera línea base ejecutadas

Características de junio comunicadas: 40.612 filas leídas, 17.447 futuras excluidas, 20.015 históricas utilizadas; 7.210 usuarios con seis características y clases conservadas (6.799/411). Rangos/promedios: transacciones90 1/7/2,78; transacciones30 0/4/0,98; cancelaciones90 0/2/0,02; días con transacciones 1/7/2,76; días desde última 1/85/15,70; días hasta vencimiento 0/29/15,22.

Estudiante ejecutó scripts/14_linea_base_temporal.py: entrenamiento 7.443, validación 7.210, 5.875 usuarios compartidos, clase predicha única 0. Exactitud 0,942995839112344; precisión/sensibilidad/F1 abandono 0; ROC-AUC 0,5; AP 0,05700416088765603; matriz [[6799,0],[411,0]]. Resultado real en experiments/baseline_marzo_junio.json. Codex leyó JSON y código y contrastó SHA-256 de las cohortes con el JSON: coinciden. No reejecutó entrenamiento ni procesamiento de filas. El umbral F1>=0,50 no se cumple; exactitud alta refleja mayoría de renovaciones. AP se declara con su nombre y se distingue de PR-AUC trapezoidal.
