# Guía 17 — Comparar regresión logística y árbol de decisión

## Objetivo inmediato

Entrenar dos familias de modelos con marzo, probar configuraciones y umbrales con junio y guardar evidencia y modelos provisionales. Se reutilizan los datos preparados. No se utiliza diciembre. Los resultados de junio se usan para seleccionar y por eso pueden ser optimistas; no son prueba final.

No entrenarás un modelo de lenguaje: estas técnicas aprenden relaciones entre las seis características históricas y el abandono. El agente posterior utilizará el predictor y una regla de decisión.

## 1. Reutilizar la carga que ya conoces

Crea `scripts/15_comparar_modelos.py`. Copia desde `scripts/14_linea_base_temporal.py` solamente el inicio, desde las importaciones hasta estas dos llamadas, incluidas:

```python
X_train, y_train, usuarios_train, hash_train = cargar(
    "cohorte_2016-03-07.csv", "2016-03-07", 7443, 1095)
X_val, y_val, usuarios_val, hash_val = cargar(
    "cohorte_2016-06-06.csv", "2016-06-06", 7210, 411)
```

No copies el entrenamiento de DummyClassifier ni su escritura de JSON. Conservamos la función cargar, sus controles, columnas_x y las importaciones de métricas. No importes directamente el script anterior: ejecutarías su entrenamiento al importarlo.

## 2. Herramientas, carpetas y rejillas

Añade a continuación:

```python
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
```

Son seis configuraciones por familia: doce entrenamientos y nueve umbrales por modelo, 108 evaluaciones de validación. ParameterGrid genera todas las combinaciones, sin particionar filas aleatoriamente.

- **Regresión logística:** produce un puntaje entre 0 y 1. C controla regularización: menor C implica mayor penalización de coeficientes. balanced pondera más la clase menos frecuente usando exclusivamente las etiquetas del entrenamiento; no duplica registros.
- **Árbol:** aprende divisiones de características. max_depth limita profundidad y min_samples_leaf exige una cantidad mínima de ejemplos en cada hoja. Estos controles reducen reglas demasiado específicas. Se fija balanced para esta rejilla acotada y se declaran los valores explorados; no representa toda configuración posible.
- **Umbral:** convierte puntaje en decisión: si puntaje >= umbral, predecir abandono. Cambiarlo altera precisión y sensibilidad sin volver a entrenar.

Estos puntajes no han sido calibrados, especialmente al usar pesos de clase. No presentarlos como probabilidades garantizadas de abandono.

## 3. Constructor y evaluación

```python
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
```

Pipeline une escalado y regresión. StandardScaler centra y escala características con media/desviación aprendidas SOLO en entrenamiento; fit se llamará con marzo, nunca con junio. El árbol no requiere escalado. El comparador elige por F1 de abandono, coherente con la propuesta; la exactitud se informa por separado y no garantiza cumplir las dos metas. AP conserva su nombre exacto, distinto del área trapezoidal PR-AUC.

El argumento **parametros distribuye las claves del diccionario como argumentos al constructor. El retorno de criterio es una tupla, que Python compara de izquierda a derecha. Si persiste empate se conserva el primer resultado encontrado, en orden determinista de rejilla.

## 4. Entrenar y seleccionar en validación

```python
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
```

Se entrena una vez por configuración, no una vez por umbral. Junio participa en seleccionar configuración y umbral: por eso debe llamarse validación. No es una validación cruzada completa; falta la ronda de septiembre del protocolo. No usar estos resultados para abrir o ajustar la prueba de diciembre.

Si aparece ConvergenceWarning convertida en error, comparte el mensaje y detén el proceso; no quites la comprobación para esconder el problema. Si falla, una carpeta parcial no equivale a una corrida completa.

## 5. Guardar artefactos provisionales y compararlos con la referencia

```python
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
```

Los archivos joblib sirven para cargar el modelo después sin reentrenarlo; cargar únicamente artefactos propios o de confianza. No contienen una demostración del agente ni constituyen el modelo final. El orden de las características y el umbral deben acompañar siempre al modelo.

## Ejecutar y continuar

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\15_comparar_modelos.py"
```

Comparte la salida final desde BASELINE F1, los parámetros y métricas de ambas familias, y la ruta del resultado. No necesitas contestar otro cuestionario antes de continuar hoy. Sí debes poder explicar después: qué aprende cada modelo, por qué escalamos dentro del Pipeline, qué hace el umbral y por qué junio no es prueba final.

No conocemos los resultados hasta tu ejecución. Si F1 no llega a 0,50, no cambies las etiquetas ni escondas el resultado; revisaremos evidencia y limitaciones. La comparación con parámetros ajustados cumple un avance real hacia los dos modelos exigidos, pero no completa todavía informe, demo ni evaluación final.

## Fuentes de implementación

- Pipeline y preprocesamiento: https://scikit-learn.org/stable/getting_started.html y https://scikit-learn.org/stable/modules/preprocessing.html
- Árbol y parámetros: https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html

Consultadas el 22 de noviembre de 2026. Las referencias académicas del informe final se prepararán por separado; estas páginas documentan la implementación.
