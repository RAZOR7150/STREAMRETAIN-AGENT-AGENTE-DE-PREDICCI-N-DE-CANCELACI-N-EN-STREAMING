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

import warnings
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import ParameterGrid

warnings.filterwarnings("error", category=ConvergenceWarning)
archivo_anterior = raiz / "experiments" / "comparacion_20261122T202144442375Z" / "resultados.json"
archivo_seleccion = raiz / "experiments" / "seleccion_congelada.json"
if archivo_seleccion.exists():
    raise FileExistsError("Ya existe una decisión congelada; no reemplazar sin revisión")
anterior = json.loads(archivo_anterior.read_text(encoding="utf-8-sig"))
manifiesto = json.loads((carpeta / "preparacion_cohortes_finales.json").read_text(encoding="utf-8-sig"))
meta_sep = next(c for c in manifiesto["cohortes"] if c["corte"] == "2016-09-05")
meta_dic = next(c for c in manifiesto["cohortes"] if c["corte"] == "2016-12-05")

Xm, ym, um, hm = cargar("cohorte_2016-03-07.csv", "2016-03-07", 7443, 1095)
Xj, yj, uj, hj = cargar("cohorte_2016-06-06.csv", "2016-06-06", 7210, 411)
Xs, ys, us, hs = cargar("cohorte_2016-09-05.csv", "2016-09-05", meta_sep["filas"])
if (hm != anterior["datos"]["entrenamiento"]["sha256"]
        or hj != anterior["datos"]["validacion"]["sha256"]
        or hs != meta_sep["sha256"]):
    raise ValueError("Las huellas no coinciden con los datos de referencia")
if set(ys) != {0, 1}:
    raise ValueError("Septiembre no contiene ambas clases; revisar evaluación")
if columnas_x != anterior["caracteristicas"]:
    raise ValueError("Las características no coinciden")

# Son listas: + concatena ejemplos de meses anteriores.
X_train = Xm + Xj
y_train = ym + yj
rejillas = anterior["rejillas"]
umbrales = anterior["umbrales"]

def construir(familia, parametros):
    if familia == "logistica":
        return Pipeline([
            ("escala", StandardScaler()),
            ("modelo", LogisticRegression(
                solver="lbfgs", max_iter=5000, random_state=42, **parametros)),
        ])
    if familia == "arbol":
        return DecisionTreeClassifier(random_state=42, **parametros)
    raise ValueError("Familia no reconocida")


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


def clave(familia, parametros, umbral):
    # Mismo contenido produce misma clave, independientemente del orden del diccionario.
    return json.dumps([familia, parametros, umbral], sort_keys=True)


primera_ronda = {}
for fila in anterior["ensayos"]:
    k = clave(fila["familia"], fila["parametros"], fila["umbral"])
    if k in primera_ronda:
        raise ValueError("Ensayo duplicado en la primera ronda")
    primera_ronda[k] = fila["metricas"]

combinados = []
claves_visitadas = set()
for familia, rejilla in rejillas.items():
    for parametros in ParameterGrid(rejilla):
        modelo = construir(familia, parametros)
        modelo.fit(X_train, y_train)
        indice = list(modelo.classes_).index(1)
        puntajes = modelo.predict_proba(Xs)[:, indice]
        for umbral in umbrales:
            k = clave(familia, parametros, umbral)
            if k not in primera_ronda:
                raise ValueError("La rejilla no coincide con los ensayos de junio")
            claves_visitadas.add(k)
            m1 = primera_ronda[k]
            m2 = medir(ys, (puntajes >= umbral).astype(int), puntajes)
            combinados.append({
                "familia": familia, "parametros": parametros, "umbral": umbral,
                "junio": m1, "septiembre": m2,
                "f1_medio": (m1["f1_abandono"] + m2["f1_abandono"]) / 2,
                "ap_media": (m1["average_precision"] + m2["average_precision"]) / 2,
            })
        print("Configuración evaluada:", familia, parametros)
if claves_visitadas != set(primera_ronda):
    raise ValueError("Faltan configuraciones de la primera ronda")


def criterio(fila):
    return (fila["f1_medio"], fila["ap_media"], -abs(fila["umbral"] - 0.5))


mejores = {}
for familia in rejillas:
    mejores[familia] = max((f for f in combinados if f["familia"] == familia), key=criterio)
ganador = max(mejores.values(), key=criterio)

# Referencia mayoritaria de esta segunda ronda: aprender SOLO de marzo+junio.
baseline = DummyClassifier(strategy="most_frequent", random_state=42)
baseline.fit(X_train, y_train)
indice = list(baseline.classes_).index(1)
metricas_baseline = medir(ys, baseline.predict(Xs), baseline.predict_proba(Xs)[:, indice])

seleccion = {
    "estado": "congelado_antes_de_evaluar_diciembre",
    "semilla": 42, "python": platform.python_version(), "sklearn": sklearn.__version__,
    "caracteristicas": columnas_x,
    "criterio": "media simple F1 junio/septiembre, luego AP media, luego umbral cercano a 0.5",
    "fuente_primera_ronda": str(archivo_anterior.relative_to(raiz)),
    "sha256_primera_ronda": hashlib.sha256(archivo_anterior.read_bytes()).hexdigest(),
    "cohortes_desarrollo": [
        {"corte": "2016-03-07", "filas": len(ym), "sha256": hm, "seguimiento_hasta": "2016-05-05"},
        {"corte": "2016-06-06", "filas": len(yj), "sha256": hj, "seguimiento_hasta": "2016-08-04"},
        {"corte": "2016-09-05", "filas": len(ys), "sha256": hs, "seguimiento_hasta": "2016-11-03"},
    ],
    "prueba_reservada": meta_dic,
    "mejores_por_familia": mejores,
    "ganador": ganador,
    "baseline_septiembre": metricas_baseline,
    "ensayos_dos_rondas": combinados,
    "limitaciones": ["Etiquetas reconstruidas bajo supuesto de cobertura",
                     "Validación usada para seleccionar; prueba final aún no evaluada",
                     "Auditoría manual parcial de junio; sin auditoría manual completa de nuevos cortes"],
}
with archivo_seleccion.open("x", encoding="utf-8") as archivo:
    json.dump(seleccion, archivo, ensure_ascii=False, indent=2, allow_nan=False)
    archivo.write("\n")
print("\nRESUMEN SEGUNDA RONDA")
print("Entrenamiento marzo+junio:", len(y_train), "Validación septiembre:", len(ys))
print("Abandonos septiembre:", sum(ys))
print("Baseline septiembre:", metricas_baseline)
for familia, fila in mejores.items():
    print("\nFamilia:", familia, "Parámetros:", fila["parametros"], "Umbral:", fila["umbral"])
    print("F1 junio:", fila["junio"]["f1_abandono"],
          "F1 septiembre:", fila["septiembre"]["f1_abandono"], "F1 medio:", fila["f1_medio"])
    print("Métricas septiembre:", fila["septiembre"])
print("\nGanador congelado:", ganador["familia"])
print("Decisión guardada:", archivo_seleccion)
print("Diciembre NO se ha evaluado en este programa.")
