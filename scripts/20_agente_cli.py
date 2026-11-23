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
