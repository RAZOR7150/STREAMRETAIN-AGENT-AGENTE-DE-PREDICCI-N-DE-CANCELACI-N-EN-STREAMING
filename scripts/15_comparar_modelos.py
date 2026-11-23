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


def cargar(nombre, corte, esperados, abandonos_esperados):
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
    if len(y) != esperados or sum(y) != abandonos_esperados:
        raise ValueError(f"Tamaño o clases diferentes a lo revisado: {nombre}")
    # Una huella del archivo ayuda a identificar exactamente los datos de esta corrida.
    # Estos CSV son pequeños; no aplicar read_bytes al comprimido completo.
    huella = hashlib.sha256(ruta.read_bytes()).hexdigest()
    return X, y, usuarios, huella

X_train, y_train, usuarios_train, hash_train = cargar(
    "cohorte_2016-03-07.csv", "2016-03-07", 7443, 1095)
X_val, y_val, usuarios_val, hash_val = cargar(
    "cohorte_2016-06-06.csv", "2016-06-06", 7210, 411)

from datetime import datetime, timezone
import warnings
import joblib
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import ParameterGrid

# Una regresión que no convergió requiere revisión; no ocultamos la advertencia.
warnings.filterwarnings("error", category=ConvergenceWarning)

# Cada ejecución conserva su evidencia en una carpeta distinta.
identificador = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
carpeta_resultados = raiz / "experiments" / ("comparacion_" + identificador)
carpeta_resultados.mkdir(parents=True, exist_ok=False)

rejillas = {
    "logistica": {
        "C": [0.1, 1.0, 10.0],
        "class_weight": [None, "balanced"],
    },
    "arbol": {
        "max_depth": [3, 5, 8],
        "min_samples_leaf": [20, 100],
        "class_weight": ["balanced"],
    },
}
umbrales = [i / 10 for i in range(1, 10)]  # 0,1; 0,2; ...; 0,9.

def construir(familia, parametros):
    if familia == "logistica":
        # La escala se aprende en fit con marzo y se reutiliza en junio.
        return Pipeline([
            ("escala", StandardScaler()),
            ("modelo", LogisticRegression(
                solver="lbfgs", max_iter=5000, random_state=42, **parametros)),
        ])
    return DecisionTreeClassifier(random_state=42, **parametros)


def evaluar(puntajes, umbral):
    predicciones = (puntajes >= umbral).astype(int)
    return {
        "accuracy": float(accuracy_score(y_val, predicciones)),
        "precision_abandono": float(precision_score(y_val, predicciones, zero_division=0)),
        "recall_abandono": float(recall_score(y_val, predicciones, zero_division=0)),
        "f1_abandono": float(f1_score(y_val, predicciones, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_val, puntajes)),
        "average_precision": float(average_precision_score(y_val, puntajes)),
        "matriz_confusion": confusion_matrix(y_val, predicciones, labels=[0, 1]).tolist(),
    }


def criterio(fila):
    # Prioridad declarada: F1; empate -> AP; otro empate -> umbral cercano a 0,5.
    m = fila["metricas"]
    return (m["f1_abandono"], m["average_precision"], -abs(fila["umbral"] - 0.5))

ensayos = []
mejores = {}
modelos_mejores = {}

for familia, rejilla in rejillas.items():
    for parametros in ParameterGrid(rejilla):
        modelo = construir(familia, parametros)
        modelo.fit(X_train, y_train)
        indice_positivo = list(modelo.classes_).index(1)
        puntajes = modelo.predict_proba(X_val)[:, indice_positivo]
        resultados_configuracion = []
        for umbral in umbrales:
            fila = {
                "familia": familia, "parametros": parametros,
                "umbral": umbral, "metricas": evaluar(puntajes, umbral),
            }
            ensayos.append(fila)
            resultados_configuracion.append(fila)
            if familia not in mejores or criterio(fila) > criterio(mejores[familia]):
                mejores[familia] = fila
                modelos_mejores[familia] = modelo
        mejor_configuracion = max(resultados_configuracion, key=criterio)
        print(familia, parametros, "mejor F1 de esta configuracion:",
              round(mejor_configuracion["metricas"]["f1_abandono"], 4))

referencia = json.loads(
    (raiz / "experiments" / "baseline_marzo_junio.json").read_text(encoding="utf-8-sig"))
if (referencia["entrenamiento"]["sha256"] != hash_train
        or referencia["validacion"]["sha256"] != hash_val):
    raise ValueError("Los datos no coinciden con los de la baseline; investigar")

for familia, modelo in modelos_mejores.items():
    # Guardamos el modelo junto con el umbral y orden de características necesarios.
    paquete = {
        "modelo": modelo,
        "umbral": mejores[familia]["umbral"],
        "caracteristicas": columnas_x,
        "corte_entrenamiento": "2016-03-07",
        "estado": "provisional_seleccionado_en_junio",
    }
    joblib.dump(paquete, carpeta_resultados / (familia + "_provisional.joblib"))

ganador = max(mejores.values(), key=criterio)
resultado = {
    "estado": "seleccion_provisional_en_validacion_no_prueba_final",
    "semilla": 42,
    "python": platform.python_version(), "sklearn": sklearn.__version__,
    "caracteristicas": columnas_x,
    "datos": {
        "entrenamiento": {"corte": "2016-03-07", "n": len(y_train), "sha256": hash_train},
        "validacion": {"corte": "2016-06-06", "n": len(y_val), "sha256": hash_val},
    },
    "rejillas": rejillas, "umbrales": umbrales,
    "criterio": "F1, luego AP y luego cercania de umbral a 0.5",
    "baseline": referencia["metricas"],
    "mejores_por_familia": mejores,
    "ganador_provisional": ganador,
    "ensayos": ensayos,
    "advertencias": [
        "Validacion usada para seleccionar parametros y umbral; resultado optimista posible",
        "Etiquetas reconstruidas bajo supuesto de cobertura; auditoria junio parcial",
        "Puntajes no calibrados; prueba final y segunda ronda temporal pendientes",
    ],
}
with (carpeta_resultados / "resultados.json").open("x", encoding="utf-8") as archivo:
    json.dump(resultado, archivo, ensure_ascii=False, indent=2, allow_nan=False)
    archivo.write("\n")

print("\nBASELINE F1:", referencia["metricas"]["f1_abandono"])
for familia, mejor in mejores.items():
    print("\nMODELO:", familia)
    print("Parametros:", mejor["parametros"], "Umbral:", mejor["umbral"])
    print("Metricas:", mejor["metricas"])
print("\nGanador provisional:", ganador["familia"])
print("Evidencia y modelos:", carpeta_resultados)
