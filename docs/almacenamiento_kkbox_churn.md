# Ubicación y almacenamiento de KKBox Churn

Fecha de comprobación: 15 de noviembre de 2026.

## Ubicación actual

`D:\Users\Nelson\Desktop\RAZOR\Tareas\Sexto Semestre\Inteligencia Artificial\Proyecto Final`

El usuario trasladó el proyecto desde C al disco D (Acer). La ubicación anterior ya no existe. La sesión todavía puede conservar el directorio de trabajo anterior: usar la ruta actual explícitamente en las herramientas. Esta nota no cambia por sí sola los permisos del entorno.

## Datos presentes

La carpeta actual es `data/kkbox-churn-prediction-challenge`. Contiene nueve archivos 7z y `WSDMChurnLabeller.scala`. Las notas anteriores sobre recomendación describen la descarga previa; no corresponden a estos archivos nuevos. No se ha completado todavía una auditoría de su contenido.

| Archivo comprimido | Tamaño comprimido (GB) | Tamaño CSV declarado (GB) |
| --- | ---: | ---: |
| `members_v3.csv.7z` | 0.242 | 0.428 |
| `sample_submission_v2.csv.7z` | 0.031 | 0.043 |
| `sample_submission_zero.csv.7z` | 0.033 | 0.046 |
| `train.csv.7z` | 0.034 | 0.047 |
| `train_v2.csv.7z` | 0.033 | 0.046 |
| `transactions.csv.7z` | 0.708 | 1.729 |
| `transactions_v2.csv.7z` | 0.049 | 0.115 |
| `user_logs.csv.7z` | 7.136 | 30.514 |
| `user_logs_v2.csv.7z` | 0.686 | 1.431 |

Total comprimido: **8.951 GB**. Total CSV declarado: **34.399 GB (32.04 GiB)**. Espacio libre en D durante la revisión: **48.92 GB (45.56 GiB)**.

GB usa 1.000.000.000 bytes; GiB usa 1.073.741.824 bytes. Los tamaños se consultaron con el listado de archivos de tar incluido en Windows, sin extraer los CSV. No se realizó comprobación CRC de los comprimidos; sus tamaños declarados no garantizan integridad.

## Extracciones incompletas o vacías

Se encontraron cuatro CSV de cero bytes. No son datasets utilizables ni evidencia de extracción correcta. No se eliminaron:
- `data\kkbox-churn-prediction-challenge\data\churn_comp_refresh\sample_submission_v2.csv`
- `data\kkbox-churn-prediction-challenge\data\churn_comp_refresh\train_v2.csv`
- `data\kkbox-churn-prediction-challenge\data\churn_comp_refresh\transactions_v2.csv`
- `data\kkbox-churn-prediction-challenge\data\churn_comp_refresh\user_logs_v2.csv`

## Estrategia propuesta

1. Mantener los archivos grandes comprimidos; no iniciar una extracción masiva.
2. Auditar primero etiquetas y documentación temporal. La línea base mayoritaria no requiere cargar los logs completos.
3. Definir una muestra reproducible por usuario y una separación temporal válida. Conservar el historial necesario de esos usuarios, no una muestra arbitraria de filas de actividad.
4. Leer los CSV desde la salida del descompresor, filtrar por usuarios y fechas y guardar solo resúmenes o fragmentos necesarios. Esta estrategia reduce almacenamiento, pero sigue requiriendo tiempo de lectura y memoria para el diccionario de descompresión.
5. Guardar tablas procesadas compactas, por ejemplo Parquet, con límites explícitos de espacio temporal.
6. No mezclar versiones originales y v2 sin comprobar fechas y etiquetas. Un archivo menor no es automáticamente un reemplazo válido para el periodo de entrenamiento.

No se ejecutó extracción, limpieza, muestreo ni entrenamiento en esta revisión. El diagnóstico de espacio por sí solo no completa el hito 2.
