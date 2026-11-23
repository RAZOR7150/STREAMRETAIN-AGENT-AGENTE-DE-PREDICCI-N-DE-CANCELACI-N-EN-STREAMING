# Guía 29 — Preparación reutilizable de diciembre para V4

## Estado

El estudiante entrenó V4 con22904 filas y10 características: árbol depth10,leaf100,class_weight=None,umbral0,30. Artefacto experiments/modelo_v4/modelo_agente.joblib, SHA256 8a9c3cc742bd1d240e400ec893243f686881c58a267ec9953ee560d5b931b6c3. F1medio de validación0,53975. No hay aún evaluación posterior de esta versión.

Ahora extraemos la preparación del script23 a una función con parámetros. Esta es una migración inicial de código existente; después cualquier corte se prepara llamando la función, sin copiar su lógica. La nueva ejecución reconstruirá los tres cortes de desarrollo y diciembre en una carpeta distinta. Comparará las huellas de desarrollo para comprobar que la reorganización no cambió sus resultados. Todo se obtiene en una sola pasada del comprimido.

Diciembre ya fue observado con V1: la evaluación posterior de V4 será exploratoria, no una nueva prueba independiente. No se reajustan parámetros durante esta preparación. La interfaz continúa en pausa.

## 1. Extraer la lógica a streamretain/preparacion.py

Crea `streamretain/preparacion.py` con las mismas importaciones del script23:

```python
import csv
import hashlib
import json
import subprocess
from datetime import date, timedelta
from pathlib import Path
```

Después coloca esta cabecera:

```python
def preparar_suscripcion(raiz, metas, base, salida, *, estado):
    carpeta = raiz / "data" / "derived"
    if len(base) != 6 or not metas:
        raise ValueError("Se necesitan seis características base y al menos una cohorte")
    if len({m["corte"] for m in metas}) != len(metas):
        raise ValueError("Cortes repetidos")
```

Debajo, dentro de la función, incorpora **una sola vez** el bloque existente de `scripts/23_enriquecer_cohortes.py` desde la línea `extras = [...]` hasta el final del archivo. Selecciona ese bloque y aumenta su indentación cuatro espacios para que quede dentro de preparar_suscripcion. Mantén la indentación relativa de sus bucles y condiciones.

No copies las líneas previas que asignaban raiz, carpeta, seleccion o base: ahora son parámetros o se calculan en la cabecera. El script23 histórico se conserva; no lo importes porque ejecutaría todo su procesamiento.

Realiza estos cambios concretos en el bloque trasladado:

1. **Elimina** la asignación `salida = carpeta / "caracteristicas_suscripcion_v4"`. La carpeta de salida ahora la decide quien llama a la función. Conserva el control `if salida.exists()`.
2. Sustituye las **dos apariciones** de `seleccion["cohortes_desarrollo"]` por `metas`: una en el bucle de cohortes y otra en el manifiesto.
3. En el manifiesto sustituye `"estado": "desarrollo_exploratorio_v4_sin_diciembre"` por `"estado": estado`.
4. Sustituye el último mensaje `print("Diciembre no procesado; ningún modelo entrenado.")` por:

```python
    print("Cortes preparados:", [m["corte"] for m in metas])
    print("Ningún modelo entrenado ni evaluado.")
    return manifiesto
```

La función leer_fecha puede permanecer definida dentro de preparar_suscripcion como está en el bloque trasladado; así solo existe para esa preparación. No cambies sus reglas. Tampoco modifiques ventanas, orden de columnas, promedios, controles ni escritura de CSV: queremos reproducir el procedimiento anterior.

Al terminar, `preparacion.py` solo debe contener importaciones y la definición de preparar_suscripcion. No debe llamarla al final. Las referencias a `seleccion` deben haber desaparecido del módulo.

### Contrato de la función

| Parámetro | Significado |
| --- | --- |
| raiz | Carpeta raíz del proyecto, como Path |
| metas | Lista de cohortes originales con corte, filas y sha256 |
| base | Nombres de las seis características originales |
| salida | Carpeta nueva donde guardar CSV y manifiesto |
| estado | Descripción del uso de la preparación; se pasa por nombre |

La función devuelve el manifiesto. Los usuarios y etiquetas se leen de las cohortes originales, sin reconstruir etiquetas ni cambiar elegibilidad. Las cuatro características añadidas solo usan registros en [corte-90d,corte). Que el comprimido contenga fechas posteriores no autoriza a usarlas.

## 2. Verificar que importar no procesa datos

Desde la raíz:

```powershell
python -c "from streamretain.preparacion import preparar_suscripcion; print('Importación correcta; sin procesamiento')"
```

No deben aparecer contadores ni nuevos CSV. Si aparecen, parte del bloque quedó fuera de la función: corrige la indentación antes de continuar.

## 3. Crear scripts/preparar_diciembre_v4.py

Este programa contiene solo la coordinación: lee metadatos, llama a la función compartida y verifica equivalencia. Usa las utilidades del módulo comun creado en la guía28.

```python
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
```

La huella comprueba los bytes del archivo: si una cohorte de desarrollo no coincide, no se ignora el control ni se sobrescribe el original. Se revisa la reorganización. El archivo verificacion.json solo se escribe si todos los controles pasan.

## 4. Ejecutar

Desde la raíz del proyecto, con el entorno activo:

```powershell
python -m scripts.preparar_diciembre_v4
```

O con el intérprete explícito:

```powershell
& ".\.venv\Scripts\python.exe" -m scripts.preparar_diciembre_v4
```

Es normal volver a recorrer21547746 filas del comprimido; no se guarda descomprimido completo. La ejecución conserva solo los acumuladores necesarios para las cuatro cohortes. Las tablas resultantes son pequeñas y están en una carpeta nueva.

Comparte el RESUMEN PREPARACIÓN DICIEMBRE V4 y los mensajes de equivalencia. El paso siguiente será un programa pequeño que importe cargar_par y medir, cargue el joblib congelado, prediga y guarde las métricas exploratorias. Ese programa no volverá a entrenar ni buscar umbrales.
