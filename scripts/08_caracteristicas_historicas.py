import csv
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data" / "derived"
archivo_piloto = carpeta / "piloto_2016-03-07.csv"
archivo_candidatos = carpeta / "candidatos_2016-03-07.csv"
archivo_etiquetas = carpeta / "etiquetas_piloto_2016-03-07.csv"
salida = carpeta / "cohorte_2016-03-07.csv"
corte = date(2016, 3, 7)
inicio_90 = corte - timedelta(days=90)
inicio_30 = corte - timedelta(days=30)

# Lista explícita: más adelante X se construirá SOLO con estas columnas.
CARACTERISTICAS = [
    "transacciones_90d", "transacciones_30d", "cancelaciones_90d",
    "dias_con_transacciones_90d", "dias_desde_ultima_transaccion",
    "dias_hasta_vencimiento",
]

def leer_fecha(texto):
    texto = texto.strip()
    if len(texto) != 8 or not texto.isascii() or not texto.isdigit():
        raise ValueError(f"Formato de fecha inválido: {texto!r}")
    return date(int(texto[:4]), int(texto[4:6]), int(texto[6:8]))

candidatos = {}
with archivo_candidatos.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "corte", "vencimiento_conocido",
                  "ultima_transaccion_historica", "transacciones_historicas"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera inesperada en candidatos")
    for fila in lector:
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Candidato mal formado")
        usuario = fila["msno"].strip()
        if not usuario or usuario in candidatos:
            raise ValueError("Identificador vacío o repetido en candidatos")
        if date.fromisoformat(fila["corte"]) != corte:
            raise ValueError("Candidato de otro corte")
        vence = date.fromisoformat(fila["vencimiento_conocido"])
        if not corte <= vence <= corte + timedelta(days=29):
            raise ValueError("Vencimiento fuera de candidatos")
        candidatos[usuario] = {
            "vence": vence,
            "ultima": date.fromisoformat(fila["ultima_transaccion_historica"]),
            "cantidad": int(fila["transacciones_historicas"]),
        }
if len(candidatos) != 7443:
    raise ValueError("No corresponde al piloto de 7.443 candidatos")

# Un acumulador independiente por candidato; aún no hemos leído is_churn.
acumuladores = {
    usuario: {"n90": 0, "n30": 0, "cancelaciones": 0,
              "fechas": set(), "ultima": None}
    for usuario in candidatos
}

filas_piloto = 0
filas_futuras_excluidas = 0
filas_historicas_candidatos = 0
with archivo_piloto.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "transaction_date", "is_cancel"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera inesperada en piloto")
    for fila in lector:
        filas_piloto += 1
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Evento mal formado")
        fecha = leer_fecha(fila["transaction_date"])
        if fecha >= corte:
            filas_futuras_excluidas += 1
            continue  # Esta exclusión ocurre ANTES de cualquier acumulación.
        if fecha < inicio_90:
            raise ValueError("Historia fuera de la ventana esperada")
        usuario = fila["msno"].strip()
        if not usuario:
            raise ValueError("Evento sin usuario")
        if usuario not in acumuladores:
            continue  # No todos los usuarios del piloto fueron candidatos.
        cancelacion = fila["is_cancel"].strip()
        if cancelacion not in {"0", "1"}:
            raise ValueError("is_cancel inválido")
        a = acumuladores[usuario]
        a["n90"] += 1
        a["n30"] += int(fecha >= inicio_30)
        a["cancelaciones"] += int(cancelacion == "1")
        a["fechas"].add(fecha)
        if a["ultima"] is None or fecha > a["ultima"]:
            a["ultima"] = fecha
        filas_historicas_candidatos += 1

if filas_piloto != 40503 or filas_futuras_excluidas != 15449:
    raise ValueError("Los tamaños no coinciden con el piloto revisado")

# Construimos X por usuario antes de cargar las etiquetas.
caracteristicas = {}
for usuario, a in acumuladores.items():
    referencia = candidatos[usuario]
    if a["ultima"] is None:
        raise ValueError("Hay un candidato sin historia")
    if a["n90"] != referencia["cantidad"] or a["ultima"] != referencia["ultima"]:
        raise ValueError("La historia no coincide con el archivo de candidatos")
    valores = {
        "transacciones_90d": a["n90"],
        "transacciones_30d": a["n30"],
        "cancelaciones_90d": a["cancelaciones"],
        "dias_con_transacciones_90d": len(a["fechas"]),
        "dias_desde_ultima_transaccion": (corte - a["ultima"]).days,
        "dias_hasta_vencimiento": (referencia["vence"] - corte).days,
    }
    if not 0 <= a["n30"] <= a["n90"]:
        raise ValueError("Conteos de 30/90 días inconsistentes")
    if not 0 <= a["cancelaciones"] <= a["n90"]:
        raise ValueError("Conteo de cancelaciones inconsistente")
    if not 1 <= len(a["fechas"]) <= min(90, a["n90"]):
        raise ValueError("Cantidad de fechas distintas inválida")
    if not 1 <= valores["dias_desde_ultima_transaccion"] <= 90:
        raise ValueError("Distancia histórica fuera de ventana")
    if not 0 <= valores["dias_hasta_vencimiento"] <= 29:
        raise ValueError("Distancia al vencimiento fuera de candidatos")
    caracteristicas[usuario] = valores

etiquetas = {}
with archivo_etiquetas.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "corte", "is_churn", "observado_hasta"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera inesperada en etiquetas")
    for fila in lector:
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Etiqueta mal formada")
        usuario = fila["msno"].strip()
        if not usuario or usuario in etiquetas:
            raise ValueError("Identificador vacío o repetido en etiquetas")
        if date.fromisoformat(fila["corte"]) != corte:
            raise ValueError("Etiqueta de otro corte")
        if date.fromisoformat(fila["observado_hasta"]) != date(2016, 5, 5):
            raise ValueError("Etiqueta con otro seguimiento")
        if fila["is_churn"] not in {"0", "1"}:
            raise ValueError("Etiqueta desconocida o inválida: revisar, no eliminar")
        etiquetas[usuario] = int(fila["is_churn"])

if set(etiquetas) != set(caracteristicas):
    raise ValueError("Usuarios de etiquetas y características no coinciden")

filas_salida = []
for usuario in sorted(caracteristicas):
    filas_salida.append({
        "msno": usuario,
        "corte": corte.isoformat(),
        **caracteristicas[usuario],
        "is_churn": etiquetas[usuario],
    })

columnas = ["msno", "corte", *CARACTERISTICAS, "is_churn"]
with salida.open("x", encoding="utf-8", newline="") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=columnas)
    escritor.writeheader()
    escritor.writerows(filas_salida)

clases = Counter(etiquetas.values())
print("Corte:", corte)
print("Filas del piloto recorridas:", filas_piloto)
print("Filas futuras excluidas:", filas_futuras_excluidas)
print("Filas históricas de candidatos utilizadas:", filas_historicas_candidatos)
print("Usuarios / filas de la cohorte:", len(filas_salida))
print("Características:", len(CARACTERISTICAS))
print("Renovación (0):", clases[0])
print("Abandono (1):", clases[1])
print("Resumen de características: mínimo / máximo / promedio")
for nombre in CARACTERISTICAS:
    valores = [fila[nombre] for fila in filas_salida]
    print(f"  {nombre}: {min(valores)} / {max(valores)} / "
          f"{sum(valores) / len(valores):.2f}")
print("Archivo local:", salida)
print("Tabla preparada; ningún modelo entrenado ni evaluado.")
