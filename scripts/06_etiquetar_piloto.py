import csv
from collections import defaultdict, Counter
from datetime import date, timedelta
from functools import cmp_to_key
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data" / "derived"
archivo_candidatos = carpeta / "candidatos_2016-03-07.csv"
archivo_eventos = carpeta / "piloto_2016-03-07.csv"
salida = carpeta / "etiquetas_piloto_2016-03-07.csv"
corte = date(2016, 3, 7)
inicio = corte - timedelta(days=90)
fin_vencimientos = corte + timedelta(days=29)
# Es el final de la ventana extraída, no el último evento de cada usuario.
fin_observacion = fin_vencimientos + timedelta(days=30)

def leer_fecha(texto):
    texto = texto.strip()
    if len(texto) != 8 or not texto.isascii() or not texto.isdigit():
        raise ValueError(f"Formato de fecha inválido: {texto!r}")
    return date(int(texto[:4]), int(texto[4:6]), int(texto[6:8]))

def comparar_eventos(a, b):
    # Un resultado negativo coloca a antes que b; positivo, después; cero, empate.
    if a["fecha"] != b["fecha"]:
        return -1 if a["fecha"] < b["fecha"] else 1

    # Mismo día: firma del plan en orden descendente, como texto en el Scala.
    if a["firma"] != b["firma"]:
        return -1 if a["firma"] > b["firma"] else 1

    # Misma firma y día: renovación antes que cancelación.
    if a["cancelacion"] != b["cancelacion"]:
        return -1 if a["cancelacion"] < b["cancelacion"] else 1

    if a["vencimiento"] == b["vencimiento"]:
        return 0
    if a["cancelacion"] == "1":
        # Entre cancelaciones, el vencimiento más temprano queda al final.
        return -1 if a["vencimiento"] > b["vencimiento"] else 1
    # Entre renovaciones, el vencimiento más tardío queda al final.
    return -1 if a["vencimiento"] < b["vencimiento"] else 1

def etiquetar(vencimiento, eventos, observado_hasta):
    # Esta variable puede adelantarse por cancelaciones posteriores al corte.
    efectivo = vencimiento
    renovacion = None
    gap = None

    for evento in sorted(eventos, key=cmp_to_key(comparar_eventos)):
        if evento["fecha"] > observado_hasta:
            raise ValueError("Evento posterior al seguimiento declarado")
        if evento["cancelacion"] == "1":
            efectivo = min(efectivo, evento["vencimiento"])
        else:
            renovacion = evento["fecha"]
            gap = (renovacion - efectivo).days
            break  # Como en Scala, detenemos la búsqueda en la primera renovación.

    if renovacion is not None:
        etiqueta = 0 if gap < 30 else 1
        motivo = "renovacion_oportuna" if etiqueta == 0 else "renovacion_tardia"
    elif observado_hasta >= efectivo + timedelta(days=30):
        etiqueta = 1  # Depende del supuesto explícito de cobertura del historial.
        motivo = "sin_renovacion_en_plazo"
    else:
        etiqueta = None  # No sabemos el resultado: no equivale a abandono.
        motivo = "seguimiento_insuficiente"

    return {
        "is_churn": etiqueta,
        "motivo": motivo,
        "vencimiento_efectivo": efectivo.isoformat(),
        "primera_renovacion": renovacion.isoformat() if renovacion else "",
        "gap_dias": gap,
    }

def evento_ejemplo(fecha, cancelacion="0", vence="2016-04-20"):
    return {
        "fecha": date.fromisoformat(fecha),
        "vencimiento": date.fromisoformat(vence),
        "cancelacion": cancelacion,
        "firma": "plan-ejemplo",
    }

v = date(2016, 3, 20)
f = date(2016, 5, 5)
casos = [
    ("anticipada", [evento_ejemplo("2016-03-10")], f, 0),
    ("a los 29 dias", [evento_ejemplo("2016-04-18")], f, 0),
    ("a los 30 dias", [evento_ejemplo("2016-04-19")], f, 1),
    ("sin eventos, plazo cubierto", [], f, 1),
    ("sin eventos, plazo insuficiente", [], date(2016, 4, 1), None),
    ("cancelacion y renovacion oportuna", [
        evento_ejemplo("2016-03-10", "1", "2016-03-10"),
        evento_ejemplo("2016-03-15"),
    ], f, 0),
    ("cancelacion adelanta el limite", [
        evento_ejemplo("2016-03-10", "1", "2016-03-10"),
        evento_ejemplo("2016-04-09"),
    ], f, 1),
    ("sin renovar tras cancelacion", [
        evento_ejemplo("2016-03-10", "1", "2016-03-10"),
    ], f, 1),
    ("mismo dia: renovacion antes de cancelacion", [
        evento_ejemplo("2016-03-10", "1", "2016-03-10"),
        evento_ejemplo("2016-03-10"),
    ], f, 0),
]
for nombre, eventos, final, esperado in casos:
    obtenido = etiquetar(v, eventos, final)["is_churn"]
    if obtenido != esperado:
        raise AssertionError(f"{nombre}: esperado {esperado}, obtenido {obtenido}")
print("Casos ilustrativos correctos:", len(casos))

candidatos = {}
with archivo_candidatos.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "corte", "vencimiento_conocido"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera de candidatos inesperada")
    for fila in lector:
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Fila de candidato mal formada")
        usuario = fila["msno"].strip()
        if not usuario or usuario in candidatos:
            raise ValueError("Identificador vacío o repetido en candidatos")
        if date.fromisoformat(fila["corte"]) != corte:
            raise ValueError("El candidato pertenece a otro corte")
        vence = date.fromisoformat(fila["vencimiento_conocido"])
        if not corte <= vence <= fin_vencimientos:
            raise ValueError("Vencimiento fuera de la ventana de candidatos")
        candidatos[usuario] = vence
if not candidatos:
    raise ValueError("No hay candidatos")

seguimiento = defaultdict(list)
filas_piloto = 0
with archivo_eventos.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "transaction_date", "membership_expire_date",
                  "is_cancel", "plan_list_price", "payment_plan_days", "payment_method_id"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera del piloto inesperada")
    for fila in lector:
        filas_piloto += 1
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Fila de evento mal formada")
        fecha = leer_fecha(fila["transaction_date"])
        if not inicio <= fecha <= fin_observacion:
            raise ValueError("Evento fuera de la ventana extraída")
        usuario = fila["msno"].strip()
        if not usuario:
            raise ValueError("Evento sin usuario")
        if fecha < corte or usuario not in candidatos:
            continue  # La historia ya sirvió para seleccionar candidatos.
        cancelacion = fila["is_cancel"].strip()
        if cancelacion not in {"0", "1"}:
            raise ValueError("is_cancel inválido")
        plan = [fila[c] for c in
                ("plan_list_price", "payment_plan_days", "payment_method_id")]
        if any(not valor.strip() for valor in plan):
            raise ValueError("Campo de plan vacío")
        seguimiento[usuario].append({
            "fecha": fecha,
            "vencimiento": leer_fecha(fila["membership_expire_date"]),
            "cancelacion": cancelacion,
            "firma": "".join(plan),
        })

# Para este ejercicio conocemos los tamaños del piloto y candidatos ya revisados.
if filas_piloto != 40503 or len(candidatos) != 7443:
    raise ValueError("Los tamaños no coinciden con el piloto revisado; investigar")

resultados = []
por_etiqueta = Counter()
por_motivo = Counter()
sin_eventos = 0
adelantados = 0

for usuario, vencimiento in sorted(candidatos.items()):
    eventos = seguimiento.get(usuario, [])
    sin_eventos += int(not eventos)
    resultado = etiquetar(vencimiento, eventos, fin_observacion)
    adelantados += int(date.fromisoformat(resultado["vencimiento_efectivo"]) < vencimiento)
    por_etiqueta[resultado["is_churn"]] += 1
    por_motivo[resultado["motivo"]] += 1
    resultados.append({
        "msno": usuario,
        "corte": corte.isoformat(),
        "vencimiento_conocido": vencimiento.isoformat(),
        "observado_hasta": fin_observacion.isoformat(),
        "supuesto_cobertura": "historial_publicado_completo_en_ventana",
        **resultado,
    })

if sum(por_etiqueta.values()) != len(candidatos):
    raise RuntimeError("No cuadra el total de etiquetas")
if sum(por_motivo.values()) != len(candidatos):
    raise RuntimeError("No cuadra el total de motivos")

# El orden de las claves del primer diccionario define las columnas del CSV.
with salida.open("x", encoding="utf-8", newline="") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=list(resultados[0]))
    escritor.writeheader()
    escritor.writerows(resultados)

print("Candidatos procesados:", len(candidatos))
print("Candidatos sin eventos de seguimiento:", sin_eventos)
print("Vencimientos adelantados antes de primera renovacion:", adelantados)
print("Renovacion (0):", por_etiqueta[0])
print("Abandono (1):", por_etiqueta[1])
print("Sin etiqueta:", por_etiqueta[None])
for motivo, cantidad in sorted(por_motivo.items()):
    print(f"  {motivo}: {cantidad}")
con_etiqueta = por_etiqueta[0] + por_etiqueta[1]
if con_etiqueta:
    print("Abandono entre etiquetados:",
          f"{100 * por_etiqueta[1] / con_etiqueta:.2f}%")
print("Seguimiento declarado hasta:", fin_observacion)
print("Etiquetas reconstruidas bajo supuesto de cobertura; no oficiales")
print("Archivo local:", salida)
