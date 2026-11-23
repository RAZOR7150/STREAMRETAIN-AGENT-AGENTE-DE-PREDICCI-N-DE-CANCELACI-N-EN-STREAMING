import csv
import hashlib
import json
import math
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, average_precision_score,
)

def leer_tabla(ruta, campos, huella):
    if hashlib.sha256(ruta.read_bytes()).hexdigest() != huella:
        raise ValueError(f"Cambió el archivo: {ruta.name}")
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != campos:
            raise ValueError(f"Esquema inesperado: {ruta.name}")
        filas = list(lector)
    if any(None in f or any(v is None for v in f.values()) for f in filas):
        raise ValueError("Fila mal formada")
    return filas


def cargar_par(meta, meta_base, *, carpeta, carpeta_nueva, base, columnas):
    nombre = f"cohorte_{meta['corte']}.csv"
    originales = leer_tabla(carpeta / nombre, ["msno", "corte", *base, "is_churn"], meta_base["sha256"])
    nuevas = leer_tabla(carpeta_nueva / nombre, ["msno", "corte", *columnas, "is_churn"], meta["sha256"])
    indice = {f["msno"]: f for f in originales}
    if len(indice) != len(originales) or len(nuevas) != meta["filas"] or len(originales) != meta_base["filas"]:
        raise ValueError("Tamaño o duplicados en tabla original")
    X6, X10, y, usuarios = [], [], [], set()
    for fila in nuevas:
        u = fila["msno"]
        if not u or u in usuarios or u not in indice or fila["corte"] != meta["corte"]:
            raise ValueError("Usuario o corte inválido")
        if any(fila[c] != indice[u][c] for c in ["msno", "corte", *base, "is_churn"]):
            raise ValueError("Cambió una variable original o la etiqueta")
        if fila["is_churn"] not in ("0", "1"):
            raise ValueError("Etiqueta inválida")
        seis = [int(fila[c]) for c in base]
        n90, n30, cancelaciones, dias, reciente, restantes = seis
        if not (n90 >= 1 and 0 <= n30 <= n90 and 0 <= cancelaciones <= n90
                and 1 <= dias <= min(90, n90) and 1 <= reciente <= 90 and 0 <= restantes <= 29):
            raise ValueError("Características originales fuera de dominio")
        diez = [float(fila[c]) for c in columnas]
        if not all(math.isfinite(v) for v in diez) or diez[6] < 0 or not 0 <= diez[9] <= 1:
            raise ValueError("Nueva característica inválida")
        X6.append(seis)
        X10.append(diez)
        y.append(int(fila["is_churn"]))
        usuarios.add(u)
    if usuarios != set(indice) or set(y) != {0, 1}:
        raise ValueError("Cambió el conjunto de usuarios o faltan clases")
    return X6, X10, y

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

def leer_json(ruta):
    return json.loads(ruta.read_text(encoding="utf-8-sig"))


def huella(ruta):
    # Para manifiestos, modelos y CSV pequeños. No usar para cargar un comprimido enorme en memoria.
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def guardar_json(ruta, contenido):
    # El modo x falla si ya existe: conserva la evidencia de ejecuciones anteriores.
    with ruta.open("x", encoding="utf-8") as archivo:
        json.dump(contenido, archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write("\n")
