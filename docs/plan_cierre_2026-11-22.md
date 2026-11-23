# Cierre del proyecto — 22 de noviembre de 2026

El estudiante solicita terminar hoy porque estima la sustentación para mañana, 23 de noviembre; la fecha no se ha confirmado con el docente. Se mantiene aprendizaje guiado: estudiante escribe/ejecuta procesamiento y modelos; Codex prepara guías, documentación y soporte. No se autorizan nuevas operaciones de Git.

## Estado comprobado

Existen cohortes de marzo y junio, baseline ejecutado y PDF de hitos 1/2. No hay aún modelos logístico/árbol entrenados, cohortes septiembre/diciembre, evaluación final, demostración ejecutable, informe IEEE ni presentación. La auditoría manual de junio sigue parcial por decisión previa del estudiante.

## Orden de trabajo para avanzar hoy

1. **Ahora:** guía 17, regresión logística y árbol, rejillas pequeñas de parámetros y umbrales en junio. Usar las cohortes existentes. Estudiante ejecuta y comparte resumen; Codex revisa. Son resultados de selección, no prueba final.
2. **Datos finales:** preparar septiembre y diciembre reutilizando las reglas ya verificadas. Priorizar un programa parametrizado explicado, sin repetir quince ejercicios por cohorte. Mantener diciembre fuera de selección. La reducción de auditoría manual previa no autoriza omitir controles automáticos o ignorar errores.
3. **Validación temporal:** completar segunda ronda (marzo+junio -> septiembre), elegir configuración/umbral con validaciones y congelarlos. Entrenar con marzo+junio+septiembre, evaluar diciembre una vez. No cambiar objetivo para alcanzar la nota si el F1 es menor que la meta.
4. **Agente demostrable:** CLI local que reciba las seis características, estime puntaje, aplique el umbral, recomiende revisión humana y registre decisiones localmente. Sin campañas reales ni acciones sobre clientes. Explicar PEAS y límites de puntajes no calibrados.
5. **Evaluación final:** baseline y modelos, matriz y métricas, al menos diez errores reales con hipótesis, subgrupos disponibles definidos con datos históricos y tamaños. Si no hay edad/género/antigüedad real, no inventarlos.
6. **Entregables:** informe IEEE 6–8 páginas y referencias requeridas, PDF hito 3; presentación hito 4 y guion de 8 minutos + demo de 4 + preguntas; bitácora, README, dependencias y evidencia. Finales en Entregables. Las secciones de resultados dependen de ejecuciones reales.

## Qué no podemos afirmar todavía

No prometer F1>=0,50, validación cruzada completada, prototipo funcional o entrega final lista antes de tener evidencia. Tampoco el 94,30 % de exactitud de la baseline significa utilidad: su F1 de abandono es cero.

La prioridad reduce preguntas repetitivas y documentación por micro-paso. Se revisará la comprensión en los puntos críticos: corte temporal, selección de umbral, modelo elegido, errores y defensa del agente. Los bloqueos que requieran ejecución del estudiante se comunicarán con un siguiente paso concreto.

## Actualización de cierre: mejoras y demostración web

Las etapas de modelos, cuatro cohortes, dos rondas temporales, prueba final y análisis de errores ya fueron ejecutadas por el estudiante. También se ejecutaron ambos perfiles de la CLI y reprodujeron los puntajes esperados. El F1 final de la versión1 es0,34615: la meta0,50 no se cumplió.

Por solicitud posterior del estudiante, se preparó una búsqueda ampliada acotada del árbol (guía23), solo sobre desarrollo. Es una iteración iniciada después de conocer la prueba de versión1; no debe presentarse como una nueva prueba independiente ni reemplazar los resultados previos. Pendiente ejecución por el estudiante.

Se preparó guía24 para una aplicación Streamlit que el profesor pueda probar localmente y posteriormente por enlace. El alumno crea streamlit_app.py; Codex prepara dependencias. La app usa la versión1 evaluada y no necesita datasets brutos. No está publicada y no existe aún enlace verificable. Git sigue a cargo del usuario. N8n no se ha confirmado como requisito del curso.

Pendientes principales: salida de búsqueda ampliada, implementación/prueba/publicación de interfaz, revisión personal de los diez errores, informe IEEE, presentación y verificación de entregables. Mantener prototipo y resultados de versión1 como respaldo para la sustentación.
