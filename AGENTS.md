# Contexto del proyecto final de Inteligencia Artificial

## Regla prioritaria de colaboración: aprendizaje guiado

Leer y aplicar `guidelines.md` antes de cualquier tarea de implementación. Según la aclaración del usuario, Codex se encarga directamente del soporte técnico: entorno, herramientas, rutas, espacio y metadatos de comprimidos, además de documentación. El estudiante escribe y ejecuta el procesamiento de las filas del dataset y el entrenamiento del modelo, con guías, ejemplos comentados y revisión de Codex. Esto incluye lectura de registros, preparación, particiones, línea base y evaluación; no ejecutar esas tareas autónomamente. No pedir al estudiante que repita la inspección técnica. Una solicitud puntual de ayuda solo autoriza ese alcance. `docs/guias/01_entorno_y_comprimidos.md` se conserva como referencia, no como ejercicio pendiente. Estado técnico comprobado en `docs/estado_entorno.md`. Primera guía de procesamiento para que el estudiante escriba y ejecute: `docs/guias/02_lectura_etiquetas.md` (conteo de etiquetas de train_v2 desde el comprimido). El estudiante ya ejecutó el primer conteo: comunicó 970.960 filas, 883.630 etiquetas 0 y 87.330 etiquetas 1, sin incidencias en los tres controles implementados. Codex revisó el código y la aritmética, sin reejecutar el procesamiento. Evidencia reportada en `docs/resultado_lectura_etiquetas.md`. El estudiante completó también unicidad: 970.960 usuarios únicos, cero filas adicionales y cero usuarios con etiquetas contradictorias. Código revisado por Codex sin reejecución. Siguiente guía: `docs/guias/04_comparar_versiones.md`; comparación de versiones y protocolo temporal pendientes. No crear ni modificar el script entregable por él.

## Ubicación actual y actualización de datos

El proyecto fue trasladado a `D:\Users\Nelson\Desktop\RAZOR\Tareas\Sexto Semestre\Inteligencia Artificial\Proyecto Final` (disco Acer). Usar esta ruta como directorio de trabajo; la ruta anterior de C ya no existe. Consultar `docs/almacenamiento_kkbox_churn.md` y `docs/inventario_almacenamiento_kkbox_churn.json`. Ahora hay nueve comprimidos del desafío correcto en `data/kkbox-churn-prediction-challenge`, no los CSV de recomendación de la auditoría previa. Los CSV internos suman aproximadamente 34,4 GB según sus metadatos, no 1 TB. Hay cuatro CSV de cero bytes. No se ha auditado el contenido nuevo ni entrenado la línea base. Conservar comprimidos y priorizar lectura progresiva y un subconjunto reproducible. No iniciar extracción masiva ni tratar los CSV vacíos como válidos. Las notas anteriores de recomendación son históricas.

## Fuente y alcance

Este archivo resume las 11 imágenes PNG de `context/`, leídas el 15 de noviembre de 2026. Las imágenes son la fuente original de las instrucciones del profesor. Consultarlas si se necesita comprobar una redacción o resolver una duda; no es necesario volver a analizarlas para cada tarea.

El usuario confirmó que continuará **StreamRetain-Agent**, eligió **KKBox** como fuente y ratificó la modalidad individual (Levis Adrian Ortiz Cano). El hito 1 actualizado está en `Entregables/streamretain_hito1.pdf`, con fuente editable en `docs/streamretain_hito1.md`. Se adaptó la definición de abandono a no renovar dentro de los 30 días posteriores al vencimiento, conforme a KKBox, explicitando el cambio respecto de los 28 días iniciales. El ciclo semanal se conserva como diseño; la evaluación depende de cortes históricos válidos y seguimiento completo. La selección de la fuente no equivale a verificar descarga, esquema o aceptación de reglas. No se ha solicitado implementar el agente. El estado actual prevalece sobre las notas históricas siguientes. Las imágenes no incluyen fechas concretas de entrega.

## Estado del hito 2 y datos locales

El usuario informó que ya entregó el hito 1 y solicitó auditar los datos descargados para el hito 2. Consultar **`docs/analisis_datos_kkbox.md`** y **`docs/auditoria_datos_kkbox.json`** antes de trabajar con `data/`. Se revisaron todos los registros de los seis CSV y las cuatro imágenes descriptivas. **Los archivos locales corresponden a `kkbox-music-recommendation-challenge`, no al desafío de abandono elegido en la propuesta.** `target` indica reescucha de una canción dentro de un mes; nunca usarlo, ni su complemento, como etiqueta de churn. `test.csv` no tiene etiquetas y `sample_submission.csv` solo contiene valores de ejemplo `0.5`. No hay fechas de escucha ni historial de renovaciones suficiente. Debe obtenerse el conjunto correcto de Churn Prediction antes de entrenar la línea base de StreamRetain. No alterar el hito 1 entregado ni cambiar el objetivo a recomendación por esta descarga. El script de auditoría es `scripts/auditar_datos_kkbox.py`; los CSV originales permanecen intactos. Todavía no se ejecutó una línea base y la carpeta no es un repositorio Git según la comprobación realizada. La entrega del hito 1 no acredita por sí sola aprobación docente.

## Guía de conceptos para el estudiante

Conservar también las preguntas de comprensión y sus respuestas corregidas en `Conceptos clave/Preguntas de repaso.md`, por solicitud del usuario. Ampliar ese archivo al revisar nuevas preguntas, con ejemplos, matices y una respuesta breve para estudio. Distinguir resultados comunicados por el estudiante, ejemplos hipotéticos y verificaciones realizadas; no atribuir ejecución a guías pendientes.

Por solicitud del usuario, conservar las definiciones de términos importantes o potencialmente confusos en `Conceptos clave/Glosario.md`. Al introducir nuevos conceptos relevantes, ampliar esta guía con explicación sencilla, ejemplo aplicado a StreamRetain y diferencias frente a términos similares. Marcar los ejemplos numéricos como hipotéticos y distinguir metas propuestas de resultados reales. Este glosario es material de estudio; no es un entregable académico ni implica adoptar todas las técnicas que describe.

## Continuidad de StreamRetain-Agent

Los puntos sobre 28 días y datasets candidatos describen el diseño inicial; para decisiones actuales prevalece «Fuente y alcance». El hito 1 adopta el estilo visual de la plantilla (Times New Roman, encabezado institucional centrado, apartados numerados azules), condensado en una página. La modalidad individual ya fue ratificada por el usuario: no reiterar solicitudes de confirmación ni afirmar aprobación docente inexistente.

- Consultar `docs/analisis_contexto_streamretain.md` para el contraste del diseño, el JSON, el material del curso y los requisitos finales.
- Fuentes principales: `context/docs/Diseño Agente inteligente 1er Corte.pdf` (5 páginas) y `context/StreamRetain_Agent_Contexto_Codex.json`. El JSON es un contexto estructurado, no una transcripción íntegra de la conversación anterior.
- Docente confirmado en la entrega: Edwin Alexander Puertas Del Castillo. Autor del diseño inicial: Levis Adrian Ortiz Cano. No inferir la composición del equipo final de esta portada ni de otros trabajos.
- Objetivo heredado: evaluar semanalmente suscriptores activos y estimar la cancelación durante los siguientes 28 días para priorizar retención.
- Meta heredada: exactitud global >= 75 %, calculada como aciertos / total; no confundir con precisión de la clase positiva. Evaluar cohortes solo cuando el resultado futuro sea conocido. Complementar con métricas por clase y comparación con una línea base; las metas adicionales no están fijadas.
- Agente de aprendizaje con memoria: percepción → historial real → predicción → decisión → acción/recomendación → registro → evaluación y eventual reentrenamiento validado. El modelo predictivo no es un actuador.
- No hay evidencia aportada de implementación funcional, entrenamiento, dataset definitivo o integración real con marketing. Ofertas, umbral de intervención, SHAP, XGBoost e infraestructura no son decisiones aprobadas.
- Datos candidatos en las fuentes: Netflix Customer Churn y KKBox. Sus esquemas, licencias, disponibilidad y capacidad para definir cancelación a 28 días no se han auditado. No fabricar evolución semanal a partir de un archivo estático ni atributos ausentes.
- Documentación académica formal, impersonal o en tercera persona; explicar tecnicismos de forma integrada. Ser objetivo y señalar inconsistencias. La plantilla del primer corte aplica a ese documento; el informe final sigue la estructura IEEE exigida en las imágenes.
- El material de arquitectura de software y el parcial del robot aspirador son contextos distintos; no importar sus entregables como obligaciones de StreamRetain.

## Propósito y condiciones generales

- Resolver un problema real con una solución de IA funcional, evaluada con evidencia y defendida oralmente. Se evalúa la calidad del razonamiento, la elección de técnica, la medición y las limitaciones, no la herramienta usada.
- Equipos de 2 o 3 estudiantes; cada integrante debe poder explicar cualquier parte del proyecto.
- Dominio libre. Se valoran problemas locales de Cartagena, el Caribe y Colombia.
- Al menos una técnica del curso debe ser el núcleo de la solución. Un chatbot que solo llama a una API, sin diseño, datos propios ni evaluación, no cumple.
- Datos con fuente identificada, licencia o autorización. No usar datos personales identificables salvo anonimización justificada.
- Python como lenguaje base. Notebooks para exploración; las condiciones generales exigen que la solución final se ejecute desde scripts o una app.
- Debe correr con recursos gratuitos: equipo personal, Colab o Kaggle. Si se usan APIs pagas, reportar el costo.
- Se permite partir de código o modelos existentes con cita y aporte propio identificable de diseño, experimentación o adaptación.
- Se puede evolucionar el agente de una actividad anterior si aumenta claramente el alcance mediante nuevos datos, técnica o evaluación.
- Implementación reproducible: código versionado, dependencias declaradas y semillas fijas.

## Nueve componentes obligatorios

Si falta un componente, el criterio correspondiente de la rúbrica no puede superar «Insuficiente».

1. **Problema y usuario real:** quién lo tiene, cómo lo resuelve hoy, qué cambiaría y al menos una fuente que respalde su relevancia (dato, noticia, entrevista o artículo).
2. **Formulación como problema de IA:** PEAS del agente o sistema, tipo de entorno y, según la ruta, espacio de estados, variables del modelo o tarea de aprendizaje.
3. **Datos o conocimiento:** origen, tamaño, licencia, preprocesamiento y particiones de entrenamiento, validación y prueba. En rutas A y B: base de conocimiento, instancias de prueba o simulador.
4. **Justificación de la técnica:** por qué esa técnica frente a otra, con referencia al libro guía o a un artículo científico.
5. **Línea base y comparación:** cumplir la línea base y la comparación mínima de la ruta elegida.
6. **Evaluación previa a experimentar:** declarar métricas y umbral de éxito en la propuesta. Cualquier cambio posterior requiere justificación escrita.
7. **Análisis de errores:** al menos 10 casos de fallo, clasificados por tipo y con hipótesis de causa.
8. **IA responsable:** sesgos, impacto en grupos afectados, privacidad, uso indebido, limitaciones y mitigaciones concretas.
9. **Prototipo funcional:** demostración ejecutable de principio a fin. Esta imagen admite app web (Streamlit, Gradio o similar), API, CLI o notebook.

**Diferencia entre fuentes:** la imagen de componentes admite notebook como prototipo, pero las condiciones generales exigen scripts o app para la solución final. Para satisfacer ambas, prever scripts o app y reservar notebooks para exploración, salvo aclaración del docente.

## Rutas admitidas

Elegir una ruta principal. Se permiten proyectos híbridos si se declara cuál se evaluará con rigor. Todas las rutas requieren una línea base sencilla.

| Ruta | Núcleo de IA y capítulos de Russell y Norvig | Línea base mínima | Comparación mínima | Métricas típicas |
| --- | --- | --- | --- | --- |
| A. Agente que busca o planifica | Búsqueda no informada e informada, CSP, planificación (3–6, 11) | Búsqueda no informada o heurística voraz | 2 algoritmos o 2 heurísticas | Costo de solución, nodos expandidos, tiempo, optimalidad |
| B. Razonamiento con conocimiento o incertidumbre | Lógica, representación del conocimiento, redes bayesianas, modelos de Markov (7–10, 12–14) | Reglas simples o frecuencias | Modelo con y sin razonamiento, o 2 estructuras | Exactitud de inferencia, calibración, casos explicados |
| C. Aprendizaje automático | Aprendizaje supervisado o no supervisado, CRISP-ML(Q) (19–21) | Clasificador mayoritario, regresión lineal o logística | Al menos 2 modelos y ajuste de hiperparámetros | F1, AUC, RMSE, matriz de confusión, métricas por subgrupo |
| D. Lenguaje natural y LLM | PLN, embeddings, Transformers, RAG (23–24) | n-gramas, TF-IDF o LLM sin recuperación | Con vs. sin RAG, o 2 modelos / 2 estrategias de prompting | Exactitud sobre conjunto de prueba propio, fidelidad a la fuente, tasa de alucinación |
| E. Agente con herramientas (agentic AI) | Agente LLM con herramientas, memoria o planificación (2, 11, 18) | Prompt único sin herramientas | Agente vs. línea base en al menos 20 tareas de prueba | Éxito por tarea, pasos, costo, errores de herramienta |
| F. Visión por computador | CNN, transferencia de aprendizaje, modelos visión-lenguaje (25) | Modelo preentrenado sin ajuste | Ajuste fino vs. sin ajuste, o 2 arquitecturas | Exactitud, mAP o IoU, errores por clase |

## Ejemplos ilustrativos del profesor

No son temas obligatorios ni seleccionados por el equipo.

| Dominio | Proyecto y ruta | Comparación ilustrativa |
| --- | --- | --- |
| Logística urbana | Recolección de residuos en un barrio de Cartagena (A) | A* con 2 heurísticas vs. búsqueda de costo uniforme |
| Educación | Horarios de salones como CSP (A) | Backtracking simple vs. MRV + forward checking |
| Salud | Apoyo al triaje con red bayesiana (B) | Red bayesiana vs. reglas fijas, con casos de literatura |
| Agro | Rendimiento de cultivos con datos climáticos abiertos (C) | Regresión lineal vs. gradient boosting, con error por región |
| Energía | Consumos anómalos en medidores (C) | Umbral estadístico vs. Isolation Forest |
| Universidad | Asistente sobre reglamento estudiantil (D) | LLM sin recuperación vs. RAG en 50 preguntas con respuesta conocida |
| Turismo | Opiniones de visitantes en español (D) | TF-IDF + regresión logística vs. Transformer ajustado |
| Productividad | Agente que agenda tutorías con calendario y correo simulados (E) | Prompt único vs. agente con herramientas en 20 tareas |
| Medio ambiente | Residuos plásticos en playas a partir de fotos (F) | Modelo preentrenado sin ajuste vs. ajuste fino |

## Hitos y entregables

Por instrucción del usuario, todos los archivos destinados a entrega de los hitos (PDF, presentaciones y otros formatos finales) deben guardarse en `Entregables/`, en la raíz del proyecto. El PDF actual del hito 1 está en `Entregables/streamretain_hito1.pdf`. La versión anterior se conserva en `docs/historial/streamretain_hito1_borrador.pdf`. Las fuentes editables y notas de trabajo pueden permanecer en `docs/`. Aplicar esta ubicación también a los hitos 2, 3 y 4.

Cada hito habilita el siguiente. Sin propuesta aprobada no hay proyecto.

1. **Propuesta (1 página):** problema y usuario, ruta, fuente de datos con licencia, línea base prevista, métricas y umbral de éxito antes de experimentar. Para avanzar: aprobación docente del alcance y viabilidad de datos.
2. **Avance:** datos o conocimiento listos, línea base ejecutándose y primer resultado en el repositorio. Una página de avance y primeras entradas de bitácora IA. Para avanzar: línea base reproducible siguiendo el README.
3. **Entrega final:** informe IEEE, repositorio completo, prototipo funcional y bitácora IA. Criterios 1–8: 85 puntos. Para avanzar: repositorio ejecutable y comparación mínima de la ruta completa.
4. **Sustentación (20 minutos):** presentación, demostración con caso del docente y preguntas individuales. Criterio 9: 15 puntos individuales.

Los hitos 1 y 2 no suman puntos, pero son obligatorios: cada uno no entregado a tiempo descuenta 5 puntos de la nota final.

Se sube un archivo independiente por hito: `nombre_proyecto_hito1.pdf`, `nombre_proyecto_hito2.pdf`, `nombre_proyecto_hito3.pdf` y `nombre_proyecto_hito4.pdf`. La fuente añade «presentación en ppt» junto al último archivo; conservar esa indicación y aclarar el formato si resulta necesario al entregar.

## Informe técnico

Artículo IEEE de doble columna, de 6 a 8 páginas sin contar referencias ni anexos, en español o inglés. Debe contener:

- Resumen de máximo 200 palabras y palabras clave.
- Introducción: problema, usuario, relevancia y pregunta del proyecto.
- Trabajo relacionado: mínimo 5 referencias, al menos 3 artículos científicos (IEEE, ACM, Springer, Elsevier, ACL, arXiv revisado) y el libro guía.
- Formulación: PEAS, tipo de entorno y definición formal de la tarea.
- Datos o conocimiento: origen, licencia, estadísticas descriptivas y preprocesamiento.
- Método: línea base, técnica propuesta, alternativas comparadas y diagrama de arquitectura o secuencia.
- Experimentos y resultados: configuración, métricas, tabla comparativa, gráficos y análisis de errores.
- IA responsable y limitaciones.
- Conclusiones y trabajo futuro, con respuesta explícita a la pregunta de la introducción.
- Declaraciones de contribución de cada integrante y de uso de IA generativa.
- Referencias en formato IEEE.
- Reflexión de media página sobre uso de IA, con al menos un caso de propuesta incorrecta o inadecuada de la IA y cómo se detectó.

## Repositorio mínimo

GitHub o GitLab, público o compartido con el docente:

- `README.md`: descripción, instalación y ejecución en menos de 5 comandos.
- `requirements.txt` o `environment.yml`: versiones fijadas.
- `data/`: datos o script de descarga; nunca datos personales sin anonimizar.
- `src/`: código de la solución.
- `notebooks/`: exploración.
- `experiments/`: resultados que respaldan cada tabla del informe y semilla usada.
- `docs/bitacora_ia.md`: bitácora humano–IA.
- Historial de commits distribuido en el tiempo y entre integrantes. Un único commit la víspera es señal de alerta.

## Uso de IA y bitácora

Se permite y se espera usar asistentes de IA si se declara y el equipo puede explicar y defender todo lo entregado. No declararlo o no poder explicar código o texto durante la sustentación se trata como falta de integridad académica.

Registrar cada uso relevante en `docs/bitacora_ia.md` con las columnas: **Fecha | Integrante | Herramienta | Para qué se usó | Qué se aceptó, modificó o descartó | Cómo se verificó**.

En futuras tareas, conservar información verificable para la bitácora. No inventar integrantes, verificaciones, experimentos, resultados ni casos de errores de IA.

## Sustentación oral

- 20 minutos por equipo, nota individual; el docente decide quién responde.
- Presentación: 8 minutos para problema, formulación, método, resultado principal y una limitación.
- Demostración en vivo: 4 minutos con un caso propuesto por el docente, no preparado por el equipo.
- Preguntas: 8 minutos, al menos una conceptual por integrante y una modificación pequeña en vivo (hiperparámetro, regla o prompt), prediciendo su efecto antes de ejecutar.
- Quien no explique su contribución declarada recibe una nota individual inferior a la del equipo en sustentación.

## Rúbrica: 100 puntos

Niveles: Excelente (100 % del puntaje), Satisfactorio (75 %), Básico (50 %) e Insuficiente (0–25 %). Criterios 1–8 grupales; criterio 9 individual.

| Criterio | Puntos | Evidencia para Excelente |
| --- | --- | --- |
| 1. Problema y formulación | 10 | Problema real con evidencia; PEAS y tarea formal completos y coherentes |
| 2. Datos o conocimiento | 10 | Fuente, licencia, preprocesamiento y partición justificados; sin fuga de datos |
| 3. Fundamento y justificación técnica | 10 | Elección argumentada con libro guía y artículos; alternativas discutidas |
| 4. Implementación y reproducibilidad | 15 | Ejecución siguiendo README; resultados replicables; commits distribuidos |
| 5. Experimentación y evaluación | 15 | Línea base y comparación mínima de ruta; métricas declaradas; varias corridas o validación cruzada |
| 6. Análisis crítico de resultados | 10 | Al menos 10 errores clasificados con hipótesis de causa; conclusiones limitadas a la evidencia |
| 7. IA responsable | 10 | Riesgos específicos, medidos cuando sea posible (p. ej., métricas por subgrupo), con mitigaciones |
| 8. Comunicación escrita y bitácora IA | 5 | Informe IEEE claro; bitácora completa con verificación y reflexión |
| 9. Sustentación individual | 15 | Precisión conceptual y predicción del efecto de la modificación en vivo |

## Imágenes consultadas

- `context/Proposito y resultados de aprendizaje.png`
- `context/Condiciones generales.png`
- `context/Componentes Obligatorios.png`
- `context/Rutas de proyecto admitidas.png`
- `context/Ejemplo de Proyectos.png`
- `context/Fases hitos y Entregables.png`
- `context/Hitos detallados.png`
- `context/Informe Tecnico y Repositorio.png`
- `context/Uso de IA generativa y bitacora humano-IA.png`
- `context/Sustentacion Oral.png`
- `context/Rubrica de evaluacion.png`

## Actualización: comparación de versiones completada

El estudiante comunicó 992.931 usuarios en original, 881.701 compartidos, 111.230 exclusivos de original y 89.259 de v2. Entre compartidos, 835.711 etiquetas coinciden y 45.990 difieren. Codex revisó código y sumas sin ejecutar el procesamiento. Evidencia en docs/resultado_lectura_etiquetas.md y preguntas en Conceptos clave/Preguntas de repaso.md. Esta actualización sustituye el pendiente de comparación de la cabecera. data/Tablas1.png identifica v2 como abandono de marzo de 2017. Próximo paso: definir corte, historial permitido y disponibilidad de etiquetas antes de particiones y línea base. No asignar automáticamente original a entrenamiento y v2 a prueba sin comprobar cuándo se conocen las etiquetas. Procesamiento y entrenamiento siguen a cargo del estudiante.

## Próximo ejercicio preparado: auditoría de fechas

Guía `docs/guias/05_revisar_fechas.md`, solicitada el 2026-11-16. El estudiante debe crear y ejecutar `scripts/03_revisar_fechas.py` siguiendo sus bloques. Analiza primero transactions_v2 desde el comprimido: estructura, validez de fechas de transacción y vencimiento, rango de transacciones y conteos mensuales. Codex solo preparó documentación; no creó ni ejecutó el script. Resultados pendientes. Criterios temporales en `docs/comprobacion_temporal.md`; diseño operativo de lunes separado de validación histórica.

## Guía 05 ejecutada por el estudiante

Salida completa recibida el 2026-11-16: transactions_v2 tiene 1.431.009 filas; cero mal formadas y cero fechas vacías/inválidas en ambas columnas; transaction_date entre 2015-01-01 y 2017-03-31. Conteos y límites en docs/resultado_fechas_transacciones.md. Respuestas corregidas añadidas a preguntas de repaso. Codex comprobó aritmética y leyó el bloque de código, sin ejecutar filas. Siguiente paso: el estudiante repite el control en transactions.csv.7z, ruta interna transactions.csv. No fusionar archivos ni asumir historial completo por el rango.

## Auditoría temporal de ambos archivos completada

El estudiante reportó para transactions.csv.7z 21.547.746 filas, sin incidencias de estructura/calendario, entre 2015-01-01 y 2017-02-28. Suma mensual verificada por Codex, sin reejecución. Detalle de ambos archivos en docs/resultado_fechas_transacciones.md. El error de ruta interna fue corregido por el estudiante. Siguiente paso: definir protocolo de evaluación, cohorte, corte, disponibilidad de etiquetas y partición; no confundir una partición de usuarios de la misma cohorte con validación temporal. No asumir duplicados entre archivos por compartir meses; no fusionarlos automáticamente.

## Evaluación temporal elegida y piloto preparado

El usuario eligió evaluación temporal y validación cruzada temporal si hay suficientes cohortes. docs/protocolo_evaluacion_temporal.md propone cortes lunes 2016-03-07, 2016-06-06, 2016-09-05 y 2016-12-05; dos rondas de validación y diciembre reservado para prueba. Viabilidad de calendario, no etiquetas verificadas. Se requieren etiquetas reconstruidas con reglas Scala, documentando adaptaciones. Guía 06 docs/guias/06_piloto_temporal.md para que el estudiante cree scripts/04_preparar_piloto_temporal.py: muestra determinista de aproximadamente 1 % de usuarios del original, ventana 2015-12-08 a 2016-05-05, archivo local reducido data/derived/piloto_2016-03-07.csv. No ejecutado por Codex. Revisar salida antes de ordenar, seleccionar candidatos o etiquetar. Usuarios sin historia en 90 días quedan fuera del futuro piloto; no afirmar población completa ni validación de todos los lunes. Mantener test final sin utilizar para ajustes.

## Piloto extraído por el estudiante

Salida de scripts/04_piloto_temporal.py recibida: 21.547.746 filas recorridas, 25.054 históricas y 15.449 de seguimiento guardadas (40.503 total, 3,14 MiB). Evidencia en docs/resultado_piloto_temporal.md. La guía 06 queda ejecutada; cohortes y etiquetas aún pendientes. Próximo procesamiento del estudiante sobre data/derived/piloto_2016-03-07.csv: ordenar/agrupar, reconstruir estado al corte y elegibilidad, verificar seguimiento y etiquetar. No reutilizar el archivo previo no validado. Se corrigió la confusión historia=entrenamiento y seguimiento=validación en Conceptos clave/Preguntas de repaso.md: historia genera X y seguimiento genera y dentro de la misma cohorte. No entrenar sin revisar el etiquetado.

## Guía 07 preparada

Próximo ejercicio: docs/guias/07_candidatos_temporales.md. El estudiante creará scripts/05_candidatos_temporales.py; agrupa historia del piloto, reproduce orden calculateLastday de Scala y selecciona vencimientos entre 2016-03-07 y 2016-04-05. Salida propuesta data/derived/candidatos_2016-03-07.csv, sin etiquetas. No ejecutado por Codex. Seguimiento solo contado, nunca usado para seleccionar elegibilidad. Respetar limitación de historia de 90 días y convenciones de desempate. Revisar conteos antes del etiquetado.

## Guía 07 ejecutada por el estudiante

Resultado comunicado: 10.447 usuarios históricos; 2.120 con vencimiento anterior, 884 posterior y 7.443 candidatos. 8.385 usuarios con seguimiento, 1.100 solo seguimiento y 383 históricos con varios eventos el último día. Sumatorias revisadas por Codex, sin procesar CSV. Evidencia en docs/resultado_piloto_temporal.md; respuestas corregidas en preguntas de repaso. Candidatos reportados en data/derived/candidatos_2016-03-07.csv, aún sin etiqueta. Siguiente paso: guía de etiquetado y comprobaciones de reglas/seguimiento antes de entrenar.

## Guía 08 preparada: etiquetas reconstruidas

Guía docs/guias/08_etiquetar_piloto.md para que el estudiante cree scripts/06_etiquetar_piloto.py. Reutiliza solo funciones leer_fecha/comparar_eventos de guía 07, no importa sus scripts. Nueve casos sintéticos antes de procesar. Reglas Scala: primera renovación desde corte, cancelaciones previas adelantan vencimiento, gap < 30 -> 0 y >=30 ->1; sin renovación exige seguimiento suficiente. Cobertura del historial publicado es supuesto explícito, no comprobación de completitud por usuario. Etiquetas reconstruidas, no oficiales; auditoría futura no puede usarse como features. Salida propuesta data/derived/etiquetas_piloto_2016-03-07.csv. Ejecución y resultados pendientes del estudiante.

## Guía 08 ejecutada y gap explicado

El estudiante reportó 7.443 etiquetas: 6.348 renovaciones, 1.095 abandonos (34 tardíos + 1.061 sin renovación), cero sin etiqueta; 895 sin eventos y 103 vencimientos adelantados. Tasa 14,71 %, no métrica de modelo. Resultados en docs/resultado_piloto_temporal.md. Gap definido con ejemplos en Glosario.md y guía 08, respuestas corregidas en Preguntas de repaso.md. Supuesto de cobertura sigue vigente. Próximo paso: auditoría de ejemplos reales del etiquetado antes de características y línea base. Sin procesamiento adicional por Codex.

## Guía 09 preparada: auditoría de casos reales

docs/guias/09_auditar_etiquetas.md indica al estudiante crear scripts/07_auditar_etiquetas.py y generar docs/auditorias/piloto_2016-03-07.md. Coherencia interna de etiquetas y evidencia de historia/seguimiento para hasta diez casos distintos, alias sin msno. Categorías pueden solaparse o faltar. No ejecutado por Codex; veredictos manuales pendientes. Revisar primero tres casos con el estudiante y completar restantes antes de entrenar. Esto no cumple el requisito de diez fallos de un modelo: aún no hay modelo. Tras auditoría, preparar características históricas y cohorte posterior para línea base temporal.

## Guía 09 ejecutada; revisión manual en curso

Estudiante reportó coherencia interna de 7.443 etiquetas y nueve casos. Codex leyó casos 01–03 del Markdown y corrigió confusión entre episodio de marzo y pagos posteriores de mayo: etiquetas 0 con gaps -1, 0 y 4. Revisiones en resultado_piloto_temporal.md y Preguntas de repaso.md. No marcar auditoría completada ni veredictos como independientes del estudiante; falta afianzar comprensión y revisar restantes casos, en particular límites y cancelaciones. Sin procesamiento de CSV por Codex.

## Nueve casos comentados; aclaración final pendiente

Revisión guiada 06–09: todos coinciden con etiqueta 1 bajo cobertura asumida; detalle en resultado_piloto_temporal.md y Preguntas de repaso.md. El usuario confundió cambio de plan anterior al corte (Caso 09, febrero) con renovación posterior del vencimiento de marzo. Confirmar que distingue ambos antes de características. No afirmar validación exhaustiva ni auditoría independiente; no se modificaron etiquetas. Próximo desarrollo: características históricas, luego cohorte posterior y línea base temporal.

## Auditoría guiada cerrada; guía 10 preparada

El usuario explicó correctamente el Caso 09, distinguiendo cambio de plan histórico y renovación posterior. Nueve casos revisados con guía, sin discrepancias identificadas bajo las reglas y supuesto de cobertura. Próximo ejercicio docs/guias/10_caracteristicas_historicas.md: el estudiante creará scripts/08_caracteristicas_historicas.py para generar data/derived/cohorte_2016-03-07.csv con seis características de 90/30 días y etiqueta enlazada por identificador/corte. No creado ni ejecutado por Codex. No usar gap, motivo, renovación futura ni vencimiento modificado después del corte como características. Tras revisar salida, preparar junio para línea base temporal, sin sustituirla por partición aleatoria de marzo.

## Guía 10 ejecutada por el estudiante

Cohorte marzo reportada: 7.443 filas, seis características, 6.348 ceros y 1.095 unos; 19.656 transacciones históricas utilizadas y 15.449 futuras excluidas. Tabla en data/derived/cohorte_2016-03-07.csv. Script real se llama scripts/08_caracterustucas_historicas.py; no renombrado. Detalles en resultado_piloto_temporal.md y preguntas de repaso. Próximo paso: preparar junio 2016-06-06 con mismas reglas y muestra, luego línea base entrenada en marzo y validada en junio. Sin modelo ejecutado hasta ahora. No hacer partición aleatoria como reemplazo temporal.

## Guía 11 preparada: inicio de junio

docs/guias/11_cohorte_junio.md pide al estudiante copiar scripts/04_piloto_temporal.py a scripts/09_piloto_junio.py, cambiando corte a 2016-06-06 y salida a piloto_2016-06-06.csv. Fechas verificadas: historia desde 2016-03-08, 30 días desde 2016-05-07, candidatos hasta 2016-07-05, seguimiento hasta 2016-08-04. Conservar regla SHA-256 y fuente original. Solo guía preparada por Codex, extracción pendiente. Revisar resumen antes de adaptar candidatos/etiquetas/auditoría/características, cuyos scripts aún contienen rutas y números de marzo. No copiar números de marzo a junio ni exigir mismos candidatos. Junio será validación inicial, diciembre sigue prueba final.

## Junio extraído; guía 12 preparada

Estudiante comunicó 40.612 transacciones de junio: 23.165 historia, 17.447 seguimiento, 3,15 MiB; resultados en docs/resultado_cohorte_junio.md. Conteos mensuales cuadran. Respuestas corregidas: no forzar usuarios nuevos ni tamaños diferentes; marzo es cohorte de entrenamiento, no línea base; disponibilidad de etiquetas determina validez temporal. Próximo paso docs/guias/12_candidatos_junio.md: estudiante copia 05_candidatos_temporales.py a 10_candidatos_junio.py y cambia entrada/salida/corte a junio. No ejecutado por Codex. Revisar número real de candidatos antes de adaptar etiquetador.

## Candidatos de junio listos; guía 13 preparada

Estudiante reportó 7.210 candidatos de 9.038 históricos (1.318 anteriores, 510 posteriores); resultados en docs/resultado_cohorte_junio.md. Aclaraciones de elegibilidad y evaluación de suscriptores conocidos en preguntas de repaso. Próximo: docs/guias/13_etiquetas_junio.md, copiar 06_etiquetar_piloto.py a 11_etiquetar_junio.py; adaptar tres rutas, corte y control a 40.612 filas/7.210 candidatos. Mantener las fechas de los nueve casos sintéticos. No creado ni ejecutado por Codex; revisar salida antes de auditoría y características de junio.

## Junio etiquetado; auditoría pendiente

Resultados del estudiante: 7.210 etiquetas, 6.799 ceros, 411 unos (85 tardías + 326 sin renovación), cero desconocidas; 206 sin eventos, 78 vencimientos adelantados; 5,70 %. Evidencia en resultado_cohorte_junio.md. Se corrigió confusión entre pruebas ficticias y usuarios reales, y entre proporción etiquetada y rendimiento del modelo. Guía 14 docs/guias/14_auditoria_junio.md para estudiante copiar 07_auditar_etiquetas.py a 12_auditar_junio.py, adaptar rutas/fechas/tamaños y revisar informe de junio. No creado ni ejecutado por Codex. No afirmar mejora del modelo: todavía no existe predictor evaluado.

## Informe de auditoría de junio generado

Estudiante reportó coherencia interna de 7.210 etiquetas y nueve casos. Resumen registrado en resultado_cohorte_junio.md. Codex leyó informe de junio y pide razonamiento sobre Casos 03 y 08; este último cancela el 14 de junio, pero establece vencimiento el 15 (no confundir ambas fechas). No hay casos reales gap29 en junio. Revisión manual en curso; no marcar completada ni avanzar aún a entrenamiento.

## Prioridad temporal: hito 2

Por solicitud expresa del usuario se omiten por ahora siete casos manuales restantes de junio; solo casos 03 y 08 revisados, coherencia interna completa reportada. No exigir completar esos casos para avanzar ni afirmar auditoría completa. Guías 15_caracteristicas_junio.md y 16_linea_base_temporal.md preparadas para ejecución sucesiva por el estudiante con controles. Scripts previstos 13_caracteristicas_junio.py y 14_linea_base_temporal.py; no creados/ejecutados por Codex. Resultado previsto experiments/baseline_marzo_junio.json. Revisar ambas salidas antes de publicar resultados en hito 2. Faltan avance de una página, README reproducible y repositorio con resultado; Git disponible 2.47.1 pero raíz aún sin .git al último listado. No inventar URL ni métricas. Archivo de características de marzo ya corregido a 08_caracteristicas_historicas.py.

## Hito 2 preparado con evidencia real

Primera línea base ejecutada por el estudiante: accuracy 0,942996; precisión/recall/F1 abandono 0; ROC-AUC 0,5; AP 0,057004; matriz [[6799,0],[411,0]], 5.875 usuarios compartidos. JSON en experiments/baseline_marzo_junio.json. Codex revisó código/JSON, hashes de ambos CSV y aritmética sin reejecutar entrenamiento. PDF Entregables/streamretain_hito2.pdf generado y revisado visualmente: una página; fuente docs/streamretain_hito2.md y generador HTML docs/generar_hito2.py. README y requirements.txt preparados; .gitignore excluye datos, contexto, informes con eventos y temporales. Usuario se encarga del repositorio remoto; no crear ni publicar remoto por él. Falta su publicación/entrega externa; no afirmar envío ni aprobación docente. Reproducibilidad del pipeline descrita y sintaxis revisada, no repetida de extremo a extremo por Codex.
