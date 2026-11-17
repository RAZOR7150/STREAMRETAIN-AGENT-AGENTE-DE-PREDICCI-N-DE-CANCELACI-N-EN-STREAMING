# Protocolo temporal propuesto — StreamRetain

Fecha: 2026-11-16. El estudiante eligió evaluación temporal y validación cruzada temporal cuando sea viable. Este documento desarrolla la propuesta entregada; no constituye un resultado experimental.

## Unidad y objetivo

Unidad: usuario y corte de predicción. Se propone evaluar suscriptores cuyo vencimiento conocido al corte esté entre ese lunes y los siguientes 29 días (ventana de selección de 30 días). Esta ventana selecciona usuarios; no cambia la definición de abandono: el resultado depende de la renovación respecto del vencimiento, con gap < 30 como renovación y gap >= 30 como abandono según el Scala de referencia. Revisar cancelaciones y desempates antes de implementar las etiquetas.

Características inicialmente limitadas a transacciones de los 90 días anteriores al lunes. Un usuario sin historial en esa ventana no tendrá estado reconstruible en este piloto y quedará fuera; reportar esa limitación, especialmente para planes largos. No afirmar que la población representa a todos los suscriptores activos. No usar msno como predictor.

## Calendario candidato

| Corte (lunes) | Papel previsto | Seguimiento máximo requerido para vencimientos seleccionados |
| --- | --- | --- |
| 2016-03-07 | Cohorte inicial de entrenamiento | 2016-05-05 |
| 2016-06-06 | Validación 1 | 2016-08-04 |
| 2016-09-05 | Validación 2 | 2016-11-03 |
| 2016-12-05 | Prueba final reservada | 2017-02-02 |

La última fecha se calcula como corte + 29 días + 30 días. Todos estos límites caben en el rango observado del original, hasta 2017-02-28. Esto es viabilidad de calendario, no prueba de cobertura completa por usuario. Suponer cobertura de transacciones dentro del periodo publicado exige documentar sus límites; no se deduce del máximo por sí solo.

Ronda 1: entrenar con marzo y validar en junio. Ronda 2: entrenar con marzo y junio, validar en septiembre. Elegir modelo, parámetros y umbral con estas validaciones. Después reajustar con marzo, junio y septiembre y evaluar una sola vez diciembre. Todas las cohortes de entrenamiento habrían completado su seguimiento antes del siguiente corte, bajo este calendario. No usar particiones aleatorias ni TimeSeriesSplit sobre filas sin controlar cohortes y disponibilidad de etiquetas.

Los usuarios pueden repetirse en cortes diferentes porque se estudia retención futura de suscriptores conocidos. No es una estimación de generalización a usuarios nuevos. Controlar que todos los ejemplos de un mismo corte sigan el calendario asignado. Este diseño evalúa cuatro lunes separados; no demuestra desempeño estable todos los lunes del año.

## Piloto previo a validar modelos

Comenzar con una muestra determinista aproximada del 1 % de identificadores, independiente de etiquetas y actividad futura. Mantener todas sus transacciones dentro de las ventanas definidas, no el 1 % de filas. Fuente inicial: transactions.csv.7z; no combinar con v2. Primera ventana: 2015-12-08 a 2016-05-05; historia hasta 2016-03-06 y seguimiento desde 2016-03-07. Guía 06 explica la extracción por el estudiante.

La muestra todavía no es una cohorte etiquetada: incluye usuarios que luego podrían no ser elegibles. Los registros posteriores al corte se usarán exclusivamente para construir/verificar resultados, nunca como características. No usar falta de filas futuras como abandono sin haber justificado cobertura y seguimiento suficientes.

Pasos posteriores: ordenar por usuario y reglas temporales del Scala, reconstruir estado conocido al corte, seleccionar candidatos, construir etiquetas con seguimiento, revisar casos manuales y límites de 29/30 días y cancelaciones, y recién entonces línea base. Reproducir y citar las reglas del Scala; documentar las adaptaciones (90 días de historia y ventana móvil de vencimientos). Las constantes del ejemplo Scala no identifican necesariamente las cohortes oficiales. No presentar etiquetas reconstruidas como etiquetas oficiales train/train_v2.

El piloto debe confirmar tamaños de ambas clases y validez del etiquetado antes de fijar definitivamente calendario y fracción de muestreo. Ajustes por viabilidad deben registrarse antes de entrenar y no basarse en resultados de la prueba final. Para hito 2 se busca primero una línea base reproducible en la primera separación temporal; completar todas las rondas corresponde al desarrollo posterior.

## Cierre de revisión guiada y características iniciales

El estudiante explicó correctamente por qué el cambio de plan de febrero del Caso 09 no garantiza renovación del vencimiento de marzo. Se cierra la revisión guiada de nueve casos sin discrepancias identificadas con las reglas y el informe; no es validación exhaustiva ni independiente de todas las etiquetas.

Guía 10 prepara seis características, sin procesarlas por Codex: transacciones_90d, transacciones_30d, cancelaciones_90d, dias_con_transacciones_90d, dias_desde_ultima_transaccion y dias_hasta_vencimiento conocido al corte. Se excluyen msno/corte de X, y toda información de seguimiento. Los contadores describen transacciones, no escucha ni antigüedad real. Mantener misma definición en cohortes posteriores. Preparación y resultados pendientes del estudiante.
