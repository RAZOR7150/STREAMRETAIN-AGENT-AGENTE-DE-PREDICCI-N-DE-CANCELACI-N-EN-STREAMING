import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from datetime import date, timedelta
from functools import cmp_to_key
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data" / "derived"
comprimido = raiz / "data" / "kkbox-churn-prediction-challenge" / "transactions.csv.7z"
tar = Path(r"C:\Windows\System32\tar.exe")
cortes = [date(2016, 3, 7), date(2016, 6, 6), date(2016, 9, 5), date(2016, 12, 5)]
columnas_x = ["transacciones_90d", "transacciones_30d", "cancelaciones_90d",
              "dias_con_transacciones_90d", "dias_desde_ultima_transaccion",
              "dias_hasta_vencimiento"]
columnas = ["msno", "corte", *columnas_x, "is_churn"]

def incluir_usuario(usuario):
    # El prefijo fija una versión de la regla de muestreo: no cambiar entre cortes.
    texto = "streamretain-v1:" + usuario
    resumen = hashlib.sha256(texto.encode("utf-8")).digest()
    # Convertimos los primeros 8 bytes en un entero estable.
    numero = int.from_bytes(resumen[:8], byteorder="big")
    # Aproximadamente uno de cada cien identificadores cae en este grupo.
    return numero % 100 == 0

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

def construir_cohorte(eventos_por_usuario, corte):
    inicio = corte - timedelta(days=90)
    inicio_30 = corte - timedelta(days=30)
    ultimo_vencimiento = corte + timedelta(days=29)
    fin = ultimo_vencimiento + timedelta(days=30)
    filas, auditoria = [], []
    for usuario in sorted(eventos_por_usuario):
        eventos = eventos_por_usuario[usuario]
        # Solo esta lista aporta información a candidatos y características.
        historia = [e for e in eventos if inicio <= e["fecha"] < corte]
        if not historia:
            continue
        ultimo = sorted(historia, key=cmp_to_key(comparar_eventos))[-1]
        vence = ultimo["vencimiento"]
        if not corte <= vence <= ultimo_vencimiento:
            continue
        seguimiento = [e for e in eventos if corte <= e["fecha"] <= fin]
        etiqueta = etiquetar(vence, seguimiento, fin)
        if etiqueta["is_churn"] not in (0, 1):
            raise ValueError("Candidato sin seguimiento suficiente; revisar sin descartarlo")
        fila = {
            "msno": usuario, "corte": corte.isoformat(),
            "transacciones_90d": len(historia),
            "transacciones_30d": sum(e["fecha"] >= inicio_30 for e in historia),
            "cancelaciones_90d": sum(e["cancelacion"] == "1" for e in historia),
            "dias_con_transacciones_90d": len({e["fecha"] for e in historia}),
            "dias_desde_ultima_transaccion": (corte - ultimo["fecha"]).days,
            "dias_hasta_vencimiento": (vence - corte).days,
            "is_churn": etiqueta["is_churn"],
        }
        filas.append(fila)
        auditoria.append({
            "msno": usuario, "corte": corte.isoformat(),
            "vencimiento_conocido": vence.isoformat(),
            "observado_hasta": fin.isoformat(),
            "supuesto_cobertura": "historial_publicado_completo_en_ventana",
            **etiqueta,
        })
    if not filas:
        raise ValueError(f"Cohorte vacía: {corte}")
    return filas, auditoria

def construir_cohorte(eventos_por_usuario, corte):
    inicio = corte - timedelta(days=90)
    inicio_30 = corte - timedelta(days=30)
    ultimo_vencimiento = corte + timedelta(days=29)
    fin = ultimo_vencimiento + timedelta(days=30)
    filas, auditoria = [], []
    for usuario in sorted(eventos_por_usuario):
        eventos = eventos_por_usuario[usuario]
        # Solo esta lista aporta información a candidatos y características.
        historia = [e for e in eventos if inicio <= e["fecha"] < corte]
        if not historia:
            continue
        ultimo = sorted(historia, key=cmp_to_key(comparar_eventos))[-1]
        vence = ultimo["vencimiento"]
        if not corte <= vence <= ultimo_vencimiento:
            continue
        seguimiento = [e for e in eventos if corte <= e["fecha"] <= fin]
        etiqueta = etiquetar(vence, seguimiento, fin)
        if etiqueta["is_churn"] not in (0, 1):
            raise ValueError("Candidato sin seguimiento suficiente; revisar sin descartarlo")
        fila = {
            "msno": usuario, "corte": corte.isoformat(),
            "transacciones_90d": len(historia),
            "transacciones_30d": sum(e["fecha"] >= inicio_30 for e in historia),
            "cancelaciones_90d": sum(e["cancelacion"] == "1" for e in historia),
            "dias_con_transacciones_90d": len({e["fecha"] for e in historia}),
            "dias_desde_ultima_transaccion": (corte - ultimo["fecha"]).days,
            "dias_hasta_vencimiento": (vence - corte).days,
            "is_churn": etiqueta["is_churn"],
        }
        filas.append(fila)
        auditoria.append({
            "msno": usuario, "corte": corte.isoformat(),
            "vencimiento_conocido": vence.isoformat(),
            "observado_hasta": fin.isoformat(),
            "supuesto_cobertura": "historial_publicado_completo_en_ventana",
            **etiqueta,
        })
    if not filas:
        raise ValueError(f"Cohorte vacía: {corte}")
    return filas, auditoria

carpeta.mkdir(parents=True, exist_ok=True)
resumen_ruta = carpeta / "preparacion_cohortes_finales.json"
# Comprobar antes del recorrido largo para no perder tiempo ni sobrescribir evidencia.
salidas_previstas = [resumen_ruta]
for corte in cortes[2:]:
    salidas_previstas.extend([
        carpeta / f"cohorte_{corte}.csv",
        carpeta / f"etiquetas_piloto_{corte}.csv",
    ])
if any(p.exists() for p in salidas_previstas):
    raise FileExistsError("Ya existe alguna salida prevista; revisar antes de repetir")
for p in [tar, comprimido, carpeta / "cohorte_2016-03-07.csv", carpeta / "cohorte_2016-06-06.csv"]:
    if not p.is_file():
        raise FileNotFoundError(p)

inicio_global = min(cortes) - timedelta(days=90)
fin_global = max(cortes) + timedelta(days=59)
eventos_por_usuario = defaultdict(list)
leidas, conservadas = 0, 0
proceso = subprocess.Popen(
    [str(tar), "-xOf", str(comprimido), "transactions.csv"],
    stdout=subprocess.PIPE, text=True, encoding="utf-8-sig",
)
try:
    lector = csv.DictReader(proceso.stdout)
    requeridos = {"msno", "transaction_date", "membership_expire_date", "is_cancel",
                  "plan_list_price", "payment_plan_days", "payment_method_id"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera inesperada")
    if len(set(lector.fieldnames)) != len(lector.fieldnames):
        raise ValueError("Cabecera con columnas repetidas")
    for fila in lector:
        leidas += 1
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Fila mal formada")
        fecha = leer_fecha(fila["transaction_date"])
        if not inicio_global <= fecha <= fin_global:
            continue
        usuario = fila["msno"].strip()
        if not usuario:
            raise ValueError("Usuario vacío")
        if not incluir_usuario(usuario):
            continue
        cancelacion = fila["is_cancel"].strip()
        plan = [fila[c] for c in ("plan_list_price", "payment_plan_days", "payment_method_id")]
        if cancelacion not in {"0", "1"} or any(not x.strip() for x in plan):
            raise ValueError("Evento seleccionado inválido")
        eventos_por_usuario[usuario].append({
            "fecha": fecha, "vencimiento": leer_fecha(fila["membership_expire_date"]),
            "cancelacion": cancelacion, "firma": "".join(plan),
        })
        conservadas += 1
        # Un límite operativo evita un crecimiento inesperado de memoria.
        if conservadas > 500000:
            raise RuntimeError("Muestra inesperadamente grande; revisar antes de continuar")
    codigo = proceso.wait()
    if codigo != 0:
        raise RuntimeError(f"tar terminó con código {codigo}")
finally:
    proceso.stdout.close()
    if proceso.poll() is None:
        proceso.terminate()
    proceso.wait()
if leidas != 21547746:
    raise ValueError("No coincide el total del archivo original auditado")
print("Filas originales recorridas:", leidas)
print("Eventos de la muestra conservados:", conservadas)

for corte in cortes[:2]:
    reconstruida, _ = construir_cohorte(eventos_por_usuario, corte)
    # csv.DictReader devuelve texto: normalizamos la reconstrucción a texto también.
    actual = {f["msno"]: {k: str(v) for k, v in f.items()} for f in reconstruida}
    referencia = {}
    with (carpeta / f"cohorte_{corte}.csv").open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != columnas:
            raise ValueError("Esquema de referencia distinto")
        for fila in lector:
            if None in fila or any(v is None for v in fila.values()):
                raise ValueError("Referencia mal formada")
            if fila["msno"] in referencia:
                raise ValueError("Usuario repetido en referencia")
            referencia[fila["msno"]] = fila
    if actual != referencia:
        faltantes = len(set(referencia) - set(actual))
        adicionales = len(set(actual) - set(referencia))
        distintos = sum(actual[u] != referencia[u] for u in set(actual) & set(referencia))
        raise ValueError(f"No coincide {corte}: faltantes={faltantes}, adicionales={adicionales}, distintos={distintos}")
    print("Equivalencia exacta de valores verificada:", corte, "filas:", len(actual))

resumen = {
    "fuente": "transactions.csv.7z", "filas_originales": leidas,
    "regla_muestra": "sha256(streamretain-v1:msno), primeros 8 bytes modulo 100 = 0",
    "equivalencia_marzo_junio": True,
    "cohortes": [],
}
for corte in cortes[2:]:
    filas, auditoria = construir_cohorte(eventos_por_usuario, corte)
    archivo_cohorte = carpeta / f"cohorte_{corte}.csv"
    archivo_auditoria = carpeta / f"etiquetas_piloto_{corte}.csv"
    with archivo_cohorte.open("x", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)
    with archivo_auditoria.open("x", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(auditoria[0]))
        escritor.writeheader()
        escritor.writerows(auditoria)
    resumen["cohortes"].append({
        "corte": corte.isoformat(),
        "historia_desde": (corte - timedelta(days=90)).isoformat(),
        "seguimiento_hasta": (corte + timedelta(days=59)).isoformat(),
        "filas": len(filas),
        "sha256": hashlib.sha256(archivo_cohorte.read_bytes()).hexdigest(),
        "uso": "validacion_2" if corte.month == 9 else "prueba_final_reservada",
    })
    print("Cohorte preparada:", corte, "filas:", len(filas))
    print("Seguimiento hasta:", corte + timedelta(days=59))
with resumen_ruta.open("x", encoding="utf-8") as archivo:
    json.dump(resumen, archivo, ensure_ascii=False, indent=2)
    archivo.write("\n")
print("Manifiesto:", resumen_ruta)
print("Diciembre reservado: no inspeccionar sus resultados para ajustar el modelo.")
