# Hito 2 — Paso 5: comprobar las fechas de las transacciones

## Objetivo y alcance

Comprobar qué fechas contiene realmente `transactions_v2.csv.7z`: rango de fechas de transacción, cantidad de transacciones por mes y fechas vacías o inválidas. También revisaremos la validez de las fechas de vencimiento. Esto ayuda a elegir un corte de predicción sin utilizar eventos posteriores.

Tú escribirás y ejecutarás el programa. Esta guía no es una ejecución ni contiene resultados observados. No entrenaremos un modelo en este paso. El comprimido tiene aproximadamente 49 MB y su CSV interno 115 MB según el inventario; no necesitas guardar ese CSV descomprimido.

## 1. Crea un archivo separado

Crea `scripts/03_revisar_fechas.py`. No añadas este ejercicio al script anterior: así no tendrás que volver a recorrer las etiquetas cada vez que revises fechas.

Copia o escribe los cuatro bloques siguientes, en orden, en ese mismo archivo. Lee las explicaciones antes de ejecutarlo.

## 2. Importaciones, rutas y validación de fechas

```python
# csv interpreta las columnas del CSV sin cargar el archivo entero.
import csv
# subprocess permite recibir la salida del descompresor tar.
import subprocess
# Counter acumula cuántas veces aparece cada categoría o mes.
from collections import Counter
# date construye fechas y rechaza días o meses imposibles.
from datetime import date
# Path permite construir rutas independientes del directorio de la terminal.
from pathlib import Path

# __file__ es este script; parents[1] sube de scripts a la raíz del proyecto.
raiz = Path(__file__).resolve().parents[1]
comprimido = raiz / "data" / "kkbox-churn-prediction-challenge" / "transactions_v2.csv.7z"
# Es la ruta DENTRO del comprimido, no una carpeta que debas crear.
ruta_interna = "data/churn_comp_refresh/transactions_v2.csv"
tar = Path(r"C:\Windows\System32\tar.exe")

# Fallamos pronto si no están los archivos necesarios.
for archivo in (tar, comprimido):
    if not archivo.is_file():
        raise FileNotFoundError(f"No se encontró: {archivo}")


def revisar_fecha(texto):
    # Quitamos espacios alrededor; no corregimos fechas imposibles.
    texto = texto.strip()
    if texto == "":
        return "vacia", None

    # Exigimos ocho dígitos ASCII: YYYYMMDD, por ejemplo 20170306.
    if len(texto) != 8 or not texto.isascii() or not texto.isdigit():
        return "invalida", None

    try:
        # Los cortes separan año, mes y día; int convierte texto a enteros.
        fecha = date(int(texto[:4]), int(texto[4:6]), int(texto[6:8]))
    except ValueError:
        # Ejemplo: 20170230 tiene ocho dígitos, pero no existe en el calendario.
        return "invalida", None

    return "valida", fecha
```

La función devuelve dos elementos: una categoría y una fecha, o `None` cuando no hay fecha utilizable. `return` termina esa llamada a la función. `try/except` permite contar una fecha imposible sin detener todo el recorrido. Una fecha válida de calendario todavía podría ser incorrecta para el negocio: este control no prueba su veracidad.

## 3. Prepara los contadores y abre el flujo

```python
filas_leidas = 0
filas_mal_formadas = 0
# Revisamos las dos columnas por separado: una puede fallar y la otra ser válida.
columnas_fecha = ("transaction_date", "membership_expire_date")
estados = {columna: Counter() for columna in columnas_fecha}
por_mes = Counter()
fecha_minima = None
fecha_maxima = None

proceso = subprocess.Popen(
    # -x extrae, -O envía el contenido a stdout y -f indica el comprimido.
    [str(tar), "-xOf", str(comprimido), ruta_interna],
    # Python lee esa salida como un flujo de texto, no como un CSV en disco.
    stdout=subprocess.PIPE,
    text=True,
    encoding="utf-8-sig",  # También admite una marca BOM al comienzo.
)
```

`Counter` devuelve cero para una clave que todavía no existe. `por_mes["2017-03"] += 1` crea o incrementa el conteo de marzo. `None` significa que todavía no hemos encontrado una fecha válida. Los mensajes de error de tar aparecen en la terminal porque no redirigimos su salida de errores.

## 4. Recorre y comprueba las filas

```python
try:
    lector = csv.DictReader(proceso.stdout)
    cabecera = lector.fieldnames
    # Aceptamos las demás columnas del dataset, pero exigimos estas dos.
    if not cabecera or not set(columnas_fecha).issubset(cabecera):
        raise ValueError(f"Faltan columnas de fecha. Cabecera: {cabecera}")
    if len(cabecera) != len(set(cabecera)):
        raise ValueError("La cabecera contiene nombres repetidos")

    for fila in lector:
        filas_leidas += 1
        # DictReader usa None cuando sobran campos o faltan valores de columnas.
        if None in fila or any(valor is None for valor in fila.values()):
            filas_mal_formadas += 1
            continue  # Esta fila no entra en ninguno de los controles de fechas.

        for columna in columnas_fecha:
            estado, fecha = revisar_fecha(fila[columna])
            estados[columna][estado] += 1

            # El rango y los meses describen eventos, no vencimientos.
            if columna == "transaction_date" and estado == "valida":
                mes = f"{fecha.year:04d}-{fecha.month:02d}"
                por_mes[mes] += 1
                if fecha_minima is None or fecha < fecha_minima:
                    fecha_minima = fecha
                if fecha_maxima is None or fecha > fecha_maxima:
                    fecha_maxima = fecha

    # Solo consideramos completo el recorrido si tar terminó correctamente.
    codigo = proceso.wait()
    if codigo != 0:
        raise RuntimeError(f"tar terminó con código {codigo}; no usar este resumen")
finally:
    # Cerramos los recursos incluso si ocurre un error o interrumpes la lectura.
    proceso.stdout.close()
    if proceso.poll() is None:
        proceso.terminate()
    proceso.wait()
```

`issubset` comprueba que las columnas requeridas existen. `continue` salta a la siguiente fila. La asignación `estado, fecha = ...` desempaqueta los dos resultados de la función. El formato `04d` escribe el año con cuatro cifras y `02d` el mes con dos.

El mínimo y el máximo se actualizan comparando fechas reales. No guardamos una lista de todas las filas: conservamos la fila actual y contadores pequeños. El descompresor y Python sí consumen memoria; lectura progresiva no significa consumo cero. Debes dejar terminar el archivo entero: parar a mitad no demuestra su rango completo.

## 5. Verifica las sumas e imprime el informe

```python
filas_con_estructura_valida = filas_leidas - filas_mal_formadas
for columna in columnas_fecha:
    # Cada fila estructuralmente válida aporta una categoría por columna.
    if sum(estados[columna].values()) != filas_con_estructura_valida:
        raise RuntimeError(f"No cuadran los controles de {columna}")

if sum(por_mes.values()) != estados["transaction_date"]["valida"]:
    raise RuntimeError("Los conteos mensuales no cuadran con las fechas válidas")

print("Archivo:", comprimido.name)
print("Filas leídas:", filas_leidas)
print("Filas mal formadas:", filas_mal_formadas)
for columna in columnas_fecha:
    print(f"\nColumna: {columna}")
    for estado in ("valida", "vacia", "invalida"):
        print(f"  {estado}: {estados[columna][estado]}")

print("\nPrimera fecha de transacción:", fecha_minima)
print("Última fecha de transacción:", fecha_maxima)
print("Transacciones por mes:")
for mes, cantidad in sorted(por_mes.items()):
    print(f"  {mes}: {cantidad}")

if fecha_minima is None:
    print("No se encontraron fechas de transacción válidas")
if filas_mal_formadas or any(
    estados[columna]["vacia"] + estados[columna]["invalida"]
    for columna in columnas_fecha
):
    print("Hay incidencias: revisarlas antes de fijar el corte temporal")
```

`sorted` ordena los meses de más antiguo a más reciente porque usamos el formato año-mes con anchura fija. Los controles son identidades contables, no una prueba de que el dataset esté completo. Las filas mal formadas se informan aparte; sus fechas no se clasifican como vacías ni inválidas.

## 6. Ejecución

En una terminal PowerShell abierta en la raíz del proyecto:

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\03_revisar_fechas.py"
```

No requiere instalar paquetes nuevos: todos los módulos usados pertenecen a Python. El programa no imprime progreso durante el recorrido; espera a que termine. Si aparece una excepción, comparte el mensaje completo en lugar de tratar una salida parcial como resultado válido.

Comparte toda la salida del informe. No hay conteos esperados inventados: contrastaremos el máximo observado con la documentación, que describe transactions_v2 hasta el 31 de marzo de 2017. Un máximo diferente merece investigación; no debe corregirse automáticamente. El nombre v2 no garantiza qué meses contiene ni que incluya todo el historial original.

## 7. Qué podemos concluir y qué no

- El rango se refiere a fechas de transacción válidas de las filas revisadas. Si hubo incidencias, no representa necesariamente todas las fechas del archivo.
- Los conteos son transacciones, no usuarios únicos. Un mismo usuario puede tener varios pagos o cancelaciones.
- Un vencimiento posterior al corte puede ser conocido de antemano. Por ejemplo, una compra registrada antes del domingo puede informar que la suscripción vencerá el mes siguiente. No debe descartarse solo porque su vencimiento esté en el futuro.
- La fecha del evento es nuestra aproximación inicial a su disponibilidad. No prueba que no hubiera retrasos en su registro.
- Llegar al 31 de marzo no demuestra seguimiento suficiente para cualquier usuario ni etiquetas para todos los lunes. Tampoco demuestra que no falten días o eventos entre el mínimo y el máximo.
- No construiremos etiquetas semanales ni elegiremos automáticamente entrenamiento/prueba a partir de este informe.

Después de revisar tu salida, podremos aplicar el mismo control al archivo original y contrastar ambos periodos. Todavía no necesitas recorrer los archivos grandes de escucha.

## 8. Preguntas para explicar con tus palabras

1. ¿Por qué comprobamos ocho dígitos y también construimos una fecha de calendario?
2. ¿Por qué contamos los meses usando transaction_date y no membership_expire_date?
3. ¿Por qué una transacción anterior al corte puede tener un vencimiento posterior sin que eso sea información futura?
4. ¿Por qué conocer el máximo del archivo no basta para afirmar que podemos evaluar todos los lunes?

Las respuestas de referencia quedan en `Conceptos clave/Preguntas de repaso.md`. Intenta responder primero sin consultarlas.
