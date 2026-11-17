# Guía 11 — Cohorte de junio: extraer la nueva ventana temporal

## Objetivo de este paso

Empezar la cohorte de validación del lunes 2016-06-06 usando exactamente el mismo procedimiento de muestreo que en marzo. Primero extraerás su ventana; revisaremos el resumen antes de seleccionar candidatos, etiquetar y construir características. No es todavía una cohorte terminada ni una evaluación de modelo.

Conservaremos el piloto y la cohorte de marzo. No volveremos a ejecutarlos ni cambiaremos sus resultados. Usaremos el mismo original transactions.csv.7z; no hay que combinarlo con transactions_v2.

## 1. Calendario de junio

| Elemento | Fecha |
| --- | --- |
| Inicio de historia de 90 días | 2016-03-08 |
| Inicio de historia de 30 días para características posteriores | 2016-05-07 |
| Último día histórico permitido | 2016-06-05 |
| Corte de predicción (lunes) | 2016-06-06 |
| Último vencimiento elegible (corte + 29 días) | 2016-07-05 |
| Final de seguimiento (último vencimiento + 30 días) | 2016-08-04 |

Todo cabe en el rango del archivo original hasta febrero de 2017. El mismo supuesto de cobertura del historial publicado sigue vigente; no deducimos cobertura perfecta del máximo.

El seguimiento de marzo terminó el 5 de mayo, 32 días antes de este corte. Eso permite simular entrenar con marzo antes de predecir junio. Las etiquetas de junio se conocerán después, con su seguimiento hasta agosto: sirven para evaluar esas predicciones, no para entrenar el modelo que las produce.

## 2. Crea una copia del extractor, sin cambiar el de marzo

En el editor, copia el contenido de `scripts/04_piloto_temporal.py` a un archivo nuevo llamado:

`scripts/09_piloto_junio.py`

Usamos una copia para que puedas identificar qué cambia entre cortes sin introducir todavía una refactorización de varios programas. La lógica sigue siendo la que ya escribiste y ejecutaste. Codex no ha creado ni modificado estos scripts.

En la copia, cambia estas **dos asignaciones**:

```python
# Nuevo momento de predicción; las demás fechas se calculan con timedelta.
corte = date(2016, 6, 6)

# Nombre distinto para conservar intacto el piloto de marzo.
salida = raiz / "data" / "derived" / "piloto_2016-06-06.csv"
```

No añadas una segunda asignación de corte al final: sustituye la original en la sección inicial, ANTES de calcular inicio y fin de seguimiento. La parte de fechas debe quedar así:

```python
corte = date(2016, 6, 6)
inicio = corte - timedelta(days=90)
fin_vencimientos = corte + timedelta(days=29)
fin_seguimiento = fin_vencimientos + timedelta(days=30)

salida = raiz / "data" / "derived" / "piloto_2016-06-06.csv"
```

Esto es una comprobación visual del bloque, no otro bloque que debas pegar además del anterior. El resto del script permanece igual.

## 3. Qué debe mantenerse

- Fuente: `transactions.csv.7z`; ruta interna: `transactions.csv`.
- Regla de muestra: prefijo `streamretain-v1:`, SHA-256 y condición `% 100 == 0`.
- Historia de 90 días y ventana de vencimientos de 30 días.
- Lectura secuencial y recorrido completo del comprimido.
- Controles de estructura, fechas y usuarios.
- Modo de escritura x, para no sobrescribir una salida previa.

No cambies el prefijo ni el porcentaje para conseguir un tamaño o proporción de abandono parecidos a marzo. No filtres únicamente los 7.443 candidatos anteriores: en junio la elegibilidad se volverá a determinar según el estado de ese momento. Un identificador que cumple la regla de muestreo seguirá cumpliéndola; eso no garantiza que tenga eventos o sea candidato en ambos cortes.

Tampoco elijas solo usuarios que renueven después: estarías condicionando la población a información futura.

## 4. Ejecuta una vez

Desde PowerShell en la raíz:

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\09_piloto_junio.py"
```

Se recorre otra vez el archivo original completo, porque la ventana cambió. No se guarda su descompresión completa; solo el nuevo CSV reducido. El programa puede tardar y no imprime progreso mientras recorre. Si aparece FileExistsError, conserva el archivo existente y comparte el mensaje; no lo sobrescribas sin revisar.

## 5. Qué comprobar al terminar

La salida debe indicar:

- Archivo de origen: transactions.csv.7z.
- Filas recorridas: 21.547.746 si usas el mismo original y termina correctamente.
- Inicio histórico: 2016-03-08.
- Corte: 2016-06-06.
- Fin de seguimiento: 2016-08-04.
- Archivo de salida: piloto_2016-06-06.csv.

**Los demás conteos todavía no se conocen.** No esperamos 40.503 filas, 25.054 históricas ni 15.449 de seguimiento: esos fueron resultados de marzo. La suma de historia y seguimiento debe coincidir con el total guardado y con la suma por meses.

Los meses extremos están recortados: marzo empieza el día 8 y agosto termina el día 4. Junio mezcla historia hasta el día 5 y seguimiento desde el 6. No separes las fases usando solo el mes.

Comparte el resumen completo. Hasta revisarlo, no copies ni ejecutes en cadena los demás programas: contienen rutas y controles numéricos específicos de marzo que tenemos que adaptar con los resultados reales de junio, conservando las comprobaciones.

## 6. Ruta para completar la cohorte de junio

Después de revisar esta extracción seguiremos, sin cambiar las reglas, con:

1. Candidatos: reconstruir el vencimiento conocido al 6 de junio y seleccionar los que vencen entre ese día y el 5 de julio.
2. Etiquetas: primera renovación desde el nuevo corte, mismas reglas de cancelación y gap < 30 / >= 30; seguimiento hasta el 4 de agosto.
3. Auditoría: coherencia y casos de ejemplo del nuevo periodo. Si faltan categorías no inventaremos ejemplos.
4. Características: las mismas seis columnas, solo con historia anterior al 6 de junio.
5. Línea base: aprender la clase mayoritaria con marzo y predecir junio. Las etiquetas de junio se usan para medir, no para decidir la clase mayoritaria del entrenamiento.

La auditoría de calidad de las etiquetas de validación no equivale a ajustar un modelo a sus resultados. No alteraremos reglas para mejorar una métrica. Diciembre sigue reservado como prueba final; junio será validación, no prueba final ni validación cruzada completa por sí solo.

Nota de continuidad: tu script de características de marzo se llama realmente `08_caracterustucas_historicas.py`. No hace falta cambiarlo para este ejercicio; al adaptar esa fase usaremos el nombre real.

## 7. Preguntas de comprensión

1. ¿Por qué mantenemos la misma regla de selección de usuarios, pero no exigimos los mismos candidatos de marzo?
2. ¿Por qué podemos entrenar con las etiquetas de marzo antes de predecir junio, pero no con las de junio?
3. ¿Por qué no debemos modificar los controles de junio para forzar que sus conteos sean iguales a marzo?

No es necesario instalar nada ni entrenar en este paso. Primero revisaremos tu nueva extracción.
