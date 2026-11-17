# Comprobación temporal antes de la línea base

Fecha: 2026-11-16. Diseño operativo acordado: ejecutar cada lunes con información disponible hasta el domingo anterior. No implica que existan etiquetas semanales.

## Evidencia documental revisada

- data/Tablas1.png: train_v2 contiene abandono de marzo de 2017; no incluye una fecha por etiqueta en su esquema msno,is_churn.
- data/Tablas2.png: transactions y user_logs originales se describen hasta 2017-02-28; transactions_v2 hasta 2017-03-31.
- data/Tablas3.png: user_logs_v2 hasta 2017-03-31. La descripción advierte que las fechas del ejemplo Scala fueron modificadas para facilitar su ejecución. No usar sus constantes para identificar de manera concluyente el periodo exacto de todos los archivos de etiquetas.
- WSDMChurnLabeller.scala local: ejemplo con historia de enero, corte 2017-01-31 y candidatos cuyo vencimiento cae en febrero. Usa transacciones futuras para construir la etiqueta. gap < 30 implica renovación y gap >= 30 abandono; también maneja cancelaciones que adelantan el vencimiento. No es un entrenamiento.

## Próximo ejercicio del estudiante

Auditar primero transactions_v2.csv.7z, sin guardar el CSV descomprimido. Leer secuencialmente con tar y csv como en el ejercicio anterior. Para transaction_date: validar fecha calendario con formato YYYYMMDD, contar fechas vacías/inválidas, obtener mínimo, máximo y conteos por mes. Contar también fechas inválidas de membership_expire_date. Recorrer todo el archivo para afirmar su rango real; una muestra solo permite describir esa muestra. Repetir después en transactions.csv.7z si el primer ejercicio funciona. No empezar por los logs de mayor tamaño.

No confundir fecha de transacción con fecha de vencimiento: un vencimiento posterior al corte puede ser conocido desde una transacción anterior. Filtrar por la fecha del evento disponible, no eliminar automáticamente vencimientos futuros. La fecha de evento sirve como aproximación a disponibilidad; el dataset no prueba ausencia de retrasos de registro.

## Decisión posterior

Con los rangos observados y la definición de cohortes, fijar un corte histórico y el objetivo exacto. Para evaluar predicciones semanales se necesitan etiquetas vinculadas al usuario y al objetivo temporal de cada corte, con seguimiento suficiente. No copiar sin justificación una etiqueta mensual a todos los lunes ni inferir abandono por ausencia de renovación si el seguimiento termina antes del plazo. No entrenar con etiquetas cuyo resultado aún no se conocía en el corte simulado.

Si el seguimiento no permite varios lunes, se documentará una evaluación limitada a cortes respaldados por los datos; la ejecución semanal seguirá siendo diseño operativo, sin afirmar validación semanal. La línea base y las particiones aún están pendientes. Codex revisó documentos y código Scala, pero no procesó filas del dataset.
