# Guía 08 — Construir y revisar las etiquetas del piloto

## Objetivo

Asignar el resultado observado a los 7.443 candidatos del corte 2016-03-07. Trabajaremos con los dos CSV pequeños ya generados. No entrenaremos ni calcularemos métricas de un modelo.

Crea tú `scripts/06_etiquetar_piloto.py`. Escribe los bloques en orden. No importes los scripts anteriores: contienen instrucciones que se ejecutarían al importarlos. En este ejercicio copiaremos únicamente dos funciones de la guía 07; más adelante podremos separarlas en un módulo reutilizable.

## Qué significa gap

Gap significa diferencia o intervalo. Aquí es la fecha de renovación menos la fecha de vencimiento efectivo, expresada en días. Si renueva el 15 y vencía el 20, gap = -5; si renueva el 25, gap = 5. No es la duración del plan. Sin renovación no hay gap calculable. Consulta también Conceptos clave/Glosario.md.

## Qué regla aplicaremos

Referencia: `data/kkbox-churn-prediction-challenge/WSDMChurnLabeller.scala`, funciones calculateRenewalGap y clasificación de gap.

1. Partir del vencimiento conocido al corte.
2. Ordenar los eventos de seguimiento con el mismo comparador de la guía 07.
3. Antes de la primera renovación, una cancelación puede adelantar el vencimiento; no lo retrasa.
4. Tomar la primera transacción con is_cancel=0 posterior o igual al corte. Puede ocurrir ANTES del vencimiento: no descartarla.
5. Calcular gap = fecha de esa renovación menos vencimiento efectivo.
6. gap < 30: etiqueta 0. gap >= 30: etiqueta 1. Renovar exactamente 30 días después cuenta como abandono en este código de referencia.
7. Sin renovación observada: asignar 1 solo si el periodo observado cubre el límite y bajo el supuesto de cobertura explicado a continuación; de lo contrario dejar sin etiqueta.

Una cancelación no es automáticamente abandono: puede haber una renovación oportuna después. Tras la primera renovación, el Scala deja de buscar; no estudia todos los ciclos futuros de suscripción. Mantendremos ese alcance y lo documentaremos, aunque el comportamiento posterior pueda cambiar.

## Supuesto de cobertura y límites

El original se describe hasta 2017-02-28 y tu auditoría encontró ese máximo. Tu extracción recorrió todo el archivo y conservó todas las filas disponibles de los usuarios seleccionados entre 2015-12-08 y 2016-05-05. Para este piloto asumimos que ese historial publicado representa las transacciones necesarias dentro de la ventana. Esto NO demuestra que el proveedor no haya omitido eventos.

Las etiquetas que construiremos son **reconstruidas bajo ese supuesto**, no etiquetas oficiales verificadas contra train/train_v2. El informe deberá declarar esta limitación. No deducimos cobertura del último evento particular de cada usuario: un usuario puede no tener más eventos precisamente porque abandonó.

El seguimiento del piloto termina el 2016-05-05: alcanza los 30 días posteriores al último vencimiento elegible (2016-04-05). La ausencia de renovación será interpretada conforme a esa cobertura asumida. Si se descubre una extracción incompleta o una limitación de la fuente, esas etiquetas deben revisarse. Conservamos una categoría sin etiqueta para ventanas insuficientes, sin forzarla a 0 o 1.

## 1. Preparación

```python
import csv
from collections import defaultdict, Counter
from datetime import date, timedelta
from functools import cmp_to_key
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data" / "derived"
archivo_candidatos = carpeta / "candidatos_2016-03-07.csv"
archivo_eventos = carpeta / "piloto_2016-03-07.csv"
salida = carpeta / "etiquetas_piloto_2016-03-07.csv"
corte = date(2016, 3, 7)
inicio = corte - timedelta(days=90)
fin_vencimientos = corte + timedelta(days=29)
# Es el final de la ventana extraída, no el último evento de cada usuario.
fin_observacion = fin_vencimientos + timedelta(days=30)
```

**Ahora copia aquí, completas, las funciones `leer_fecha` y `comparar_eventos` de la guía 07.** No copies su lectura de archivos ni sus impresiones. leer_fecha interpreta YYYYMMDD; para las fechas ISO de candidatos utilizaremos date.fromisoformat.

## 2. Función de etiquetado

```python
def etiquetar(vencimiento, eventos, observado_hasta):
    # Esta variable puede adelantarse por cancelaciones posteriores al corte.
    efectivo = vencimiento
    renovacion = None
    gap = None

    for evento in sorted(eventos, key=cmp_to_key(comparar_eventos)):
        if evento["fecha"] > observado_hasta:
            raise ValueError("Evento posterior al seguimiento declarado")
        if evento["cancelacion"] == "1":
            efectivo = min(efectivo, evento["vencimiento"])
        else:
            renovacion = evento["fecha"]
            gap = (renovacion - efectivo).days
            break  # Como en Scala, detenemos la búsqueda en la primera renovación.

    if renovacion is not None:
        etiqueta = 0 if gap < 30 else 1
        motivo = "renovacion_oportuna" if etiqueta == 0 else "renovacion_tardia"
    elif observado_hasta >= efectivo + timedelta(days=30):
        etiqueta = 1  # Depende del supuesto explícito de cobertura del historial.
        motivo = "sin_renovacion_en_plazo"
    else:
        etiqueta = None  # No sabemos el resultado: no equivale a abandono.
        motivo = "seguimiento_insuficiente"

    return {
        "is_churn": etiqueta,
        "motivo": motivo,
        "vencimiento_efectivo": efectivo.isoformat(),
        "primera_renovacion": renovacion.isoformat() if renovacion else "",
        "gap_dias": gap,
    }
```

La función devuelve un diccionario con la etiqueta y datos de auditoría. `None` representa un valor desconocido; al escribir CSV se guardará vacío. Un gap negativo significa renovación anticipada y es válido. No reemplazamos un gap ausente por 9999 como hace el Scala: conservamos el motivo para que no parezca una distancia real de 9999 días.

## 3. Casos de comprobación antes de tocar los datos

Estos son casos inventados para comprobar la lógica, no resultados de usuarios reales. Deben ejecutarse antes de las lecturas siguientes.

```python
def evento_ejemplo(fecha, cancelacion="0", vence="2016-04-20"):
    return {
        "fecha": date.fromisoformat(fecha),
        "vencimiento": date.fromisoformat(vence),
        "cancelacion": cancelacion,
        "firma": "plan-ejemplo",
    }

v = date(2016, 3, 20)
f = date(2016, 5, 5)
casos = [
    ("anticipada", [evento_ejemplo("2016-03-10")], f, 0),
    ("a los 29 dias", [evento_ejemplo("2016-04-18")], f, 0),
    ("a los 30 dias", [evento_ejemplo("2016-04-19")], f, 1),
    ("sin eventos, plazo cubierto", [], f, 1),
    ("sin eventos, plazo insuficiente", [], date(2016, 4, 1), None),
    ("cancelacion y renovacion oportuna", [
        evento_ejemplo("2016-03-10", "1", "2016-03-10"),
        evento_ejemplo("2016-03-15"),
    ], f, 0),
    ("cancelacion adelanta el limite", [
        evento_ejemplo("2016-03-10", "1", "2016-03-10"),
        evento_ejemplo("2016-04-09"),
    ], f, 1),
    ("sin renovar tras cancelacion", [
        evento_ejemplo("2016-03-10", "1", "2016-03-10"),
    ], f, 1),
    ("mismo dia: renovacion antes de cancelacion", [
        evento_ejemplo("2016-03-10", "1", "2016-03-10"),
        evento_ejemplo("2016-03-10"),
    ], f, 0),
]
for nombre, eventos, final, esperado in casos:
    obtenido = etiquetar(v, eventos, final)["is_churn"]
    if obtenido != esperado:
        raise AssertionError(f"{nombre}: esperado {esperado}, obtenido {obtenido}")
print("Casos ilustrativos correctos:", len(casos))
```

Si falla un caso, no continúes con el dataset: comparte el error. Los casos cubren situaciones importantes, pero no prueban exhaustivamente todos los desempates ni certifican las etiquetas reales.

## 4. Leer los candidatos y el seguimiento

```python
candidatos = {}
with archivo_candidatos.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "corte", "vencimiento_conocido"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera de candidatos inesperada")
    for fila in lector:
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Fila de candidato mal formada")
        usuario = fila["msno"].strip()
        if not usuario or usuario in candidatos:
            raise ValueError("Identificador vacío o repetido en candidatos")
        if date.fromisoformat(fila["corte"]) != corte:
            raise ValueError("El candidato pertenece a otro corte")
        vence = date.fromisoformat(fila["vencimiento_conocido"])
        if not corte <= vence <= fin_vencimientos:
            raise ValueError("Vencimiento fuera de la ventana de candidatos")
        candidatos[usuario] = vence
if not candidatos:
    raise ValueError("No hay candidatos")

seguimiento = defaultdict(list)
filas_piloto = 0
with archivo_eventos.open(encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)
    requeridos = {"msno", "transaction_date", "membership_expire_date",
                  "is_cancel", "plan_list_price", "payment_plan_days", "payment_method_id"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera del piloto inesperada")
    for fila in lector:
        filas_piloto += 1
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Fila de evento mal formada")
        fecha = leer_fecha(fila["transaction_date"])
        if not inicio <= fecha <= fin_observacion:
            raise ValueError("Evento fuera de la ventana extraída")
        usuario = fila["msno"].strip()
        if not usuario:
            raise ValueError("Evento sin usuario")
        if fecha < corte or usuario not in candidatos:
            continue  # La historia ya sirvió para seleccionar candidatos.
        cancelacion = fila["is_cancel"].strip()
        if cancelacion not in {"0", "1"}:
            raise ValueError("is_cancel inválido")
        plan = [fila[c] for c in
                ("plan_list_price", "payment_plan_days", "payment_method_id")]
        if any(not valor.strip() for valor in plan):
            raise ValueError("Campo de plan vacío")
        seguimiento[usuario].append({
            "fecha": fecha,
            "vencimiento": leer_fecha(fila["membership_expire_date"]),
            "cancelacion": cancelacion,
            "firma": "".join(plan),
        })

# Para este ejercicio conocemos los tamaños del piloto y candidatos ya revisados.
if filas_piloto != 40503 or len(candidatos) != 7443:
    raise ValueError("Los tamaños no coinciden con el piloto revisado; investigar")
```

El control de tamaños ayuda a detectar archivos equivocados o incompletos; no prueba integridad perfecta. La memoria se limita al seguimiento de candidatos de la muestra pequeña. Conservar candidatos sin eventos es esencial: no usar una unión que los descarte.

## 5. Etiquetar, guardar e imprimir

```python
resultados = []
por_etiqueta = Counter()
por_motivo = Counter()
sin_eventos = 0
adelantados = 0

for usuario, vencimiento in sorted(candidatos.items()):
    eventos = seguimiento.get(usuario, [])
    sin_eventos += int(not eventos)
    resultado = etiquetar(vencimiento, eventos, fin_observacion)
    adelantados += int(date.fromisoformat(resultado["vencimiento_efectivo"]) < vencimiento)
    por_etiqueta[resultado["is_churn"]] += 1
    por_motivo[resultado["motivo"]] += 1
    resultados.append({
        "msno": usuario,
        "corte": corte.isoformat(),
        "vencimiento_conocido": vencimiento.isoformat(),
        "observado_hasta": fin_observacion.isoformat(),
        "supuesto_cobertura": "historial_publicado_completo_en_ventana",
        **resultado,
    })

if sum(por_etiqueta.values()) != len(candidatos):
    raise RuntimeError("No cuadra el total de etiquetas")
if sum(por_motivo.values()) != len(candidatos):
    raise RuntimeError("No cuadra el total de motivos")

# El orden de las claves del primer diccionario define las columnas del CSV.
with salida.open("x", encoding="utf-8", newline="") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=list(resultados[0]))
    escritor.writeheader()
    escritor.writerows(resultados)

print("Candidatos procesados:", len(candidatos))
print("Candidatos sin eventos de seguimiento:", sin_eventos)
print("Vencimientos adelantados antes de primera renovacion:", adelantados)
print("Renovacion (0):", por_etiqueta[0])
print("Abandono (1):", por_etiqueta[1])
print("Sin etiqueta:", por_etiqueta[None])
for motivo, cantidad in sorted(por_motivo.items()):
    print(f"  {motivo}: {cantidad}")
con_etiqueta = por_etiqueta[0] + por_etiqueta[1]
if con_etiqueta:
    print("Abandono entre etiquetados:",
          f"{100 * por_etiqueta[1] / con_etiqueta:.2f}%")
print("Seguimiento declarado hasta:", fin_observacion)
print("Etiquetas reconstruidas bajo supuesto de cobertura; no oficiales")
print("Archivo local:", salida)
```

`**resultado` incorpora las claves del diccionario devuelto por la función. `int` convierte verdadero/falso en 1/0 para acumular conteos. **Todos los campos derivados del seguimiento** (motivo, vencimiento efectivo, primera renovación, gap) son información de auditoría del resultado, no características permitidas al corte. No pasar este CSV completo al modelo. is_churn será el objetivo; msno servirá solo para enlazar tablas.

No uses un abandono similar al 8,99 % de train_v2 como criterio de éxito: cambian fecha, población y construcción. Un porcentaje diferente no prueba un error ni valida el método. Tampoco es exactitud de un modelo.

## 6. Ejecutar y revisar

Desde la raíz:

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\06_etiquetar_piloto.py"
```

Comparte el resumen completo, incluidos los casos ilustrativos. Si aparece FileExistsError, conserva la salida anterior y avisa; no sobrescribas sin revisar. Una interrupción al escribir puede dejar un CSV parcial.

Esperamos procesar 7.443 candidatos y que los conteos cuadren. No conocemos todavía cuántos serán 0 o 1. El calendario permite seguimiento suficiente para los vencimientos previstos, pero el supuesto de cobertura permanece. La salida debe revisarse antes de entrenar. Posteriormente auditaremos ejemplos reales localmente sin publicar identificadores y prepararemos características históricas.

## 7. Preguntas de comprensión

1. ¿Por qué renovar exactamente 30 días después produce etiqueta 1 según esta implementación?
2. ¿Por qué un gap negativo puede ser correcto?
3. ¿Por qué una cancelación no basta para asignar abandono?
4. ¿Qué diferencia hay entre no observar renovación con seguimiento suficiente y no observarla porque el archivo termina demasiado pronto?
5. ¿Por qué gap_dias y motivo no pueden entrar como características del modelo del 7 de marzo?

Responde con tus palabras al compartir la salida. Guardaremos las respuestas revisadas en el archivo de estudio.

