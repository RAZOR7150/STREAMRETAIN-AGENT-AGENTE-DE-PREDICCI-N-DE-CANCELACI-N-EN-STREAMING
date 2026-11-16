# Guía 16 — Ejecutar la línea base temporal y guardar evidencia

## Objetivo

Entrenar un clasificador mayoritario con marzo y medir sus predicciones en junio. Es la línea base prometida, no la regresión logística ni el árbol final. Junio es validación; diciembre sigue reservado para prueba final. Una sola separación no constituye todavía validación cruzada temporal completa.

Requisito: guía 15 terminada con controles correctos. Crea `scripts/14_linea_base_temporal.py` con estos bloques en orden. No necesitas instalar paquetes nuevos: scikit-learn ya está disponible en el intérprete del proyecto.

## 1. Leer y comprobar las cohortes

```python
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
```

X contiene solo las seis características. No contiene msno, corte, is_churn ni datos de seguimiento. y contiene las etiquetas. Los conjuntos de usuarios sirven para comprobar identidad y describir solapamiento, no como predictores. Las comprobaciones de clases verifican archivos; no eligen la predicción. La selección de clase se hará solo con y_train.

## 2. Entrenar y predecir

```python
# Aprende la clase más frecuente de marzo e ignora los valores de X para predecir.
modelo = DummyClassifier(strategy="most_frequent", random_state=42)
modelo.fit(X_train, y_train)

# Junio no interviene en fit: lo usamos para predicción y evaluación.
predicciones = modelo.predict(X_val)
# Localizamos la columna de probabilidad correspondiente a abandono (clase 1).
indice_abandono = list(modelo.classes_).index(1)
puntajes = modelo.predict_proba(X_val)[:, indice_abandono]

matriz = confusion_matrix(y_val, predicciones, labels=[0, 1])
metricas = {
    "accuracy": float(accuracy_score(y_val, predicciones)),
    "precision_abandono": float(precision_score(y_val, predicciones, zero_division=0)),
    "recall_abandono": float(recall_score(y_val, predicciones, zero_division=0)),
    "f1_abandono": float(f1_score(y_val, predicciones, zero_division=0)),
    "roc_auc": float(roc_auc_score(y_val, puntajes)),
    "average_precision": float(average_precision_score(y_val, puntajes)),
}
```

fit determina la clase mayoritaria del entrenamiento. DummyClassifier no aprende relaciones entre características y abandono; ofrece un punto de comparación para los modelos posteriores. La semilla queda declarada por reproducibilidad, aunque most_frequent es determinista.

zero_division=0 establece cómo reportar precisión cuando no se predice ningún positivo. No significa que detectemos abandonos. Las filas de la matriz son clases reales [0,1] y las columnas predicciones [0,1]: [[TN,FP],[FN,TP]].

ROC-AUC y Average Precision usan puntajes, no etiquetas duras como sustituto de probabilidades. Este clasificador da puntajes constantes: no ordena usuarios por riesgo. Average Precision (AP) resume la curva precisión-recall y se reporta con su nombre exacto; no la llames área trapezoidal PR-AUC, porque son cálculos distintos. Se documentará esta precisión del cálculo en el avance. Ambas clases están presentes en junio según los controles.

## 3. Guardar un resultado verificable

```python
resultado = {
    "experimento": "baseline_mayoritaria_marzo_validacion_junio",
    "modelo": "DummyClassifier",
    "estrategia": "most_frequent",
    "semilla": 42,
    "python": platform.python_version(),
    "scikit_learn": sklearn.__version__,
    "caracteristicas": columnas_x,
    "entrenamiento": {
        "corte": "2016-03-07", "seguimiento_hasta": "2016-05-05",
        "filas": len(y_train), "abandono": sum(y_train), "sha256": hash_train,
    },
    "validacion": {
        "corte": "2016-06-06", "seguimiento_hasta": "2016-08-04",
        "filas": len(y_val), "abandono": sum(y_val), "sha256": hash_val,
    },
    "usuarios_compartidos": len(usuarios_train & usuarios_val),
    "clases_predichas": sorted(set(int(v) for v in predicciones)),
    "metricas": metricas,
    "matriz_confusion": matriz.tolist(),
    "orden_clases": [0, 1],
    "limitaciones": [
        "Etiquetas reconstruidas bajo supuesto de cobertura del historial publicado",
        "Junio: auditoria manual parcial, dos de nueve casos revisados",
        "Una separacion temporal; no validacion cruzada completa ni prueba final",
        "Muestra determinista aproximada del 1 por ciento de usuarios; historia de 90 dias",
    ],
}
salida = raiz / "experiments" / "baseline_marzo_junio.json"
salida.parent.mkdir(parents=True, exist_ok=True)
with salida.open("x", encoding="utf-8") as archivo:
    json.dump(resultado, archivo, ensure_ascii=False, indent=2, allow_nan=False)
    archivo.write("\n")

print("Entrenamiento:", len(y_train), "Validacion:", len(y_val))
print("Usuarios compartidos:", resultado["usuarios_compartidos"])
print("Clases predichas:", resultado["clases_predichas"])
for nombre, valor in metricas.items():
    print(f"{nombre}: {valor:.6f}")
print("Matriz [[TN, FP], [FN, TP]]:", matriz.tolist())
print("Resultado guardado:", salida)
```

El JSON conserva métricas, contexto, versiones y huellas; no publica identificadores. No es el dataset ni un modelo serializado: el script permite volver a entrenar el baseline. No sobrescribir corridas previas sin revisión: si aparece FileExistsError, conserva la evidencia y avisa. Si falla cualquier validación, comparte el error sin quitarla.

## Ejecutar y entregar la evidencia

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\14_linea_base_temporal.py"
```

Comparte la salida de esta ejecución y la de características de junio. Todavía no hay resultados experimentales hasta que ejecutes. Por la definición de la línea base, esperamos que prediga la clase mayoritaria de marzo: verificarlo en la salida. Una exactitud alta no será suficiente para cumplir el proyecto si no detecta abandonos.

Con los resultados revisados, Codex preparará el avance de una página en Entregables, README y soporte del repositorio. El requisito de resultado en repositorio requiere versionar el script y JSON; una carpeta local sin Git no satisface por sí sola ese requisito. Si debe alojarse en GitHub/GitLab, se necesita el destino real, sin inventar enlaces. No publicar los CSV ni los comprimidos.
