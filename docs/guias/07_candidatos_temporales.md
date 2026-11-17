# Guía 07 — Reconstruir el vencimiento conocido y seleccionar candidatos

## Objetivo

Pasar de transacciones a una fila por usuario candidato para el lunes 2016-03-07. Usaremos únicamente la historia anterior al corte para decidir quién entra. Las renovaciones futuras no deciden la elegibilidad y todavía no calcularemos is_churn.

Entrada: data/derived/piloto_2016-03-07.csv, creado por ti: 40.503 transacciones. No volveremos a leer los 21 millones de registros originales. Salida local: data/derived/candidatos_2016-03-07.csv. No publicar estos CSV con identificadores.

Crea `scripts/05_candidatos_temporales.py` y escribe los bloques en orden. El código de esta guía no ha sido ejecutado sobre el dataset por Codex.

## 1. Preparación y fechas

```python
import csv
from collections import defaultdict, Counter
from datetime import date, timedelta
from functools import cmp_to_key
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
entrada = raiz / "data" / "derived" / "piloto_2016-03-07.csv"
salida = raiz / "data" / "derived" / "candidatos_2016-03-07.csv"
corte = date(2016, 3, 7)
inicio = corte - timedelta(days=90)
fin_vencimientos = corte + timedelta(days=29)
fin_seguimiento = fin_vencimientos + timedelta(days=30)


def leer_fecha(texto):
    texto = texto.strip()
    if len(texto) != 8 or not texto.isascii() or not texto.isdigit():
        raise ValueError(f"Formato de fecha inválido: {texto!r}")
    return date(int(texto[:4]), int(texto[4:6]), int(texto[6:8]))
```

Aquí una fecha inválida detiene el ejercicio: la muestra ya pasó controles básicos, y no queremos reconstruir un usuario con parte de su historia omitida silenciosamente. Los errores de calendario los detecta date. `!r` muestra el texto con comillas para hacer visibles espacios o valores vacíos.

## 2. Agrupar únicamente la historia

```python
# Cada identificador tendrá una lista de eventos anteriores al corte.
historia = defaultdict(list)
usuarios_seguimiento = set()
filas = Counter()

with entrada.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    campos = lector.fieldnames
    requeridos = {
        "msno", "transaction_date", "membership_expire_date",
        "plan_list_price", "payment_plan_days", "payment_method_id", "is_cancel",
    }
    if not campos or not requeridos.issubset(campos):
        raise ValueError(f"Cabecera inesperada: {campos}")
    if len(campos) != len(set(campos)):
        raise ValueError("Hay columnas repetidas")

    for numero, fila in enumerate(lector, start=1):
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError(f"Fila mal formada: {numero}")
        usuario = fila["msno"].strip()
        if not usuario:
            raise ValueError(f"Identificador vacío: fila {numero}")
        fecha = leer_fecha(fila["transaction_date"])
        if not inicio <= fecha <= fin_seguimiento:
            raise ValueError(f"Evento fuera de ventana: fila {numero}")

        if fecha >= corte:
            filas["seguimiento"] += 1
            usuarios_seguimiento.add(usuario)
            continue  # No incorporamos estos eventos al estado conocido al corte.

        cancelacion = fila["is_cancel"].strip()
        if cancelacion not in {"0", "1"}:
            raise ValueError(f"is_cancel inválido: fila {numero}")
        # El Scala concatena estos campos como texto para desempatar planes.
        campos_plan = [fila[c] for c in
                       ("plan_list_price", "payment_plan_days", "payment_method_id")]
        if any(not valor.strip() for valor in campos_plan):
            raise ValueError(f"Campo de plan vacío: fila {numero}")
        evento = {
            "fecha": fecha,
            "vencimiento": leer_fecha(fila["membership_expire_date"]),
            "firma": "".join(campos_plan),
            "cancelacion": cancelacion,
        }
        historia[usuario].append(evento)
        filas["historia"] += 1
```

`defaultdict(list)` crea una lista vacía cuando aparece por primera vez un usuario. `append` añade su evento. Ahora sí conservamos historia en memoria, pero solo las 25.054 transacciones históricas del piloto, no todo el dataset. Los diccionarios consumen más memoria que el texto del CSV.

El conjunto de usuarios con seguimiento sirve exclusivamente para describir cobertura. No exigiremos tener una transacción futura para entrar: eso excluiría precisamente a usuarios que podrían abandonar. Tampoco la ausencia de eventos basta todavía para asignar abandono.

## 3. Ordenar como el código de referencia de KKBox

Una fecha puede contener varios eventos del mismo usuario. No basta con tomar la última fila del CSV ni el mayor vencimiento: una cancelación puede adelantarlo. Este comparador reproduce el orden usado por calculateLastday en `data/kkbox-churn-prediction-challenge/WSDMChurnLabeller.scala`.

```python
def comparar_eventos(a, b):
    # Un resultado negativo coloca a antes que b; positivo, después; cero, empate.
    if a["fecha"] != b["fecha"]:
        return -1 if a["fecha"] < b["fecha"] else 1

    # Mismo día: firma del plan en orden descendente, como texto en el Scala.
    if a["firma"] != b["firma"]:
        return -1 if a["firma"] > b["firma"] else 1

    # Misma firma y día: renovación antes que cancelación.
    if a["cancelacion"] != b["cancelacion"]:
        return -1 if a["cancelacion"] < b["cancelacion"] else 1

    if a["vencimiento"] == b["vencimiento"]:
        return 0
    if a["cancelacion"] == "1":
        # Entre cancelaciones, el vencimiento más temprano queda al final.
        return -1 if a["vencimiento"] > b["vencimiento"] else 1
    # Entre renovaciones, el vencimiento más tardío queda al final.
    return -1 if a["vencimiento"] < b["vencimiento"] else 1
```

`cmp_to_key` permitirá usar este comparador con sorted. La firma es una convención del código de referencia, no una medida de calidad del plan. Se concatena y compara como texto: no cambiarla por una suma numérica. Estas reglas resuelven empates cuando no tenemos hora; no demuestran el orden intradía real.

Si dos eventos empatan en todos estos campos, su vencimiento es igual y el estado calculado aquí no cambia. Eso no autoriza a borrar transacciones automáticamente ni a asumir que todos los demás atributos son iguales. No utilizaremos esta selección para escoger atributos ajenos a los campos comparados sin revisar empates.

## 4. Seleccionar el vencimiento y los candidatos

```python
candidatos = []
clasificacion = Counter()
usuarios_con_empate_ultimo_dia = 0

for usuario, eventos in historia.items():
    ordenados = sorted(eventos, key=cmp_to_key(comparar_eventos))
    ultimo = ordenados[-1]  # Último según las reglas, no según el orden del CSV.
    vencimiento = ultimo["vencimiento"]
    if sum(e["fecha"] == ultimo["fecha"] for e in eventos) > 1:
        usuarios_con_empate_ultimo_dia += 1

    if vencimiento < corte:
        clasificacion["vencimiento_anterior"] += 1
    elif vencimiento > fin_vencimientos:
        clasificacion["vencimiento_posterior"] += 1
    else:
        clasificacion["candidato"] += 1
        candidatos.append({
            "msno": usuario,
            "corte": corte.isoformat(),
            "vencimiento_conocido": vencimiento.isoformat(),
            "ultima_transaccion_historica": ultimo["fecha"].isoformat(),
            "transacciones_historicas": len(eventos),
        })

if sum(clasificacion.values()) != len(historia):
    raise RuntimeError("No cuadra la clasificación de usuarios históricos")
if len(candidatos) != clasificacion["candidato"]:
    raise RuntimeError("No cuadra el número de candidatos")

usuarios_historicos = set(historia)
solo_seguimiento = usuarios_seguimiento - usuarios_historicos
if not candidatos:
    raise RuntimeError("No hay candidatos: revisar antes de crear la salida")
```

La ventana de candidatos es del 7 de marzo al 5 de abril, incluidos. Un vencimiento fuera de ella excluye al usuario de ESTE corte; no significa que su etiqueta sea abandono ni renovación. Usamos únicamente el estado reconstruible en los 90 días anteriores: usuarios sin eventos allí quedan fuera, incluidos posibles planes largos. Esta es una limitación explícita del piloto.

`isoformat()` escribe fechas como YYYY-MM-DD. No confundir ese formato de la salida con YYYYMMDD del archivo original. Una fila candidata aún no contiene is_churn.

## 5. Guardar e informar

```python
columnas = ["msno", "corte", "vencimiento_conocido",
            "ultima_transaccion_historica", "transacciones_historicas"]
# Creamos la salida después de terminar los controles y no sobrescribimos otra.
with salida.open("x", encoding="utf-8", newline="") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=columnas)
    escritor.writeheader()
    # Ordenar por identificador hace reproducible el orden del archivo.
    escritor.writerows(sorted(candidatos, key=lambda fila: fila["msno"]))

print("Filas históricas:", filas["historia"])
print("Filas de seguimiento:", filas["seguimiento"])
print("Total de filas:", sum(filas.values()))
print("Usuarios con historia:", len(historia))
print("Usuarios con seguimiento:", len(usuarios_seguimiento))
print("Usuarios solo con seguimiento:", len(solo_seguimiento))
print("Usuarios con varios eventos en su último día histórico:",
      usuarios_con_empate_ultimo_dia)
print("Vencimiento anterior al corte:", clasificacion["vencimiento_anterior"])
print("Vencimiento posterior a la ventana:", clasificacion["vencimiento_posterior"])
print("Candidatos:", len(candidatos))
print("Archivo local:", salida)
```

`lambda` aquí es una función breve que indica ordenar cada fila por msno. No convierte el identificador en predictor. Si vuelve a aparecer FileExistsError, significa que ya existe una salida: no cambies x por w ni la borres sin revisar si terminó una ejecución anterior.

## 6. Ejecuta y comparte la salida

Desde la raíz del proyecto:

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\05_candidatos_temporales.py"
```

No requiere paquetes nuevos. Las filas de historia y seguimiento deberían coincidir con 25.054 y 15.449, total 40.503, si utilizas el piloto correcto. No conocemos aún cuántos usuarios o candidatos habrá. Comparte el resumen, no identificadores. Si aparece un error, comparte el mensaje completo.

## 7. Comprensión

1. ¿Por qué no usamos simplemente el mayor membership_expire_date de cada usuario?
2. ¿Por qué alguien cuyo vencimiento queda fuera de la ventana no recibe automáticamente is_churn=1?
3. ¿Por qué no exigimos que el candidato tenga transacciones después del corte?
4. ¿Qué diferencia hay entre un candidato y un ejemplo ya etiquetado?

Después revisaremos los conteos y construiremos la etiqueta con el seguimiento, usando casos de ejemplo para verificar renovaciones, cancelaciones y el límite de 30 días. No entrenar todavía con este CSV.
