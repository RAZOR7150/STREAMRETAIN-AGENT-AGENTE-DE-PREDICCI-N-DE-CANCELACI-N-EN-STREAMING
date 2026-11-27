import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import joblib
import sklearn
import streamlit as st

from streamretain.comun import leer_json, huella as calcular_huella


st.set_page_config(page_title="StreamRetain", page_icon="🎵", layout="wide")
st.title("StreamRetain · Evaluación de riesgo de abandono")
st.write("Explora cómo un modelo histórico evalúa una suscripción a partir de sus transacciones.")
st.caption("Versión V4 · Diez características históricas · Sin contacto real con clientes.")

raiz = Path(__file__).resolve().parent
carpeta = raiz / "experiments" / "modelo_v4"
try:
    evidencia = leer_json(carpeta / "evaluacion_diciembre.json")
    seleccion = leer_json(carpeta / "seleccion.json")
    ruta_modelo = carpeta / "modelo_agente.joblib"
    huella = calcular_huella(ruta_modelo)
    # Comprobamos que usamos el artefacto y la selección que se evaluaron.
    # Git puede convertir CRLF (Windows) en LF (Linux). Comparamos los
    # mismos bytes con ambas convenciones, sin ignorar cambios de contenido.
    seleccion_bytes = (carpeta / "seleccion.json").read_bytes()
    seleccion_lf = seleccion_bytes.replace(b"\r\n", b"\n")
    huellas_seleccion = {
        hashlib.sha256(contenido).hexdigest()
        for contenido in (seleccion_bytes, seleccion_lf,
                          seleccion_lf.replace(b"\n", b"\r\n"))
    }
    if huella != evidencia["sha256_modelo"]:
        raise ValueError("El archivo del modelo no coincide con la evaluación")
    if evidencia["sha256_seleccion"] not in huellas_seleccion:
        raise ValueError("El contenido de seleccion.json no coincide con la evaluación")
    if sklearn.__version__ != evidencia["sklearn"]:
        raise ValueError("La versión de scikit-learn no coincide")
    # Se carga exclusivamente nuestro artefacto local de confianza.
    paquete = joblib.load(ruta_modelo)
    columnas = paquete["caracteristicas"]
    familia = paquete["familia"]
    if (paquete["version"] != "v4" or familia != "arbol" or len(columnas) != 10
            or columnas != evidencia["caracteristicas"]
            or columnas != seleccion["caracteristicas"]
            or paquete["parametros"] != evidencia["parametros"]
            or paquete["parametros"] != seleccion["parametros"]
            or paquete["umbral"] != evidencia["umbral"]
            or paquete["umbral"] != seleccion["umbral"]
            or paquete["sha256_seleccion"] != evidencia["sha256_seleccion"]
            or paquete["modelo"].n_features_in_ != 10):
        raise ValueError("Contrato V4 inconsistente")
    metricas = evidencia["metricas_v4"]
except Exception as error:
    st.error(f"No se pudo cargar V4: {error}")
    st.stop()

a, b, c = st.columns(3)
a.metric("F1 exploratorio · diciembre", f"{metricas['f1_abandono']:.3f}")
b.metric("Abandonos detectados (recall)", f"{100 * metricas['recall_abandono']:.1f}%")
c.metric("Umbral fijo", f"{paquete['umbral']:.2f}")
st.warning("La versión evaluada no alcanzó la meta F1 ≥ 0,50. El puntaje no es una probabilidad calibrada.")
st.caption("Diciembre ya fue observado durante el desarrollo; esta comparación no es una nueva prueba independiente.")

# Escenarios simulados: no tienen una etiqueta real de abandono conocida.
perfiles = {
    "Escenario A · editable": [2, 0, 0, 2, 34, 14, 30.0, 149.0, 149.0, 1.0],
    "Escenario B · editable": [3, 1, 0, 3, 18, 12, 30.0, 149.0, 149.0, 0.0],
}
elegido = st.selectbox("Perfil inicial", list(perfiles))
st.caption("Escenarios ilustrativos sin resultado real conocido. Las medias se calculan sobre registros de los 90 días anteriores al corte.")
etiquetas = [
    "Transacciones en 90 días", "Transacciones en 30 días", "Cancelaciones en 90 días",
    "Días distintos con transacciones en 90 días", "Días desde la última transacción",
    "Días hasta el vencimiento conocido", "Duración media registrada del plan (días)",
    "Precio de lista medio registrado", "Importe pagado medio registrado",
    "Proporción histórica de autorrenovación (0 a 1)",
]
minimos = [1, 0, 0, 1, 1, 0, 0.0, None, None, 0.0]
maximos = [None, None, None, 90, 90, 29, None, None, None, 1.0]
with st.form("entrada_v4"):
    valores = []
    for i, nombre in enumerate(etiquetas):
        valor = st.number_input(
            nombre, min_value=minimos[i], max_value=maximos[i],
            value=perfiles[elegido][i], step=1 if i < 6 else 0.1,
            key=f"v4_{elegido}_{columnas[i]}",
        )
        # Conservamos decimales en las medias y la proporción.
        valores.append(int(valor) if i < 6 else float(valor))
    evaluar = st.form_submit_button("Evaluar suscripción")

# La memoria V4 se mantiene separada de sesiones anteriores de V1.
if "historial_v4" not in st.session_state:
    st.session_state.historial_v4 = []

if evaluar:
    n90, n30, cancelaciones, dias, reciente, restantes = valores[:6]
    valido = (n90 >= 1 and 0 <= n30 <= n90 and 0 <= cancelaciones <= n90
              and 1 <= dias <= min(90, n90) and 1 <= reciente <= 90 and 0 <= restantes <= 29)
    coherente = (reciente <= 30 and n30 > 0) or (reciente > 30 and n30 == 0)
    nuevas_validas = (all(math.isfinite(v) for v in valores)
                      and valores[6] >= 0 and 0 <= valores[9] <= 1)
    if not valido or not coherente or not nuevas_validas:
        st.error("Revisa los conteos y la recencia, la duración no negativa y la proporción de autorrenovación entre 0 y 1. No se registró una decisión.")
    else:
        modelo = paquete["modelo"]
        indice = list(modelo.classes_).index(1)
        puntaje = float(modelo.predict_proba([valores])[0, indice])
        alerta = puntaje >= paquete["umbral"]
        recomendacion = (
            "Revisión humana sugerida: comprobar situación y pertinencia de una acción de retención."
            if alerta else "Sin alerta por el umbral actual; mantener seguimiento, sin garantizar renovación."
        )
        # El recorrido describe reglas del árbol, no causas del abandono.
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
            "modo": "simulacion_web", "version": "v4", "sha256_modelo": huella,
            "caracteristicas": dict(zip(columnas, valores)),
            "puntaje_no_calibrado": puntaje, "umbral": paquete["umbral"],
            "alerta": bool(alerta), "recomendacion": recomendacion, "recorrido": recorrido,
        }
        st.session_state.historial_v4.append(decision)
        st.session_state.historial_v4 = st.session_state.historial_v4[-20:]
        st.metric("Puntaje de esta evaluación", f"{puntaje:.4f}")
        if alerta:
            st.warning(recomendacion)
        else:
            st.info(recomendacion)
        st.write("Recorrido de decisión")
        # Tabla Markdown: no requiere conversion a Arrow ni cambiar NumPy del modelo.
        tabla = ["| Variable | Valor | Condicion | Limite |",
                 "| --- | ---: | :---: | ---: |"]
        tabla.extend(
            f"| {paso['variable']} | {paso['valor']:g} | {paso['condicion']} | {paso['limite']:g} |"
            for paso in recorrido
        )
        st.markdown("\n".join(tabla))

with st.expander("Historial de esta sesión y descarga"):
    st.caption("Se conservan las últimas 20 evaluaciones en esta sesión. No es una base de datos permanente ni un historial compartido entre visitantes.")
    st.json(st.session_state.historial_v4)
    st.download_button("Descargar historial JSON",
                       json.dumps(st.session_state.historial_v4, ensure_ascii=False, indent=2),
                       file_name="streamretain_decisiones_v4.json", mime="application/json")

with st.expander("Cómo se evaluó y qué límites tiene"):
    st.write("V4 se entrenó con marzo, junio y septiembre de 2016. Diciembre se reutilizó como evaluación exploratoria después de observar los resultados de V1.")
    st.write("Etiquetas reconstruidas bajo supuesto de cobertura. Los usuarios pueden repetirse entre periodos.")
    st.write("Las diez características incluyen seis conteos o tiempos históricos y cuatro estadísticas del plan. El análisis de subgrupos de V1 no se presenta como resultado de V4.")
    st.write("Ventana de candidatos: vencimiento conocido entre 0 y 29 días; una renovación con gap ≥ 30 días se considera tardía. No equivale a predecir exactamente 28 días.")
    st.write("La interfaz no calcula características desde transacciones, no reentrena ni prueba la eficacia de una campaña de retención.")
    st.json(metricas)
