# Guía 18 — Preparar septiembre y diciembre en una sola pasada

## Objetivo y protección de la prueba final

Mantendremos las mismas reglas y seis características. Septiembre será la segunda validación; diciembre queda reservado para una evaluación final, después de congelar modelo y umbral. Construir sus etiquetas con reglas ya fijadas no es entrenar ni evaluar un modelo. No inspecciones su distribución ni sus casos para elegir hiperparámetros.

Para acelerar, unificaremos operaciones ya conocidas en un programa. Primero comprobará que reconstruye exactamente las cohortes de marzo/junio que ya existen. Solo si coinciden guardará las dos nuevas. No cambia las cohortes anteriores ni entrena modelos.

Crea `scripts/16_preparar_cohortes_finales.py`. Escribe los siguientes bloques en orden.

## 1. Preparación y funciones conocidas

```python
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from datetime import date, timedelta
from functools import cmp_to_key
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data" / "derived"
comprimido = raiz / "data" / "kkbox-churn-prediction-challenge" / "transactions.csv.7z"
tar = Path(r"C:\Windows\System32\tar.exe")
cortes = [date(2016, 3, 7), date(2016, 6, 6), date(2016, 9, 5), date(2016, 12, 5)]
columnas_x = ["transacciones_90d", "transacciones_30d", "cancelaciones_90d",
              "dias_con_transacciones_90d", "dias_desde_ultima_transaccion",
              "dias_hasta_vencimiento"]
columnas = ["msno", "corte", *columnas_x, "is_churn"]
```

Copia aquí únicamente estas cuatro funciones completas de tus programas anteriores:

- `incluir_usuario`, de `04_piloto_temporal.py`.
- `leer_fecha`, `comparar_eventos` y `etiquetar`, de `06_etiquetar_piloto.py`.

No importes los scripts completos: se ejecutarían. No copies variables globales, lecturas, casos o escrituras de esos archivos. Las funciones conservan SHA-256, prefijo streamretain-v1 y regla gap <30. Esta reutilización mantiene el método, no constituye una prueba independiente del etiquetado.

## 2. Una función para construir cada cohorte

```python
def construir_cohorte(eventos_por_usuario, corte):
    inicio = corte - timedelta(days=90)
    inicio_30 = corte - timedelta(days=30)
    ultimo_vencimiento = corte + timedelta(days=29)
    fin = ultimo_vencimiento + timedelta(days=30)
    filas, auditoria = [], []
    for usuario in sorted(eventos_por_usuario):
        eventos = eventos_por_usuario[usuario]
        # Solo esta lista aporta información a candidatos y características.
        historia = [e for e in eventos if inicio <= e["fecha"] < corte]
        if not historia:
            continue
        ultimo = sorted(historia, key=cmp_to_key(comparar_eventos))[-1]
        vence = ultimo["vencimiento"]
        if not corte <= vence <= ultimo_vencimiento:
            continue
        seguimiento = [e for e in eventos if corte <= e["fecha"] <= fin]
        etiqueta = etiquetar(vence, seguimiento, fin)
        if etiqueta["is_churn"] not in (0, 1):
            raise ValueError("Candidato sin seguimiento suficiente; revisar sin descartarlo")
        fila = {
            "msno": usuario, "corte": corte.isoformat(),
            "transacciones_90d": len(historia),
            "transacciones_30d": sum(e["fecha"] >= inicio_30 for e in historia),
            "cancelaciones_90d": sum(e["cancelacion"] == "1" for e in historia),
            "dias_con_transacciones_90d": len({e["fecha"] for e in historia}),
            "dias_desde_ultima_transaccion": (corte - ultimo["fecha"]).days,
            "dias_hasta_vencimiento": (vence - corte).days,
            "is_churn": etiqueta["is_churn"],
        }
        filas.append(fila)
        auditoria.append({
            "msno": usuario, "corte": corte.isoformat(),
            "vencimiento_conocido": vence.isoformat(),
            "observado_hasta": fin.isoformat(),
            "supuesto_cobertura": "historial_publicado_completo_en_ventana",
            **etiqueta,
        })
    if not filas:
        raise ValueError(f"Cohorte vacía: {corte}")
    return filas, auditoria
```

La lista historia selecciona eventos anteriores al corte; seguimiento solo produce y y campos de auditoría. Los 90 días, los 30 de actividad reciente, el vencimiento y sus desempates son idénticos a lo ya aplicado. Los nombres/orden de características se conservan. No agrupamos por mes ni exigimos actividad futura.

## 3. Comprobar salidas y leer el original una vez

```python
carpeta.mkdir(parents=True, exist_ok=True)
resumen_ruta = carpeta / "preparacion_cohortes_finales.json"
# Comprobar antes del recorrido largo para no perder tiempo ni sobrescribir evidencia.
salidas_previstas = [resumen_ruta]
for corte in cortes[2:]:
    salidas_previstas.extend([
        carpeta / f"cohorte_{corte}.csv",
        carpeta / f"etiquetas_piloto_{corte}.csv",
    ])
if any(p.exists() for p in salidas_previstas):
    raise FileExistsError("Ya existe alguna salida prevista; revisar antes de repetir")
for p in [tar, comprimido, carpeta / "cohorte_2016-03-07.csv", carpeta / "cohorte_2016-06-06.csv"]:
    if not p.is_file():
        raise FileNotFoundError(p)

inicio_global = min(cortes) - timedelta(days=90)
fin_global = max(cortes) + timedelta(days=59)
eventos_por_usuario = defaultdict(list)
leidas, conservadas = 0, 0
proceso = subprocess.Popen(
    [str(tar), "-xOf", str(comprimido), "transactions.csv"],
    stdout=subprocess.PIPE, text=True, encoding="utf-8-sig",
)
try:
    lector = csv.DictReader(proceso.stdout)
    requeridos = {"msno", "transaction_date", "membership_expire_date", "is_cancel",
                  "plan_list_price", "payment_plan_days", "payment_method_id"}
    if not lector.fieldnames or not requeridos.issubset(lector.fieldnames):
        raise ValueError("Cabecera inesperada")
    if len(set(lector.fieldnames)) != len(lector.fieldnames):
        raise ValueError("Cabecera con columnas repetidas")
    for fila in lector:
        leidas += 1
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError("Fila mal formada")
        fecha = leer_fecha(fila["transaction_date"])
        if not inicio_global <= fecha <= fin_global:
            continue
        usuario = fila["msno"].strip()
        if not usuario:
            raise ValueError("Usuario vacío")
        if not incluir_usuario(usuario):
            continue
        cancelacion = fila["is_cancel"].strip()
        plan = [fila[c] for c in ("plan_list_price", "payment_plan_days", "payment_method_id")]
        if cancelacion not in {"0", "1"} or any(not x.strip() for x in plan):
            raise ValueError("Evento seleccionado inválido")
        eventos_por_usuario[usuario].append({
            "fecha": fecha, "vencimiento": leer_fecha(fila["membership_expire_date"]),
            "cancelacion": cancelacion, "firma": "".join(plan),
        })
        conservadas += 1
        # Un límite operativo evita un crecimiento inesperado de memoria.
        if conservadas > 500000:
            raise RuntimeError("Muestra inesperadamente grande; revisar antes de continuar")
    codigo = proceso.wait()
    if codigo != 0:
        raise RuntimeError(f"tar terminó con código {codigo}")
finally:
    proceso.stdout.close()
    if proceso.poll() is None:
        proceso.terminate()
    proceso.wait()
if leidas != 21547746:
    raise ValueError("No coincide el total del archivo original auditado")
print("Filas originales recorridas:", leidas)
print("Eventos de la muestra conservados:", conservadas)
```

La lectura del original sigue siendo progresiva. Ahora sí almacenamos en memoria los eventos de la muestra para repartirlos entre cuatro cortes. No cargamos todos los usuarios del original. El límite de 500.000 eventos es una protección operativa, no un tamaño al que recortar la muestra; si se alcanza, se detiene para revisión. No se guarda el CSV original descomprimido.

## 4. Verificar equivalencia de marzo/junio antes de crear lo nuevo

```python
for corte in cortes[:2]:
    reconstruida, _ = construir_cohorte(eventos_por_usuario, corte)
    # csv.DictReader devuelve texto: normalizamos la reconstrucción a texto también.
    actual = {f["msno"]: {k: str(v) for k, v in f.items()} for f in reconstruida}
    referencia = {}
    with (carpeta / f"cohorte_{corte}.csv").open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != columnas:
            raise ValueError("Esquema de referencia distinto")
        for fila in lector:
            if None in fila or any(v is None for v in fila.values()):
                raise ValueError("Referencia mal formada")
            if fila["msno"] in referencia:
                raise ValueError("Usuario repetido en referencia")
            referencia[fila["msno"]] = fila
    if actual != referencia:
        faltantes = len(set(referencia) - set(actual))
        adicionales = len(set(actual) - set(referencia))
        distintos = sum(actual[u] != referencia[u] for u in set(actual) & set(referencia))
        raise ValueError(f"No coincide {corte}: faltantes={faltantes}, adicionales={adicionales}, distintos={distintos}")
    print("Equivalencia exacta de valores verificada:", corte, "filas:", len(actual))
```

Este control compara cada usuario, seis características y etiqueta, independientemente del orden de filas. No solo compara promedios. Si falla, no se debe aceptar septiembre/diciembre ni quitar el control: revisaremos la implementación unificada. Que coincida verifica equivalencia con el procedimiento anterior, no corrige automáticamente sus supuestos sobre cobertura.

## 5. Guardar cohortes nuevas sin seleccionar modelos con diciembre

```python
resumen = {
    "fuente": "transactions.csv.7z", "filas_originales": leidas,
    "regla_muestra": "sha256(streamretain-v1:msno), primeros 8 bytes modulo 100 = 0",
    "equivalencia_marzo_junio": True,
    "cohortes": [],
}
for corte in cortes[2:]:
    filas, auditoria = construir_cohorte(eventos_por_usuario, corte)
    archivo_cohorte = carpeta / f"cohorte_{corte}.csv"
    archivo_auditoria = carpeta / f"etiquetas_piloto_{corte}.csv"
    with archivo_cohorte.open("x", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)
    with archivo_auditoria.open("x", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(auditoria[0]))
        escritor.writeheader()
        escritor.writerows(auditoria)
    resumen["cohortes"].append({
        "corte": corte.isoformat(),
        "historia_desde": (corte - timedelta(days=90)).isoformat(),
        "seguimiento_hasta": (corte + timedelta(days=59)).isoformat(),
        "filas": len(filas),
        "sha256": hashlib.sha256(archivo_cohorte.read_bytes()).hexdigest(),
        "uso": "validacion_2" if corte.month == 9 else "prueba_final_reservada",
    })
    print("Cohorte preparada:", corte, "filas:", len(filas))
    print("Seguimiento hasta:", corte + timedelta(days=59))
with resumen_ruta.open("x", encoding="utf-8") as archivo:
    json.dump(resumen, archivo, ensure_ascii=False, indent=2)
    archivo.write("\n")
print("Manifiesto:", resumen_ruta)
print("Diciembre reservado: no inspeccionar sus resultados para ajustar el modelo.")
```

No se imprimen distribuciones de clases ni se evalúa diciembre. Se generan ambos archivos con reglas previamente definidas. La selección posterior utilizará junio y septiembre; el resultado final se medirá en diciembre después de congelar modelo/umbral. Si el programa se interrumpe al escribir, las salidas pueden quedar parciales: comparte el error antes de repetir o borrar nada.

## Ejecutar y compartir

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\16_preparar_cohortes_finales.py"
```

Comparte la salida completa, incluidas las dos comprobaciones de equivalencia. No conocemos aún los tamaños de septiembre/diciembre. No hace falta otro cuestionario antes de ejecutar.

Después aplicaremos la misma rejilla de la guía 17 en la segunda ronda (marzo+junio -> septiembre), combinaremos evidencia de ambas validaciones para congelar la decisión y evaluaremos diciembre una vez. No repetiremos la comparación de junio ni modificaremos sus resultados ya obtenidos.
