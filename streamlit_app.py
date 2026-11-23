import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import joblib
import sklearn
import streamlit as st

st.set_page_config(page_title="StreamRetain", page_icon="🎵", layout="wide")
st.title("StreamRetain · Evaluación de riesgo de abandono")
st.write("Explora cómo un modelo histórico evalúa una suscripción a partir de sus transacciones.")
st.caption("Demostración con características calculadas antes del corte. Sin contacto real con clientes.")
raiz = Path(__file__).resolve().parent
carpeta = raiz / "experiments" / "prueba_final"
try:
    evidencia = json.loads((carpeta / "resultados.json").read_text(encoding="utf-8-sig"))
    ruta_modelo = carpeta / "modelo_agente.joblib"
    huella = hashlib.sha256(ruta_modelo.read_bytes()).hexdigest()
    if huella != evidencia["sha256_modelo_agente"]:
        raise ValueError("El modelo no coincide con su evidencia")
    if sklearn.__version__ != evidencia["sklearn"]:
        raise ValueError("La versión de scikit-learn no coincide")
    # Solo nuestro artefacto de confianza, nunca un archivo subido por un visitante.
    paquete = joblib.load(ruta_modelo)
    columnas = paquete["caracteristicas"]
    familia = evidencia["modelo_agente"]
    if (paquete["familia"] != familia or columnas != evidencia["caracteristicas"]
            or paquete["umbral"] != evidencia["modelos"][familia]["umbral"]
            or paquete["sha256_seleccion"] != evidencia["sha256_seleccion"]):
        raise ValueError("Contrato del modelo inconsistente")
except Exception as error:
    st.error(f"No se pudo cargar la versión evaluada: {error}")
    st.stop()

metricas = evidencia["modelos"][familia]["metricas"]
a, b, c = st.columns(3)
a.metric("F1 en prueba histórica", f"{metricas['f1_abandono']:.3f}")
b.metric("Abandonos detectados (recall)", f"{100 * metricas['recall_abandono']:.1f}%")
c.metric("Umbral fijo", f"{paquete['umbral']:.2f}")
st.warning("La versión evaluada no alcanzó la meta F1 ≥ 0,50. El puntaje no es una probabilidad calibrada.")

# Perfiles usados para demostrar comportamiento, no para una evaluación nueva.
perfiles = {
    "E01 · alerta incorrecta conocida": [2, 0, 0, 2, 34, 14],
    "E06 · abandono omitido conocido": [3, 1, 0, 3, 18, 12],
}
elegido = st.selectbox("Perfil inicial editable", list(perfiles))
st.caption("Los perfiles provienen de errores conocidos. Si cambias valores, no conocemos la etiqueta de tu escenario.")
etiquetas = [
    "Transacciones en 90 días", "Transacciones en 30 días", "Cancelaciones en 90 días",
    "Días distintos con transacciones en 90 días", "Días desde la última transacción",
    "Días hasta el vencimiento conocido",
]
minimos = [1, 0, 0, 1, 1, 0]
maximos = [None, None, None, 90, 90, 29]
with st.form("entrada"):
    valores = [int(st.number_input(nombre, min_value=minimo, max_value=maximo,
                                   value=valor, step=1))
               for nombre, minimo, maximo, valor in
               zip(etiquetas, minimos, maximos, perfiles[elegido])]
    evaluar = st.form_submit_button("Evaluar suscripción")

if "historial" not in st.session_state:
    st.session_state.historial = []

if evaluar:
    n90, n30, cancelaciones, dias, reciente, restantes = valores
    valido = (n90 >= 1 and 0 <= n30 <= n90 and 0 <= cancelaciones <= n90
              and 1 <= dias <= min(90, n90) and 1 <= reciente <= 90 and 0 <= restantes <= 29)
    coherente = (reciente <= 30 and n30 > 0) or (reciente > 30 and n30 == 0)
    if not valido or not coherente:
        st.error("Revisa los conteos: días y cancelaciones no pueden superar transacciones; la recencia debe concordar con el conteo de30 días.")
    else:
        modelo = paquete["modelo"]
        indice = list(modelo.classes_).index(1)
        puntaje = float(modelo.predict_proba([valores])[0, indice])
        alerta = puntaje >= paquete["umbral"]
        recomendacion = (
            "Revisión humana sugerida: comprobar situación y pertinencia de una acción de retención."
            if alerta else "Sin alerta por el umbral actual; mantener seguimiento, sin garantizar renovación."
        )
        # Son condiciones reales del árbol, no causas del comportamiento del cliente.
        arbol, nodo, recorrido = modelo.tree_, 0, []
        while arbol.children_left[nodo] != arbol.children_right[nodo]:
            j = int(arbol.feature[nodo])
            limite = float(arbol.threshold[nodo])
            izquierda = valores[j] <= limite
            recorrido.append({"variable": columnas[j], "valor": valores[j],
                              "condicion": "<=" if izquierda else ">", "limite": limite})
            nodo = int(arbol.children_left[nodo] if izquierda else arbol.children_right[nodo])
        decision = {
            "id": str(uuid4()), "fecha_utc": datetime.now(timezone.utc).isoformat(),
            "modo": "simulacion_web", "version": "v1", "sha256_modelo": huella,
            "caracteristicas": dict(zip(columnas, valores)),
            "puntaje_no_calibrado": puntaje, "umbral": paquete["umbral"],
            "alerta": bool(alerta), "recomendacion": recomendacion, "recorrido": recorrido,
        }
        st.session_state.historial.append(decision)
        st.session_state.historial = st.session_state.historial[-20:]
        st.metric("Puntaje de esta evaluación", f"{puntaje:.4f}")
        if alerta:
            st.warning(recomendacion)
        else:
            st.info(recomendacion)
        st.write("Recorrido de decisión")
        st.dataframe(recorrido, hide_index=True)

with st.expander("Historial de esta sesión y descarga"):
    st.caption("Se conservan las últimas20 evaluaciones en esta sesión. No es una base de datos permanente ni un historial compartido entre visitantes.")
    st.json(st.session_state.historial)
    st.download_button("Descargar historial JSON",
                       json.dumps(st.session_state.historial, ensure_ascii=False, indent=2),
                       file_name="streamretain_decisiones.json", mime="application/json")

with st.expander("Cómo se evaluó y qué límites tiene"):
    st.write("Entrenamiento: marzo, junio y septiembre de2016. Prueba: diciembre de2016. Selección previa con dos rondas temporales.")
    st.write("Etiquetas reconstruidas bajo supuesto de cobertura. Los usuarios pueden repetirse entre periodos.")
    st.write("En la prueba, el grupo con última transacción hace30 días o más tuvo recall de10,40 %. Este análisis es exploratorio.")
    st.write("Ventana de candidatos: vencimiento conocido entre0 y29 días; no renovación oportuna definida con gap>=30 días. No equivale a predecir exactamente28 días.")
    st.write("La interfaz no calcula características desde transacciones, no reentrena ni prueba la eficacia de una campaña de retención.")
    st.json(metricas)
