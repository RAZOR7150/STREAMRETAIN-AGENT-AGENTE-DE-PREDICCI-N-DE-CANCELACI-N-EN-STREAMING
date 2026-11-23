# Guía 20 — Reajuste y prueba temporal final

## Qué quedó decidido

La segunda ronda fue ejecutada por el estudiante. La selección usa el promedio del F1 de junio y septiembre para una misma configuración y umbral:

| Familia | Configuración congelada | Umbral | F1 junio | F1 septiembre | F1 medio |
| --- | --- | --- | --- | --- | --- |
| Logística | C=10, class_weight=balanced | 0,7 | 0,38938 | 0,21197 | 0,30067 |
| Árbol | profundidad=5, hoja mínima=20, class_weight=balanced | 0,6 | 0,41879 | 0,47929 | 0,44904 |

El árbol es el modelo elegido para el agente. Su matriz de septiembre fue [[7315, 431], [210, 295]]: detectó 295 abandonos, dejó pasar 210 y produjo 431 falsas alertas. El baseline no detectó ninguno. La meta F1 >= 0,50 aún no se alcanza; esto debe informarse sin cambiar la meta. La caída de la logística indica variación del rendimiento entre periodos, pero por sí sola no identifica su causa.

Ahora reajustaremos cada configuración congelada con marzo+junio+septiembre (22.904 ejemplos temporales, no necesariamente usuarios distintos) y evaluaremos diciembre (8.220 ejemplos). Los resultados finales de ambas familias se reportan, pero no se cambia de ganador, umbral ni características después de mirarlos. Esta es validación temporal progresiva con dos rondas; no una partición aleatoria.

## 1. Crear el archivo y reutilizar funciones

Crea `scripts/18_prueba_final.py`.

De `17_validacion_temporal.py`, copia únicamente el inicio desde las importaciones hasta el final de `cargar`. Después agrega estas importaciones y copia las definiciones completas de `construir` y `medir` de ese mismo archivo. No copies las cargas, bucles de entrenamiento ni la escritura de selección de la guía 19. No importes ese script como módulo, porque ejecutaría sus instrucciones de nivel superior.

```python
import warnings
import joblib
from datetime import datetime, timezone
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

warnings.filterwarnings("error", category=ConvergenceWarning)
# Pega aquí las funciones construir y medir, sin modificarlas.
```

## 2. Verificar la selección y cargar los periodos

Agrega después de las funciones:

```python
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
```

Las etiquetas de desarrollo ya serían observables antes de diciembre. Leer diciembre para evaluar no autoriza a usarlo en fit. `usuarios_des` sirve para contar solapamiento; nunca entra como característica. Las fechas ISO permiten la comparación cronológica usada arriba.

## 3. Ajustar los modelos congelados y guardar evidencia

```python
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
```

Un puntaje de 0,6 se considera alerta porque se compara con `>= 0.6`. Con class_weight=balanced no debemos anunciar ese puntaje como una probabilidad de abandono calibrada del 60 %. El umbral es una regla de decisión elegida en validación. Carga archivos joblib únicamente si conoces y confías en su origen.

## 4. Conservar predicciones locales para analizar errores

Este CSV permitirá revisar falsos positivos y negativos sin entrenar otra vez. Se guarda en `data/derived`, excluido de Git por las reglas actuales. Contiene identificadores del dataset; el informe público posterior usará casos anónimos.

```python
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
```

## Ejecutar y continuar

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\18_prueba_final.py"
```

Comparte la salida desde RESUMEN PRUEBA FINAL. No se ha ejecutado este entrenamiento desde Codex: te corresponde incorporar y ejecutar el código. Si la meta F1 no se cumple, se reportará como limitación, sin ajustar con diciembre. Después haremos el análisis de al menos diez errores, resultados por grupos históricos y la demostración del agente usando el paquete guardado. Estos análisis describirán la prueba, sin convertirla en datos para seleccionar otra versión.
