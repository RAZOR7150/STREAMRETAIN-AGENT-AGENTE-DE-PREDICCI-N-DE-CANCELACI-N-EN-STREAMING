# Guía 10 — Construir características históricas y unir las etiquetas

## Objetivo

Ya terminamos la revisión guiada de nueve casos. No encontramos discrepancias con las reglas aplicadas; esto no certifica todas las etiquetas ni elimina el supuesto de cobertura.

Ahora crearás una tabla de la cohorte de marzo: **una fila por usuario y corte**, con seis características históricas y la etiqueta reconstruida. Los identificadores y el corte se conservan para trazabilidad, no como entradas del modelo. Todavía no entrenaremos: después necesitaremos preparar la cohorte posterior para evaluar temporalmente.

Crea `scripts/08_caracteristicas_historicas.py`. Escribe los bloques en orden. Trabajaremos sobre los CSV pequeños; no hace falta recorrer de nuevo el comprimido original.

## Características elegidas para este primer experimento

| Columna | Significado |
| --- | --- |
| transacciones_90d | Número de transacciones en los 90 días anteriores al corte, incluidas cancelaciones |
| transacciones_30d | Número de transacciones en los últimos 30 días anteriores al corte |
| cancelaciones_90d | Número de transacciones históricas con is_cancel=1 |
| dias_con_transacciones_90d | Cantidad de fechas distintas con alguna transacción; no mide días de escucha |
| dias_desde_ultima_transaccion | Días desde la última transacción histórica hasta el corte |
| dias_hasta_vencimiento | Días desde el corte hasta el vencimiento CONOCIDO al corte |

Son un punto de partida sencillo para describir frecuencia, cancelaciones, actividad transaccional reciente y proximidad del vencimiento. No se afirma que sean las mejores variables ni que garanticen el umbral de F1. No calculamos antigüedad real del cliente porque 90 días de observación no equivalen a tiempo desde su registro.

Ventana de 90 días: 2015-12-08 <= fecha < 2016-03-07. Ventana de 30 días: 2016-02-06 <= fecha < 2016-03-07. La fecha del corte queda excluida: representa la predicción al comenzar el lunes. Una transacción del domingo anterior tiene una distancia de un día al corte.

No eliminamos automáticamente transacciones múltiples del mismo día: pueden ser eventos distintos. Un duplicado real podría inflar estos conteos; el ejercicio no certifica ausencia de duplicados de origen.

## 1. Preparar rutas y columnas permitidas

```python
import csv
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data" / "derived"
archivo_piloto = carpeta / "piloto_2016-03-07.csv"
archivo_candidatos = carpeta / "candidatos_2016-03-07.csv"
archivo_etiquetas = carpeta / "etiquetas_piloto_2016-03-07.csv"
salida = carpeta / "cohorte_2016-03-07.csv"
corte = date(2016, 3, 7)
inicio_90 = corte - timedelta(days=90)
inicio_30 = corte - timedelta(days=30)

# Lista explícita: más adelante X se construirá SOLO con estas columnas.
CARACTERISTICAS = [
    "transacciones_90d", "transacciones_30d", "cancelaciones_90d",
    "dias_con_transacciones_90d", "dias_desde_ultima_transaccion",
    "dias_hasta_vencimiento",
]
```

Copia aquí **solo la función `leer_fecha` de la guía 07** para interpretar fechas YYYYMMDD. No necesitamos comparar_eventos: el vencimiento al corte ya fue reconstruido en candidatos, y estos agregados no requieren resolver empates de orden. No importes scripts completos anteriores, pues ejecutarían sus instrucciones.

## 2. Leer candidatos sin utilizar etiquetas

```python
candidatos = {}
with archivo_candidatos.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "corte", "vencimiento_conocido",
                  "ultima_transaccion_historica", "transacciones_historicas"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera inesperada en candidatos")
    for fila in lector:
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Candidato mal formado")
        usuario = fila["msno"].strip()
        if not usuario or usuario in candidatos:
            raise ValueError("Identificador vacío o repetido en candidatos")
        if date.fromisoformat(fila["corte"]) != corte:
            raise ValueError("Candidato de otro corte")
        vence = date.fromisoformat(fila["vencimiento_conocido"])
        if not corte <= vence <= corte + timedelta(days=29):
            raise ValueError("Vencimiento fuera de candidatos")
        candidatos[usuario] = {
            "vence": vence,
            "ultima": date.fromisoformat(fila["ultima_transaccion_historica"]),
            "cantidad": int(fila["transacciones_historicas"]),
        }
if len(candidatos) != 7443:
    raise ValueError("No corresponde al piloto de 7.443 candidatos")

# Un acumulador independiente por candidato; aún no hemos leído is_churn.
acumuladores = {
    usuario: {"n90": 0, "n30": 0, "cancelaciones": 0,
              "fechas": set(), "ultima": None}
    for usuario in candidatos
}
```

Separar candidatos y etiquetas deja claro que la respuesta futura no interviene en el cálculo de entradas. Los candidatos ya se eligieron usando información anterior al corte. `set()` permitirá contar fechas distintas y `None` indica que todavía no hemos encontrado la última transacción.

## 3. Acumular únicamente eventos históricos

```python
filas_piloto = 0
filas_futuras_excluidas = 0
filas_historicas_candidatos = 0
with archivo_piloto.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "transaction_date", "is_cancel"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera inesperada en piloto")
    for fila in lector:
        filas_piloto += 1
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Evento mal formado")
        fecha = leer_fecha(fila["transaction_date"])
        if fecha >= corte:
            filas_futuras_excluidas += 1
            continue  # Esta exclusión ocurre ANTES de cualquier acumulación.
        if fecha < inicio_90:
            raise ValueError("Historia fuera de la ventana esperada")
        usuario = fila["msno"].strip()
        if not usuario:
            raise ValueError("Evento sin usuario")
        if usuario not in acumuladores:
            continue  # No todos los usuarios del piloto fueron candidatos.
        cancelacion = fila["is_cancel"].strip()
        if cancelacion not in {"0", "1"}:
            raise ValueError("is_cancel inválido")
        a = acumuladores[usuario]
        a["n90"] += 1
        a["n30"] += int(fecha >= inicio_30)
        a["cancelaciones"] += int(cancelacion == "1")
        a["fechas"].add(fecha)
        if a["ultima"] is None or fecha > a["ultima"]:
            a["ultima"] = fecha
        filas_historicas_candidatos += 1

if filas_piloto != 40503 or filas_futuras_excluidas != 15449:
    raise ValueError("Los tamaños no coinciden con el piloto revisado")

# Construimos X por usuario antes de cargar las etiquetas.
caracteristicas = {}
for usuario, a in acumuladores.items():
    referencia = candidatos[usuario]
    if a["ultima"] is None:
        raise ValueError("Hay un candidato sin historia")
    if a["n90"] != referencia["cantidad"] or a["ultima"] != referencia["ultima"]:
        raise ValueError("La historia no coincide con el archivo de candidatos")
    valores = {
        "transacciones_90d": a["n90"],
        "transacciones_30d": a["n30"],
        "cancelaciones_90d": a["cancelaciones"],
        "dias_con_transacciones_90d": len(a["fechas"]),
        "dias_desde_ultima_transaccion": (corte - a["ultima"]).days,
        "dias_hasta_vencimiento": (referencia["vence"] - corte).days,
    }
    if not 0 <= a["n30"] <= a["n90"]:
        raise ValueError("Conteos de 30/90 días inconsistentes")
    if not 0 <= a["cancelaciones"] <= a["n90"]:
        raise ValueError("Conteo de cancelaciones inconsistente")
    if not 1 <= len(a["fechas"]) <= min(90, a["n90"]):
        raise ValueError("Cantidad de fechas distintas inválida")
    if not 1 <= valores["dias_desde_ultima_transaccion"] <= 90:
        raise ValueError("Distancia histórica fuera de ventana")
    if not 0 <= valores["dias_hasta_vencimiento"] <= 29:
        raise ValueError("Distancia al vencimiento fuera de candidatos")
    caracteristicas[usuario] = valores
```

`a` apunta al acumulador del usuario: actualizarlo modifica ese registro del diccionario. `int(True)` vale 1 e `int(False)` vale 0. El conjunto de fechas evita contar dos veces el mismo día, pero n90 cuenta ambos eventos si hubo dos transacciones.

`dias_hasta_vencimiento` usa el vencimiento conocido ANTES del corte. No sustituirlo por vencimiento_efectivo de etiquetas, que puede haber sido modificado por cancelaciones futuras. Es posible conocer un vencimiento futuro sin conocer el futuro comportamiento del usuario.

Las filas históricas de candidatos pueden ser menos de 25.054, porque ese total incluía usuarios que después quedaron fuera de la cohorte.

## 4. Enlazar la etiqueta por identificador y corte

```python
etiquetas = {}
with archivo_etiquetas.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "corte", "is_churn", "observado_hasta"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera inesperada en etiquetas")
    for fila in lector:
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Etiqueta mal formada")
        usuario = fila["msno"].strip()
        if not usuario or usuario in etiquetas:
            raise ValueError("Identificador vacío o repetido en etiquetas")
        if date.fromisoformat(fila["corte"]) != corte:
            raise ValueError("Etiqueta de otro corte")
        if date.fromisoformat(fila["observado_hasta"]) != date(2016, 5, 5):
            raise ValueError("Etiqueta con otro seguimiento")
        if fila["is_churn"] not in {"0", "1"}:
            raise ValueError("Etiqueta desconocida o inválida: revisar, no eliminar")
        etiquetas[usuario] = int(fila["is_churn"])

if set(etiquetas) != set(caracteristicas):
    raise ValueError("Usuarios de etiquetas y características no coinciden")

filas_salida = []
for usuario in sorted(caracteristicas):
    filas_salida.append({
        "msno": usuario,
        "corte": corte.isoformat(),
        **caracteristicas[usuario],
        "is_churn": etiquetas[usuario],
    })
```

El enlace se hace por identificador y verificando el corte, no por posición de fila. Dos CSV podrían tener los mismos usuarios en distinto orden. Comprobar igualdad de conjuntos impide perder usuarios silenciosamente mediante una unión incompleta.

Aunque el CSV final contenga X e y juntos, el modelo solo recibirá como X las seis columnas enumeradas. is_churn es la respuesta objetivo; msno y corte son metadatos. No copiamos gap, motivo ni fechas de renovación futura.

## 5. Guardar y describir la tabla

```python
columnas = ["msno", "corte", *CARACTERISTICAS, "is_churn"]
with salida.open("x", encoding="utf-8", newline="") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=columnas)
    escritor.writeheader()
    escritor.writerows(filas_salida)

clases = Counter(etiquetas.values())
print("Corte:", corte)
print("Filas del piloto recorridas:", filas_piloto)
print("Filas futuras excluidas:", filas_futuras_excluidas)
print("Filas históricas de candidatos utilizadas:", filas_historicas_candidatos)
print("Usuarios / filas de la cohorte:", len(filas_salida))
print("Características:", len(CARACTERISTICAS))
print("Renovación (0):", clases[0])
print("Abandono (1):", clases[1])
print("Resumen de características: mínimo / máximo / promedio")
for nombre in CARACTERISTICAS:
    valores = [fila[nombre] for fila in filas_salida]
    print(f"  {nombre}: {min(valores)} / {max(valores)} / "
          f"{sum(valores) / len(valores):.2f}")
print("Archivo local:", salida)
print("Tabla preparada; ningún modelo entrenado ni evaluado.")
```

La estrella `*CARACTERISTICAS` incorpora cada nombre a la lista de columnas. `**caracteristicas[usuario]` del bloque anterior incorpora pares nombre-valor al diccionario. El promedio es descriptivo, no normalización ni parámetro aprendido para el modelo. Más adelante cualquier escalado se ajustará solo con entrenamiento.

El CSV sigue siendo local, con identificadores: no publicarlo. Se usa modo x para no sobrescribir. Si ya existe, revisa la ejecución previa; no cambies automáticamente a w ni borres tus resultados.

## 6. Ejecutar

Desde la raíz del proyecto:

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\08_caracteristicas_historicas.py"
```

No necesita paquetes adicionales. Esperamos conservar 7.443 filas, 6.348 etiquetas 0 y 1.095 etiquetas 1, porque no estamos filtrando candidatos nuevos ni cambiando las etiquetas. Los valores de las características aún no se conocen: comparte el resumen completo y cualquier error.

Estas características describen lo conocido el 7 de marzo, pero las etiquetas usan observación hasta el 5 de mayo. La tabla completa solo puede utilizarse para entrenar un modelo en un momento posterior compatible, por ejemplo antes de la validación de junio. No afirmar que el modelo se entrenó el 7 de marzo usando respuestas que aún no se conocían.

## 7. Comprobar con ejemplos que ya entiendes

En el informe de auditoría, el Caso 01 tiene tres transacciones históricas: 22 de diciembre, 22 de enero y 22 de febrero. Según esos eventos, deberías poder justificar:

- transacciones_90d = 3 y transacciones_30d = 1.
- cancelaciones_90d = 0 y dias_con_transacciones_90d = 3.
- dias_desde_ultima_transaccion = 14 (2016 es bisiesto).
- dias_hasta_vencimiento = 16 (del 7 al 23 de marzo).

Son valores deducidos del caso del informe, no una ejecución de este programa por Codex. Comprueba las fechas con el calendario; no uses meses aproximados de 30 días.

Preguntas para responder con tus palabras:

1. ¿Por qué dias_hasta_vencimiento sí puede usarse, mientras que gap_dias no?
2. ¿Por qué transacciones_90d y dias_con_transacciones_90d pueden ser distintos?
3. ¿Por qué enlazamos por identificador en lugar de unir la primera fila de cada CSV?
4. ¿Por qué tener esta cohorte lista todavía no demuestra que el modelo funciona?

Después de revisar tu salida, prepararemos la cohorte de junio con el mismo método para obtener la primera evaluación temporal de la línea base. No usar una partición aleatoria de marzo como reemplazo silencioso del protocolo elegido.
