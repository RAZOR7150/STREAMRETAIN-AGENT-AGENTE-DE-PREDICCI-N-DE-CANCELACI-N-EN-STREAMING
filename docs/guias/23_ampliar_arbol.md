# Guía 23 — Búsqueda ampliada del árbol (versión 2 exploratoria)

## Alcance acordado

El estudiante pidió ampliar parámetros para intentar alcanzar F1>=0,50 con el menor trabajo de preparación adicional. Reutilizamos exactamente las seis variables y las cohortes de marzo, junio y septiembre. Diciembre no se carga. La versión1, sus modelos y su prueba final F1=0,34615 se conservan.

Esta nueva búsqueda comienza después de conocer la prueba final de la versión1. Aunque solo ajusta usando desarrollo, debe declararse como una iteración posterior: alcanzar0,50 en validación no demostraría haberlo alcanzado en una prueba independiente. Reutilizar diciembre después solo permitiría una comparación exploratoria, no una nueva prueba intacta.

Probamos 7 profundidades, 4 mínimos por hoja y 2 políticas de ponderación: 56 configuraciones. Cada una se ajusta en dos rondas (112 ajustes), con 19 umbrales por configuración. Son1064 combinaciones de configuración/umbral, cada una con dos resultados de validación. Mantendremos el criterio anterior: F1 medio de ambos periodos; desempate por AP media y cercanía del umbral a0,5. No se prueban parámetros hasta conseguir arbitrariamente una cifra en diciembre.

- max_depth limita cuántas decisiones consecutivas puede tomar el árbol; None permite crecer hasta los demás límites.
- min_samples_leaf exige un mínimo de ejemplos en cada hoja; hojas pequeñas pueden capturar más patrones, pero también ruido.
- class_weight=None usa pesos uniformes; balanced pondera las clases según su frecuencia en el entrenamiento de cada ronda.
- El umbral cambia qué puntajes producen una alerta; no vuelve a entrenar el árbol.

## 1. Crea scripts/21_ampliar_arbol.py

Copia de scripts/17_validacion_temporal.py únicamente las importaciones y variables iniciales hasta el final de cargar. Copia además la función medir completa. No copies sus cargas ni bucles; no importes el script como módulo. Agrega:

```python
from datetime import datetime, timezone
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import ParameterGrid

ruta_v1 = raiz / "experiments" / "seleccion_congelada.json"
v1 = json.loads(ruta_v1.read_text(encoding="utf-8-sig"))
salida = raiz / "experiments" / "busqueda_arbol_v2"
if salida.exists():
    raise FileExistsError("Ya existe esta búsqueda; revisar antes de repetir")
if v1["caracteristicas"] != columnas_x or v1["sklearn"] != sklearn.__version__:
    raise ValueError("Cambió el contrato o la versión de sklearn")

# Solo tres CSV de desarrollo. No leer prueba_reservada ni diciembre.
datos = {}
for meta in v1["cohortes_desarrollo"]:
    X, y, usuarios, huella = cargar(
        f"cohorte_{meta['corte']}.csv", meta["corte"], meta["filas"])
    if huella != meta["sha256"] or set(y) != {0, 1}:
        raise ValueError("Cambió una cohorte o faltan clases")
    datos[meta["corte"]] = (X, y)
Xm, ym = datos["2016-03-07"]
Xj, yj = datos["2016-06-06"]
Xs, ys = datos["2016-09-05"]
rondas = [(Xm, ym, Xj, yj), (Xm + Xj, ym + yj, Xs, ys)]
rejilla = {
    "max_depth": [3, 4, 5, 6, 8, 10, None],
    "min_samples_leaf": [10, 20, 50, 100],
    "class_weight": [None, "balanced"],
}
umbrales = [round(i / 100, 2) for i in range(5, 100, 5)]
# Guardar el protocolo antes de entrenar deja constancia de la búsqueda.
salida.mkdir(parents=True, exist_ok=False)
protocolo = {
    "estado": "exploracion_v2_posterior_a_prueba_v1",
    "fecha_utc": datetime.now(timezone.utc).isoformat(),
    "semilla": 42, "sklearn": sklearn.__version__, "python": platform.python_version(),
    "sha256_seleccion_v1": hashlib.sha256(ruta_v1.read_bytes()).hexdigest(),
    "caracteristicas": columnas_x, "cohortes": v1["cohortes_desarrollo"],
    "rejilla": rejilla, "umbrales": umbrales,
    "criterio": "F1 medio, AP media, cercanía a 0.5; empate restante por orden de rejilla",
}
with (salida / "protocolo.json").open("x", encoding="utf-8") as f:
    json.dump(protocolo, f, ensure_ascii=False, indent=2, allow_nan=False)
```

## 2. Ejecutar las mismas dos rondas por configuración

Cada fit recibe exclusivamente meses anteriores a su validación. La evaluación de los umbrales usa los puntajes ya calculados; no son19 entrenamientos adicionales. No usamos GridSearchCV con su partición por defecto porque necesitamos estas rondas temporales concretas.

```python
ensayos = []
configuraciones = list(ParameterGrid(rejilla))
for numero, parametros in enumerate(configuraciones, 1):
    por_ronda = []
    for X_train, y_train, X_val, y_val in rondas:
        modelo = DecisionTreeClassifier(random_state=42, **parametros)
        modelo.fit(X_train, y_train)
        indice = list(modelo.classes_).index(1)
        puntajes = modelo.predict_proba(X_val)[:, indice]
        por_ronda.append({
            u: medir(y_val, (puntajes >= u).astype(int), puntajes)
            for u in umbrales
        })
    for u in umbrales:
        junio, septiembre = por_ronda[0][u], por_ronda[1][u]
        ensayos.append({
            "familia": "arbol", "parametros": parametros, "umbral": u,
            "junio": junio, "septiembre": septiembre,
            "f1_medio": (junio["f1_abandono"] + septiembre["f1_abandono"]) / 2,
            "ap_media": (junio["average_precision"] + septiembre["average_precision"]) / 2,
        })
    print(f"Configuración {numero}/{len(configuraciones)}:", parametros)


def criterio(fila):
    return (fila["f1_medio"], fila["ap_media"], -abs(fila["umbral"] - 0.5))


ordenados = sorted(ensayos, key=criterio, reverse=True)
mejor = ordenados[0]
anterior = v1["mejores_por_familia"]["arbol"]
# La configuración anterior está incluida: comprobamos su reproducción.
referencia = next(f for f in ensayos
                  if f["parametros"] == anterior["parametros"]
                  and f["umbral"] == anterior["umbral"])
for periodo in ("junio", "septiembre"):
    if abs(referencia[periodo]["f1_abandono"] - anterior[periodo]["f1_abandono"]) > 1e-12:
        raise ValueError("La configuración de referencia no reproduce el F1 anterior")

resumen = {
    **protocolo, "configuraciones": len(configuraciones), "ajustes": 2 * len(configuraciones),
    "ensayos": ensayos, "mejor_validacion": mejor,
    "referencia_v1": referencia,
    "mejora_f1_medio": mejor["f1_medio"] - referencia["f1_medio"],
    "supera_050_en_ambas_validaciones": all(
        mejor[p]["f1_abandono"] >= 0.5 for p in ("junio", "septiembre")),
    "advertencia": "No hay nueva prueba independiente; no sustituye resultados de versión1",
}
with (salida / "resultados.json").open("x", encoding="utf-8") as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2, allow_nan=False)
print("\nRESUMEN BÚSQUEDA AMPLIADA")
print("Configuraciones:", len(configuraciones), "Ajustes:", 2 * len(configuraciones))
print("Mejor configuración:", mejor["parametros"], "Umbral:", mejor["umbral"])
print("F1 junio:", mejor["junio"]["f1_abandono"])
print("F1 septiembre:", mejor["septiembre"]["f1_abandono"])
print("F1 medio:", mejor["f1_medio"])
print("F1 medio anterior:", referencia["f1_medio"])
print("Mejora:", resumen["mejora_f1_medio"])
print("F1>=0.50 en ambos periodos:", resumen["supera_050_en_ambas_validaciones"])
print("Evidencia:", salida)
print("Diciembre no leído; modelo de la demo no modificado.")
```

## Ejecutar

```powershell
python scripts/21_ampliar_arbol.py
```

Comparte desde RESUMEN BÚSQUEDA AMPLIADA. Es un experimento acotado, sin garantías de alcanzar la meta. Veremos si la mejora es consistente en ambos periodos antes de decidir el siguiente paso. La guía24 permite avanzar en la interfaz con la versión1 evaluada, independientemente de este resultado.

Referencia: https://scikit-learn.org/stable/modules/grid_search.html
