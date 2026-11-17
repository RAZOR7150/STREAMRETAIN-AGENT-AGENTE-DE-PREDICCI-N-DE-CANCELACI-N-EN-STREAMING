# StreamRetain-Agent — avance del hito 2

Autor: Levis Adrian Ortiz Cano. Proyecto individual de Inteligencia Artificial, Universidad Tecnológica de Bolívar.

Predicción de abandono de suscripciones KKBox. Estado: dos cohortes preparadas y **línea base temporal ejecutada por el estudiante**. Se preservan las guías de aprendizaje y bitácora. No hay todavía regresión logística, árbol entrenado, aplicación final ni prueba final evaluada.

## Resultado actual

Entrenamiento marzo: 7.443 usuarios, 1.095 abandonos. Validación junio: 7.210 usuarios, 411 abandonos. Corte de entrenamiento 2016-03-07, etiquetas observadas hasta 2016-05-05; validación al 2016-06-06, seguida hasta 2016-08-04. Usuarios compartidos: 5.875; no es un experimento exclusivo de usuarios nuevos.

La línea base `DummyClassifier(strategy="most_frequent", random_state=42)` aprende solo con marzo y predice 0 para todo junio.

| Métrica de validación | Resultado |
| --- | ---: |
| Exactitud | 0,942996 |
| Precisión de abandono | 0 |
| Sensibilidad de abandono | 0 |
| F1 de abandono | 0 |
| ROC-AUC | 0,5 |
| Average Precision (AP) | 0,057004 |

Matriz: `[[6799, 0], [411, 0]]`, filas reales y columnas predichas, orden [0,1]. La exactitud alta no implica detectar abandonos: no se detectó ninguno. Precisión sin positivos predichos se reporta como cero mediante zero_division=0. AP no es área trapezoidal PR-AUC. No se alcanzó la meta propuesta de F1 de abandono ≥0,50.

## Requisitos y datos

Windows, Python 3.11 (ejecución registrada con 3.11.16), PowerShell y `C:\Windows\System32\tar.exe` con soporte 7z. Dependencias fijadas en requirements.txt. En el equipo del estudiante se usa `C:\Users\HP\anaconda3\python.exe`; en los comandos siguientes `python` debe apuntar a ese entorno o a uno equivalente. Verificar el intérprete antes de ejecutar.

Consultar primero [data/README.md](data/README.md) y el script [data/descargar_datos.ps1](data/descargar_datos.ps1), con manifiesto y verificación SHA-256. Obtener [transactions.csv.7z de KKBox Churn](https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data) aceptando las reglas correspondientes, y colocar el comprimido en `data/kkbox-churn-prediction-challenge/transactions.csv.7z`. El miembro interno debe llamarse `transactions.csv`. No es el dataset de recomendación musical. No descomprimir masivamente. Los CSV brutos/derivados y temporales se excluyen de Git; el contexto documental se incluye por solicitud expresa del usuario; no redistribuirlos. Las guías documentan la fuente y extracción. El baseline no necesita los archivos gigantes de escucha.

## Reproducción en cuatro comandos

Ejecutar desde la raíz, en PowerShell. En un checkout limpio con el comprimido disponible, los comandos 1 y 2 preparan las cohortes. El comando 2 tarda: recorre el original una vez por cohorte. Las comprobaciones detienen errores. **El procesamiento y entrenamiento los ejecuta el estudiante/evaluador, no se han reejecutado por Codex.** Las métricas publicadas provienen de la ejecución del estudiante y fueron contrastadas con su JSON y huellas locales.

1. Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

2. Construir las dos cohortes con los scripts ya implementados:

```powershell
$pasos = @('04_piloto_temporal.py','05_candidatos_temporales.py','06_etiquetar_piloto.py','08_caracteristicas_historicas.py','09_piloto_junio.py','10_candidatos_junio.py','11_etiquetar_junio.py','13_caracteristicas_junio.py'); foreach ($paso in $pasos) { python (Join-Path 'scripts' $paso); if ($LASTEXITCODE -ne 0) { throw "Falló $paso; revisar sin sobrescribir resultados" } }
```

3. Conservar el JSON de referencia antes de una nueva corrida (el script usa modo x para impedir sobrescrituras):

```powershell
if (Test-Path -LiteralPath 'experiments/baseline_marzo_junio.json') { New-Item -ItemType Directory -Force 'experiments/historial' | Out-Null; Move-Item -LiteralPath 'experiments/baseline_marzo_junio.json' -Destination (Join-Path 'experiments/historial' ('baseline_referencia_' + [guid]::NewGuid().ToString('N') + '.json')) }
```

4. Entrenar y evaluar la línea base:

```powershell
python scripts/14_linea_base_temporal.py
```

Si las cohortes ya existen y corresponden a las huellas publicadas, omitir el comando 2. Sus scripts también usan modo x: si algún resultado intermedio existe, no borrarlo para forzar la ejecución; verificar si ya terminó ese paso y continuar con los siguientes o utilizar una copia limpia del proyecto. No mezclar archivos de distintos cortes ni quitar controles de tamaño. Las guías 06–16 explican cada paso y cómo revisar incidencias. Los scripts 07 y 12 generan informes para auditoría manual opcional, no alteran cohortes. Que el pipeline corra no reemplaza esa revisión.

Salida: `experiments/baseline_marzo_junio.json`, con métricas, versiones, semilla, tamaños y SHA-256 de ambos CSV. Comparar las huellas y métricas con la referencia conservada. No hay selección aleatoria por fila ni partición aleatoria del conjunto; la muestra de usuarios usa SHA-256 y el prefijo fijo streamretain-v1.

## Estructura y límites

- `Entregables/streamretain_hito2.pdf`: avance de una página.
- `docs/streamretain_hito2.md`: fuente editable.
- `scripts/`: código escrito/ejecutado por el estudiante siguiendo guías de IA.
- `experiments/baseline_marzo_junio.json`: evidencia de la primera evaluación.
- `docs/bitacora_ia.md`: responsabilidades y verificaciones.
- `docs/guias/`: explicaciones y ejercicios; no confundir guías con resultados ejecutados.
- `docs/protocolo_evaluacion_temporal.md`: definición temporal y plan posterior.

Se reconstruyen etiquetas adaptando el Scala de la fuente: primera renovación desde corte, vencimiento ajustado por cancelaciones previas, gap <30 para renovación y >=30 para abandono. Si no hay renovación, se exige plazo observado suficiente bajo el supuesto de cobertura del historial. No son las etiquetas oficiales train/train_v2. Las entradas usan historia anterior al corte y vencimiento conocido entonces; gap, motivo y renovación futura quedan fuera.

Auditoría guiada de marzo: nueve casos. Junio: dos casos de nueve revisados manualmente; siete pospuestos por petición del estudiante. Ambos cortes pasaron comprobaciones internas reportadas. La muestra aproximada del 1 % y la exigencia de historia en 90 días limitan la población, especialmente planes largos. Una separación temporal es solo el primer resultado, no validación cruzada completa. Diciembre sigue reservado. No se ha medido desempeño por subgrupos ni completado el análisis de errores de modelos.

## Repositorio remoto

[Repositorio del proyecto](https://github.com/RAZOR7150/STREAMRETAIN-AGENT-AGENTE-DE-PREDICCI-N-DE-CANCELACI-N-EN-STREAMING).

El usuario autorizó expresamente sincronizar el contenido local. Se publican código, documentación, contexto, entregables, métricas y la carpeta data con instrucciones de descarga y manifiesto. Se excluyen los datasets brutos/derivados, informes con eventos individuales, credenciales y temporales. Las exclusiones están en .gitignore; no añadir esos archivos con git add -f.
