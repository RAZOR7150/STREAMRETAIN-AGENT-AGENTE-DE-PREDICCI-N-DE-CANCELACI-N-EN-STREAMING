# Guía 27 — Comparar seis y diez características en desarrollo

## Objetivo

La preparación conservó7443 ejemplos de marzo,7210 de junio y8251 de septiembre. Tenemos diez variables numéricas; cuatro son medias o proporciones y deben leerse como float, sin convertirlas a enteros. El máximo de395 días de duración media en marzo es una observación que merece revisar si resulta relevante; por sí solo no demuestra un error y no se recorta automáticamente. La autorrenovación está entre0 y1.

Haremos dos comparaciones distintas:

1. **Aporte de las características:** seis frente a diez con exactamente el árbol seleccionado en V2 (depth5,leaf20,weightNone) y umbral0,20.
2. **Selección con diez características:** la misma rejilla de56 configuraciones y19umbrales de V2, bajo las mismas dos rondas temporales. Así ambas versiones tienen el mismo presupuesto de búsqueda.

El criterio sigue siendo F1 medio de junio y septiembre; AP media y cercanía a0,5 desempatan. No se entrena usando diciembre. Cualquier resultado>=0,50 aquí será de validación, no una prueba final independiente. No se cambia el modelo de la CLI ni de la interfaz.

## 1. Crea scripts/24_comparar_caracteristicas.py

Copia la función medir completa de scripts/17_validacion_temporal.py después de las siguientes importaciones. No importes ni ejecutes ese script; no copies cargar porque espera seis enteros.

```python
import csv
import hashlib
import json
import math
import platform
from pathlib import Path
from datetime import datetime, timezone
import sklearn
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import ParameterGrid
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, average_precision_score,
)
# Pega aquí la definición de medir.

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data" / "derived"
carpeta_nueva = carpeta / "caracteristicas_suscripcion_v4"
ruta_manifiesto = carpeta_nueva / "manifiesto.json"
ruta_referencia = raiz / "experiments" / "busqueda_arbol_v2" / "resultados.json"
manifiesto = json.loads(ruta_manifiesto.read_text(encoding="utf-8-sig"))
referencia = json.loads(ruta_referencia.read_text(encoding="utf-8-sig"))
columnas = manifiesto["caracteristicas"]
base = referencia["caracteristicas"]
salida = raiz / "experiments" / "comparacion_caracteristicas_v4"
if salida.exists():
    raise FileExistsError("Ya existe esta comparación; revisar antes de repetir")
if (len(base) != 6 or len(columnas) != 10 or columnas[:6] != base
        or columnas[6:] != manifiesto["nuevas"]
        or manifiesto["cohortes_base"] != referencia["cohortes"]
        or referencia["sklearn"] != sklearn.__version__):
    raise ValueError("Contrato, cohortes o entorno diferentes")


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


def cargar_par(meta, meta_base):
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


datos = {}
for meta in manifiesto["cohortes"]:
    meta_base = next(m for m in manifiesto["cohortes_base"] if m["corte"] == meta["corte"])
    datos[meta["corte"]] = cargar_par(meta, meta_base)
if set(datos) != {"2016-03-07", "2016-06-06", "2016-09-05"}:
    raise ValueError("Se esperan solo tres cohortes de desarrollo")
```

La unión se verifica por identificador, no por posición entre archivos. Ambas matrices se construyen en el mismo orden y con las mismas etiquetas. Los hashes fijan los datos utilizados. Los precios e importes se conservan como valores registrados: no se inventa un rango máximo ni se interpreta un promedio como ingreso neto.

## 2. Fijar protocolo y reproducir el control de seis variables

```python
rejilla, umbrales = referencia["rejilla"], referencia["umbrales"]
control = referencia["mejor_validacion"]
salida.mkdir(parents=True, exist_ok=False)
protocolo = {
    "estado": "desarrollo_exploratorio_v4_posterior_a_prueba_v1",
    "fecha_utc": datetime.now(timezone.utc).isoformat(),
    "semilla": 42, "sklearn": sklearn.__version__, "python": platform.python_version(),
    "sha256_manifiesto": hashlib.sha256(ruta_manifiesto.read_bytes()).hexdigest(),
    "sha256_referencia": hashlib.sha256(ruta_referencia.read_bytes()).hexdigest(),
    "cohortes": manifiesto["cohortes"], "caracteristicas": columnas,
    "rejilla": rejilla, "umbrales": umbrales,
    "criterio": referencia["criterio"],
}
with (salida / "protocolo.json").open("x", encoding="utf-8") as f:
    json.dump(protocolo, f, ensure_ascii=False, indent=2, allow_nan=False)


def evaluar(parametros, numero_columnas, lista_umbrales):
    posicion = 0 if numero_columnas == 6 else 1
    Xm, Xj, Xs = (datos[c][posicion] for c in ("2016-03-07", "2016-06-06", "2016-09-05"))
    ym, yj, ys = (datos[c][2] for c in ("2016-03-07", "2016-06-06", "2016-09-05"))
    rondas = [(Xm, ym, Xj, yj), (Xm + Xj, ym + yj, Xs, ys)]
    metricas = []
    for X_train, y_train, X_val, y_val in rondas:
        modelo = DecisionTreeClassifier(random_state=42, **parametros)
        modelo.fit(X_train, y_train)
        puntajes = modelo.predict_proba(X_val)[:, list(modelo.classes_).index(1)]
        metricas.append({u: medir(y_val, (puntajes >= u).astype(int), puntajes) for u in lista_umbrales})
    return [{"familia": "arbol", "n_caracteristicas": numero_columnas,
             "parametros": parametros, "umbral": u,
             "junio": metricas[0][u], "septiembre": metricas[1][u],
             "f1_medio": (metricas[0][u]["f1_abandono"] + metricas[1][u]["f1_abandono"]) / 2,
             "ap_media": (metricas[0][u]["average_precision"] + metricas[1][u]["average_precision"]) / 2}
            for u in lista_umbrales]


control6 = evaluar(control["parametros"], 6, [control["umbral"]])[0]
for periodo in ("junio", "septiembre"):
    if (abs(control6[periodo]["f1_abandono"] - control[periodo]["f1_abandono"]) > 1e-12
            or control6[periodo]["matriz_confusion"] != control[periodo]["matriz_confusion"]):
        raise ValueError("No se reprodujo el control; revisar antes de comparar")
print("Control de seis características reproducido:", control6["f1_medio"])
```

## 3. Comparar y guardar resultados

```python
ensayos = []
configuraciones = list(ParameterGrid(rejilla))
for i, parametros in enumerate(configuraciones, 1):
    ensayos.extend(evaluar(parametros, 10, umbrales))
    print(f"Diez características: configuración {i}/{len(configuraciones)} lista")


def criterio(fila):
    return (fila["f1_medio"], fila["ap_media"], -abs(fila["umbral"] - 0.5))


# Compara el aporte de información SIN cambiar parámetros ni umbral.
control10 = next(f for f in ensayos if f["parametros"] == control["parametros"]
                 and f["umbral"] == control["umbral"])
mejor10 = max(ensayos, key=criterio)
ganador = mejor10 if criterio(mejor10) > criterio(control6) else control6
resumen = {
    **protocolo, "control_6": control6, "control_10_misma_configuracion": control10,
    "mejor_10": mejor10, "ganador_desarrollo": ganador, "ensayos": ensayos,
    "delta_solo_caracteristicas": control10["f1_medio"] - control6["f1_medio"],
    "delta_tras_seleccion": mejor10["f1_medio"] - control6["f1_medio"],
    "meta_050_ambos_periodos_mejor10": all(mejor10[p]["f1_abandono"] >= 0.5 for p in ("junio", "septiembre")),
    "advertencia": "Sin nueva prueba independiente ni reemplazo del agente v1",
}
with (salida / "resultados.json").open("x", encoding="utf-8") as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2, allow_nan=False)
print("\nRESUMEN COMPARACIÓN DE CARACTERÍSTICAS")
print("F1 medio seis:", control6["f1_medio"])
print("F1 medio diez, mismos parámetros/umbral:", control10["f1_medio"])
print("Cambio atribuible a añadir características en este control:", resumen["delta_solo_caracteristicas"])
print("Mejor configuración diez:", mejor10["parametros"], "Umbral:", mejor10["umbral"])
print("Junio:", mejor10["junio"])
print("Septiembre:", mejor10["septiembre"])
print("F1 medio diez seleccionado:", mejor10["f1_medio"])
print("F1>=0.50 en ambos periodos:", resumen["meta_050_ambos_periodos_mejor10"])
print("Número de características ganador:", ganador["n_caracteristicas"])
print("Evidencia:", salida)
print("Diciembre no leído; agente actual no modificado.")
```

El control mide el efecto del conjunto de cuatro variables, no cuál de ellas lo explica individualmente ni causalidad sobre los clientes. La búsqueda posterior permite que el árbol adapte su complejidad a las diez variables. Si mejora solo en un periodo, no se oculta el otro.

## Ejecutar

```powershell
python scripts/24_comparar_caracteristicas.py
```

Comparte desde RESUMEN COMPARACIÓN DE CARACTERÍSTICAS. No hacen falta nuevas lecturas del comprimido. La ejecución ajusta114 árboles: dos para reproducir el control y112 para la búsqueda con diez variables. Ni los modelos ni los umbrales de la versión entregable se reemplazan en este paso.
