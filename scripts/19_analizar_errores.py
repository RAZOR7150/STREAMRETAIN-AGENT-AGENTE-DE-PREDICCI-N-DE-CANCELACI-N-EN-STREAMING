import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
ruta = raiz / "data" / "derived" / "predicciones_prueba_final.csv"
ruta_resultado = raiz / "experiments" / "prueba_final" / "resultados.json"
resultado = json.loads(ruta_resultado.read_text(encoding="utf-8-sig"))
columnas = resultado["caracteristicas"]
familia = resultado["modelo_agente"]
umbral = resultado["modelos"][familia]["umbral"]
salida = raiz / "experiments" / "prueba_final" / "analisis_errores.json"
if salida.exists():
    raise FileExistsError("Ya existe el análisis; revisar antes de reemplazar")

filas, usuarios = [], set()
with ruta.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    esperado = ["msno", "corte", *columnas, "is_churn", "puntaje", "prediccion", "tipo"]
    if lector.fieldnames != esperado:
        raise ValueError("Esquema de predicciones inesperado")
    for fila in lector:
        usuario = fila["msno"].strip()
        if not usuario or usuario in usuarios:
            raise ValueError("Usuario vacío o repetido")
        usuarios.add(usuario)
        if fila["corte"] != resultado["prueba"]["corte"]:
            raise ValueError("Corte incorrecto")
        real, pred = int(fila["is_churn"]), int(fila["prediccion"])
        p = float(fila["puntaje"])
        if real not in (0, 1) or pred not in (0, 1) or not math.isfinite(p) or not 0 <= p <= 1:
            raise ValueError("Etiqueta, predicción o puntaje inválido")
        tipo = {(0, 0): "TN", (0, 1): "FP", (1, 0): "FN", (1, 1): "TP"}[(real, pred)]
        if pred != int(p >= umbral) or fila["tipo"] != tipo:
            raise ValueError("Predicción incoherente con el umbral o tipo")
        filas.append({"msno": usuario, "real": real, "pred": pred,
                      "puntaje": p, "tipo": tipo,
                      "x": {c: int(fila[c]) for c in columnas}})

conteos = Counter(f["tipo"] for f in filas)
matriz = [[conteos["TN"], conteos["FP"]], [conteos["FN"], conteos["TP"]]]
if len(filas) != resultado["filas_prueba"] or sum(f["real"] for f in filas) != resultado["abandonos_prueba"]:
    raise ValueError("Tamaño o clases diferentes de la prueba final")
if matriz != resultado["modelos"][familia]["metricas"]["matriz_confusion"]:
    raise ValueError("La matriz no coincide con la evidencia final")

def dividir(numerador, denominador):
    return numerador / denominador if denominador else None


def resumir(grupo):
    c = Counter(f["tipo"] for f in grupo)
    tn, fp, fn, tp = (c[k] for k in ("TN", "FP", "FN", "TP"))
    n = len(grupo)
    return {
        "n": n, "abandonos": tp + fn, "alertas": tp + fp,
        "prevalencia": dividir(tp + fn, n),
        "precision": dividir(tp, tp + fp), "recall": dividir(tp, tp + fn),
        "f1": dividir(2 * tp, 2 * tp + fp + fn),
        "tasa_falsos_positivos": dividir(fp, fp + tn),
        "matriz": [[tn, fp], [fn, tp]],
    }


grupos = {
    "sin_cancelaciones_90d": [f for f in filas if f["x"]["cancelaciones_90d"] == 0],
    "con_cancelaciones_90d": [f for f in filas if f["x"]["cancelaciones_90d"] > 0],
    "ultima_transaccion_menos_30d": [f for f in filas if f["x"]["dias_desde_ultima_transaccion"] < 30],
    "ultima_transaccion_30d_o_mas": [f for f in filas if f["x"]["dias_desde_ultima_transaccion"] >= 30],
}
resumen_grupos = {nombre: resumir(grupo) for nombre, grupo in grupos.items()}

fp = sorted((f for f in filas if f["tipo"] == "FP"),
            key=lambda f: (-f["puntaje"], f["msno"]))[:5]
fn = sorted((f for f in filas if f["tipo"] == "FN"),
            key=lambda f: (f["puntaje"], f["msno"]))[:5]
if len(fp) < 5 or len(fn) < 5:
    raise ValueError("No hay cinco casos de cada tipo; revisar selección")
casos = []
for i, fila in enumerate(fp + fn, 1):
    x = fila["x"]
    # Hipótesis de limitación del modelo, no afirmaciones sobre motivos personales.
    if fila["tipo"] == "FP":
        hipotesis = "El patrón histórico se parece al de riesgo, pero la etiqueta reconstruida indica renovación oportuna."
        impacto = "Revisión o contacto innecesario si se actuara automáticamente."
    else:
        hipotesis = "Las seis variables históricas no distinguen este abandono; podrían faltar señales o la regla aprendida ser insuficiente."
        impacto = "Oportunidad de revisión de retención omitida."
    if x["cancelaciones_90d"] > 0:
        observacion = "Existe cancelación histórica; una cancelación por sí sola no determina abandono futuro."
    else:
        observacion = "No hay cancelaciones históricas registradas; su ausencia no garantiza renovación."
    casos.append({
        "caso": f"E{i:02d}", "tipo": fila["tipo"], "etiqueta": fila["real"],
        "prediccion": fila["pred"], "puntaje": fila["puntaje"],
        "caracteristicas": x, "observacion": observacion,
        "hipotesis_no_confirmada": hipotesis, "impacto_potencial": impacto,
        "revision_manual": "pendiente",
    })

informe = {
    "modelo": familia, "umbral": umbral,
    "sha256_predicciones": hashlib.sha256(ruta.read_bytes()).hexdigest(),
    "sha256_resultado_final": hashlib.sha256(ruta_resultado.read_bytes()).hexdigest(),
    "global": resumir(filas), "grupos_exploratorios": resumen_grupos,
    "seleccion_casos": "5 FP de mayor puntaje y 5 FN de menor puntaje; no representativos",
    "casos": casos,
    "limites": ["No se reajustó el modelo", "Hipótesis pendientes de revisión humana",
                "Etiquetas reconstruidas sujetas al supuesto de cobertura",
                "Sin datos demográficos: no acredita equidad demográfica"],
}
with salida.open("x", encoding="utf-8") as archivo:
    json.dump(informe, archivo, ensure_ascii=False, indent=2, allow_nan=False)
    archivo.write("\n")

print("RESUMEN ANÁLISIS DE ERRORES")
print("Global:", informe["global"])
for nombre, resumen in resumen_grupos.items():
    print(nombre, resumen)
print("Casos preparados:", len(casos), "Revisión manual: pendiente")
for caso in casos:
    print(caso["caso"], caso["tipo"], "puntaje:", round(caso["puntaje"], 4),
          "características:", caso["caracteristicas"])
print("Informe:", salida)
