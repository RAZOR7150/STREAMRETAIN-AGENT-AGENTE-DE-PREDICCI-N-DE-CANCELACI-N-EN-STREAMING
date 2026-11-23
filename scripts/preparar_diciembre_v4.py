from pathlib import Path
from streamretain.comun import leer_json, huella, guardar_json
from streamretain.preparacion import preparar_suscripcion


def main():
    raiz = Path(__file__).resolve().parents[1]
    carpeta = raiz / "data" / "derived"
    anterior = leer_json(carpeta / "caracteristicas_suscripcion_v4" / "manifiesto.json")
    v1 = leer_json(raiz / "experiments" / "seleccion_congelada.json")
    seleccion_v4 = leer_json(raiz / "experiments" / "modelo_v4" / "seleccion.json")
    entrenamiento = leer_json(raiz / "experiments" / "modelo_v4" / "entrenamiento.json")
    ruta_modelo = raiz / "experiments" / "modelo_v4" / "modelo_agente.joblib"
    if huella(ruta_modelo) != entrenamiento["sha256_modelo"]:
        raise ValueError("Cambió el modelo V4 entrenado")
    if huella(raiz / "experiments" / "modelo_v4" / "seleccion.json") != entrenamiento["sha256_seleccion"]:
        raise ValueError("Cambió la selección V4")
    if huella(carpeta / "caracteristicas_suscripcion_v4" / "manifiesto.json") != seleccion_v4["sha256_manifiesto"]:
        raise ValueError("Cambió la preparación de desarrollo")
    if (anterior["caracteristicas"] != seleccion_v4["caracteristicas"]
            or anterior["cohortes_base"] != v1["cohortes_desarrollo"]):
        raise ValueError("Datos o características de desarrollo diferentes")
    diciembre = v1["prueba_reservada"]
    if diciembre["corte"] != "2016-12-05" or diciembre["filas"] != 8220:
        raise ValueError("No es la cohorte de diciembre esperada")
    metas = [*anterior["cohortes_base"], diciembre]
    salida = carpeta / "evaluacion_v4"

    # Una llamada, una pasada del comprimido, cuatro cohortes en carpeta nueva.
    nuevo = preparar_suscripcion(
        raiz, metas, v1["caracteristicas"], salida,
        estado="preparacion_comparacion_exploratoria_v4",
    )
    if nuevo["caracteristicas"] != anterior["caracteristicas"]:
        raise ValueError("La función reorganizada cambió el esquema")
    for meta in anterior["cohortes"]:
        reconstruida = next(m for m in nuevo["cohortes"] if m["corte"] == meta["corte"])
        if reconstruida["filas"] != meta["filas"] or reconstruida["sha256"] != meta["sha256"]:
            raise ValueError("La reorganización no reproduce exactamente desarrollo; revisar antes de evaluar")
        print("Equivalencia exacta verificada:", meta["corte"], meta["filas"])
    meta_dic = next(m for m in nuevo["cohortes"] if m["corte"] == "2016-12-05")
    if meta_dic["filas"] != diciembre["filas"]:
        raise ValueError("Cambió el tamaño de diciembre")
    verificacion = {
        "estado": "preparacion_v4_verificada_sin_evaluar",
        "sha256_modelo_v4": entrenamiento["sha256_modelo"],
        "sha256_seleccion_v4": entrenamiento["sha256_seleccion"],
        "sha256_manifiesto_preparacion": huella(salida / "manifiesto.json"),
        "equivalencia_desarrollo": True, "diciembre": meta_dic,
        "advertencia": "Diciembre conocido durante desarrollo; comparación posterior exploratoria",
    }
    guardar_json(salida / "verificacion.json", verificacion)
    print("\nRESUMEN PREPARACIÓN DICIEMBRE V4")
    print("Filas:", meta_dic["filas"], "Características:", len(nuevo["caracteristicas"]))
    print("Desarrollo reproducido sin cambios: sí")
    print("Carpeta:", salida)
    print("Verificación:", salida / "verificacion.json")
    print("Modelo V4 no reajustado; diciembre todavía no evaluado en V4.")


if __name__ == "__main__":
    main()
