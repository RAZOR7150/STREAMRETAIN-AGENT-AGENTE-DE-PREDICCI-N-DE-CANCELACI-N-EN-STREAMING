# Análisis de contexto de StreamRetain-Agent

Fecha de revisión: 15 de noviembre de 2026.

**Actualización posterior:** el usuario eligió KKBox y ratificó entrega individual. El hito 1 adapta la etiqueta a no renovación dentro de 30 días posteriores al vencimiento. Las menciones siguientes a fuente pendiente y horizonte de 28 días documentan el estado histórico del diseño inicial. Véanse el hito actualizado y AGENTS.md.

## Alcance y fuentes

Se leyó el JSON completo, el texto de la entrega inicial en PDF, el caso de uso y la plantilla. Se extrajo el texto de los documentos académicos PDF y DOCX para identificar sus contenidos, revisar su relación con el proyecto y profundizar en las secciones de agentes, evaluación, regresión logística, árboles, explicabilidad y aprendizaje automático. La revisión del conjunto docente es temática; no constituye una auditoría de cada fórmula, ejemplo de código o figura de todas las diapositivas.

Fuentes centrales:

- `context/StreamRetain_Agent_Contexto_Codex.json`: contexto estructurado de decisiones, propuestas y pendientes; no contiene el historial literal completo de ChatGPT.
- `context/docs/Diseño Agente inteligente 1er Corte.pdf`: entrega de 5 páginas, fechada el 25 de agosto de 2026, por Levis Adrian Ortiz Cano. Docente: Edwin Alexander Puertas Del Castillo, Universidad Tecnológica de Bolívar.
- `context/docs/Diseño Agente inteligente 1er Corte.docx`: versión editable disponible.
- `context/docs/Agente Caso de uso.docx` y `Intelligent Agents_UseCases.pdf`, páginas 16–17: objetivo y descripción de StreamRetain.
- `context/docs/Plantilla_Diseño_Agente.docx`: estructura del primer diseño.
- `context/docs/Fuente de diseño del Agente Caso de uso.pdf`: artículo de Jitendra Maan y Harsh Maan, 2023, sobre predicción de cancelación en telecomunicaciones.
- Los 11 PNG de `context/`: requisitos actuales del proyecto final, resumidos en `AGENTS.md`.

El JSON cita un archivo llamado `Diseno_Inicial_StreamRetain_Agent_v2.docx` que no aparece con ese nombre en la carpeta. El diseño entregado coincide en sus decisiones centrales con el JSON, pero no se afirma que ambos archivos sean idénticos o que se haya verificado esa versión ausente.

## Diseño que se continuará

**Objetivo:** identificar semanalmente suscriptores activos con riesgo de cancelar durante las cuatro semanas siguientes y priorizar ofertas de retención.

**Tarea predictiva:** clasificación binaria supervisada, con probabilidad estimada de cancelación. La definición exacta del evento —baja voluntaria, impago, no renovación, etc.— todavía debe fijarse según la fuente de datos.

**Entradas previstas:** horas vistas, días desde el último acceso, tipo de plan y cambios recientes del método de pago. El historial permitiría calcular tendencias y variaciones únicamente cuando existan observaciones reales fechadas. Estos campos describen el diseño, no un esquema de datos confirmado.

**Ciclo del agente:** recibir y validar datos; actualizar memoria; calcular variables disponibles; estimar riesgo; aplicar una política explícita; priorizar usuarios; comunicar o solicitar una intervención; registrar decisiones y resultados; evaluar cohortes maduras; considerar reentrenamiento validado.

**Tipo:** agente de aprendizaje con estado interno. El entorno se describe como parcialmente observable, estocástico, secuencial, dinámico, con variables continuas y discretas y un agente en el alcance inicial. La implementación debe distinguir ese entorno previsto de una eventual evaluación retrospectiva por lotes.

**PEAS:** desempeño cuantitativo; entorno de suscripciones, consumo, pagos y retención; sensores mediante lectura de registros; actuadores mediante comunicación con marketing y escritura de decisiones/intervenciones. Una probabilidad es una salida del procesamiento interno, no un actuador por sí misma.

**Arquitectura conceptual:** los siete componentes de la plantilla son percepción, planificación de tareas, memoria, razonamiento, herramientas/acción, comunicación y aprendizaje/adaptación. Su presencia en el diseño no demuestra que ya existan implementados.

## Decisiones heredadas y pendientes

| Elemento | Estado |
| --- | --- |
| Continuar StreamRetain en el proyecto final | Confirmado por el usuario |
| Frecuencia semanal y horizonte de 28 días | Objetivo heredado confirmado por PDF y JSON |
| Exactitud global mínima de 75 % | Meta heredada; no es un resultado obtenido |
| Historial de observaciones reales y ciclo completo del agente | Diseño heredado |
| Netflix Customer Churn / KKBox | Candidatos, sin selección ni auditoría |
| Regresión logística, árbol, Random Forest, XGBoost | Alternativas citadas; sin ganador seleccionado |
| SHAP | Propuesta opcional de explicación |
| Umbral de riesgo y selección de ofertas | Pendientes |
| Integración de marketing | No confirmada; no prometer acciones reales |
| Base de datos, interfaz, despliegue y módulos concretos | Pendientes |
| Política de reentrenamiento y promoción de modelos | Pendiente |
| Equipo final y aprobación docente de la nueva propuesta | No acreditados en el material revisado |

## Contrastes y correcciones importantes

1. **Exactitud y precisión.** La sección 7 del PDF usa «precisión general», pero define aciertos / total, es decir, exactitud o accuracy. La precisión de cancelación es TP/(TP+FP). El JSON desambigua expresamente esta diferencia. Debe preservarse el objetivo del 75 % usando el nombre correcto.
2. **75 % no basta para demostrar utilidad.** Como ejemplo hipotético, si el 90 % permanece, predecir siempre permanencia obtiene 90 % de exactitud y no detecta ninguna cancelación. Hay que comparar contra la clase mayoritaria y evaluar la clase de cancelación. F1, recall, precisión, PR-AUC, ROC-AUC y calibración son opciones apoyadas en el material; las métricas y metas finales deben declararse antes de experimentar.
3. **Evaluación semanal no significa resultado inmediato.** Una predicción a 28 días se evalúa cuando hay seguimiento suficiente. No clasificar como permanencia a personas cuyo resultado aún se desconoce. En un experimento retrospectivo, las fechas históricas pueden permitir esa evaluación sin esperar 28 días de calendario actuales.
4. **Historial real.** Releer el mismo CSV no crea evolución. Las capturas semanales requieren una fuente que cambie o registros históricos fechados. No derivar una caída sostenida de consumo de una sola observación por cliente.
5. **Horizonte y etiqueta.** Una columna genérica de cancelación no acredita una predicción a 28 días. Será necesario verificar fechas de observación, evento y seguimiento, además de la disponibilidad de cada variable en el momento de decidir.
6. **Fuga temporal.** El preprocesamiento debe aprender solo de entrenamiento. Las particiones y ventanas deben impedir el uso de resultados futuros; también hay que definir si se evalúa a usuarios conocidos en fechas posteriores o a usuarios nuevos. Tener varias filas por persona exige atender esa dependencia, no aplicar una división aleatoria sin justificación.
7. **Predicción y retención.** Detectar riesgo no demuestra que una oferta reduzca cancelaciones. Tampoco que un usuario haya permanecido demuestra que la oferta causara su permanencia. Registrar las intervenciones permite estudiar esto, pero no sustituye un diseño causal.
8. **Viabilidad aún condicionada.** La conclusión del diseño sostiene su viabilidad conceptual, pero los datos, integración y desempeño aún no la verifican. La frase que califica el 75 % como alcanzable debe entenderse como meta por comprobar.
9. **Datos y enlaces.** El caso de uso presenta el candidato Netflix como sintético y KKBox como datos reales de música. El enlace de Kaggle del documento contiene texto malformado («conjunto de datoss»). No se verificaron enlaces, disponibilidad ni licencias externas en esta revisión local.
10. **Plantillas diferentes.** Respetar la plantilla del primer corte al editar ese diseño. Para el informe final aplican los requisitos IEEE nuevos; no trasladar automáticamente el formato anterior.

## Artículo de referencia: uso y límites

El artículo aporta un antecedente de clasificación tabular, comparación de regresión logística, árbol, Random Forest y XGBoost, y explicación mediante SHAP. Su dominio es telecomunicaciones, no streaming.

En la página 4 del PDF, la tabla 1 reporta exactitud 0,88 y F1 de cancelación 0,32; la tabla 2 reporta para XGBoost exactitud 0,962 y F1 0,836. El texto próximo menciona recall 0,83 y precisión 0,54, cuya media armónica es aproximadamente 0,654. No queda clara la correspondencia entre esas evaluaciones. No trasladar sus cifras como meta, rendimiento esperado o garantía de este proyecto. La selección del modelo debe surgir de los experimentos propios.

## Mapa del material docente

| Material | Contenido identificado y relación con StreamRetain |
| --- | --- |
| `AI_Lecture01B_Introduction.pdf` | IA, racionalidad, aprendizaje y problemas; fundamento conceptual |
| `AI_Lecture02_Intelligent_Agents.pdf` | PEAS, sensores y actuadores, entornos, tipos de agente, memoria y arquitectura; sustenta la formulación |
| `AI_Lecture04b_FOL1.pdf` y `AI_Lecture04b_FOL2.pdf` | Lógica proposicional y de primer orden, cuantificadores, representación e inferencia; posible apoyo a reglas explícitas, sin obligación de incorporarlas como técnica central |
| `AI_Lecture05a_KnowledgeRepresentation.pdf` | Representaciones simbólicas, probabilísticas, grafos, embeddings, RAG y memoria; contexto para justificar la representación elegida |
| `AI_Lecture06b_MarkovModels.pdf` y `AI_Lecture06c_MarkovModels.pdf` | Cadenas, HMM, inferencia temporal, MDP y POMDP; alternativas secuenciales si existen datos adecuados, no requisitos del agente |
| `AI_Lecture07c_MachineLearning.pdf` | CRISP-ML(Q), preparación, modelos supervisados, ensambles, validación, explicabilidad, IA responsable y operación de modelos; referencia central para la evolución |
| `AI_LectureML01_LinearRegression.pdf` | Regresión, supuestos, regularización y prevención de fuga; no confundir regresión lineal con el clasificador logístico |
| `AI_LectureML02_LogisticRegression_ES.pdf` | Clasificación, sigmoide, regularización, supuestos, umbrales y calibración; base para un modelo interpretable |
| `AI_LectureML03_SupportVectorMachine_ES.pdf` | Margen, kernels, escalado, C y gamma, calibración y evaluación; alternativa posible, no seleccionada |
| `AI_LectureML05_DecisionTree_ES.pdf` | Entropía, Gini, poda, sobreajuste, estabilidad e importancia de variables; candidato interpretable y fundamento para ensambles |
| `Correlacion de Pearson.pdf` | Asociación lineal, diagnóstico y límites de interpretación; no inferir causalidad ni convertir correlación en selector suficiente de variables |
| `N-gram Language Models.pdf` | Modelos de lenguaje, evaluación, perplejidad y suavizado; periférico para el problema tabular actual |
| `AI_Lecture13c_Transformer.pdf` | Tokenización, embeddings, atención, Transformers y evaluación; no hay requisito actual que justifique añadir un LLM |
| HTML local `ai_search_algorithms_complete.html` | Referencia de búsqueda no informada, informada, local, evolutiva, CSP y adversarial; corresponde a otras formulaciones posibles |
| `Playing Chess Against a Computer (Example).pdf` | Ejemplo PEAS; su mezcla entre planificación y actuadores no debe trasladarse al diseño |
| `Intelligent Agents_UseCases.pdf` | Banco de casos de uso; incluye el caso StreamRetain en páginas 16–17 |

Se identificaron copias con sufijo `(1)` de agentes inteligentes y del ejemplo de ajedrez, con el mismo texto extraído que las versiones sin ese sufijo.

`01_SA_Introduction.pdf` corresponde a arquitectura de software y menciona a Jairo Serrano; sus entregables no deben asumirse como requisitos de este proyecto de IA. `Parcial Practico Corte I.pdf` trata del robot aspirador, no de StreamRetain; sus autores no confirman el equipo final de este proyecto. Un archivo cuyo nombre corresponde a una liquidación personal se excluyó de la lectura por no guardar relación aparente con el material académico solicitado.

Referencias docentes especialmente útiles para futuras tareas:

- Agentes: páginas 3–11 (agente, racionalidad y PEAS), 12–25 (entornos), 27–44 (tipos y arquitectura).
- Machine Learning: páginas 13–19 (proceso y preparación), 90–96 (evaluación), 97–103 (explicabilidad), 104–110 (responsabilidad), 111–117 (versionado y operación), 125 (criterios para elegir ML clásico, LLM o híbrido).
- Regresión logística: páginas 12–18 (supuestos y calibración), 32 (buenas prácticas).
- Árboles: páginas 23–24 (poda y complejidad), 32–38 (condiciones, estabilidad, importancia y calibración), 43 (buenas prácticas).

## Encaje con el proyecto final

La **ruta C, aprendizaje automático**, es el encaje propuesto porque el núcleo es clasificación supervisada de cancelación. El nombre «agente» o el uso de una API no convierte el proyecto en ruta E: esta exige un agente LLM con herramientas, memoria o planificación y otra comparación mínima. No se registra la ruta C como decisión formal del usuario o del docente todavía.

| Exigencia final | Base heredada | Trabajo que falta demostrar |
| --- | --- | --- |
| Problema y usuario real | Plataforma piloto y retención | Usuario concreto, proceso actual y evidencia de relevancia |
| Formulación | Entorno, agente, entradas y acciones descritos | PEAS explícito, etiqueta, unidad de observación y alcance verificables |
| Datos | Dos candidatos | Licencia, esquema, fechas, calidad, particiones y factibilidad del horizonte |
| Justificación | Curso y un artículo de referencia | Comparación argumentada de alternativas y bibliografía final suficiente |
| Línea base y modelos | Modelos posibles en el JSON | Línea base, al menos dos modelos y ajuste de hiperparámetros para ruta C |
| Evaluación | Meta de exactitud del 75 % | Métricas complementarias, protocolo previo y evidencia de varias corridas o validación adecuada |
| Errores | Sin resultados aportados | Al menos 10 fallos reales clasificados con hipótesis |
| IA responsable | Riesgos enumerados | Análisis específico, métricas cuando sean posibles y mitigaciones concretas |
| Prototipo | Arquitectura conceptual | Ejecución reproducible del ciclo, persistencia y separación clara entre acciones reales y simuladas |
| Informe y defensa | Diseño inicial de 5 páginas | Informe IEEE, bitácora, repositorio y capacidad de defender decisiones y cambios en vivo |

La ampliación debe ser evidente mediante datos auditados, implementación ejecutable y evaluación comparativa. Añadir tecnologías sin una pregunta evaluable no acredita por sí solo esa ampliación.

## Próxima decisión necesaria, sin adelantar implementación

El primer asunto a resolver será la **factibilidad de los datos respecto del objetivo temporal**. Después podrán fijarse la etiqueta, la ruta formal, el protocolo experimental y el alcance de las acciones de retención. Esta revisión no seleccionó dataset, no descargó datos de clientes, no entrenó modelos y no produjo resultados experimentales.
