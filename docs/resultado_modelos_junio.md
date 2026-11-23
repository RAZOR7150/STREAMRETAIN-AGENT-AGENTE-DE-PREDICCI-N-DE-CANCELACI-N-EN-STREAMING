# Comparación de modelos en junio — resultado de selección

Fecha de revisión: 2026-11-22. Fuente: ejecución del estudiante y JSON experiments/comparacion_20261122T202144442375Z/resultados.json. Entrenamiento marzo; selección de parámetros/umbral en junio. No es prueba final.

| Modelo | Parámetros | Umbral | Exactitud | Precisión abandono | Recall abandono | F1 abandono | ROC-AUC | AP |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | most_frequent | No aplica | 0,9430 | 0 | 0 | 0 | 0,5000 | 0,0570 |
| Logística | C=0,1; balanced | 0,6 | 0,9100 | 0,3175 | 0,5036 | 0,3895 | 0,7731 | 0,2579 |
| Árbol | profundidad=3; hoja mínima=100; balanced | 0,5 | 0,9204 | 0,3592 | 0,5061 | 0,4202 | 0,8101 | 0,2441 |

Matriz logística [[6354,445],[204,207]]. Matriz árbol [[6428,371],[203,208]]. Ambos detectan abandonos frente a cero de la baseline. Árbol detecta 208 de 411, con 371 falsas alarmas. No domina todas las métricas: logística tiene AP mayor. El árbol gana por el criterio declarado de F1, provisionalmente. Ninguno alcanza F1>=0,50 aunque ambos superan exactitud>=0,75. No modificar las etiquetas o la meta para ocultarlo.

Doce entrenamientos y nueve umbrales por configuración. El ajuste y las métricas usan la misma validación de junio: pueden resultar optimistas. Falta segunda ronda temporal y prueba final. Artefactos provisionales guardados por el estudiante; Codex no entrenó. Próximo paso guía 18 para preparar nuevos cortes con comprobación de equivalencia exacta en los anteriores.

## Cohortes adicionales preparadas por el estudiante

Salida: 21.547.746 filas originales recorridas, 126.126 eventos muestreados. Equivalencia exacta de valores de marzo (7.443) y junio (7.210) confirmada por su programa. Septiembre 2016-09-05: 8.251 filas, seguimiento hasta 2016-11-03. Diciembre 2016-12-05: 8.220 filas, seguimiento hasta 2017-02-02. Manifiesto data/derived/preparacion_cohortes_finales.json leído por Codex; no se inspeccionaron etiquetas de diciembre ni se ejecutó procesamiento.

Guía 19 preparada para completar marzo+junio -> septiembre con misma rejilla y umbrales, combinar media simple de F1 de ambas rondas, desempatar por AP media y cercanía a 0,5, congelar configuración/umbral antes de diciembre. Resultados pendientes; no afirmar validación completada todavía.
