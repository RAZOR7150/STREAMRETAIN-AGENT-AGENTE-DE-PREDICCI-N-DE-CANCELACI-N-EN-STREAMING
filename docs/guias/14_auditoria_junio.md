# Guía 14 — Auditar etiquetas de junio

## Objetivo

Repetir en junio las comprobaciones de coherencia y revisión de ejemplos de marzo. La proporción 5,70 % es descriptiva, no rendimiento de un modelo. No modificar las reglas para acercarla a marzo.

Copia en tu editor `scripts/07_auditar_etiquetas.py` a `scripts/12_auditar_junio.py`. Mantén el original de marzo. En la copia realiza estas sustituciones específicas:

| Elemento | Antes | Ahora |
| --- | --- | --- |
| Ruta del informe | piloto_2016-03-07.md | piloto_2016-06-06.md |
| corte | date(2016, 3, 7) | date(2016, 6, 6) |
| fin | date(2016, 5, 5) | date(2016, 8, 4) |
| CSV de etiquetas | etiquetas_piloto_2016-03-07.csv | etiquetas_piloto_2016-06-06.csv |
| CSV de eventos | piloto_2016-03-07.csv | piloto_2016-06-06.csv |
| Control len(etiquetas) | 7443 | 7210 |
| Control leidas | 40503 | 40612 |
| Fecha del título del informe | 2016-03-07 | 2016-06-06 |

La fecha de inicio se sigue calculando como corte - timedelta(days=90). Conserva todas las demás comprobaciones, la función de ordenación y la selección de categorías. No cambiar <30 por <=30 ni incorporar datos futuros a la historia. No importar el script completo anterior, pues se ejecutaría.

Los controles de tamaño deben quedar:

```python
if len(etiquetas) != 7210:
    raise ValueError("No coincide el número de candidatos de junio")
```

```python
if leidas != 40612:
    raise ValueError("El piloto de junio no tiene el tamaño previamente revisado")
```

Son sustituciones en sus posiciones originales, no bloques adicionales al inicio. Los valores proceden de tus ejecuciones, no de una expectativa de que junio se parezca a marzo.

Ejecuta desde la raíz:

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\12_auditar_junio.py"
```

La salida será `docs/auditorias/piloto_2016-06-06.md`. No usar el informe de marzo para explicar casos de junio: los alias son locales a cada informe. Si aparece FileExistsError, conserva el informe y avisa antes de sobrescribir anotaciones.

Comparte el resumen completo. Las categorías pueden superponerse o estar vacías; el número de ejemplos distintos no tiene por qué ser nueve. Los nueve casos inventados del etiquetador son otra cosa: prueban reglas con fechas ficticias, no son estos ejemplos reales.

Para revisar los casos reales usa el corte del 6 de junio. Identifica el vencimiento conocido; luego aplica cancelaciones desde el corte anteriores a la primera renovación. Calcula gap exacto o, si falta renovación, comprueba vencimiento efectivo +30 frente al 4 de agosto y declara el supuesto de cobertura.

Empieza con un caso de renovación y uno de cancelación/vencimiento adelantado si existe. No supongas que Caso 01 o Caso 08 representan los mismos usuarios que en marzo. Revisaremos los ejemplos y completaremos el resto antes de características. Esta auditoría no es un análisis de errores de modelo ni demuestra cobertura perfecta.
