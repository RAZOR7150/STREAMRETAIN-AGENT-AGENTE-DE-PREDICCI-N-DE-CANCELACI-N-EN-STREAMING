import csv
import hashlib
import json
import subprocess
from datetime import date, timedelta
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data" / "derived"
seleccion = json.loads((raiz / "experiments" / "seleccion_congelada.json").read_text(encoding="utf-8-sig"))
base = seleccion["caracteristicas"]
extras = ["promedio_duracion_plan_90d", "promedio_precio_lista_90d",
          "promedio_importe_registrado_90d", "proporcion_autorenovacion_90d"]
salida = carpeta / "caracteristicas_suscripcion_v4"
if salida.exists():
    raise FileExistsError("Ya existe la preparación; revisar antes de repetir")
comprimido = raiz / "data" / "kkbox-churn-prediction-challenge" / "transactions.csv.7z"
tar = Path(r"C:\Windows\System32\tar.exe")
for ruta in (comprimido, tar):
    if not ruta.is_file():
        raise FileNotFoundError(ruta)

cohortes, ventanas, objetivos, acumuladores = {}, {}, {}, {}
for meta in seleccion["cohortes_desarrollo"]:
    texto_corte = meta["corte"]
    corte = date.fromisoformat(texto_corte)
    ventanas[texto_corte] = (corte - timedelta(days=90), corte)
    ruta = carpeta / f"cohorte_{texto_corte}.csv"
    if hashlib.sha256(ruta.read_bytes()).hexdigest() != meta["sha256"]:
        raise ValueError("Cambió la cohorte de referencia")
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != ["msno", "corte", *base, "is_churn"]:
            raise ValueError("Esquema inesperado")
        filas = list(lector)
    if len(filas) != meta["filas"]:
        raise ValueError("Número de filas inesperado")
    cohortes[texto_corte] = filas
    acumuladores[texto_corte] = {}
    for fila in filas:
        u = fila["msno"]
        if not u or u in acumuladores[texto_corte] or fila["corte"] != texto_corte:
            raise ValueError("Usuario o corte incorrecto")
        # n controla la igualdad con transacciones_90d. Las sumas nunca usan etiquetas.
        acumuladores[texto_corte][u] = {"n": 0, "plan": 0, "precio": 0, "importe": 0, "auto": 0}
        objetivos.setdefault(u, []).append(texto_corte)

def leer_fecha(texto):
    texto = texto.strip()
    if len(texto) != 8 or not texto.isascii() or not texto.isdigit():
        raise ValueError(f"Formato de fecha inválido: {texto!r}")
    return date(int(texto[:4]), int(texto[4:6]), int(texto[6:8]))

filas_leidas = 0
campos_fuente = ["payment_plan_days", "plan_list_price", "actual_amount_paid", "is_auto_renew"]
requeridos = {"msno", "transaction_date", *campos_fuente}
proceso = subprocess.Popen(
    [str(tar), "-xOf", str(comprimido), "transactions.csv"],
    stdout=subprocess.PIPE, text=True, encoding="utf-8-sig"
)
try:
    lector = csv.DictReader(proceso.stdout)
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError(f"Faltan columnas: {lector.fieldnames}")
    for fila in lector:
        filas_leidas += 1
        if filas_leidas % 5000000 == 0:
            print("Filas recorridas:", filas_leidas)
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Fila mal formada")
        u = fila["msno"].strip()
        cortes_usuario = objetivos.get(u)
        if not cortes_usuario:
            continue
        fecha = leer_fecha(fila["transaction_date"])
        aplicables = [c for c in cortes_usuario if ventanas[c][0] <= fecha < ventanas[c][1]]
        if not aplicables:
            continue  # Los eventos futuros no aportan ninguna característica.
        plan, precio, importe, auto = (int(fila[c]) for c in campos_fuente)
        if auto not in (0, 1) or plan < 0:
            raise ValueError("Duración o autorrenovación inesperadas; revisar sin descartar filas")
        for c in aplicables:
            a = acumuladores[c][u]
            a["n"] += 1
            a["plan"] += plan
            a["precio"] += precio
            a["importe"] += importe
            a["auto"] += auto
    if proceso.wait() != 0:
        raise RuntimeError("Falló la lectura del comprimido")
finally:
    proceso.stdout.close()
    if proceso.poll() is None:
        proceso.terminate()
        proceso.wait()
if filas_leidas != 21547746:
    raise ValueError("El archivo no tiene el número de filas previamente auditado")

preparadas = {}
for c, filas in cohortes.items():
    nuevas = []
    for fila in filas:
        a = acumuladores[c][fila["msno"]]
        n = a["n"]
        if n == 0 or n != int(fila["transacciones_90d"]):
            raise ValueError("La historia no reproduce el conteo original")
        valores = [a["plan"] / n, a["precio"] / n, a["importe"] / n, a["auto"] / n]
        nueva = {**fila, **dict(zip(extras, valores))}
        # No se modifican ninguna de las seis variables ni las etiquetas existentes.
        if any(nueva[k] != fila[k] for k in ["msno", "corte", *base, "is_churn"]):
            raise ValueError("Se alteró la cohorte original")
        nuevas.append(nueva)
    preparadas[c] = nuevas

salida.mkdir(parents=True, exist_ok=False)
metadatos = []
for c, filas in preparadas.items():
    ruta = salida / f"cohorte_{c}.csv"
    with ruta.open("x", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=["msno", "corte", *base, *extras, "is_churn"])
        escritor.writeheader()
        escritor.writerows(filas)
    resumen = {}
    for variable in extras:
        valores = [f[variable] for f in filas]
        resumen[variable] = {"min": min(valores), "max": max(valores), "media": sum(valores) / len(valores)}
    metadatos.append({"corte": c, "filas": len(filas), "sha256": hashlib.sha256(ruta.read_bytes()).hexdigest(),
                      "resumen_nuevas_caracteristicas": resumen})
    print("\nCohorte:", c, "Filas:", len(filas), "Características:", len(base) + len(extras))
    for variable, valores in resumen.items():
        print(variable, valores)
manifiesto = {
    "estado": "desarrollo_exploratorio_v4_sin_diciembre",
    "fuente": str(comprimido.relative_to(raiz)), "filas_recorridas": filas_leidas,
    "cohortes_base": seleccion["cohortes_desarrollo"],
    "caracteristicas": base + extras, "nuevas": extras, "cohortes": metadatos,
    "definicion": "Medias de registros históricos en [corte-90d,corte); incluye eventos de cancelación",
    "controles": "Mismos usuarios, seis variables y etiquetas; conteos históricos reproducidos",
}
with (salida / "manifiesto.json").open("x", encoding="utf-8") as archivo:
    json.dump(manifiesto, archivo, ensure_ascii=False, indent=2, allow_nan=False)
print("\nPreparación finalizada:", salida)
print("Diciembre no procesado; ningún modelo entrenado.")
