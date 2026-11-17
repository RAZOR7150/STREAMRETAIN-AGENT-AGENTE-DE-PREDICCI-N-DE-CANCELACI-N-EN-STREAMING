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

# Cada clave será un identificador de usuario.
# Cada valor será un conjunto de las etiquetas observadas para ese usuario.
etiquetas_por_usuario = {}

# Cuenta apariciones adicionales de usuarios ya registrados.
filas_repetidas_usuario = 0

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

        # Solo estudiamos identidad y contradicciones en registros utilizables.
        # Las incidencias de los demás registros ya se cuentan por separado.
        if usuario != "" and etiqueta in conteos:
            if usuario in etiquetas_por_usuario:
                # El usuario ya apareció: esta es una fila adicional de ese usuario.
                filas_repetidas_usuario += 1
            else:
                # Un usuario nuevo comienza con un conjunto vacío de etiquetas.
                etiquetas_por_usuario[usuario] = set()

            # Añadimos la etiqueta al conjunto del usuario.
            # add no crea otra copia si esa etiqueta ya estaba presente.
            etiquetas_por_usuario[usuario].add(etiqueta)


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

# len aplicado al diccionario cuenta sus claves: usuarios diferentes.
usuarios_unicos = len(etiquetas_por_usuario)

# Contaremos cada usuario contradictorio una vez, aunque tenga muchas filas.
usuarios_con_conflicto = 0
for etiquetas_observadas in etiquetas_por_usuario.values():
    # Un conjunto con dos etiquetas contiene tanto 0 como 1.
    if len(etiquetas_observadas) > 1:
        usuarios_con_conflicto += 1

print("Usuarios únicos con etiqueta válida:", usuarios_unicos)
print("Filas adicionales de usuarios repetidos:", filas_repetidas_usuario)
print("Usuarios con etiquetas contradictorias:", usuarios_con_conflicto)

# Estas dos cantidades reconstruyen las filas incluidas en este análisis.
print("Filas con usuario y etiqueta válidos:", usuarios_unicos + filas_repetidas_usuario)

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
