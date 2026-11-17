# Resultado de auditoría temporal de transactions_v2

Fecha: 2026-11-16. Fuente: salida completa comunicada por el estudiante tras ejecutar scripts/03_revisar_fechas.py. Sustituye su primer envío parcial. Codex revisó el bloque de recorrido y resumen del script y la aritmética; no reejecutó el dataset.

- Archivo: transactions_v2.csv.7z.
- Filas leídas: 1.431.009. Mal formadas: 0.
- transaction_date: 1.431.009 válidas, 0 vacías, 0 inválidas.
- membership_expire_date: 1.431.009 válidas, 0 vacías, 0 inválidas.
- Primera transacción: 2015-01-01. Última: 2017-03-31.

| Mes | Transacciones |
| --- | ---: |
| 2015-01 | 1169 |
| 2015-02 | 1504 |
| 2015-03 | 3371 |
| 2015-04 | 3579 |
| 2015-05 | 4393 |
| 2015-06 | 5179 |
| 2015-07 | 6247 |
| 2015-08 | 7095 |
| 2015-09 | 7692 |
| 2015-10 | 9222 |
| 2015-11 | 11295 |
| 2015-12 | 10620 |
| 2016-01 | 2607 |
| 2016-02 | 7042 |
| 2016-03 | 8262 |
| 2016-04 | 7967 |
| 2016-05 | 7431 |
| 2016-06 | 7140 |
| 2016-07 | 8516 |
| 2016-08 | 8134 |
| 2016-09 | 10586 |
| 2016-10 | 17743 |
| 2016-11 | 18819 |
| 2016-12 | 23787 |
| 2017-01 | 32871 |
| 2017-02 | 128916 |
| 2017-03 | 1069822 |

Los conteos suman 1.431.009. Marzo de 2017 representa aproximadamente 74,76 %. v2 contiene registros anteriores a marzo: no asumir que contiene exclusivamente un mes ni que sustituye todo el historial original. El máximo coincide con la cobertura documental. La validez de calendario no garantiza exactitud del evento, cobertura completa, ausencia de duplicados o seguimiento suficiente de cada usuario. Este archivo por sí solo no permite observar renovaciones de abril.

Siguiente ejercicio: aplicar el mismo script a transactions.csv.7z cambiando únicamente el nombre del comprimido y la ruta interna a transactions.csv. El estudiante realiza esa edición y ejecución. Conservar ambos informes separados. No combinar archivos todavía. Protocolo temporal, particiones y línea base siguen pendientes.

## Archivo original: auditoría completada

Fecha: 2026-11-16. Resultados comunicados por el estudiante; Codex comprobó la suma mensual y las dos rutas configuradas en el script, sin reejecutar las filas. El error previo de ruta interna quedó resuelto: el miembro se llama transactions.csv, sin subcarpetas.

- Archivo: transactions.csv.7z.
- Filas: 21.547.746; mal formadas: 0.
- transaction_date: 21.547.746 válidas, 0 vacías, 0 inválidas.
- membership_expire_date: 21.547.746 válidas, 0 vacías, 0 inválidas.
- Rango de transacciones: 2015-01-01 a 2017-02-28.

| Mes | Transacciones |
| --- | ---: |
| 2015-01 | 576349 |
| 2015-02 | 569421 |
| 2015-03 | 657379 |
| 2015-04 | 595444 |
| 2015-05 | 601063 |
| 2015-06 | 818903 |
| 2015-07 | 697086 |
| 2015-08 | 740477 |
| 2015-09 | 744636 |
| 2015-10 | 716146 |
| 2015-11 | 867730 |
| 2015-12 | 933513 |
| 2016-01 | 891582 |
| 2016-02 | 852021 |
| 2016-03 | 801239 |
| 2016-04 | 794364 |
| 2016-05 | 803763 |
| 2016-06 | 824188 |
| 2016-07 | 961914 |
| 2016-08 | 990767 |
| 2016-09 | 1007322 |
| 2016-10 | 1061077 |
| 2016-11 | 1123250 |
| 2016-12 | 994299 |
| 2017-01 | 1015550 |
| 2017-02 | 908263 |

La suma de los meses es 21.547.746 y coincide con el total reportado. Ambos archivos coinciden con sus límites documentados. v2 tiene un rango que alcanza marzo, pero considerablemente menos registros: no tratarlo como reemplazo completo del original. El solapamiento de meses no demuestra duplicación de filas; no se midió intersección de transacciones ni cobertura por usuario. No concatenar y deduplicar sin definir la semántica.

La revisión de estructura y calendario de ambos archivos queda completada según los informes aportados. No acredita seguimiento suficiente, exactitud semántica de fechas ni validación semanal. Siguiente paso: redactar el protocolo de evaluación antes de más procesamiento; fijar cohorte objetivo, corte de características, disponibilidad de etiquetas y tipo de partición. Una evaluación entre usuarios de una misma cohorte debe distinguirse explícitamente de una validación temporal. No se ha entrenado la línea base.

