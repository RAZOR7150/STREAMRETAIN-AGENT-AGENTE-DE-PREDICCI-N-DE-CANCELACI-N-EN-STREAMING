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
import joblib
from datetime import datetime, timezone
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

warnings.filterwarnings("error", category=ConvergenceWarning)
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

ruta_seleccion = raiz / "experiments" / "seleccion_congelada.json"
seleccion = json.loads(ruta_seleccion.read_text(encoding="utf-8-sig"))
hash_seleccion = hashlib.sha256(ruta_seleccion.read_bytes()).hexdigest()
salida = raiz / "experiments" / "prueba_final"
ruta_predicciones = carpeta / "predicciones_prueba_final.csv"
# Evitamos sobrescribir evidencia o repetir la prueba inadvertidamente.
if salida.exists() or ruta_predicciones.exists():
    raise FileExistsError("Ya hay archivos de prueba final; revisar antes de repetir")
if seleccion["estado"] != "congelado_antes_de_evaluar_diciembre":
    raise ValueError("La selección no tiene el estado esperado")
if seleccion["caracteristicas"] != columnas_x or seleccion["semilla"] != 42:
    raise ValueError("Características o semilla diferentes")
if seleccion["sklearn"] != sklearn.__version__:
    raise ValueError("Cambió la versión de sklearn; revisar el entorno")

# Acumulamos únicamente ejemplos de desarrollo y conservamos sus huellas.
X_des, y_des, usuarios_des = [], [], set()
for meta in seleccion["cohortes_desarrollo"]:
    X, y, usuarios, huella = cargar(
        f"cohorte_{meta['corte']}.csv", meta["corte"], meta["filas"])
    if huella != meta["sha256"]:
        raise ValueError("Cambió una cohorte de desarrollo")
    X_des.extend(X)
    y_des.extend(y)
    usuarios_des.update(usuarios)

# Diciembre se abre ahora, cuando la decisión ya está guardada.
meta_test = seleccion["prueba_reservada"]
if any(m["seguimiento_hasta"] >= meta_test["corte"]
       for m in seleccion["cohortes_desarrollo"]):
    raise ValueError("El seguimiento de desarrollo alcanza la prueba")
nombre_test = f"cohorte_{meta_test['corte']}.csv"
Xt, yt, usuarios_test, hash_test = cargar(
    nombre_test, meta_test["corte"], meta_test["filas"])
if hash_test != meta_test["sha256"]:
    raise ValueError("Cambió la cohorte reservada")
if set(y_des) != {0, 1} or set(yt) != {0, 1}:
    raise ValueError("Se necesitan ambas clases para estas métricas")

# Crear la carpeta reserva esta ejecución. Si hay un fallo posterior,
# comparte el error; no borres los archivos para intentar mejorar resultados.
salida.mkdir(parents=True, exist_ok=False)

resultados = {}
modelos = {}
paquetes = {}
for familia, decision in seleccion["mejores_por_familia"].items():
    modelo = construir(familia, decision["parametros"])
    # Único ajuste final de esta familia: SOLO los tres periodos anteriores.
    modelo.fit(X_des, y_des)
    indice = list(modelo.classes_).index(1)
    puntajes = modelo.predict_proba(Xt)[:, indice]
    umbral = decision["umbral"]
    predicciones = (puntajes >= umbral).astype(int)
    resultados[familia] = {
        "parametros": decision["parametros"], "umbral": umbral,
        "metricas": medir(yt, predicciones, puntajes),
    }
    modelos[familia] = (puntajes, predicciones)
    # Guardamos modelo + contrato de entrada + umbral, no solo el estimador.
    paquete = {
        "modelo": modelo, "familia": familia,
        "parametros": decision["parametros"], "umbral": umbral,
        "caracteristicas": columnas_x, "semilla": 42,
        "sklearn": sklearn.__version__, "python": platform.python_version(),
        "sha256_seleccion": hash_seleccion,
        "cohortes_entrenamiento": seleccion["cohortes_desarrollo"],
        "advertencia": "Puntaje no calibrado; etiquetas reconstruidas bajo supuesto de cobertura",
    }
    paquetes[familia] = paquete
    joblib.dump(paquete, salida / f"modelo_{familia}.joblib")

baseline = DummyClassifier(strategy="most_frequent", random_state=42)
baseline.fit(X_des, y_des)
indice = list(baseline.classes_).index(1)
metricas_baseline = medir(
    yt, baseline.predict(Xt), baseline.predict_proba(Xt)[:, indice])

# Conservamos el ganador de VALIDACIÓN, aunque otra familia gane en diciembre.
ganador = seleccion["ganador"]["familia"]
joblib.dump(paquetes[ganador], salida / "modelo_agente.joblib")
m = resultados[ganador]["metricas"]
informe = {
    "estado": "prueba_final_evaluada_sin_reseleccion",
    "fecha_utc": datetime.now(timezone.utc).isoformat(),
    "sha256_seleccion": hash_seleccion,
    "semilla": 42, "python": platform.python_version(),
    "sklearn": sklearn.__version__, "caracteristicas": columnas_x,
    "cohortes_desarrollo": seleccion["cohortes_desarrollo"],
    "prueba": meta_test, "filas_entrenamiento": len(y_des),
    "filas_prueba": len(yt), "abandonos_prueba": sum(yt),
    "usuarios_compartidos": len(usuarios_des & usuarios_test),
    "baseline": metricas_baseline, "modelos": resultados,
    "modelo_agente": ganador,
    "metas": {
        "accuracy_al_menos_075": m["accuracy"] >= 0.75,
        "f1_al_menos_050": m["f1_abandono"] >= 0.50,
        "f1_superior_baseline": m["f1_abandono"] > metricas_baseline["f1_abandono"],
    },
    "limitaciones": [
        "Etiquetas reconstruidas, no oficiales, bajo supuesto de cobertura",
        "Auditoría manual de junio parcial; nuevos cortes sin auditoría manual completa",
        "Muestra determinista de usuarios; cuatro cortes históricos",
        "Usuarios pueden repetirse entre periodos; no es evaluación de usuarios nuevos",
        "Puntajes no calibrados; AP es average_precision_score",
    ],
    "sha256_modelo_agente": hashlib.sha256(
        (salida / "modelo_agente.joblib").read_bytes()).hexdigest(),
}
with (salida / "resultados.json").open("x", encoding="utf-8") as archivo:
    json.dump(informe, archivo, ensure_ascii=False, indent=2, allow_nan=False)
    archivo.write("\n")

puntajes, predicciones = modelos[ganador]
# Releemos solo el CSV pequeño para mantener exactamente el orden de usuarios.
# El cargador devuelve un set de usuarios: un set NO conserva el orden de filas.
with (carpeta / nombre_test).open(encoding="utf-8-sig", newline="") as archivo:
    filas_test = list(csv.DictReader(archivo))
if len(filas_test) != len(yt):
    raise ValueError("El archivo cambió durante la ejecución")
if hashlib.sha256((carpeta / nombre_test).read_bytes()).hexdigest() != hash_test:
    raise ValueError("Cambió el contenido de prueba durante la ejecución")
campos = ["msno", "corte", *columnas_x, "is_churn", "puntaje", "prediccion", "tipo"]
with ruta_predicciones.open("x", encoding="utf-8", newline="") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=campos)
    escritor.writeheader()
    for i, fila in enumerate(filas_test):
        real, pred = int(fila["is_churn"]), int(predicciones[i])
        tipo = {(0, 0): "TN", (0, 1): "FP", (1, 0): "FN", (1, 1): "TP"}[(real, pred)]
        escritor.writerow({**fila, "puntaje": float(puntajes[i]),
                           "prediccion": pred, "tipo": tipo})

print("\nRESUMEN PRUEBA FINAL")
print("Entrenamiento:", len(y_des), "Prueba:", len(yt))
print("Abandonos en prueba:", sum(yt))
print("Usuarios compartidos:", len(usuarios_des & usuarios_test))
print("Baseline:", metricas_baseline)
for familia, resultado in resultados.items():
    print("\nFamilia:", familia, "Umbral:", resultado["umbral"])
    print("Métricas:", resultado["metricas"])
print("\nModelo del agente (elegido antes de la prueba):", ganador)
print("Metas:", informe["metas"])
print("Evidencia:", salida)
print("Predicciones locales:", ruta_predicciones)
