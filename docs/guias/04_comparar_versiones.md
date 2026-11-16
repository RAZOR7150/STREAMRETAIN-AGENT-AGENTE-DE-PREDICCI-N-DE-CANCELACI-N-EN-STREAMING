# Hito 2 — Paso 4: comparar las versiones de etiquetas

## Por qué hacemos esta comparación

Ya verificaste `train_v2`: 970.960 filas, igual número de usuarios únicos y cero contradicciones. Ahora necesitamos saber qué relación tiene con `train.csv`. El sufijo v2 significa una versión actualizada; no demuestra que sea un periodo futuro independiente.

El objetivo es medir usuarios compartidos, usuarios exclusivos y etiquetas que coinciden o difieren. No juntaremos las tablas ni decidiremos todavía que una será entrenamiento y la otra prueba. La documentación temporal también será necesaria para esa decisión.

## Dónde escribirlo

Añade los bloques siguientes al final de tu archivo `scripts/02_revisar_etiquetas.py`, después de imprimir el resumen de unicidad. Se aprovechan las importaciones y variables que ya existen. No reemplaces los bloques anteriores.

### 1. Preparación

```python
# Solo compararemos versiones si la revisión de v2 no detectó problemas.
if filas_mal_formadas or etiquetas_invalidas or usuarios_vacios or filas_repetidas_usuario:
    raise ValueError("Revisa las incidencias de train_v2 antes de comparar versiones")

# Esta es la versión original; su CSV está en la raíz interna del comprimido.
original = raiz / "data" / "kkbox-churn-prediction-challenge" / "train.csv.7z"
if not original.is_file():
    raise FileNotFoundError(f"No se encontró: {original}")

# Conservaremos cada identificador original una vez para detectar duplicados.
usuarios_original = set()
conteos_original = {"0": 0, "1": 0}

# Cada clave representa (etiqueta original, etiqueta en v2).
# Las claves son tuplas: pares ordenados de valores.
comparaciones = {("0", "0"): 0, ("0", "1"): 0, ("1", "0"): 0, ("1", "1"): 0}
```

Una tupla como `("0", "1")` es una clave válida de diccionario. En este ejercicio significa: el mismo identificador aparece con 0 en original y con 1 en v2. No implica todavía que la persona cambiara de comportamiento; puede ser una diferencia de versión, etiqueta o periodo.

### 2. Lectura de la versión original y comparación

```python
# Se abre un segundo proceso después de haber cerrado el usado para v2.
proceso_original = subprocess.Popen(
    [str(tar), "-xOf", str(original), "train.csv"],
    stdout=subprocess.PIPE,
    text=True,
    encoding="utf-8-sig",
)

try:
    lector_original = csv.DictReader(proceso_original.stdout)
    if lector_original.fieldnames != ["msno", "is_churn"]:
        raise ValueError(f"Cabecera original inesperada: {lector_original.fieldnames}")

    # enumerate añade un contador de filas; start=1 comienza en uno.
    for numero_fila, fila in enumerate(lector_original, start=1):
        # Aquí nos detenemos ante una incidencia para no comparar tablas ambiguas.
        if None in fila or any(valor is None for valor in fila.values()):
            raise ValueError(f"Estructura incorrecta en la fila {numero_fila} de original")

        usuario = fila["msno"].strip()
        etiqueta = fila["is_churn"].strip()
        if usuario == "" or etiqueta not in conteos_original:
            raise ValueError(f"Usuario o etiqueta inválidos en la fila {numero_fila}")
        if usuario in usuarios_original:
            raise ValueError(f"Usuario repetido en original, fila {numero_fila}; investigar")

        # Guardamos el usuario y actualizamos la distribución del archivo original.
        usuarios_original.add(usuario)
        conteos_original[etiqueta] += 1

        # Solo comparamos etiquetas cuando ese usuario también aparece en v2.
        if usuario in etiquetas_por_usuario:
            # Ya verificamos una sola etiqueta por usuario en v2.
            # iter permite recorrer el conjunto y next toma su único elemento.
            etiqueta_v2 = next(iter(etiquetas_por_usuario[usuario]))
            comparaciones[(etiqueta, etiqueta_v2)] += 1

    codigo_original = proceso_original.wait()
    if codigo_original != 0:
        raise RuntimeError(f"La lectura de original falló con código {codigo_original}")
finally:
    proceso_original.stdout.close()
    if proceso_original.poll() is None:
        proceso_original.terminate()
    proceso_original.wait()
```

Esta versión se detiene si encuentra un duplicado en original; no lo elimina ni elige una etiqueta. Si aparece ese error, comparte el mensaje y revisaremos el caso antes de continuar. El número de fila cuenta registros de datos, no necesariamente líneas físicas del CSV.

### 3. Resumen de la comparación

```python
# Cada usuario compartido aporta una vez a una de las cuatro combinaciones.
compartidos = sum(comparaciones.values())
solo_original = len(usuarios_original) - compartidos
solo_v2 = len(etiquetas_por_usuario) - compartidos

# La diagonal contiene etiquetas iguales; las otras dos celdas, etiquetas distintas.
coinciden = comparaciones[("0", "0")] + comparaciones[("1", "1")]
difieren = comparaciones[("0", "1")] + comparaciones[("1", "0")]

print("Usuarios de original:", len(usuarios_original))
print("Original: renovación (0):", conteos_original["0"])
print("Original: abandono (1):", conteos_original["1"])
print("Usuarios compartidos:", compartidos)
print("Usuarios solo en original:", solo_original)
print("Usuarios solo en v2:", solo_v2)
print("Compartidos con etiqueta igual:", coinciden)
print("Compartidos con etiqueta diferente:", difieren)
print("Comparaciones (original, v2):", comparaciones)

# Revisamos las identidades que deben cumplirse en este conteo.
if coinciden + difieren != compartidos:
    raise RuntimeError("La comparación de etiquetas no cuadra")
if sum(conteos_original.values()) != len(usuarios_original):
    raise RuntimeError("El conteo del archivo original no cuadra")
```

## Ejecución

Usa el mismo comando del ejercicio anterior y comparte la salida completa:

```powershell
& 'C:\Users\HP\anaconda3\python.exe' scripts/02_revisar_etiquetas.py
```

No hay resultados anticipados. Se vuelven a recorrer ambos comprimidos para conservar un programa reproducible. El conjunto de usuarios de original añade memoria al diccionario de v2; seguimos sin cargar todas las transacciones o escuchas.

## Cómo interpretar el resultado

- Compartir identificadores no significa automáticamente fuga: depende de si se pretende predecir periodos futuros de usuarios conocidos o usuarios nuevos, y de qué información se utiliza.
- Dos versiones de la misma cohorte no deben asumirse como periodos independientes de entrenamiento y prueba.
- Etiquetas distintas entre versiones no equivalen automáticamente a contradicciones dentro de un mismo archivo. Debemos investigar su significado y posibles correcciones.
- El resumen es una comparación de etiquetas reales, no una matriz de predicciones ni una medida de desempeño del modelo.

Después de revisar tu salida, resolveremos la selección de etiquetas y la viabilidad del protocolo de evaluación. No entrenaremos hasta que esa decisión esté justificada.
