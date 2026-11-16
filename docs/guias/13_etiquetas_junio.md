# Guía 13 — Etiquetar los candidatos de junio

## Objetivo

Asignar etiquetas reconstruidas a los 7.210 candidatos del corte 2016-06-06, con la misma función de etiquetado ya revisada en marzo. El seguimiento termina el 2016-08-04. No modificar la definición para obtener una proporción de abandono determinada.

## 1. Copiar el programa

En tu editor copia `scripts/06_etiquetar_piloto.py` a `scripts/11_etiquetar_junio.py`. Conserva el programa y resultados de marzo.

En el nuevo archivo sustituye las tres rutas y el corte en la sección inicial:

```python
archivo_candidatos = carpeta / "candidatos_2016-06-06.csv"
archivo_eventos = carpeta / "piloto_2016-06-06.csv"
salida = carpeta / "etiquetas_piloto_2016-06-06.csv"
corte = date(2016, 6, 6)
```

El corte debe asignarse antes de calcular las ventanas. Mantén estas expresiones:

```python
inicio = corte - timedelta(days=90)
fin_vencimientos = corte + timedelta(days=29)
fin_observacion = fin_vencimientos + timedelta(days=30)
```

Así obtendrás inicio 2016-03-08, último vencimiento 2016-07-05 y seguimiento hasta 2016-08-04.

## 2. Actualizar el control de tamaño con evidencia de junio

Busca la condición que verificaba 40.503 filas y 7.443 candidatos. Sustituye ese bloque por:

```python
# Cantidades de junio que ya ejecutaste y revisamos; no son metas a forzar.
if filas_piloto != 40612 or len(candidatos) != 7210:
    raise ValueError("Los tamaños no coinciden con el piloto de junio revisado; investigar")
```

Esta adaptación mantiene el control: ahora comprueba los archivos de junio contra los resultados de sus pasos anteriores. No eliminar el control para ocultar una discrepancia.

## 3. Mantener las reglas y los casos sintéticos

No cambies leer_fecha, comparar_eventos, etiquetar ni la lógica de escritura. Mantén también los nueve casos inventados con sus fechas de marzo/abril: son pruebas de la función, no registros de la cohorte de junio. No hagas un reemplazo global de todas las fechas del archivo.

El bloque sintético usa sus propias variables v y f, mientras que el procesamiento real utiliza corte y fin_observacion. Por eso los casos de prueba pueden permanecer idénticos entre cohortes. Deben seguir pasando los nueve.

La regla sigue siendo: primera renovación desde el corte; cancelaciones previas pueden adelantar el vencimiento; gap < 30 indica 0 y gap >= 30 indica 1. Sin renovación se requiere plazo observado suficiente bajo el supuesto documentado de cobertura del historial. Estas etiquetas reconstruidas no son etiquetas oficiales de Kaggle.

## 4. Ejecutar

Desde la raíz:

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\11_etiquetar_junio.py"
```

No requiere instalaciones ni otro recorrido del comprimido. Lee únicamente el piloto reducido y los candidatos. El modo x protege salidas anteriores; si el archivo existe, no sobrescribirlo sin revisar.

## 5. Qué revisar y compartir

Comparte la salida completa. Debe indicar nueve casos ilustrativos correctos, 7.210 candidatos procesados, seguimiento hasta 2016-08-04 y salida etiquetas_piloto_2016-06-06.csv.

Todavía no conocemos cuántos serán 0 o 1, ni el porcentaje. Las clases y los casos sin etiqueta deben sumar 7.210. Un cambio respecto de marzo no prueba por sí solo un error o una mejora: describimos otra cohorte, no rendimiento de un modelo.

Mantén todos los campos de auditoría de la etiqueta. No deben entrar como características: primera_renovacion, gap_dias, motivo y vencimiento_efectivo ajustado con eventos futuros. El archivo aún no se usa para entrenar o evaluar.

Después revisaremos coherencia y ejemplos de junio, prepararemos las mismas seis características y podremos ejecutar la primera línea base temporal entrenada con marzo y medida en junio. No cambiaremos la clase predicha por la línea base usando la distribución de junio.

## Preguntas

1. ¿Por qué los nueve ejemplos inventados pueden seguir usando fechas de marzo aunque la cohorte sea de junio?
2. Si el abandono de junio es distinto del de marzo, ¿eso demuestra que un modelo mejoró o empeoró?
