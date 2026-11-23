# Guía 19 — Segunda validación temporal y decisión congelada

## Objetivo

Completar dos rondas temporales: marzo -> junio (ya ejecutada), y marzo+junio -> septiembre (ahora). Para cada configuración y umbral usaremos la media simple del F1 de ambas rondas; desempate por AP media y cercanía del umbral a 0,5. Se elige una configuración por familia y luego la familia ganadora. El criterio queda declarado antes de ejecutar septiembre. Diciembre NO se abre ni se usa para decidir.

La media da el mismo peso a cada periodo, no a cada fila. Los resultados siguen siendo de validación utilizada para elegir; la estimación final requiere diciembre. Las etiquetas de junio se conocen hasta 4 de agosto, antes del corte de septiembre. Las de septiembre se conocen hasta 3 de noviembre, antes del corte de diciembre.

## 1. Reutilizar la carga

Crea `scripts/17_validacion_temporal.py`. Copia de `15_comparar_modelos.py` el inicio desde sus importaciones hasta el FINAL de la función `cargar`, sin copiar las llamadas que cargan marzo/junio ni el resto del programa.

En esa copia cambia la firma a:

```python
def cargar(nombre, corte, esperados, abandonos_esperados=None):
```

Reemplaza su comprobación de tamaño/clases por estas dos, en la misma posición y dentro de la función:

```python
    if len(y) != esperados:
        raise ValueError(f"Tamaño inesperado: {nombre}")
    if abandonos_esperados is not None and sum(y) != abandonos_esperados:
        raise ValueError(f"Clases diferentes a lo revisado: {nombre}")
```

El resto de cargar permanece igual. No conocemos aún los abandonos de septiembre y no inventaremos un conteo. Mantenemos el control de filas, valores, usuarios y huella; marzo/junio mantienen también su conteo conocido.

## 2. Cargar exclusivamente las tres cohortes de desarrollo

```python
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
```

El manifiesto aporta el tamaño y hash de diciembre, pero no se lee su CSV ni sus etiquetas. Guardar su identidad esperada permite evitar después evaluar accidentalmente otro archivo. En entrenamiento puede repetirse un usuario con distinto corte; son ejemplos temporales distintos. No se incluye msno como predictor.

## 3. Constructor, métricas e identidad de cada configuración

```python
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
```

En esta ronda se ajusta de nuevo un modelo por configuración, con más historia de entrenamiento. No se reutiliza un objeto ya ajustado para mezclar escalas; Pipeline aprende media/desviación solamente de marzo+junio. Se evalúan exactamente las configuraciones y umbrales de la primera ronda.

## 4. Entrenar, validar y combinar las rondas

```python
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
```

Cada configuración recibe dos métricas de validación y un promedio. No seleccionamos un umbral distinto para cada periodo para luego fingir que existía una sola decisión: elegimos el mismo umbral mediante la media de las dos rondas. No se modifica la meta F1>=0,50 si los resultados son inferiores.

## 5. Dejar la decisión congelada antes de abrir diciembre

```python
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
```

El modo x impide reemplazar una decisión anterior sin revisión. No uses los joblib provisionales de junio como modelo final: la próxima guía reajustará las configuraciones congeladas con las tres cohortes de desarrollo, evaluará diciembre una vez y guardará los modelos finales. Comparará baseline y ambas familias; el modelo del agente será el elegido aquí, no el que gane por azar al mirar diciembre.

## Ejecutar

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\17_validacion_temporal.py"
```

Comparte desde RESUMEN SEGUNDA RONDA. No hace falta repetir la ejecución de junio ni abrir el CSV de diciembre. Si falla un control, comparte el error sin eliminarlo. Con esa salida prepararemos evaluación final, casos de error y demostración.
