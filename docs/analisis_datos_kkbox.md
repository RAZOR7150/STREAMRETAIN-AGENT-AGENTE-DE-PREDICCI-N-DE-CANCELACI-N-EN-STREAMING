# Análisis de los datos locales de KKBox

Fecha: 15 de noviembre de 2026. Estado: auditoría del material recibido para iniciar el hito 2.

## Conclusión principal

**El conjunto descargado es `kkbox-music-recommendation-challenge`, para recomendación musical. No es el conjunto de predicción de abandono de suscripciones elegido en el hito 1.**

La descripción local establece que `target = 1` indica que un usuario vuelve a escuchar una canción dentro de un mes del primer evento de escucha observable; `target = 0` indica que no se observó esa repetición. Ninguna de esas etiquetas significa abandono de la suscripción.

La evidencia coincide en tres lugares:

1. El nombre de la carpeta identifica el desafío de recomendación musical.
2. `data/Descripcion del conjunto de datos.png` y `data/Tablas1.png` describen explícitamente la repetición de escucha.
3. Los CSV contienen pares `msno`–`song_id`, contexto de reproducción y metadatos musicales. No contienen `is_churn`, historial de transacciones o registros diarios fechados de actividad.

**Consecuencia:** estos archivos no permiten entrenar ni evaluar honestamente la línea base de abandono de StreamRetain. No convertir `target`, `1 - target`, ausencia de escucha o una fecha aislada de vencimiento en una etiqueta de abandono. No se ha cambiado el problema aprobado en la propuesta ni se entrenaron modelos con estos datos.

## Qué se revisó y cómo consultar los resultados

- Lectura visual de las cuatro imágenes: `Descripcion del conjunto de datos.png`, `Tablas1.png`, `Tablas2.png` y `Tsblas3.png`.
- Lectura de todos los registros de los seis CSV mediante el lector CSV de Python, respetando comillas, caracteres Unicode y saltos de línea internos. No se utilizó una muestra ni conteo de líneas físicas.
- Conteos de filas, campos vacíos, categorías, rangos numéricos, fechas de miembros, claves de tablas de metadatos y cobertura de relaciones.
- Huella SHA-256 por CSV, para identificar exactamente la versión analizada.
- Los resultados detallados están en [auditoria_datos_kkbox.json](auditoria_datos_kkbox.json). `complete: true` indica que terminó el recorrido completo.
- Script reproducible: [auditar_datos_kkbox.py](../scripts/auditar_datos_kkbox.py). Ejecutar desde la raíz: `python -X utf8 scripts/auditar_datos_kkbox.py`.

Los CSV se conservaron sin cambios. Los archivos `.7z` están presentes, pero no se comprobó que su contenido coincida con los CSV descomprimidos. No se verificaron duplicados de filas completas ni repetición de pares usuario–canción; no debe interpretarse la unicidad de las claves de metadatos como ausencia global de duplicados.

## Diccionario de tablas y campos

Los nombres españoles de algunas tablas en las imágenes son traducciones: los nombres reales de los archivos y columnas son los siguientes.

### `train.csv`: ejemplos etiquetados de recomendación

| Campo | Interpretación | Precaución |
| --- | --- | --- |
| `msno` | Identificador del usuario | Clave para relacionar tablas; no identidad personal verificada |
| `song_id` | Identificador de la canción | No es identificador de suscripción |
| `source_system_tab` | Pestaña desde donde se activa la escucha | Categórica; contiene vacíos y el texto literal `null` |
| `source_screen_name` | Pantalla desde donde se activa la escucha | Categórica; contiene vacíos y la categoría `Unknown` |
| `source_type` | Tipo de acceso: álbum, lista, radio, etc. | Categórica; no es tipo de plan de suscripción |
| `target` | Reescucha dentro del mes posterior al primer evento observable | Etiqueta de recomendación, no de cancelación |

La descripción habla de ejemplos por par usuario–canción. El CSV no incorpora la fecha de ese primer evento. No suponer que el orden de las filas equivale al orden de los eventos.

### `test.csv`: casos de recomendación sin resultado público

Contiene `id`, `msno`, `song_id`, `source_system_tab`, `source_screen_name` y `source_type`. `id` identifica la fila para el envío. **No contiene `target`**, por lo que no permite calcular métricas supervisadas locales sobre sus casos sin etiquetas reales adicionales.

### `sample_submission.csv`: formato de envío

Contiene `id` y `target`. Es una plantilla para enviar predicciones; no debe tomarse como verdad de referencia ni usarse para completar las etiquetas de prueba. Su distribución observada se registra en el JSON.

### `members.csv`: metadatos de usuarios

| Campo | Interpretación | Precaución |
| --- | --- | --- |
| `msno` | Identificador del usuario | Clave única comprobada en esta tabla |
| `city` | Código de ciudad | Código categórico, no cantidad ni orden geográfico |
| `bd` | Edad según la descripción | Ceros y valores fuera de rangos plausibles; requiere tratamiento documentado |
| `gender` | Categoría de género declarada | Numerosos vacíos; no inferir valores ausentes |
| `registered_via` | Canal o método de registro | No es método de pago ni modalidad de renovación |
| `registration_init_time` | Fecha de registro en formato AAAAMMDD | No es fecha de escucha ni de predicción |
| `expiration_date` | Fecha de vencimiento en formato AAAAMMDD | No demuestra falta de renovación en los 30 días siguientes |

Esta tabla contiene un registro por usuario; no es un historial semanal de suscripciones. Antes de cualquier uso predictivo habría que conocer cuándo se capturó cada dato para descartar información futura.

### `songs.csv`: metadatos musicales

| Campo | Interpretación |
| --- | --- |
| `song_id` | Identificador de canción; clave única comprobada |
| `song_length` | Duración de la canción en milisegundos; no tiempo escuchado por una persona |
| `genre_ids` | Uno o varios códigos de género separados por `\|` |
| `artist_name` | Nombre del artista |
| `composer` | Compositor |
| `lyricist` | Letrista |
| `language` | Código de idioma; incluye `-1.0`, cuyo significado no se presupone |

### `song_extra_info.csv`: información adicional de canciones

Contiene `song_id`, `name` e `isrc`. `name` es el título. `isrc` es un código de grabación: la descripción advierte que no fue verificado oficialmente y que puede repetirse entre canciones. No usarlo como clave única ni extraer país o año como hechos confirmados sin validación.

## Relaciones y forma correcta de leer el conjunto

Las interacciones de `train` y `test` se vinculan con `members` mediante `msno`, y con `songs` y `song_extra_info` mediante `song_id`. Las claves de las tres tablas de metadatos resultaron únicas, pero no todas las canciones de interacciones tienen información asociada.

Una unión interna descartaría las interacciones sin metadatos. Si estos datos se utilizaran para recomendación, sería preferible conservarlas con una unión izquierda y tratar explícitamente los faltantes. Esto describe la estructura del conjunto recibido, no una decisión de usarlo en StreamRetain.

## Limitaciones temporales y de interpretación

- La descripción indica que la competencia dividió entrenamiento y prueba en función del tiempo. Los CSV de interacciones no exponen ese tiempo: no podemos reconstruir ventanas semanales verificables solo con sus filas.
- Registro y vencimiento son fechas de la cuenta, no marcas de tiempo de cada reproducción.
- Duración de canción no equivale a consumo real: sumar `song_length` supondría escuchar cada canción completa y no contabilizaría correctamente las repeticiones.
- No hay evidencia de cambios recientes de método de pago, ofertas de retención, resultados de campañas o renovación automática en estas tablas.
- No repetir la interpretación del diseño inicial de “horas vistas”: este conjunto contiene música y tampoco contiene horas escuchadas por usuario directamente.
- No trasladar automáticamente los permisos de uso del desafío de abandono al de recomendación. Las imágenes no incluyen sus reglas ni licencia. La disponibilidad local no acredita por sí sola autorización de redistribución.

## Cómo continuar el hito 2

Debe obtenerse el conjunto del desafío **WSDM – KKBox’s Churn Prediction Challenge**, manteniendo el objetivo de abandono ya presentado. La [convocatoria oficial WSDM](https://www.wsdm-conference.org/2018/call-for-participants.html) distingue recomendación musical y predicción de abandono como dos tareas diferentes; la ficha del segundo está en [Kaggle: datos de churn](https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data).

Al recibir el conjunto correcto, comprobar especialmente:

1. Etiquetas reales de abandono por usuario y su definición; no confundirlas con una plantilla de envío.
2. Fechas e historial de suscripciones/transacciones que permitan identificar vencimientos, renovaciones y seguimiento.
3. Actividad fechada, si se van a construir variables temporales de consumo.
4. Versión y cobertura temporal de cada archivo; no mezclar versiones suponiendo que son intercambiables.
5. Posibilidad real de formar entrenamiento, validación y prueba temporal sin etiquetas ocultas ni fuga de información.

La selección de archivos y cortes se realizará después de verificar la documentación y el esquema del conjunto correcto. No se modificó el hito 1 ya entregado. Esta auditoría aporta evidencia de una incompatibilidad de datos; **no equivale a una línea base ejecutada ni completa el hito 2**.

## Estado del repositorio

La comprobación local de Git indicó que la carpeta actual no es todavía un repositorio Git. Los informes están guardados en el espacio de trabajo, pero no se afirma que exista un commit o publicación remota.

## Resultados cuantitativos

Conteos obtenidos de la lectura completa. Fuente: `auditoria_datos_kkbox.json`.


### Inventario completo

| CSV | Filas | Columnas | Tamaño MiB |
| --- | ---: | ---: | ---: |
| `members.csv` | 34.403 | 7 | 2.39 |
| `songs.csv` | 2.296.320 | 7 | 211.55 |
| `song_extra_info.csv` | 2.295.971 | 3 | 172.62 |
| `train.csv` | 7.377.418 | 6 | 926.66 |
| `test.csv` | 2.556.790 | 6 | 331.68 |
| `sample_submission.csv` | 2.556.790 | 2 | 28.20 |

Tamaño total descomprimido: **1.754.378.940 bytes**, aproximadamente 1,63 GiB. Se conservaron también los seis archivos `.7z`. No se detectaron filas con número de campos incorrecto ni errores de lectura UTF-8. Tiempo del recorrido registrado: 103.33 segundos.

### Etiqueta de recomendación y plantilla de envío

- `target = 1`: 3.714.656 casos (50,35 %).
- `target = 0`: 3.662.762 casos (49,65 %).
- Esta distribución pertenece a reescucha, no a abandono. No usarla como tasa de cancelación del proyecto.
- `sample_submission.csv` tiene 2.556.790 valores de `target` iguales a `0.5`. No son etiquetas verdaderas.
- Tanto `test.csv` como la plantilla contienen identificadores consecutivos desde 0 hasta 2.556.789, en orden y sin desviaciones; sus identificadores de envío coinciden.

### Cobertura de usuarios y canciones

| Archivo | Usuarios distintos | Canciones distintas | Filas sin usuario en members | Filas sin canción en songs | Filas sin canción en extra_info |
| --- | ---: | ---: | ---: | ---: | ---: |
| `train.csv` | 30.755 | 359.966 | 0 | 114 | 1.455 |
| `test.csv` | 25.131 | 224.753 | 0 | 25 | 771 |

- Claves únicas verificadas: 34.403 usuarios en `members`, 2.296.320 canciones en `songs` y 2.295.971 en `song_extra_info`; cero claves repetidas dentro de cada una de esas tablas.
- Train y test comparten 21.483 usuarios y 164.880 canciones. La evaluación entre ambos no representa exclusivamente usuarios nuevos.
- Canciones distintas sin ficha en `songs`: 52 en train y 14 en test. Sin ficha en `song_extra_info`: 159 en train y 115 en test.
- Las tablas `songs` y `song_extra_info` comparten 2.295.422 claves: su cobertura no es idéntica.

### Campos vacíos

Se cuenta cadena vacía, no códigos especiales ni categorías llamadas `null` o `Unknown`.

| CSV | Campo | Vacíos | Porcentaje de filas |
| --- | --- | ---: | ---: |
| `members.csv` | `gender` | 19.902 | 57,85 % |
| `songs.csv` | `genre_ids` | 94.116 | 4,10 % |
| `songs.csv` | `composer` | 1.071.348 | 46,65 % |
| `songs.csv` | `lyricist` | 1.945.243 | 84,71 % |
| `songs.csv` | `language` | 1 | 0,00 % |
| `song_extra_info.csv` | `isrc` | 136.548 | 5,95 % |
| `train.csv` | `source_system_tab` | 18.371 | 0,25 % |
| `train.csv` | `source_screen_name` | 414.804 | 5,62 % |
| `train.csv` | `source_type` | 21.539 | 0,29 % |
| `test.csv` | `source_system_tab` | 5.096 | 0,20 % |
| `test.csv` | `source_screen_name` | 162.883 | 6,37 % |
| `test.csv` | `source_type` | 7.297 | 0,29 % |

### Rangos y anomalías

- `bd` varía de −43 a 1.051 años. Hay 19.932 ceros, 24 edades menores que 0 o mayores que 100, y 5 edades entre 1 y 9. El umbral de 100 es un criterio exploratorio para revisión, no una regla de eliminación automática. Un cero no se interpreta como edad real confirmada.
- `gender` falta en 19.902 usuarios. Los otros valores observados son `male` (7.405) y `female` (7.096). No completar el género por suposición.
- Registro: de 2004-03-26 a 2017-02-28. Vencimiento: de 1970-01-01 a 2020-10-17. Todas esas cadenas se pudieron convertir a fechas válidas, pero hay un vencimiento anterior al registro. Fecha válida sintácticamente no significa fecha coherente ni dato disponible antes de predecir.
- Duraciones de canciones: de 185 a 12.173.850 milisegundos, aproximadamente 0,185 segundos a 3,38 horas. Revisar extremos según el tipo de contenido; no eliminarlos sin explicación.
- `language = -1.0` aparece 639.467 veces. La descripción no define ese código; no se convirtió automáticamente en nulo.
- En train, `source_system_tab` contiene el texto `null` en 6.478 filas y `source_screen_name` contiene `Unknown` en 54.170. Se registran separadamente de cadenas vacías.

### Interpretación para StreamRetain

El principal impedimento no es el volumen ni los faltantes: es que la etiqueta corresponde a otra tarea y no existe seguimiento de renovación suficiente en estos archivos. La limpieza de edades o de categorías no resuelve esa incompatibilidad.
