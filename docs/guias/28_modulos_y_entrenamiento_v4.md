# Guía 28 — Módulo compartido y entrenamiento del candidato V4

## Cambio de forma de trabajo

A partir de aquí no repetiremos las mismas funciones en cada script. Haremos una extracción inicial: las funciones ya escritas pasan a un módulo compartido; los programas nuevos las importan. Importar un módulo no debe cargar datasets, entrenar modelos ni crear archivos.

Esta separación debió introducirse antes: repetir funciones facilita que dos copias terminen comportándose distinto. Mantendremos los scripts históricos como evidencia, sin exigir reescribir todo lo ya ejecutado.

La versión seleccionada tiene10 características, depth10,leaf100,class_weight=None y umbral0,30; F1 medio de validación0,53975 (junio0,47912; septiembre0,60039). Este paso fija esa decisión y entrena un artefacto con las tres cohortes de desarrollo. No mide diciembre ni reemplaza la versión1. La comparación posterior con diciembre se identificará como exploratoria porque ese periodo ya fue observado durante el proyecto.

## 1. Crear una estructura reutilizable

Desde el explorador de VS Code crea:

```text
Proyecto Final/
  streamretain/
    __init__.py
    comun.py
  scripts/
    __init__.py
    entrenar_v4.py
```

Los dos __init__.py pueden estar vacíos. Declaran los directorios como paquetes de Python. Los scripts anteriores se conservan; los nuevos pueden tener nombres descriptivos, sin número.

En `streamretain/comun.py` coloca estas importaciones:

```python
import csv
import hashlib
import json
import math
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, average_precision_score,
)
```

Ahora traslada a ese módulo las definiciones completas de **medir**, **leer_tabla** y **cargar_par**, que ya están en `scripts/24_comparar_caracteristicas.py`. Es la única extracción inicial: no volverás a copiarlas en cada programa. Para preservar el script histórico, puedes dejar allí sus definiciones anteriores.

En la versión de `cargar_par` del módulo cambia únicamente la firma:

```python
def cargar_par(meta, meta_base, *, carpeta, carpeta_nueva, base, columnas):
```

Su cuerpo permanece igual. Antes dependía de cuatro variables globales del script; ahora se entregan explícitamente al llamarla. El asterisco exige indicar sus nombres, evitando confundir la carpeta original con la enriquecida. Por ejemplo:

```python
X6, X10, y = cargar_par(
    meta, meta_base,
    carpeta=carpeta_original,
    carpeta_nueva=carpeta_enriquecida,
    base=columnas_base,
    columnas=columnas_completas,
)
```

Ese ejemplo de llamada es explicativo: no lo pegues al final del módulo. `comun.py` solo contiene importaciones y definiciones; no copies las cargas, variables de rutas, bucles ni entrenamientos del script24.

Agrega también estas tres utilidades pequeñas al módulo. Permiten que los próximos programas compartan lectura JSON, huellas y escritura sin sobrescribir:

```python
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
```

## 2. Comprobar que importar no ejecuta un experimento

Desde la raíz del proyecto:

```powershell
python -c "from streamretain.comun import medir, leer_tabla, cargar_par, leer_json, huella, guardar_json; print('Importación correcta; ningún experimento ejecutado')"
```

No deben aparecer conteos de cohortes, ajustes ni archivos nuevos por esa importación. Si se imprimen, copiaste instrucciones de ejecución al módulo: retíralas. No uses importación del script24 para evitar esta reorganización; ese archivo ejecuta trabajo al importarse.

## 3. Crear scripts/entrenar_v4.py

Este archivo contiene las instrucciones específicas del nuevo entrenamiento. Todas las utilidades se importan del módulo compartido. Lee la decisión elegida desde el JSON; no vuelve a buscar parámetros.

```python
from datetime import datetime, timezone
from pathlib import Path
import platform
import joblib
import sklearn
from sklearn.tree import DecisionTreeClassifier
from streamretain.comun import cargar_par, leer_json, huella, guardar_json


def main():
    raiz = Path(__file__).resolve().parents[1]
    carpeta = raiz / "data" / "derived"
    carpeta_nueva = carpeta / "caracteristicas_suscripcion_v4"
    ruta_comparacion = raiz / "experiments" / "comparacion_caracteristicas_v4" / "resultados.json"
    ruta_manifiesto = carpeta_nueva / "manifiesto.json"
    comparacion = leer_json(ruta_comparacion)
    manifiesto = leer_json(ruta_manifiesto)
    decision = comparacion["ganador_desarrollo"]
    columnas = manifiesto["caracteristicas"]
    base = columnas[:6]
    salida = raiz / "experiments" / "modelo_v4"
    if salida.exists():
        raise FileExistsError("Ya existe modelo_v4; revisar antes de repetir")
    if (decision["familia"] != "arbol" or decision["n_caracteristicas"] != 10
            or decision != comparacion["mejor_10"] or len(columnas) != 10):
        raise ValueError("La selección no corresponde al árbol de diez características")
    if (comparacion["sklearn"] != sklearn.__version__
            or comparacion["caracteristicas"] != columnas
            or comparacion["cohortes"] != manifiesto["cohortes"]
            or huella(ruta_manifiesto) != comparacion["sha256_manifiesto"]):
        raise ValueError("Cambió el entorno o el manifiesto usado para seleccionar")
    if {m["corte"] for m in manifiesto["cohortes"]} != {
            "2016-03-07", "2016-06-06", "2016-09-05"}:
        raise ValueError("Solo se permiten las tres cohortes de desarrollo")

    X_total, y_total = [], []
    for meta in manifiesto["cohortes"]:
        meta_base = next(m for m in manifiesto["cohortes_base"] if m["corte"] == meta["corte"])
        _, X10, y = cargar_par(
            meta, meta_base, carpeta=carpeta, carpeta_nueva=carpeta_nueva,
            base=base, columnas=columnas,
        )
        X_total.extend(X10)
        y_total.extend(y)
    if len(y_total) != 22904 or set(y_total) != {0, 1}:
        raise ValueError("Tamaño o clases de entrenamiento inesperados")

    # La selección queda registrada antes del ajuste, sin consultar diciembre.
    salida.mkdir(parents=True, exist_ok=False)
    seleccion = {
        "estado": "seleccion_v4_previa_a_comparacion_exploratoria_diciembre",
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "familia": "arbol", "parametros": decision["parametros"],
        "umbral": decision["umbral"], "semilla": 42,
        "caracteristicas": columnas,
        "validacion": {p: decision[p] for p in ("junio", "septiembre", "f1_medio", "ap_media")},
        "sha256_comparacion": huella(ruta_comparacion),
        "sha256_manifiesto": huella(ruta_manifiesto),
        "cohortes_entrenamiento": manifiesto["cohortes"],
        "advertencia": "V4 desarrollada después de conocer pruebaV1; sin nueva prueba independiente",
    }
    ruta_seleccion = salida / "seleccion.json"
    guardar_json(ruta_seleccion, seleccion)

    modelo = DecisionTreeClassifier(random_state=42, **decision["parametros"])
    modelo.fit(X_total, y_total)
    if modelo.n_features_in_ != len(columnas):
        raise ValueError("Contrato de entrada inconsistente")
    paquete = {
        "version": "v4", "modelo": modelo, "familia": "arbol",
        "parametros": decision["parametros"], "umbral": decision["umbral"],
        "caracteristicas": columnas, "semilla": 42,
        "sklearn": sklearn.__version__, "python": platform.python_version(),
        "sha256_seleccion": huella(ruta_seleccion),
        "cohortes_entrenamiento": manifiesto["cohortes"],
        "advertencia": "Puntaje no calibrado; versiónV4 sin nueva prueba independiente",
    }
    ruta_modelo = salida / "modelo_agente.joblib"
    joblib.dump(paquete, ruta_modelo)
    registro = {
        "estado": "entrenado_sin_evaluacion_posterior",
        "version": "v4", "filas": len(y_total), "abandonos": sum(y_total),
        "caracteristicas": columnas, "parametros": decision["parametros"],
        "umbral": decision["umbral"], "semilla": 42,
        "python": platform.python_version(), "sklearn": sklearn.__version__,
        "sha256_modelo": huella(ruta_modelo), "sha256_seleccion": huella(ruta_seleccion),
        "advertencia": "La versión1 y sus resultados finales permanecen conservados",
    }
    guardar_json(salida / "entrenamiento.json", registro)
    print("RESUMEN ENTRENAMIENTO V4")
    print("Filas:", len(y_total), "Características:", len(columnas))
    print("Parámetros:", decision["parametros"], "Umbral:", decision["umbral"])
    print("F1 medio de validación previo:", decision["f1_medio"])
    print("Modelo:", ruta_modelo)
    print("Huella:", registro["sha256_modelo"])
    print("Diciembre no evaluado en V4; versión1 no modificada.")


if __name__ == "__main__":
    main()
```

`main` reúne las acciones de este programa. La condición final ejecuta main solo cuando invocas el programa, no cuando otro módulo lo importa. Esto permite organizar y comprobar el código sin disparar entrenamientos accidentalmente.

## 4. Ejecutar como módulo

Desde la raíz del proyecto:

```powershell
python -m scripts.entrenar_v4
```

Usamos -m para que Python encuentre el paquete streamretain desde la raíz. Evita ejecutar mediante una ruta absoluta al archivo como antes: podría hacer que Python no encontrara el paquete raíz. No se necesitan cambios de sys.path ni copiar comun.py dentro de scripts.

Comparte desde RESUMEN ENTRENAMIENTO V4. No habrá un F1 de prueba nuevo en esa salida: entrenar el artefacto no equivale a evaluarlo. Después prepararemos las características de diciembre mediante funciones reutilizables y evaluaremos esta versión una vez como comparación exploratoria, sin retocar parámetros a partir de ese resultado. La interfaz permanece en pausa.

## Regla para las siguientes guías

Una función general vive en streamretain y se importa. Un script específico define main y se ejecuta con python -m scripts.nombre. Los módulos no realizan lecturas de datasets ni entrenamientos al importarlos. La preparación de características también se extraerá a una función parametrizada, para no duplicar el script23 al preparar otro corte.
