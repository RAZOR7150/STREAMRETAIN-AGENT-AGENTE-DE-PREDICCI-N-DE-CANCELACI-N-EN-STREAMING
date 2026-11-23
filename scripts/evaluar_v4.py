import csv
from datetime import datetime, timezone
from pathlib import Path
import joblib
import sklearn
from streamretain.comun import cargar_par, leer_tabla, leer_json, huella, guardar_json, medir


def main():
    raiz = Path(__file__).resolve().parents[1]
    carpeta = raiz / "data" / "derived"
    preparada = carpeta / "evaluacion_v4"
    modelo_dir = raiz / "experiments" / "modelo_v4"
    ruta_modelo = modelo_dir / "modelo_agente.joblib"
    ruta_seleccion = modelo_dir / "seleccion.json"
    ruta_manifiesto = preparada / "manifiesto.json"
    ruta_verificacion = preparada / "verificacion.json"
    ruta_v1 = raiz / "experiments" / "prueba_final" / "resultados.json"
    salida = modelo_dir / "evaluacion_diciembre.json"
    ruta_predicciones = preparada / "predicciones_v4.csv"
    if salida.exists() or ruta_predicciones.exists():
        raise FileExistsError("Ya hay resultados V4; revisar antes de repetir")

    verificacion = leer_json(ruta_verificacion)
    entrenamiento = leer_json(modelo_dir / "entrenamiento.json")
    seleccion = leer_json(ruta_seleccion)
    manifiesto = leer_json(ruta_manifiesto)
    v1 = leer_json(ruta_v1)
    hash_modelo = huella(ruta_modelo)
    hash_seleccion = huella(ruta_seleccion)
    if (not verificacion["equivalencia_desarrollo"]
            or hash_modelo != verificacion["sha256_modelo_v4"]
            or hash_modelo != entrenamiento["sha256_modelo"]
            or hash_seleccion != verificacion["sha256_seleccion_v4"]
            or hash_seleccion != entrenamiento["sha256_seleccion"]
            or huella(ruta_manifiesto) != verificacion["sha256_manifiesto_preparacion"]):
        raise ValueError("Cambió el modelo, la selección o la preparación verificada")
    if entrenamiento["sklearn"] != sklearn.__version__:
        raise ValueError("Usa la versión de scikit-learn del entrenamiento")

    columnas = seleccion["caracteristicas"]
    base = columnas[:6]
    if len(columnas) != 10 or columnas != manifiesto["caracteristicas"]:
        raise ValueError("Contrato de diez características inconsistente")
    meta = next(m for m in manifiesto["cohortes"] if m["corte"] == "2016-12-05")
    meta_base = next(m for m in manifiesto["cohortes_base"] if m["corte"] == "2016-12-05")
    if (meta != verificacion["diciembre"]
            or meta_base["sha256"] != v1["prueba"]["sha256"]
            or meta_base["filas"] != v1["filas_prueba"]):
        raise ValueError("No corresponde a la misma cohorte evaluada en V1")
    _, X, y = cargar_par(
        meta, meta_base, carpeta=carpeta, carpeta_nueva=preparada,
        base=base, columnas=columnas,
    )
    if len(y) != 8220 or sum(y) != v1["abandonos_prueba"]:
        raise ValueError("No coinciden tamaño o etiquetas de diciembre")

    # Solo nuestro joblib local y verificado; nunca archivos aportados por terceros.
    paquete = joblib.load(ruta_modelo)
    if (paquete["version"] != "v4" or paquete["familia"] != "arbol"
            or paquete["caracteristicas"] != columnas
            or paquete["parametros"] != seleccion["parametros"]
            or paquete["umbral"] != seleccion["umbral"]
            or paquete["sha256_seleccion"] != hash_seleccion):
        raise ValueError("El paquete no corresponde a la selección congelada V4")
    modelo = paquete["modelo"]
    if modelo.n_features_in_ != 10 or set(modelo.classes_) != {0, 1}:
        raise ValueError("Dimensiones o clases del modelo incorrectas")
    umbral = paquete["umbral"]
    puntajes = modelo.predict_proba(X)[:, list(modelo.classes_).index(1)]
    predicciones = (puntajes >= umbral).astype(int)
    metricas = medir(y, predicciones, puntajes)

    # Comparadores históricos: ya medidos sobre exactamente estos usuarios/etiquetas.
    arbol_v1 = v1["modelos"]["arbol"]["metricas"]
    baseline = v1["baseline"]
    informe = {
        "estado": "evaluacion_exploratoria_v4_diciembre",
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "version": "v4", "familia": "arbol", "sklearn": sklearn.__version__,
        "sha256_modelo": hash_modelo, "sha256_seleccion": hash_seleccion,
        "sha256_verificacion": huella(ruta_verificacion), "sha256_resultados_v1": huella(ruta_v1),
        "cohorte": meta, "cohorte_original": meta_base,
        "filas": len(y), "abandonos": sum(y),
        "caracteristicas": columnas, "parametros": paquete["parametros"], "umbral": umbral,
        "metricas_v4": metricas, "metricas_arbol_v1": arbol_v1, "baseline": baseline,
        "cambio_f1_vs_v1": metricas["f1_abandono"] - arbol_v1["f1_abandono"],
        "metas_en_esta_comparacion": {
            "accuracy_al_menos_075": metricas["accuracy"] >= 0.75,
            "f1_al_menos_050": metricas["f1_abandono"] >= 0.50,
            "f1_superior_baseline": metricas["f1_abandono"] > baseline["f1_abandono"],
        },
        "limitaciones": [
            "Comparación exploratoria: diciembre ya fue conocido durante desarrollo de V4",
            "No equivale a una nueva prueba independiente",
            "Etiquetas reconstruidas bajo supuesto de cobertura",
            "Puntajes no calibrados; AP es average_precision_score",
            "La versión1 y su prueba original permanecen conservadas",
        ],
    }

    # La tabla conserva el orden que utiliza cargar_par. Los identificadores quedan locales.
    filas = leer_tabla(
        preparada / "cohorte_2016-12-05.csv",
        ["msno", "corte", *columnas, "is_churn"], meta["sha256"],
    )
    if len(filas) != len(y):
        raise ValueError("Cambió la tabla durante la evaluación")
    campos = ["msno", "corte", *columnas, "is_churn", "puntaje", "prediccion", "tipo"]
    with ruta_predicciones.open("x", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        for i, fila in enumerate(filas):
            real, pred = int(fila["is_churn"]), int(predicciones[i])
            if real != y[i] or [float(fila[c]) for c in columnas] != X[i]:
                raise ValueError("El orden no coincide con la matriz evaluada")
            tipo = {(0, 0): "TN", (0, 1): "FP", (1, 0): "FN", (1, 1): "TP"}[(real, pred)]
            escritor.writerow({**fila, "puntaje": float(puntajes[i]),
                               "prediccion": pred, "tipo": tipo})
    informe["sha256_predicciones"] = huella(ruta_predicciones)
    guardar_json(salida, informe)
    print("RESUMEN EVALUACIÓN EXPLORATORIA V4")
    print("Filas:", len(y), "Abandonos:", sum(y))
    print("Parámetros:", paquete["parametros"], "Umbral:", umbral)
    print("Métricas V4:", metricas)
    print("F1 árbol V1:", arbol_v1["f1_abandono"])
    print("Cambio F1:", informe["cambio_f1_vs_v1"])
    print("Metas en esta comparación:", informe["metas_en_esta_comparacion"])
    print("Evidencia:", salida)
    print("Predicciones locales:", ruta_predicciones)
    print("Sin entrenamiento ni ajuste de umbral; resultado exploratorio, no prueba independiente.")


if __name__ == "__main__":
    main()
