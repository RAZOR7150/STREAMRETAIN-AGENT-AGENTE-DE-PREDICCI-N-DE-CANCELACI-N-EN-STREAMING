# Primera lectura de etiquetas de KKBox Churn

Fuente: salida compartida por Levis Adrian Ortiz Cano tras ejecutar `scripts/02_revisar_etiquetas.py`. Codex revisó el código y la coherencia aritmética de la salida; no volvió a procesar el dataset.

| Medida | Resultado comunicado |
| --- | ---: |
| Filas leídas | 970.960 |
| Renovación (0) | 883.630 |
| Abandono (1) | 87.330 |
| Filas mal formadas | 0 |
| Etiquetas inválidas | 0 |
| Identificadores vacíos | 0 |
| Abandono entre etiquetas reconocidas | 8,99 % |
| Usuarios únicos con etiqueta válida | 970.960 |
| Filas adicionales de usuarios repetidos | 0 |
| Usuarios con etiquetas contradictorias | 0 |
| Filas con usuario y etiqueta válidos | 970.960 |

Los dos conteos de clase suman el total. No se detectaron incidencias en los controles implementados. En una segunda ejecución, el estudiante confirmó usuarios únicos y ausencia de etiquetas contradictorias dentro de train_v2. Codex revisó que las adiciones del script implementan los conteos indicados, sin reejecutar el procesamiento. La revisión no descarta fuga temporal ni acredita que los datos estén listos para entrenar.

## Interpretación

El 8,99 % describe la proporción de etiquetas de abandono entre las filas reconocidas. No mide aciertos: todavía no se generaron predicciones de un modelo.

Como cálculo ilustrativo sobre este mismo conjunto, predecir renovación en todas las filas acertaría 883.630 de 970.960, aproximadamente 91,01 %, y no detectaría ninguno de los 87.330 abandonos. Esto demuestra por qué superar 75 % de exactitud no basta. No es un resultado experimental de validación o prueba ni una línea base entrenada y evaluada.

Siguiente ejercicio: `docs/guias/04_comparar_versiones.md`. Pendientes la relación entre las versiones de etiquetas y la definición del protocolo temporal. No deduplicar automáticamente ni combinar versiones antes de estudiar sus significados.

## Comparación completada: original y v2

Salida comunicada por el estudiante; Codex revisó el código y las sumas, sin reejecutar el procesamiento ni modificar el script.

| Medida | Resultado |
| --- | ---: |
| Usuarios original | 992.931 |
| Original: renovación / abandono | 929.460 / 63.471 |
| Compartidos | 881.701 |
| Solo original / solo v2 | 111.230 / 89.259 |
| Etiqueta igual / diferente entre compartidos | 835.711 / 45.990 |

| Etiqueta original | v2: 0 | v2: 1 |
| --- | ---: | ---: |
| 0 | 824.659 | 40.721 |
| 1 | 5.269 | 11.052 |

Las sumas cuadran: compartidos más exclusivos reconstruyen cada archivo; diagonal y fuera de diagonal suman 881.701. Aproximadamente 5,22 % de los compartidos tiene etiquetas diferentes. Abandono: 6,39 % en original y 8,99 % en v2. Las poblaciones son parcialmente distintas: ese incremento no demuestra una causa ni deterioro del servicio.

Esta tabla compara etiquetas de dos archivos, no predicciones con verdad: no es una matriz de confusión de un modelo. Cero contradicciones dentro de v2 es compatible con diferencias entre archivos. La imagen data/Tablas1.png describe v2 como abandono de marzo de 2017. Debe conservarse el contexto temporal; los conteos no explican por sí solos cada diferencia. No fusionar versiones ni resolver diferencias por mayoría.

Estado actualizado: comparación completada, sustitye el pendiente anterior. Próximo paso: definir instante de predicción, historial permitido y disponibilidad de etiquetas antes de particiones y línea base. No adoptar automáticamente original como entrenamiento y v2 como prueba: las etiquetas de entrenamiento deben ser conocidas al predecir. Compartir usuarios puede ser válido para evaluar meses futuros de suscriptores existentes, pero no equivale a evaluar usuarios nuevos. No se ha ejecutado una línea base.
