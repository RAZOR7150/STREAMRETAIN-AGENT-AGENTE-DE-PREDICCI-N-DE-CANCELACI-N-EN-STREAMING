# Hito 2 — Paso 2: leer y contar las etiquetas de abandono

## Objetivo de este ejercicio

Tú escribirás y ejecutarás un primer programa que recorra las filas de `train_v2.csv.7z` y responda:

- ¿Cuántas filas contiene?
- ¿Cuántas tienen etiqueta 0 y cuántas etiqueta 1?
- ¿Hay etiquetas inesperadas, identificadores vacíos o filas con estructura incorrecta?
- ¿Qué porcentaje corresponde a abandono?

Es una primera inspección, no entrenamiento ni evaluación de la línea base. No verificará todavía usuarios repetidos, coherencia temporal o solapamiento entre versiones.

El entorno y los comprimidos ya fueron revisados por Codex: no tienes que repetir esa preparación.

## Por qué empezamos por train_v2

La imagen local `data/Tablas1.png` describe `train_v2.csv` como la actualización del 6 de noviembre de 2017 con datos de abandono de marzo de 2017. Lo inspeccionamos por separado: no se asume que `train.csv` sea otro mes independiente ni se unen las dos versiones.

- `msno`: identificador del usuario.
- `is_churn = 1`: abandono.
- `is_churn = 0`: renovación según la definición del desafío.

La ruta interna comprobada es `data/churn_comp_refresh/train_v2.csv`. No usar el CSV de cero bytes que quedó de una extracción anterior.

## Archivo que debes crear

Desde tu editor, crea `scripts/02_revisar_etiquetas.py`. Escribe los tres bloques siguientes, en este orden, dentro del mismo archivo. Codex solo proporciona el ejemplo en esta guía: no ha creado ni ejecutado ese script.

## Bloque 1. Herramientas, rutas y contadores

```python
# csv permite interpretar correctamente filas y columnas de un CSV.
import csv

# subprocess permite iniciar el descompresor y leer lo que produce.
import subprocess

# Path permite construir rutas sin concatenar manualmente barras.
from pathlib import Path

# __file__ es la ruta del programa que estás ejecutando.
# resolve() obtiene su ruta absoluta.
# parents[0] es scripts; parents[1] es la raíz del proyecto.
raiz = Path(__file__).resolve().parents[1]

# / une partes de una ruta cuando se utiliza con objetos Path.
comprimido = raiz / "data" / "kkbox-churn-prediction-challenge" / "train_v2.csv.7z"

# Esta ruta describe el CSV dentro del 7z, no un CSV ya extraído.
ruta_interna = "data/churn_comp_refresh/train_v2.csv"

# La r inicial evita interpretar las barras de Windows como escapes.
tar = Path(r"C:\Windows\System32\tar.exe")

# Si falta un archivo necesario, detenemos el programa con un error claro.
if not comprimido.is_file():
    raise FileNotFoundError(f"No se encontró el comprimido: {comprimido}")
if not tar.is_file():
    raise FileNotFoundError(f"No se encontró la herramienta: {tar}")

# Los contadores comienzan en cero; todavía no hemos leído ninguna fila.
total = 0
conteos = {"0": 0, "1": 0}
filas_mal_formadas = 0
etiquetas_invalidas = 0
usuarios_vacios = 0
```

**Qué debes entender:** las claves del diccionario `conteos` son textos porque el lector CSV entrega texto. `conteos["1"]` almacenará el número de etiquetas de abandono. No existe todavía un modelo ni una probabilidad calculada.

## Bloque 2. Leer el CSV progresivamente

```python
# -x extrae el contenido; -O lo envía a la salida estándar, no a un CSV en disco.
# -f indica qué comprimido abrir; después indicamos qué archivo interno leer.
# Cada argumento ocupa una posición de la lista; así se manejan rutas con espacios.
comando = [str(tar), "-xOf", str(comprimido), ruta_interna]

# Popen inicia tar y permite consumir su salida mientras sigue trabajando.
# PIPE conecta esa salida con Python, en lugar de mostrar todas las filas.
# text=True la entrega como texto; utf-8-sig admite una marca BOM inicial.
# Los errores de tar quedan visibles en la terminal porque no redirigimos stderr.
proceso = subprocess.Popen(
    comando,
    stdout=subprocess.PIPE,
    text=True,
    encoding="utf-8-sig",
)

try:
    # DictReader usa la primera fila como nombres de columnas.
    # Cada iteración posterior devuelve un diccionario que representa una fila.
    lector = csv.DictReader(proceso.stdout)

    # Comprobamos el esquema antes de confiar en el contenido.
    if lector.fieldnames != ["msno", "is_churn"]:
        raise ValueError(f"Cabecera inesperada: {lector.fieldnames}")

    # Este bucle consume una fila cada vez, sin convertir el CSV entero en una lista.
    for fila in lector:
        total += 1

        # DictReader usa la clave None si sobran campos; valores None si faltan.
        if None in fila or any(valor is None for valor in fila.values()):
            filas_mal_formadas += 1
            continue  # Saltamos los cálculos restantes para esta fila incorrecta.

        # strip() retira espacios al principio y al final del texto.
        usuario = fila["msno"].strip()
        etiqueta = fila["is_churn"].strip()

        # Contamos identificadores ausentes sin inventar uno para reemplazarlos.
        if usuario == "":
            usuarios_vacios += 1

        # Solo 0 y 1 son etiquetas reconocidas en este ejercicio.
        if etiqueta in conteos:
            conteos[etiqueta] += 1
        else:
            etiquetas_invalidas += 1

    # Esperamos que tar termine y comprobamos si informó un error.
    codigo_salida = proceso.wait()
    if codigo_salida != 0:
        raise RuntimeError(f"La extracción terminó con código {codigo_salida}")
finally:
    # Cerramos el canal incluso si ocurrió un error durante la lectura.
    proceso.stdout.close()

    # Si falló Python y tar seguía trabajando, lo detenemos y esperamos su cierre.
    # Así no queda un descompresor ejecutándose tras terminar este programa.
    if proceso.poll() is None:
        proceso.terminate()
    proceso.wait()
```

**Cómo fluye la información:** tar descomprime el archivo y produce texto; Python consume ese texto mediante un canal, llamado pipe. La lectura es progresiva, pero el descompresor sigue necesitando memoria para sus estructuras internas. No se promete consumo de memoria nulo ni lectura instantánea.

`try` contiene el trabajo principal; `finally` garantiza la limpieza del proceso. Un código de salida distinto de cero impide presentar un recorrido incompleto como si hubiera terminado bien.

No hay `extractall`, no se crea el CSV gigante y no se usa `list(lector)` ni `read()` para cargar todo el contenido a la vez.

## Bloque 3. Mostrar y comprobar el resumen

```python
# Mostramos conteos agregados, no los identificadores de los usuarios.
print("Filas leídas:", total)
print("Renovación (0):", conteos["0"])
print("Abandono (1):", conteos["1"])
print("Filas mal formadas:", filas_mal_formadas)
print("Etiquetas inválidas:", etiquetas_invalidas)
print("Identificadores vacíos:", usuarios_vacios)

# Toda fila debe quedar en exactamente una de estas cuatro categorías.
clasificadas = sum(conteos.values()) + etiquetas_invalidas + filas_mal_formadas
if clasificadas != total:
    raise RuntimeError("Los conteos no coinciden con el total de filas")

# Este porcentaje describe etiquetas reconocidas; no es rendimiento de un modelo.
etiquetas_validas = sum(conteos.values())
if etiquetas_validas > 0:
    porcentaje = 100 * conteos["1"] / etiquetas_validas
    print(f"Abandono entre etiquetas reconocidas: {porcentaje:.2f}%")
else:
    print("No hay etiquetas reconocidas para calcular el porcentaje")

# Una lectura exitosa no garantiza que los datos estén listos para entrenar.
if filas_mal_formadas or etiquetas_invalidas or usuarios_vacios:
    print("Hay incidencias que debemos revisar antes de usar estos datos")
```

`sum(conteos.values())` suma los dos contadores. La expresión `:.2f` muestra dos decimales. El indicador `usuarios_vacios` puede coincidir con una fila que tiene etiqueta reconocida; por eso no se suma a la comprobación de partición de filas. El porcentaje no certifica usuarios válidos o únicos: cuenta etiquetas por fila.

## Ejecución

En una terminal PowerShell abierta en la raíz del proyecto, ejecuta:

```powershell
& 'C:\Users\HP\anaconda3\python.exe' scripts/02_revisar_etiquetas.py
```

Usamos el intérprete comprobado para evitar ejecutar accidentalmente otro Python. El programa muestra el resumen al terminar; no tiene barra de progreso. No realiza ningún entrenamiento ni modifica los datos originales.

## Qué revisar y compartir

Comparte la salida completa del resumen o el error exacto si falla. No hay cifras de abandono anticipadas: todavía no hemos ejecutado este procesamiento sobre el conjunto correcto.

Antes de pasar al siguiente ejercicio, deberías poder explicar:

1. Por qué la clave del contador es `"1"` y no el entero `1`.
2. Por qué este programa no necesita guardar el CSV descomprimido completo.
3. Por qué el porcentaje de abandono no es la exactitud de un modelo.
4. Qué diferencia hay entre contar filas y contar usuarios únicos.

Con tu resultado revisaremos la distribución y los errores. Después avanzaremos a comprobar usuarios únicos y la relación entre las versiones, y finalmente a fijar la evaluación y la línea base. No se seleccionará un corte temporal únicamente a partir del nombre de un archivo.
