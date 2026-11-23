import csv
import hashlib
import json
import platform
from pathlib import Path
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, average_precision_score,
)

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data" / "derived"
columnas_x = [
    "transacciones_90d", "transacciones_30d", "cancelaciones_90d",
    "dias_con_transacciones_90d", "dias_desde_ultima_transaccion",
    "dias_hasta_vencimiento",
]


def cargar(nombre, corte, esperados, abandonos_esperados=None):
    ruta = carpeta / nombre
    X, y, usuarios = [], [], set()
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        esquema = ["msno", "corte", *columnas_x, "is_churn"]
        if lector.fieldnames != esquema:
            raise ValueError(f"Esquema inesperado: {nombre}")
        for fila in lector:
            if None in fila or any(v is None for v in fila.values()):
                raise ValueError("Fila mal formada")
            usuario = fila["msno"].strip()
            if not usuario or usuario in usuarios or fila["corte"] != corte:
                raise ValueError("Identificador repetido/vacío o corte incorrecto")
            if fila["is_churn"] not in {"0", "1"}:
                raise ValueError("Etiqueta no reconocida")
            valores = [int(fila[c]) for c in columnas_x]
            n90, n30, cancelaciones, dias, reciente, restantes = valores
            if not (n90 >= 1 and 0 <= n30 <= n90 and 0 <= cancelaciones <= n90
                    and 1 <= dias <= min(90, n90) and 1 <= reciente <= 90
                    and 0 <= restantes <= 29):
                raise ValueError("Características fuera de sus límites")
            usuarios.add(usuario)
            X.append(valores)
            y.append(int(fila["is_churn"]))
    if len(y) != esperados:
        raise ValueError(f"Tamaño inesperado: {nombre}")
    if abandonos_esperados is not None and sum(y) != abandonos_esperados:
        raise ValueError(f"Clases diferentes a lo revisado: {nombre}")
    # Una huella del archivo ayuda a identificar exactamente los datos de esta corrida.
    # Estos CSV son pequeños; no aplicar read_bytes al comprimido completo.
    huella = hashlib.sha256(ruta.read_bytes()).hexdigest()
    return X, y, usuarios, huella

def medir(y_real, predicciones, puntajes):
    return {
        "accuracy": float(accuracy_score(y_real, predicciones)),
        "precision_abandono": float(precision_score(y_real, predicciones, zero_division=0)),
        "recall_abandono": float(recall_score(y_real, predicciones, zero_division=0)),
        "f1_abandono": float(f1_score(y_real, predicciones, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_real, puntajes)),
        "average_precision": float(average_precision_score(y_real, puntajes)),
        "matriz_confusion": confusion_matrix(y_real, predicciones, labels=[0, 1]).tolist(),
    }

from datetime import datetime, timezone
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import ParameterGrid

ruta_v1 = raiz / "experiments" / "seleccion_congelada.json"
v1 = json.loads(ruta_v1.read_text(encoding="utf-8-sig"))
salida = raiz / "experiments" / "busqueda_arbol_v2"
if salida.exists():
    raise FileExistsError("Ya existe esta búsqueda; revisar antes de repetir")
if v1["caracteristicas"] != columnas_x or v1["sklearn"] != sklearn.__version__:
    raise ValueError("Cambió el contrato o la versión de sklearn")

# Solo tres CSV de desarrollo. No leer prueba_reservada ni diciembre.
datos = {}
for meta in v1["cohortes_desarrollo"]:
    X, y, usuarios, huella = cargar(
        f"cohorte_{meta['corte']}.csv", meta["corte"], meta["filas"])
    if huella != meta["sha256"] or set(y) != {0, 1}:
        raise ValueError("Cambió una cohorte o faltan clases")
    datos[meta["corte"]] = (X, y)
Xm, ym = datos["2016-03-07"]
Xj, yj = datos["2016-06-06"]
Xs, ys = datos["2016-09-05"]
rondas = [(Xm, ym, Xj, yj), (Xm + Xj, ym + yj, Xs, ys)]
rejilla = {
    "max_depth": [3, 4, 5, 6, 8, 10, None],
    "min_samples_leaf": [10, 20, 50, 100],
    "class_weight": [None, "balanced"],
}
umbrales = [round(i / 100, 2) for i in range(5, 100, 5)]
# Guardar el protocolo antes de entrenar deja constancia de la búsqueda.
salida.mkdir(parents=True, exist_ok=False)
protocolo = {
    "estado": "exploracion_v2_posterior_a_prueba_v1",
    "fecha_utc": datetime.now(timezone.utc).isoformat(),
    "semilla": 42, "sklearn": sklearn.__version__, "python": platform.python_version(),
    "sha256_seleccion_v1": hashlib.sha256(ruta_v1.read_bytes()).hexdigest(),
    "caracteristicas": columnas_x, "cohortes": v1["cohortes_desarrollo"],
    "rejilla": rejilla, "umbrales": umbrales,
    "criterio": "F1 medio, AP media, cercanía a 0.5; empate restante por orden de rejilla",
}
with (salida / "protocolo.json").open("x", encoding="utf-8") as f:
    json.dump(protocolo, f, ensure_ascii=False, indent=2, allow_nan=False)

ensayos = []
configuraciones = list(ParameterGrid(rejilla))
for numero, parametros in enumerate(configuraciones, 1):
    por_ronda = []
    for X_train, y_train, X_val, y_val in rondas:
        modelo = DecisionTreeClassifier(random_state=42, **parametros)
        modelo.fit(X_train, y_train)
        indice = list(modelo.classes_).index(1)
        puntajes = modelo.predict_proba(X_val)[:, indice]
        por_ronda.append({
            u: medir(y_val, (puntajes >= u).astype(int), puntajes)
            for u in umbrales
        })
    for u in umbrales:
        junio, septiembre = por_ronda[0][u], por_ronda[1][u]
        ensayos.append({
            "familia": "arbol", "parametros": parametros, "umbral": u,
            "junio": junio, "septiembre": septiembre,
            "f1_medio": (junio["f1_abandono"] + septiembre["f1_abandono"]) / 2,
            "ap_media": (junio["average_precision"] + septiembre["average_precision"]) / 2,
        })
    print(f"Configuración {numero}/{len(configuraciones)}:", parametros)


def criterio(fila):
    return (fila["f1_medio"], fila["ap_media"], -abs(fila["umbral"] - 0.5))


ordenados = sorted(ensayos, key=criterio, reverse=True)
mejor = ordenados[0]
anterior = v1["mejores_por_familia"]["arbol"]
# La configuración anterior está incluida: comprobamos su reproducción.
referencia = next(f for f in ensayos
                  if f["parametros"] == anterior["parametros"]
                  and f["umbral"] == anterior["umbral"])
for periodo in ("junio", "septiembre"):
    if abs(referencia[periodo]["f1_abandono"] - anterior[periodo]["f1_abandono"]) > 1e-12:
        raise ValueError("La configuración de referencia no reproduce el F1 anterior")

resumen = {
    **protocolo, "configuraciones": len(configuraciones), "ajustes": 2 * len(configuraciones),
    "ensayos": ensayos, "mejor_validacion": mejor,
    "referencia_v1": referencia,
    "mejora_f1_medio": mejor["f1_medio"] - referencia["f1_medio"],
    "supera_050_en_ambas_validaciones": all(
        mejor[p]["f1_abandono"] >= 0.5 for p in ("junio", "septiembre")),
    "advertencia": "No hay nueva prueba independiente; no sustituye resultados de versión1",
}
with (salida / "resultados.json").open("x", encoding="utf-8") as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2, allow_nan=False)
print("\nRESUMEN BÚSQUEDA AMPLIADA")
print("Configuraciones:", len(configuraciones), "Ajustes:", 2 * len(configuraciones))
print("Mejor configuración:", mejor["parametros"], "Umbral:", mejor["umbral"])
print("F1 junio:", mejor["junio"]["f1_abandono"])
print("F1 septiembre:", mejor["septiembre"]["f1_abandono"])
print("F1 medio:", mejor["f1_medio"])
print("F1 medio anterior:", referencia["f1_medio"])
print("Mejora:", resumen["mejora_f1_medio"])
print("F1>=0.50 en ambos periodos:", resumen["supera_050_en_ambas_validaciones"])
print("Evidencia:", salida)
print("Diciembre no leído; modelo de la demo no modificado.")
