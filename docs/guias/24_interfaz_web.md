# Guía 24 — Interfaz web local y publicable con Streamlit

## Qué construiremos

Una página donde el profesor selecciona un perfil ilustrativo o modifica seis características, pulsa Evaluar y ve puntaje, alerta, recomendación, recorrido del árbol y limitaciones. Tendrá un historial de las últimas20 evaluaciones de su sesión y descarga JSON. Funciona con el paquete versión1 ya evaluado; la búsqueda versión2 no lo reemplaza automáticamente.

La app realiza inferencia, no entrenamiento. No necesita los datasets de KKBox: solo código, dependencias, modelo y resultados agregados. El archivo modelo_agente.joblib actual ocupa6459 bytes. La interfaz recibe características previamente calculadas, no extrae por sí sola datos de usuarios reales. No es un chatbot ni necesita una API de lenguaje.

Streamlit permite formularios y despliegue mediante Community Cloud. n8n podría automatizar procesos después; no es necesario para esta interfaz. Si el profesor exige n8n, habría que añadir esa integración, no afirmar que Streamlit la reemplaza como requisito.

## 1. Crea streamlit_app.py en la raíz

No lo crees dentro de scripts: este programa usa su propia carpeta como raíz. El entorno .venv es soporte preparado por Codex. El código de la aplicación lo incorpora y ejecuta el estudiante.

```python
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
```

El formulario agrupa las modificaciones y solo envía una evaluación al pulsar el botón. La lista de columnas del paquete determina el orden de entrada. No pedimos nombres, correos ni identificadores reales. Son perfiles históricos o escenarios simulados: el prototipo no está validado para clientes actuales.

## 2. Agrega validación, inferencia y explicación

```python
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
```

La memoria de Streamlit es por sesión y temporal. Cambiar un campo o un perfil sin pulsar Evaluar no debe generar un registro nuevo. Una entrada rechazada tampoco añade decisiones.

## 3. Ejecutar localmente

Desde la raíz del proyecto:

```powershell
& ".\.venv\Scripts\python.exe" -m streamlit run streamlit_app.py
```

Abre la dirección local que indique la terminal, normalmente http://localhost:8501. Con los perfiles intactos debes reproducir0,9801388 y0,1265515, respectivamente. Verifica además una combinación incoherente (por ejemplo3 transacciones en90 días y4 en30): debe rechazarse sin añadir historial. Para detener el servidor usa Ctrl+C en su terminal.

## 4. Que el profesor acceda por enlace

Localhost solo sirve en tu equipo. Para un enlace accesible sin dejar tu PC encendido, publica la app en Streamlit Community Cloud desde GitHub. La gestión y subida de Git siguen a cargo del estudiante.

Archivos mínimos requeridos en el repositorio:

- streamlit_app.py en la raíz.
- requirements.txt con dependencias fijadas, incluido Streamlit.
- experiments/prueba_final/modelo_agente.joblib.
- experiments/prueba_final/resultados.json.

No hacen falta los CSV ni comprimidos para ejecutar esta app. No subas .venv ni historiales locales. Si deseas conservar el repositorio completo, la app seguirá usando solo estos archivos para la inferencia.

Pasos después de comprobar la versión local:

1. Sube los archivos mediante tu flujo de Git.
2. En Streamlit Community Cloud conecta tu cuenta GitHub y elige Create app.
3. Selecciona el repositorio, su rama y streamlit_app.py como archivo de entrada.
4. En opciones avanzadas selecciona Python3.11 para reproducir el entorno del modelo. Confirma que el servicio lo ofrece.
5. Despliega y comprueba el log de instalación. No cambies silenciosamente scikit-learn si falla una dependencia: comparte el error.
6. Prueba el enlace desde una ventana privada para comprobar qué acceso tendrá el profesor y repite ambos perfiles.

No hay todavía un enlace desplegado. Estos son los pasos para publicarlo cuando hayas implementado y probado la app. Si hay una incompatibilidad del alojamiento con las dependencias, se resolverá antes de afirmar que está publicado.

## Fuentes consultadas

- Formularios: https://docs.streamlit.io/develop/api-reference/execution-flow/st.form
- Despliegue: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

## Qué compartir

La salida de la búsqueda ampliada y el resultado de abrir la app local, incluyendo si reproduce ambos puntajes y rechaza entradas incoherentes. La app se puede preparar con versión1 mientras termina el experimento; no anuncia resultados de la versión2 ni los sustituye sin revisión.
