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
comprimido = raiz / "data" / "kkbox-churn-prediction-challenge" / "transactions.csv.7z"
# Es la ruta DENTRO del comprimido, no una carpeta que debas crear.
ruta_interna = "transactions.csv"
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
