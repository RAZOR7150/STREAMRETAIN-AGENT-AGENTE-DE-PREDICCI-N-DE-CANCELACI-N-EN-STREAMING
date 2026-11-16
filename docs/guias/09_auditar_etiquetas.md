# Guía 09 — Revisar casos reales del etiquetado

## Propósito

Antes de entrenar comprobaremos ejemplos reales del piloto. Un programa puede terminar sin errores y aun así aplicar una regla equivocada. Revisaremos los eventos que justifican las etiquetas, no solo el porcentaje final.

Crearás `scripts/07_auditar_etiquetas.py`. Leerá únicamente los CSV pequeños y escribirá un informe local con alias como Caso 01, sin imprimir msno. No cambia las etiquetas. Codex no ejecutará este procesamiento por ti.

Esta revisión de etiquetas NO es el análisis de diez fallos de un modelo exigido para la entrega final: todavía no hay predicciones de un modelo.

## 1. Preparación

```python
import csv
from collections import defaultdict, Counter
from datetime import date, timedelta
from functools import cmp_to_key
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data" / "derived"
salida = raiz / "docs" / "auditorias" / "piloto_2016-03-07.md"
corte = date(2016, 3, 7)
inicio = corte - timedelta(days=90)
fin = date(2016, 5, 5)
```

Copia aquí **solo las funciones `leer_fecha` y `comparar_eventos`** de la guía 07. No importes el script anterior ni copies su ejecución. El orden del informe sigue la convención Scala ya explicada; reutilizar el comparador no constituye una validación independiente de esa convención.

## 2. Leer y comprobar coherencia de las etiquetas

```python
etiquetas = {}
with (carpeta / "etiquetas_piloto_2016-03-07.csv").open(
    encoding="utf-8-sig", newline=""
) as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "corte", "vencimiento_conocido", "observado_hasta",
                  "is_churn", "motivo", "vencimiento_efectivo",
                  "primera_renovacion", "gap_dias"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera de etiquetas inesperada")

    for numero, fila in enumerate(lector, start=1):
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError(f"Fila mal formada: {numero}")
        usuario = fila["msno"].strip()
        if not usuario or usuario in etiquetas:
            raise ValueError(f"Identificador vacío o repetido: fila {numero}")
        if date.fromisoformat(fila["corte"]) != corte:
            raise ValueError("Otro corte en etiquetas")
        if date.fromisoformat(fila["observado_hasta"]) != fin:
            raise ValueError("Otro final de seguimiento")
        conocido = date.fromisoformat(fila["vencimiento_conocido"])
        efectivo = date.fromisoformat(fila["vencimiento_efectivo"])
        if not corte <= conocido <= corte + timedelta(days=29):
            raise ValueError("Vencimiento conocido fuera de candidatos")
        if efectivo > conocido:
            raise ValueError("La regla solo permite adelantar el vencimiento")

        if fila["primera_renovacion"]:
            renovacion = date.fromisoformat(fila["primera_renovacion"])
            if not corte <= renovacion <= fin:
                raise ValueError("Renovación fuera del seguimiento")
            gap = int(fila["gap_dias"])
            if gap != (renovacion - efectivo).days:
                raise ValueError("Gap inconsistente con las fechas guardadas")
            esperado = "0" if gap < 30 else "1"
            motivo = "renovacion_oportuna" if gap < 30 else "renovacion_tardia"
        else:
            if fila["gap_dias"] != "":
                raise ValueError("Sin renovación el gap debe estar vacío")
            completo = fin >= efectivo + timedelta(days=30)
            esperado = "1" if completo else ""
            motivo = "sin_renovacion_en_plazo" if completo else "seguimiento_insuficiente"
        if fila["is_churn"] != esperado or fila["motivo"] != motivo:
            raise ValueError(f"Etiqueta o motivo inconsistente: fila {numero}")
        etiquetas[usuario] = fila

if len(etiquetas) != 7443:
    raise ValueError("No coincide el número de candidatos del piloto")
```

Estas comprobaciones revisan que los campos guardados se correspondan. Todavía no demuestran que la renovación elegida sea realmente la primera o que el vencimiento se haya reconstruido correctamente; para eso miraremos los eventos. No confundas coherencia interna con corrección del resultado real.

## 3. Recuperar los eventos para ver la evidencia

```python
historia = defaultdict(list)
seguimiento = defaultdict(list)
leidas = 0
with (carpeta / "piloto_2016-03-07.csv").open(
    encoding="utf-8-sig", newline=""
) as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "transaction_date", "membership_expire_date",
                  "is_cancel", "plan_list_price", "payment_plan_days", "payment_method_id"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera de eventos inesperada")
    for fila in lector:
        leidas += 1
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Evento mal formado")
        usuario = fila["msno"].strip()
        if usuario not in etiquetas:
            continue
        fecha = leer_fecha(fila["transaction_date"])
        if not inicio <= fecha <= fin:
            raise ValueError("Evento fuera de ventana")
        cancelacion = fila["is_cancel"].strip()
        if cancelacion not in {"0", "1"}:
            raise ValueError("Cancelación inválida")
        plan = [fila[c] for c in
                ("plan_list_price", "payment_plan_days", "payment_method_id")]
        if any(not valor.strip() for valor in plan):
            raise ValueError("Falta información del plan")
        evento = {
            "fecha": fecha,
            "vencimiento": leer_fecha(fila["membership_expire_date"]),
            "cancelacion": cancelacion,
            "firma": "".join(plan),
        }
        destino = historia if fecha < corte else seguimiento
        destino[usuario].append(evento)
if leidas != 40503:
    raise ValueError("El piloto no tiene el tamaño previamente revisado")
if any(not historia[u] for u in etiquetas):
    raise ValueError("Hay un candidato sin historia")
```

Se conserva el historial de esta muestra pequeña. La variable destino apunta al diccionario de historia o seguimiento según la fecha. Esta separación impide confundir qué se sabía al predecir y qué ocurrió después.

## 4. Seleccionar ejemplos de forma reproducible

```python
def tiene_gap(fila, condicion):
    # Un gap vacío no es cero y no se convierte a entero.
    return fila["gap_dias"] != "" and condicion(int(fila["gap_dias"]))

categorias = {
    "renovacion_anticipada": [],
    "renovacion_mismo_dia": [],
    "renovacion_entre_1_y_28_dias": [],
    "gap_29": [],
    "gap_30": [],
    "gap_mayor_30": [],
    "sin_eventos_futuros": [],
    "solo_cancelaciones_futuras": [],
    "vencimiento_adelantado": [],
    "empate_en_dia_historico_final": [],
}
for usuario in sorted(etiquetas):
    fila = etiquetas[usuario]
    eventos = seguimiento.get(usuario, [])
    ultima_fecha = max(e["fecha"] for e in historia[usuario])
    cumple = {
        "renovacion_anticipada": tiene_gap(fila, lambda g: g < 0),
        "renovacion_mismo_dia": tiene_gap(fila, lambda g: g == 0),
        "renovacion_entre_1_y_28_dias": tiene_gap(fila, lambda g: 1 <= g <= 28),
        "gap_29": tiene_gap(fila, lambda g: g == 29),
        "gap_30": tiene_gap(fila, lambda g: g == 30),
        "gap_mayor_30": tiene_gap(fila, lambda g: g > 30),
        "sin_eventos_futuros": not eventos,
        "solo_cancelaciones_futuras": bool(eventos) and all(
            e["cancelacion"] == "1" for e in eventos),
        "vencimiento_adelantado": fila["vencimiento_efectivo"] < fila["vencimiento_conocido"],
        "empate_en_dia_historico_final": sum(
            e["fecha"] == ultima_fecha for e in historia[usuario]) > 1,
    }
    for categoria, valor in cumple.items():
        if valor:
            categorias[categoria].append(usuario)

# Un usuario puede ilustrar varias categorías: no imprimimos el mismo caso dos veces.
seleccionados = defaultdict(list)
for categoria, usuarios in categorias.items():
    if usuarios:
        seleccionados[usuarios[0]].append(categoria)
```

Cada categoría elige el primer identificador en orden: la selección es estable, pero NO es una muestra aleatoria ni representativa. Sus conteos pueden superponerse y no deben sumarse como grupos independientes. Si no hay gap 29 o 30 en los datos, se informa ausencia: no inventamos un caso real para completar una cuota. Las pruebas sintéticas de la guía 08 siguen cubriendo esos límites.

## 5. Crear el informe local

```python
lineas = [
    "# Auditoría manual pendiente — piloto 2016-03-07",
    "",
    "Ejemplos seleccionados, no predicciones ni fallos de un modelo.",
    "La cobertura del historial sigue siendo un supuesto.",
    "Los alias ocultan msno en este informe; esto no garantiza anonimización.",
    "",
    "## Categorías disponibles (pueden solaparse)",
    "",
]
for categoria, usuarios in categorias.items():
    lineas.append(f"- {categoria}: {len(usuarios)}")

for numero, (usuario, categorias_caso) in enumerate(seleccionados.items(), start=1):
    fila = etiquetas[usuario]
    lineas.extend([
        "", f"## Caso {numero:02d}", "",
        "Categorías: " + ", ".join(categorias_caso), "",
    ])
    for campo in ("corte", "vencimiento_conocido", "vencimiento_efectivo",
                  "primera_renovacion", "gap_dias", "is_churn", "motivo", "observado_hasta"):
        lineas.append(f"- {campo}: {fila[campo] or '(vacío)'}")
    for nombre, eventos in (("Historia", historia[usuario]),
                            ("Seguimiento", seguimiento.get(usuario, []))):
        lineas.extend(["", f"### {nombre}", ""])
        if not eventos:
            lineas.append("Sin eventos en esta fase.")
            continue
        lineas.extend(["| Fecha | Cancelación | Vencimiento | Firma del plan |",
                       "| --- | --- | --- | --- |"])
        for e in sorted(eventos, key=cmp_to_key(comparar_eventos)):
            firma = e["firma"].replace("|", "\\|")
            lineas.append(
                f"| {e['fecha']} | {e['cancelacion']} | {e['vencimiento']} | {firma} |")
    lineas.extend([
        "", "### Revisión del estudiante", "",
        "- Vencimiento reconstruido al corte: pendiente.",
        "- Primera renovación y efecto de cancelaciones: pendiente.",
        "- Gap calculado manualmente (o motivo de ausencia): pendiente.",
        "- Etiqueta esperada y comparación con la guardada: pendiente.",
        "- Veredicto: pendiente (coincide / discrepancia / no determinable).",
    ])

salida.parent.mkdir(parents=True, exist_ok=True)
with salida.open("x", encoding="utf-8") as archivo:
    archivo.write("\n".join(lineas) + "\n")
print("Etiquetas con coherencia interna:", len(etiquetas))
for categoria, usuarios in categorias.items():
    print(f"{categoria}: {len(usuarios)}")
print("Casos distintos para revisión manual:", len(seleccionados))
print("Informe local:", salida)
print("La revisión manual sigue pendiente; no se modificaron etiquetas.")
```

La salida contiene solo alias, pero las fechas y trayectorias siguen siendo datos derivados: conservarla local. Si ya existe, el modo x se detiene para proteger también tus anotaciones manuales. No borres un informe revisado para repetir la extracción; comparte el error si necesitas otra versión.

## 6. Ejecutar y revisar

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\07_auditar_etiquetas.py"
```

Abre `docs/auditorias/piloto_2016-03-07.md`. La selección generará hasta diez casos distintos, posiblemente menos por categorías ausentes o coincidencias. Los resultados todavía no se conocen; no esperamos una cantidad inventada por categoría.

Para cada caso, realiza estas comprobaciones con sus fechas, sin limitarte a copiar la etiqueta:

1. Recorre la historia y determina el vencimiento al corte con la convención de desempate Scala. Compara con vencimiento_conocido.
2. En seguimiento, empieza con ese vencimiento; aplica solo cancelaciones anteriores a la primera renovación. Una cancelación posterior a ella no cambia el cálculo de esta etiqueta.
3. Identifica la primera renovación desde el corte. Recuerda que puede ser anterior al vencimiento. No confundas el nuevo vencimiento de la renovación con la fecha de la renovación.
4. Resta fecha de renovación menos vencimiento efectivo. Si no hay renovación, comprueba el plazo observado y declara el supuesto de cobertura.
5. Escribe la etiqueta que esperas y compárala con la guardada. Si discrepa, no cambies valores para hacerlos coincidir: describe el motivo y detengamos el avance al entrenamiento.

Empieza compartiendo el resumen de consola y tu razonamiento para tres casos: uno de renovación, uno sin renovación y uno con vencimiento adelantado, si esas categorías aparecen. Usa Caso 01, Caso 02, etc.; no copies identificadores. Revisaremos esos primeros casos y luego completarás los restantes antes de usar las etiquetas para entrenar.

## 7. Qué viene después

Una vez revisados los casos y resueltas discrepancias, construiremos características usando solo la historia y las enlazaremos con las etiquetas. El paso siguiente será una línea base en una separación temporal válida, con la cohorte posterior preparada por el mismo procedimiento. Esta auditoría no garantiza perfección global ni mide exactitud de un modelo.

Preguntas: ¿por qué coherencia interna no equivale a corrección?, ¿por qué las categorías se solapan?, ¿por qué no son estos los diez errores de modelo del informe final?
