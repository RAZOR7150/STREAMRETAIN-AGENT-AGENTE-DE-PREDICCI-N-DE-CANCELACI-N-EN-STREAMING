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
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import ParameterGrid

ruta_v1 = raiz / "experiments" / "seleccion_congelada.json"
ruta_arbol = raiz / "experiments" / "busqueda_arbol_v2" / "resultados.json"
v1 = json.loads(ruta_v1.read_text(encoding="utf-8-sig"))
arbol_v2 = json.loads(ruta_arbol.read_text(encoding="utf-8-sig"))
salida = raiz / "experiments" / "busqueda_bosque_v3"
if salida.exists():
    raise FileExistsError("Ya existe esta búsqueda; comparte resultados o error antes de repetir")
if (v1["caracteristicas"] != columnas_x or arbol_v2["caracteristicas"] != columnas_x
        or v1["sklearn"] != sklearn.__version__
        or arbol_v2["sklearn"] != sklearn.__version__
        or arbol_v2["cohortes"] != v1["cohortes_desarrollo"]):
    raise ValueError("Datos, características o entorno diferentes")

# Cargamos SOLO los periodos de desarrollo con control de identidad del archivo.
datos = {}
for meta in v1["cohortes_desarrollo"]:
    X, y, usuarios, huella = cargar(
        f"cohorte_{meta['corte']}.csv", meta["corte"], meta["filas"])
    if huella != meta["sha256"] or set(y) != {0, 1}:
        raise ValueError("Cambió una cohorte o no contiene ambas clases")
    datos[meta["corte"]] = (X, y)
Xm, ym = datos["2016-03-07"]
Xj, yj = datos["2016-06-06"]
Xs, ys = datos["2016-09-05"]
rondas = [(Xm, ym, Xj, yj), (Xm + Xj, ym + yj, Xs, ys)]
rejilla = {
    "max_depth": [5, 10, None],
    "min_samples_leaf": [5, 20],
    "class_weight": [None, "balanced"],
}
fijos = {"n_estimators": 200, "random_state": 42, "n_jobs": 2,
         "max_features": "sqrt", "bootstrap": True}
umbrales = [round(i / 100, 2) for i in range(5, 100, 5)]
if umbrales != arbol_v2["umbrales"]:
    raise ValueError("Los umbrales no coinciden con la comparación anterior")

# El protocolo se escribe antes de ver las métricas de los bosques.
salida.mkdir(parents=True, exist_ok=False)
protocolo = {
    "estado": "desarrollo_exploratorio_posterior_a_prueba_v1",
    "fecha_utc": datetime.now(timezone.utc).isoformat(),
    "python": platform.python_version(), "sklearn": sklearn.__version__,
    "sha256_resultados_arbol_v2": hashlib.sha256(ruta_arbol.read_bytes()).hexdigest(),
    "cohortes": v1["cohortes_desarrollo"], "caracteristicas": columnas_x,
    "rejilla": rejilla, "parametros_fijos": fijos, "umbrales": umbrales,
    "criterio": "F1 medio, AP media, cercanía a 0.5; empate restante por orden de rejilla",
}
with (salida / "protocolo.json").open("x", encoding="utf-8") as f:
    json.dump(protocolo, f, ensure_ascii=False, indent=2, allow_nan=False)

ensayos = []
configuraciones = list(ParameterGrid(rejilla))
for numero, parametros in enumerate(configuraciones, 1):
    por_ronda = []
    for numero_ronda, (X_train, y_train, X_val, y_val) in enumerate(rondas, 1):
        bosque = RandomForestClassifier(**fijos, **parametros)
        bosque.fit(X_train, y_train)
        indice = list(bosque.classes_).index(1)
        puntajes = bosque.predict_proba(X_val)[:, indice]
        por_ronda.append({
            u: medir(y_val, (puntajes >= u).astype(int), puntajes)
            for u in umbrales
        })
        print(f"Configuración {numero}/{len(configuraciones)}, ronda {numero_ronda}/2 lista")
    for u in umbrales:
        junio, septiembre = por_ronda[0][u], por_ronda[1][u]
        ensayos.append({
            "familia": "bosque", "parametros": parametros, "umbral": u,
            "junio": junio, "septiembre": septiembre,
            "f1_medio": (junio["f1_abandono"] + septiembre["f1_abandono"]) / 2,
            "ap_media": (junio["average_precision"] + septiembre["average_precision"]) / 2,
        })


def criterio(fila):
    return (fila["f1_medio"], fila["ap_media"], -abs(fila["umbral"] - 0.5))


mejor = max(ensayos, key=criterio)
referencia = arbol_v2["mejor_validacion"]
# En empate completo conservamos el árbol ya disponible.
ganador_desarrollo = mejor if criterio(mejor) > criterio(referencia) else referencia
resumen = {
    **protocolo, "configuraciones": len(configuraciones), "ajustes": 2 * len(configuraciones),
    "mejor_bosque": mejor, "referencia_arbol_v2": referencia,
    "ganador_desarrollo": ganador_desarrollo, "ensayos": ensayos,
    "mejora_f1_medio_vs_arbol": mejor["f1_medio"] - referencia["f1_medio"],
    "meta_050_ambos_periodos_bosque": all(
        mejor[p]["f1_abandono"] >= 0.5 for p in ("junio", "septiembre")),
    "advertencia": "Resultados de selección; sin nueva prueba independiente ni sustitución de versión1",
}
with (salida / "resultados.json").open("x", encoding="utf-8") as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2, allow_nan=False)
print("\nRESUMEN COMPARACIÓN BOSQUE")
print("Configuración:", mejor["parametros"])
print("Parámetros fijos:", fijos)
print("Umbral:", mejor["umbral"])
print("Junio:", mejor["junio"])
print("Septiembre:", mejor["septiembre"])
print("F1 medio bosque:", mejor["f1_medio"])
print("F1 medio árbol ampliado:", referencia["f1_medio"])
print("Mejora:", resumen["mejora_f1_medio_vs_arbol"])
print("F1>=0.50 en ambos periodos:", resumen["meta_050_ambos_periodos_bosque"])
print("Ganador de desarrollo:", ganador_desarrollo["familia"])
print("Evidencia:", salida)
print("No se leyó diciembre ni se reemplazó el agente actual.")
