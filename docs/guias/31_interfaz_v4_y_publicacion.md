# Guía 31 — Alinear la interfaz con V4 y preparar su publicación

## Objetivo

La app existente todavía usaV1. Adaptaremos ese archivo, conservando su formulario, recorrido del árbol e historial. No se entrena ni se calcula de nuevo la evaluación. Se reutilizan las utilidades de streamretain.comun. Esta guía queda para implementación/ejecución del estudiante; no se publicó ni modificó la app automáticamente.

## 1. Carga y contrato de V4

Añade a las importaciones de streamlit_app.py:

```python
import math
from streamretain.comun import leer_json, huella as calcular_huella
```

Conserva la asignación de raiz. Reemplaza desde la asignación de carpeta hasta el final de except (incluido st.stop) por:

```python
carpeta = raiz / "experiments" / "modelo_v4"
try:
    evidencia = leer_json(carpeta / "evaluacion_diciembre.json")
    seleccion = leer_json(carpeta / "seleccion.json")
    ruta_modelo = carpeta / "modelo_agente.joblib"
    huella = calcular_huella(ruta_modelo)
    if (huella != evidencia["sha256_modelo"]
            or calcular_huella(carpeta / "seleccion.json") != evidencia["sha256_seleccion"]):
        raise ValueError("El modelo o su selección no coinciden con la evaluación")
    if sklearn.__version__ != evidencia["sklearn"]:
        raise ValueError("La versión de scikit-learn no coincide")
    paquete = joblib.load(ruta_modelo)
    columnas = paquete["caracteristicas"]
    familia = paquete["familia"]
    if (paquete["version"] != "v4" or familia != "arbol" or len(columnas) != 10
            or columnas != evidencia["caracteristicas"]
            or paquete["parametros"] != evidencia["parametros"]
            or paquete["umbral"] != evidencia["umbral"]
            or paquete["sha256_seleccion"] != evidencia["sha256_seleccion"]):
        raise ValueError("Contrato V4 inconsistente")
except Exception as error:
    st.error(f"No se pudo cargar V4: {error}")
    st.stop()
```

Cambia la asignación de metricas por `metricas = evidencia["metricas_v4"]`. Cambia el título de la métrica F1 a “F1 exploratorio · diciembre”. Conserva la advertencia de meta no alcanzada y añade “Diciembre ya fue observado durante el desarrollo; no es una nueva prueba independiente.”

## 2. Diez entradas y perfiles ilustrativos

Reemplaza desde perfiles hasta el final del formulario por este bloque. Los perfiles son simulaciones sin etiqueta conocida. No los llames falsos positivos/negativos ni asegures qué alerta darán antes de ejecutarlos.

```python
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
        )
        valores.append(int(valor) if i < 6 else float(valor))
    evaluar = st.form_submit_button("Evaluar suscripción")
```

No conviertas las cuatro medias a enteros. No se ofrece un control para ajustar el umbral: se conserva0,30.

## 3. Validación y registro

Dentro de if evaluar cambia `n90, n30, cancelaciones, dias, reciente, restantes = valores` para usar `valores[:6]`. Conserva los controles valido y coherente de las seis variables; añade:

```python
    nuevas_validas = (all(math.isfinite(v) for v in valores)
                      and valores[6] >= 0 and 0 <= valores[9] <= 1)
```

Cambia `if not valido or not coherente:` por `if not valido or not coherente or not nuevas_validas:`. Conserva el resto de la predicción y el recorrido: ya utilizan la lista de columnas del paquete y admiten diez entradas.

En el diccionario decision cambia `"version": "v1"` por `"version": "v4"`.

Para separar el historial anterior del nuevo, sustituye en todo el archivo el nombre de estado `historial` por `historial_v4` solo en las referencias a `st.session_state` y en su comprobación de existencia. Las etiquetas visibles “Historial” pueden permanecer. No se necesitan datos personales.

## 4. Corregir el texto de resultados y límites

En el bloque “Cómo se evaluó…”:

- Especifica entrenamiento marzo/junio/septiembre y **evaluación exploratoriaV4 en diciembre**.
- Elimina la cifra de recall10,40% del grupo de recencia>=30: pertenece al análisisV1. No se ha calculado aquí paraV4.
- Conserva etiquetas reconstruidas, usuarios repetidos, puntaje no calibrado y ausencia de campañas reales.
- Presenta diez características y no “seis”. No prometas integración actual con KKBox.
- Mantén F1diciembre0,4205 y advertencia de meta0,50 no alcanzada.

## 5. Ejecutar y comprobar localmente

```powershell
& ".\.venv\Scripts\python.exe" -m streamlit run streamlit_app.py
```

Comprobar:

1. Se ven10campos; F1exploratorio0,421,recall39,0% y umbral0,30 (redondeos de pantalla).
2. Los escenarios pueden evaluarse y producen recorrido, recomendación y registroV4. No presuponer su clase.
3. Una entrada con transacciones30d mayores que90d se rechaza sin añadir historial.
4. El JSON descargado identificaV4 y la huella8a9c3cc742bd1d240e400ec893243f686881c58a267ec9953ee560d5b931b6c3.

Comparte los resultados de ambos escenarios. Con ellos elegiremos casos de demostración sin inventar predicciones.

## 6. Publicar para el profesor, después de verificar la app

La gestión de Git sigue a cargo del estudiante. Archivos necesarios en el repositorio:

- streamlit_app.py y requirements.txt.
- streamretain/__init__.py y streamretain/comun.py.
- experiments/modelo_v4/modelo_agente.joblib, seleccion.json y evaluacion_diciembre.json.

No hacen falta comprimidos ni CSV de usuarios para inferencia. No publicar .venv ni credenciales.

En Streamlit Community Cloud: Create app -> seleccionar repositorio/rama/streamlit_app.py -> Advanced settings -> Python3.11 -> Deploy. La versión de scikit-learn debe coincidir con la del modelo; comparte errores de instalación antes de cambiarla. Tras obtener la URL, probarla en una ventana privada y comprobar que el profesor tiene acceso. La URL solo se añade a diapositivas/guion cuando funcione.

Fuente oficial consultada26nov2026: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

No hay todavía enlace publicado. Una grabación local sirve como ensayo, pero no sustituye el acceso público solicitado.
