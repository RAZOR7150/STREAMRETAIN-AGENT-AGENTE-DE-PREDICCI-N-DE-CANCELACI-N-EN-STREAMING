import csv
from collections import defaultdict, Counter
from datetime import date, timedelta
from functools import cmp_to_key
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data" / "derived"
salida = raiz / "docs" / "auditorias" / "piloto_2016-03-07.md"
corte = date(2016, 3, 7)
inicio = corte - timedelta(days=90)
fin = date(2016, 5, 5)

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

etiquetas = {}
with (carpeta / "etiquetas_piloto_2016-03-07.csv").open(
    encoding="utf-8-sig", newline=""
) as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "corte", "vencimiento_conocido", "observado_hasta",
                  "is_churn", "motivo", "vencimiento_efectivo",
                  "primera_renovacion", "gap_dias"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera de etiquetas inesperada")

    for numero, fila in enumerate(lector, start=1):
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError(f"Fila mal formada: {numero}")
        usuario = fila["msno"].strip()
        if not usuario or usuario in etiquetas:
            raise ValueError(f"Identificador vacío o repetido: fila {numero}")
        if date.fromisoformat(fila["corte"]) != corte:
            raise ValueError("Otro corte en etiquetas")
        if date.fromisoformat(fila["observado_hasta"]) != fin:
            raise ValueError("Otro final de seguimiento")
        conocido = date.fromisoformat(fila["vencimiento_conocido"])
        efectivo = date.fromisoformat(fila["vencimiento_efectivo"])
        if not corte <= conocido <= corte + timedelta(days=29):
            raise ValueError("Vencimiento conocido fuera de candidatos")
        if efectivo > conocido:
            raise ValueError("La regla solo permite adelantar el vencimiento")

        if fila["primera_renovacion"]:
            renovacion = date.fromisoformat(fila["primera_renovacion"])
            if not corte <= renovacion <= fin:
                raise ValueError("Renovación fuera del seguimiento")
            gap = int(fila["gap_dias"])
            if gap != (renovacion - efectivo).days:
                raise ValueError("Gap inconsistente con las fechas guardadas")
            esperado = "0" if gap < 30 else "1"
            motivo = "renovacion_oportuna" if gap < 30 else "renovacion_tardia"
        else:
            if fila["gap_dias"] != "":
                raise ValueError("Sin renovación el gap debe estar vacío")
            completo = fin >= efectivo + timedelta(days=30)
            esperado = "1" if completo else ""
            motivo = "sin_renovacion_en_plazo" if completo else "seguimiento_insuficiente"
        if fila["is_churn"] != esperado or fila["motivo"] != motivo:
            raise ValueError(f"Etiqueta o motivo inconsistente: fila {numero}")
        etiquetas[usuario] = fila

if len(etiquetas) != 7443:
    raise ValueError("No coincide el número de candidatos del piloto")

historia = defaultdict(list)
seguimiento = defaultdict(list)
leidas = 0
with (carpeta / "piloto_2016-03-07.csv").open(
    encoding="utf-8-sig", newline=""
) as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "transaction_date", "membership_expire_date",
                  "is_cancel", "plan_list_price", "payment_plan_days", "payment_method_id"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera de eventos inesperada")
    for fila in lector:
        leidas += 1
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Evento mal formado")
        usuario = fila["msno"].strip()
        if usuario not in etiquetas:
            continue
        fecha = leer_fecha(fila["transaction_date"])
        if not inicio <= fecha <= fin:
            raise ValueError("Evento fuera de ventana")
        cancelacion = fila["is_cancel"].strip()
        if cancelacion not in {"0", "1"}:
            raise ValueError("Cancelación inválida")
        plan = [fila[c] for c in
                ("plan_list_price", "payment_plan_days", "payment_method_id")]
        if any(not valor.strip() for valor in plan):
            raise ValueError("Falta información del plan")
        evento = {
            "fecha": fecha,
            "vencimiento": leer_fecha(fila["membership_expire_date"]),
            "cancelacion": cancelacion,
            "firma": "".join(plan),
        }
        destino = historia if fecha < corte else seguimiento
        destino[usuario].append(evento)
if leidas != 40503:
    raise ValueError("El piloto no tiene el tamaño previamente revisado")
if any(not historia[u] for u in etiquetas):
    raise ValueError("Hay un candidato sin historia")

def tiene_gap(fila, condicion):
    # Un gap vacío no es cero y no se convierte a entero.
    return fila["gap_dias"] != "" and condicion(int(fila["gap_dias"]))

categorias = {
    "renovacion_anticipada": [],
    "renovacion_mismo_dia": [],
    "renovacion_entre_1_y_28_dias": [],
    "gap_29": [],
    "gap_30": [],
    "gap_mayor_30": [],
    "sin_eventos_futuros": [],
    "solo_cancelaciones_futuras": [],
    "vencimiento_adelantado": [],
    "empate_en_dia_historico_final": [],
}
for usuario in sorted(etiquetas):
    fila = etiquetas[usuario]
    eventos = seguimiento.get(usuario, [])
    ultima_fecha = max(e["fecha"] for e in historia[usuario])
    cumple = {
        "renovacion_anticipada": tiene_gap(fila, lambda g: g < 0),
        "renovacion_mismo_dia": tiene_gap(fila, lambda g: g == 0),
        "renovacion_entre_1_y_28_dias": tiene_gap(fila, lambda g: 1 <= g <= 28),
        "gap_29": tiene_gap(fila, lambda g: g == 29),
        "gap_30": tiene_gap(fila, lambda g: g == 30),
        "gap_mayor_30": tiene_gap(fila, lambda g: g > 30),
        "sin_eventos_futuros": not eventos,
        "solo_cancelaciones_futuras": bool(eventos) and all(
            e["cancelacion"] == "1" for e in eventos),
        "vencimiento_adelantado": fila["vencimiento_efectivo"] < fila["vencimiento_conocido"],
        "empate_en_dia_historico_final": sum(
            e["fecha"] == ultima_fecha for e in historia[usuario]) > 1,
    }
    for categoria, valor in cumple.items():
        if valor:
            categorias[categoria].append(usuario)

# Un usuario puede ilustrar varias categorías: no imprimimos el mismo caso dos veces.
seleccionados = defaultdict(list)
for categoria, usuarios in categorias.items():
    if usuarios:
        seleccionados[usuarios[0]].append(categoria)

lineas = [
    "# Auditoría manual pendiente — piloto 2016-03-07",
    "",
    "Ejemplos seleccionados, no predicciones ni fallos de un modelo.",
    "La cobertura del historial sigue siendo un supuesto.",
    "Los alias ocultan msno en este informe; esto no garantiza anonimización.",
    "",
    "## Categorías disponibles (pueden solaparse)",
    "",
]
for categoria, usuarios in categorias.items():
    lineas.append(f"- {categoria}: {len(usuarios)}")

for numero, (usuario, categorias_caso) in enumerate(seleccionados.items(), start=1):
    fila = etiquetas[usuario]
    lineas.extend([
        "", f"## Caso {numero:02d}", "",
        "Categorías: " + ", ".join(categorias_caso), "",
    ])
    for campo in ("corte", "vencimiento_conocido", "vencimiento_efectivo",
                  "primera_renovacion", "gap_dias", "is_churn", "motivo", "observado_hasta"):
        lineas.append(f"- {campo}: {fila[campo] or '(vacío)'}")
    for nombre, eventos in (("Historia", historia[usuario]),
                            ("Seguimiento", seguimiento.get(usuario, []))):
        lineas.extend(["", f"### {nombre}", ""])
        if not eventos:
            lineas.append("Sin eventos en esta fase.")
            continue
        lineas.extend(["| Fecha | Cancelación | Vencimiento | Firma del plan |",
                       "| --- | --- | --- | --- |"])
        for e in sorted(eventos, key=cmp_to_key(comparar_eventos)):
            firma = e["firma"].replace("|", "\\|")
            lineas.append(
                f"| {e['fecha']} | {e['cancelacion']} | {e['vencimiento']} | {firma} |")
    lineas.extend([
        "", "### Revisión del estudiante", "",
        "- Vencimiento reconstruido al corte: pendiente.",
        "- Primera renovación y efecto de cancelaciones: pendiente.",
        "- Gap calculado manualmente (o motivo de ausencia): pendiente.",
        "- Etiqueta esperada y comparación con la guardada: pendiente.",
        "- Veredicto: pendiente (coincide / discrepancia / no determinable).",
    ])

salida.parent.mkdir(parents=True, exist_ok=True)
with salida.open("x", encoding="utf-8") as archivo:
    archivo.write("\n".join(lineas) + "\n")
print("Etiquetas con coherencia interna:", len(etiquetas))
for categoria, usuarios in categorias.items():
    print(f"{categoria}: {len(usuarios)}")
print("Casos distintos para revisión manual:", len(seleccionados))
print("Informe local:", salida)
print("La revisión manual sigue pendiente; no se modificaron etiquetas.")
