# Revisión descriptiva de errores y grupos — prueba de diciembre

Salida ejecutada por Levis Adrian Ortiz Cano; interpretación asistida por Codex. No se modificaron modelos ni umbrales. Esta revisión de características y predicciones no sustituye una auditoría de las transacciones originales ni confirma causas de abandono. Los diez casos siguen pendientes de revisión personal del estudiante en el JSON original.

## Grupos: hallazgo principal

| Grupo | n | Abandonos | Detectados | Omitidos | Recall | F1 | Tasa de falsos positivos |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sin cancelaciones históricas | 7959 | 520 | 175 | 345 | 33,65 % | 0,3458 | 4,26 % |
| Con cancelaciones históricas | 261 | 37 | 14 | 23 | 37,84 % | 0,3500 | 12,95 % |
| Última transacción hace menos de 30 días | 7932 | 355 | 168 | 187 | 47,32 % | 0,3990 | 4,21 % |
| Última transacción hace 30 días o más | 288 | 202 | 21 | 181 | 10,40 % | 0,1680 | 31,40 % |

El último grupo representa el 3,50 % de la prueba, pero concentra el 49,18 % de los falsos negativos (181/368). Su prevalencia de abandono es 70,14 %. Es una debilidad importante del modelo en este periodo. No equivale a demostrar su causa ni autoriza añadir ahora una regla especial para ese grupo y seguir llamándolo la misma prueba final.

La tasa de falsos positivos divide FP entre usuarios que realmente renovaron. No debe confundirse con la proporción de falsas alertas entre todas las alertas (1-precisión). En el grupo de 30 días o más, 27/86 renovadores recibieron falsa alerta; 27/48 alertas fueron falsas. Son denominadores diferentes.

Estos grupos son exploratorios, definidos después de la evaluación global. No son grupos demográficos ni una prueba de equidad. Las comparaciones de cancelaciones y recencia se solapan entre sí. La recencia mide tiempo desde una transacción, no tiempo sin escuchar música ni antigüedad del cliente.

## Diez errores: evidencia e hipótesis

Seleccionados cinco FP de mayor puntaje y cinco FN de menor puntaje. No son una muestra representativa de los 714 errores. Puntajes iguales pueden corresponder a una misma hoja o a hojas con igual estimación; sin inspeccionar el recorrido no se afirma que sean la misma hoja. Los puntajes no están calibrados.

| Caso | Tipo / puntaje | Observación verificable | Hipótesis y límite |
| --- | --- | --- | --- |
| E01 | FP / 0,9801 | 2 transacciones en 2 días; ninguna en últimos 30 días; recencia34; vencimiento en14 | La escasa actividad transaccional no impidió la renovación según la etiqueta. Una periodicidad distinta podría explicarlo, pero no se comprobó. |
| E02 | FP / 0,9801 | 3 transacciones en 2 días, 1 cancelación; recencia35; vencimiento en18 | Cancelar históricamente no obliga a abandonar. Cambio de plan es una hipótesis, no un hecho confirmado. |
| E03 | FP / 0,9801 | 2 transacciones en 2 días; recencia33; vencimiento en6 | El patrón recibió alta alerta, pero la etiqueta indica renovación. Las seis variables pueden no representar bien el ciclo de pagos. |
| E04 | FP / 0,9334 | Una transacción reciente, hace8 días; vencimiento en21 | Historia escasa dentro de la ventana no equivale a cliente nuevo ni a abandono; no se conoce la antigüedad real. |
| E05 | FP / 0,9334 | Igual que E04 salvo vencimiento en22 | Un día de diferencia conserva el puntaje observado. Ambos casos muestran falsas alertas con historia reducida. |
| E06 | FN / 0,1266 | 3 transacciones en3 días; recencia18; vencimiento en12 | Actividad previa relativamente regular no garantiza renovación futura. Faltan señales para identificar este abandono. |
| E07 | FN / 0,1266 | Recencia30; vencimiento el día del corte; una transacción en ventana30d | El vencimiento inmediato no activó alerta. Recencia30 y una transacción en30d pueden coexistir si se incluye el límite inferior de la ventana. |
| E08 | FN / 0,1266 | 3 transacciones, 1 cancelación; recencia24; vencimiento en6 | La cancelación histórica no bastó para diferenciar este caso. No se atribuye causalidad sin eventos y recorrido del árbol. |
| E09 | FN / 0,1266 | 3 transacciones, sin cancelaciones; recencia25; vencimiento en4 | La ausencia de cancelaciones históricas no protege frente al abandono reconstruido. |
| E10 | FN / 0,1266 | Mismas seis variables que E07 | Usuarios diferentes pueden tener idénticas características. Eso no demuestra duplicación del usuario ni aporta información para distinguirlos. |

Los FP podrían generar revisiones o contactos innecesarios; los FN dejan oportunidades de retención sin detectar. No hay evidencia de que una intervención hubiera evitado esos abandonos. Las etiquetas son reconstruidas y dependen del supuesto de cobertura, por lo que una auditoría de eventos puede revelar errores de etiqueta además de errores predictivos.

Mejoras para trabajo futuro: examinar cobertura y etiquetas, representar ciclo/duración de pago y posibles señales de uso, revisar estabilidad temporal y calibración con desarrollo. Requerirían una evaluación futura independiente; diciembre no se reutilizaría como prueba intacta.
