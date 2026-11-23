# Guía 25 — Comparar un bosque aleatorio sobre las mismas cohortes

## Por qué este paso

La búsqueda del árbol ejecutada por el estudiante dio profundidad5, hoja20, class_weight=None y umbral0,20. F1 junio0,427419, septiembre0,487116 y medio0,457267, frente al anterior0,449040. La mejora absoluta es0,008228. Ninguna combinación ensayada logró0,50 en ambos periodos. El máximo de septiembre fue0,544199, pero esa configuración obtuvo0,235489 en junio: no debe escogerse solo por ese máximo.

0,50 es nuestra **meta de F1**. 0,20 es un **umbral de decisión**: el valor a partir del cual un puntaje produce alerta. Son conceptos distintos. El nuevo árbol no ha sido evaluado en una nueva prueba independiente.

Un Random Forest entrena varios árboles sobre muestras de entrenamiento y combina sus puntajes. Introduce diversidad entre árboles que puede reducir la variación de un árbol individual, sin garantizar mejor F1. Sigue usando solo las seis características existentes. No requiere descomprimir ni reconstruir datos. Es un modelo adicional: los comparadores obligatorios logística y árbol se conservan.

Esta búsqueda sigue siendo desarrollo exploratorio posterior a conocer la prueba de versión1. No se abre diciembre ni se afirma haber cumplido la meta final por alcanzar un valor de validación. La interfaz web queda en pausa por petición del estudiante.

## Diseño fijado antes de ejecutar

- 200 árboles por bosque, semilla42, max_features=sqrt y bootstrap=True.
- Profundidad máxima5,10 o sin límite; mínimo5 o20 ejemplos por hoja; pesos None o balanced.
- 12 configuraciones, cada una con las dos rondas temporales: marzo->junio y marzo+junio->septiembre (24 ajustes de bosques).
- 19 umbrales de0,05 a0,95, mismo umbral para ambas rondas de cada candidato.
- Selección por F1 medio; empate por AP media y cercanía del umbral a0,5. No cambiamos el criterio al ver resultados.
- n_jobs=2 limita el paralelismo para no ocupar todos los núcleos. El tiempo depende de tu equipo; un bosque cuesta más que un árbol individual.

No utilizamos OOB como sustituto de validación temporal ni muestreamos al azar fechas para crear una partición nueva. Si este experimento tampoco aporta mejora suficiente, revisaremos características y etiquetas antes de seguir ampliando rejillas indefinidamente: la información disponible puede ser el límite.

## 1. Crea scripts/22_comparar_bosque.py

Copia de scripts/17_validacion_temporal.py solo las importaciones y variables iniciales hasta el final de cargar. Copia también la función medir completa. No copies otras instrucciones ni importes el script como módulo. Agrega:

```python
from datetime import datetime, timezone
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import ParameterGrid

ruta_v1 = raiz / "experiments" / "seleccion_congelada.json"
ruta_arbol = raiz / "experiments" / "busqueda_arbol_v2" / "resultados.json"
v1 = json.loads(ruta_v1.read_text(encoding="utf-8-sig"))
arbol_v2 = json.loads(ruta_arbol.read_text(encoding="utf-8-sig"))
salida = raiz / "experiments" / "busqueda_bosque_v3"
if salida.exists():
    raise FileExistsError("Ya existe esta búsqueda; comparte resultados o error antes de repetir")
if (v1["caracteristicas"] != columnas_x or arbol_v2["caracteristicas"] != columnas_x
        or v1["sklearn"] != sklearn.__version__
        or arbol_v2["sklearn"] != sklearn.__version__
        or arbol_v2["cohortes"] != v1["cohortes_desarrollo"]):
    raise ValueError("Datos, características o entorno diferentes")

# Cargamos SOLO los periodos de desarrollo con control de identidad del archivo.
datos = {}
for meta in v1["cohortes_desarrollo"]:
    X, y, usuarios, huella = cargar(
        f"cohorte_{meta['corte']}.csv", meta["corte"], meta["filas"])
    if huella != meta["sha256"] or set(y) != {0, 1}:
        raise ValueError("Cambió una cohorte o no contiene ambas clases")
    datos[meta["corte"]] = (X, y)
Xm, ym = datos["2016-03-07"]
Xj, yj = datos["2016-06-06"]
Xs, ys = datos["2016-09-05"]
rondas = [(Xm, ym, Xj, yj), (Xm + Xj, ym + yj, Xs, ys)]
rejilla = {
    "max_depth": [5, 10, None],
    "min_samples_leaf": [5, 20],
    "class_weight": [None, "balanced"],
}
fijos = {"n_estimators": 200, "random_state": 42, "n_jobs": 2,
         "max_features": "sqrt", "bootstrap": True}
umbrales = [round(i / 100, 2) for i in range(5, 100, 5)]
if umbrales != arbol_v2["umbrales"]:
    raise ValueError("Los umbrales no coinciden con la comparación anterior")

# El protocolo se escribe antes de ver las métricas de los bosques.
salida.mkdir(parents=True, exist_ok=False)
protocolo = {
    "estado": "desarrollo_exploratorio_posterior_a_prueba_v1",
    "fecha_utc": datetime.now(timezone.utc).isoformat(),
    "python": platform.python_version(), "sklearn": sklearn.__version__,
    "sha256_resultados_arbol_v2": hashlib.sha256(ruta_arbol.read_bytes()).hexdigest(),
    "cohortes": v1["cohortes_desarrollo"], "caracteristicas": columnas_x,
    "rejilla": rejilla, "parametros_fijos": fijos, "umbrales": umbrales,
    "criterio": "F1 medio, AP media, cercanía a 0.5; empate restante por orden de rejilla",
}
with (salida / "protocolo.json").open("x", encoding="utf-8") as f:
    json.dump(protocolo, f, ensure_ascii=False, indent=2, allow_nan=False)
```

n_estimators es el número de árboles, no el número de usuarios. max_features=sqrt limita las variables candidatas que cada árbol considera en cada división. class_weight=balanced calcula pesos con la frecuencia de clases del entrenamiento, sin consultar las etiquetas de validación.

## 2. Entrenar y medir

```python
ensayos = []
configuraciones = list(ParameterGrid(rejilla))
for numero, parametros in enumerate(configuraciones, 1):
    por_ronda = []
    for numero_ronda, (X_train, y_train, X_val, y_val) in enumerate(rondas, 1):
        bosque = RandomForestClassifier(**fijos, **parametros)
        bosque.fit(X_train, y_train)
        indice = list(bosque.classes_).index(1)
        puntajes = bosque.predict_proba(X_val)[:, indice]
        por_ronda.append({
            u: medir(y_val, (puntajes >= u).astype(int), puntajes)
            for u in umbrales
        })
        print(f"Configuración {numero}/{len(configuraciones)}, ronda {numero_ronda}/2 lista")
    for u in umbrales:
        junio, septiembre = por_ronda[0][u], por_ronda[1][u]
        ensayos.append({
            "familia": "bosque", "parametros": parametros, "umbral": u,
            "junio": junio, "septiembre": septiembre,
            "f1_medio": (junio["f1_abandono"] + septiembre["f1_abandono"]) / 2,
            "ap_media": (junio["average_precision"] + septiembre["average_precision"]) / 2,
        })


def criterio(fila):
    return (fila["f1_medio"], fila["ap_media"], -abs(fila["umbral"] - 0.5))


mejor = max(ensayos, key=criterio)
referencia = arbol_v2["mejor_validacion"]
# En empate completo conservamos el árbol ya disponible.
ganador_desarrollo = mejor if criterio(mejor) > criterio(referencia) else referencia
resumen = {
    **protocolo, "configuraciones": len(configuraciones), "ajustes": 2 * len(configuraciones),
    "mejor_bosque": mejor, "referencia_arbol_v2": referencia,
    "ganador_desarrollo": ganador_desarrollo, "ensayos": ensayos,
    "mejora_f1_medio_vs_arbol": mejor["f1_medio"] - referencia["f1_medio"],
    "meta_050_ambos_periodos_bosque": all(
        mejor[p]["f1_abandono"] >= 0.5 for p in ("junio", "septiembre")),
    "advertencia": "Resultados de selección; sin nueva prueba independiente ni sustitución de versión1",
}
with (salida / "resultados.json").open("x", encoding="utf-8") as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2, allow_nan=False)
print("\nRESUMEN COMPARACIÓN BOSQUE")
print("Configuración:", mejor["parametros"])
print("Parámetros fijos:", fijos)
print("Umbral:", mejor["umbral"])
print("Junio:", mejor["junio"])
print("Septiembre:", mejor["septiembre"])
print("F1 medio bosque:", mejor["f1_medio"])
print("F1 medio árbol ampliado:", referencia["f1_medio"])
print("Mejora:", resumen["mejora_f1_medio_vs_arbol"])
print("F1>=0.50 en ambos periodos:", resumen["meta_050_ambos_periodos_bosque"])
print("Ganador de desarrollo:", ganador_desarrollo["familia"])
print("Evidencia:", salida)
print("No se leyó diciembre ni se reemplazó el agente actual.")
```

predict_proba promedia los puntajes de los árboles. No implica que estén calibrados. Un bosque no tiene un único recorrido de decisión como el árbol de la demo; si se adopta posteriormente habrá que adaptar esa explicación. Por ahora solo comparamos resultados, sin guardar un modelo sustituto ni tocar la interfaz.

## Ejecutar

```powershell
python scripts/22_comparar_bosque.py
```

Comparte desde RESUMEN COMPARACIÓN BOSQUE. La búsqueda tiene un final definido de12 configuraciones. No repitas rejillas o cambies el criterio según qué periodo dé la cifra deseada. Revisaremos la mejora frente al árbol y el comportamiento en ambas rondas antes de decidir si vale la pena continuar con esta familia.

Fuente oficial: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
