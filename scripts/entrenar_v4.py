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
