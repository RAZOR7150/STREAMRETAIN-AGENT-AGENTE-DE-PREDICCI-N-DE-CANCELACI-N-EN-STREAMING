# Guía 22 — Demostración del agente local

## Objetivo

Crear un prototipo que perciba seis características históricas, consulte el árbol final, aplique el umbral congelado, recomiende una revisión humana y guarde una memoria de la decisión. No entrena, no cambia el umbral ni envía campañas reales. Es una demostración con características ya calculadas; la extracción desde transacciones sigue en los scripts anteriores y no está automatizada en esta interfaz.

La prueba final dio F1=0,3462, inferior a la meta0,50. El prototipo no debe ocultarlo ni presentar ausencia de alerta como garantía de renovación. Un puntaje tampoco es una probabilidad calibrada.

PEAS: desempeño medido por precisión/recall/F1 y limitaciones observadas; entorno de suscripciones históricas; actuadores de recomendación y registro local; sensores de las seis variables disponibles al corte. La memoria registra decisiones, no implica aprendizaje automático continuo.

## 1. Crea scripts/20_agente_cli.py

Usaremos argparse para recibir un archivo JSON, joblib para cargar nuestro propio modelo y hashlib para comprobar que es el artefacto evaluado. No importes los scripts de entrenamiento porque ejecutarían sus instrucciones superiores.

```python
import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4
import joblib
import sklearn

raiz = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description="StreamRetain: apoyo local a revisión de retención")
parser.add_argument("--entrada", required=True, type=Path, help="JSON con corte y características")
args = parser.parse_args()

ruta_resultados = raiz / "experiments" / "prueba_final" / "resultados.json"
ruta_modelo = raiz / "experiments" / "prueba_final" / "modelo_agente.joblib"
evidencia = json.loads(ruta_resultados.read_text(encoding="utf-8-sig"))
huella = hashlib.sha256(ruta_modelo.read_bytes()).hexdigest()
if huella != evidencia["sha256_modelo_agente"]:
    raise ValueError("El modelo no coincide con el evaluado")
if evidencia["sklearn"] != sklearn.__version__:
    raise ValueError("Usa el entorno registrado en la evaluación")
# Joblib se carga solo desde nuestro artefacto local de confianza.
paquete = joblib.load(ruta_modelo)
columnas = paquete["caracteristicas"]
familia = evidencia["modelo_agente"]
if (paquete["familia"] != familia or columnas != evidencia["caracteristicas"]
        or paquete["umbral"] != evidencia["modelos"][familia]["umbral"]
        or paquete["sha256_seleccion"] != evidencia["sha256_seleccion"]):
    raise ValueError("Contrato del modelo inconsistente")
```

La huella comprueba integridad respecto al JSON local; no hace seguro un archivo recibido de terceros ni valida que los datos de entrada sean verdaderos.

## 2. Validar la percepción

La entrada no acepta is_churn, gap, futuras renovaciones ni identificadores personales. Los valores deben calcularse con historia anterior al corte. No añadimos campos que el modelo nunca aprendió.

```python
entrada = json.loads(args.entrada.read_text(encoding="utf-8-sig"))
if not isinstance(entrada, dict) or set(entrada) != {"corte", "caracteristicas"}:
    raise ValueError("Se esperan solo corte y caracteristicas")
corte = date.fromisoformat(entrada["corte"])
x = entrada["caracteristicas"]
if not isinstance(x, dict) or set(x) != set(columnas):
    raise ValueError("Deben aparecer exactamente las seis características")
if any(type(x[c]) is not int for c in columnas):
    raise ValueError("Las características deben ser enteros, no texto ni booleanos")
# El orden se toma del contrato del modelo, no del orden del JSON.
valores = [x[c] for c in columnas]
n90, n30, cancelaciones, dias, reciente, restantes = valores
if not (n90 >= 1 and 0 <= n30 <= n90 and 0 <= cancelaciones <= n90
        and 1 <= dias <= min(90, n90) and 1 <= reciente <= 90
        and 0 <= restantes <= 29):
    raise ValueError("Valores fuera del dominio de la cohorte")
if (reciente <= 30 and n30 == 0) or (reciente > 30 and n30 > 0):
    raise ValueError("La recencia y el conteo de transacciones en 30 días no concuerdan")
# El prototipo reproduce el protocolo experimental de cortes en lunes.
if corte.weekday() != 0:
    raise ValueError("El protocolo usa cortes en lunes")
```

El rango de vencimiento aceptado es 0..29 días, conforme a las cohortes ejecutadas. No lo describas en la sustentación como si se hubiera evaluado exactamente un horizonte de28 días. Además, la etiqueta usa la tolerancia de renovación respecto al vencimiento: son conceptos distintos.

## 3. Decisión, explicación del recorrido y memoria

El árbol ofrece un recorrido de condiciones comprobables. Son reglas del modelo, no causas de abandono. La recomendación es una política de demostración, no una intervención cuya eficacia se haya probado.

```python
modelo = paquete["modelo"]
indice = list(modelo.classes_).index(1)
puntaje = float(modelo.predict_proba([valores])[0, indice])
umbral = float(paquete["umbral"])
alerta = puntaje >= umbral

# Recorremos las condiciones reales del árbol para esta entrada.
arbol = modelo.tree_
nodo = 0
recorrido = []
while arbol.children_left[nodo] != arbol.children_right[nodo]:
    j = int(arbol.feature[nodo])
    limite = float(arbol.threshold[nodo])
    izquierda = valores[j] <= limite
    recorrido.append({"caracteristica": columnas[j], "valor": valores[j],
                      "operador": "<=" if izquierda else ">", "limite": limite})
    nodo = int(arbol.children_left[nodo] if izquierda else arbol.children_right[nodo])

recomendacion = (
    "Revisión humana sugerida: comprobar situación y pertinencia de una acción de retención."
    if alerta else
    "Sin alerta por el umbral actual; mantener seguimiento, sin garantizar renovación."
)
salida = {
    "id_decision": str(uuid4()), "fecha_utc": datetime.now(timezone.utc).isoformat(),
    "corte": corte.isoformat(), "modo": "demostracion_local",
    "modelo": familia, "sha256_modelo": huella,
    "caracteristicas": x, "puntaje_no_calibrado": puntaje,
    "umbral": umbral, "alerta": alerta, "recorrido": recorrido,
    "recomendacion": recomendacion,
    "advertencias": [
        "No es una probabilidad calibrada ni una garantía de abandono o renovación",
        "Modelo histórico de KKBox; uso actual no validado",
        "F1 final 0.3462: meta 0.50 no alcanzada",
        "Registros locales; no se contacta a clientes",
    ],
}
# JSONL guarda una decisión por línea; conserva ejecuciones previas.
memoria = raiz / "data" / "derived" / "decisiones_demo.jsonl"
memoria.parent.mkdir(parents=True, exist_ok=True)
with memoria.open("a", encoding="utf-8") as archivo:
    archivo.write(json.dumps(salida, ensure_ascii=False, allow_nan=False) + "\n")
print(json.dumps(salida, ensure_ascii=False, indent=2, allow_nan=False))
print("Registro local:", memoria)
```

La memoria está en data/derived, excluida de Git. No requiere nombres de clientes. El algoritmo no llama a fit ni recibe etiquetas. Recibir una decisión no prueba que esa decisión sea acertada.

## 4. Preparar dos entradas y ejecutar

Crea `data/derived/demo_alerta.json` con este contenido. Es un perfil ilustrativo tomado de E01, un falso positivo conocido: la alerta no significa que realmente abandonó. No es una prueba independiente nueva.

```json
{
  "corte": "2016-12-05",
  "caracteristicas": {
    "transacciones_90d": 2,
    "transacciones_30d": 0,
    "cancelaciones_90d": 0,
    "dias_con_transacciones_90d": 2,
    "dias_desde_ultima_transaccion": 34,
    "dias_hasta_vencimiento": 14
  }
}
```

Crea `data/derived/demo_sin_alerta.json`. Reproduce las características de E06, un falso negativo conocido. Mostrar ambos es útil para explicar la diferencia entre decisión y acierto.

```json
{
  "corte": "2016-12-05",
  "caracteristicas": {
    "transacciones_90d": 3,
    "transacciones_30d": 1,
    "cancelaciones_90d": 0,
    "dias_con_transacciones_90d": 3,
    "dias_desde_ultima_transaccion": 18,
    "dias_hasta_vencimiento": 12
  }
}
```

Desde la raíz del proyecto, ejecuta cada comando por separado:

```powershell
python scripts/20_agente_cli.py --entrada data/derived/demo_alerta.json
python scripts/20_agente_cli.py --entrada data/derived/demo_sin_alerta.json
```

Esperamos aproximadamente0,9801 con alerta en el primero y0,1266 sin alerta en el segundo, según las predicciones que ya obtuviste. Comprueba que se muestran recorrido, recomendación, limitaciones y dos registros en la memoria. Comparte ambas salidas.

Como control de entrada, en una copia de un JSON cambia dias_hasta_vencimiento a30: debe rechazarlo sin añadir una decisión a memoria. Ese control verifica el contrato de la cohorte, no la calidad predictiva.

## Guion de demostración de cuatro minutos

1. Explicar que las características provienen de historia anterior al corte y el modelo fue elegido antes de diciembre.
2. Ejecutar ambos perfiles y mostrar puntaje, umbral, recorrido y recomendación.
3. Mostrar que el registro conserva ambas decisiones sin nombres ni campañas reales.
4. Aclarar que son errores conocidos usados para ilustrar límites. Presentar F1 final y el problema del grupo de recencia>=30 días. No afirmar que el modelo aprendió de esta ejecución.

Después de comprobar esta ejecución quedarán la preparación del informe final IEEE, presentación y verificación de entregables. Crear esta guía no equivale a tener la demo ya ejecutada.
