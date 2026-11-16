# Referencia técnica: entorno y comprimidos

**Actualización:** por aclaración del usuario, estas comprobaciones las realiza Codex. No son una tarea pendiente del estudiante ni hay que repetirlas para avanzar. Resultados en `docs/estado_entorno.md`. Los pasos siguientes se conservan únicamente como explicación de los comandos.

## Objetivo

Antes de escribir el cargador, comprobar dónde trabajamos, qué Python tenemos y cómo consultar los CSV internos sin extraerlos. Este ejercicio no entrena modelos ni procesa filas del dataset.

La ruta actual del proyecto es:

`D:\Users\Nelson\Desktop\RAZOR\Tareas\Sexto Semestre\Inteligencia Artificial\Proyecto Final`

## 1. Abre PowerShell y sitúate en el proyecto

Ejecuta estas instrucciones una por una. Las líneas que empiezan con `#` son comentarios explicativos y no ejecutan acciones.

```powershell
# Cambia la carpeta de trabajo de esta terminal.
# Las comillas permiten que la ruta contenga espacios.
# LiteralPath indica que la ruta se interpreta tal como está escrita.
Set-Location -LiteralPath 'D:\Users\Nelson\Desktop\RAZOR\Tareas\Sexto Semestre\Inteligencia Artificial\Proyecto Final'

# Muestra la carpeta actual: debe coincidir con la ruta anterior.
Get-Location

# Informa qué versión de Python ejecuta esta terminal.
python --version

# Muestra el ejecutable resuelto por PowerShell.
# El símbolo | entrega el resultado del primer comando al segundo.
# Select-Object limita lo mostrado a la propiedad Source.
Get-Command python | Select-Object Source
```

La versión y ruta dependen de tu entorno. No hay que suponer que la terminal del estudiante usa el mismo intérprete que las herramientas de Codex.

## 2. Lista los archivos comprimidos

```powershell
# Lee el directorio y selecciona archivos cuyos nombres terminan en .7z.
# Esta instrucción enumera archivos; no abre ni extrae sus datos.
# Length es el tamaño del archivo comprimido en bytes.
Get-ChildItem -LiteralPath 'data\kkbox-churn-prediction-challenge' -Filter '*.7z' |
    Select-Object Name, Length
```

La inspección anterior de Codex encontró nueve comprimidos. Si ahora aparecen más o menos, registraremos la diferencia antes de continuar.

## 3. Consulta el contenido de los archivos de etiquetas sin extraerlos

```powershell
# & ejecuta el programa ubicado en la ruta entre comillas.
# tar es la herramienta de archivos disponible en este Windows.
# -t lista el contenido; -v incluye detalles; -f indica el archivo que se abrirá.
# No usamos -x, que correspondería a extraer.
& 'C:\Windows\System32\tar.exe' -tvf 'data\kkbox-churn-prediction-challenge\train.csv.7z'

# Repite la consulta para la segunda versión de etiquetas.
& 'C:\Windows\System32\tar.exe' -tvf 'data\kkbox-churn-prediction-challenge\train_v2.csv.7z'
```

En la revisión anterior se observaron estos resultados, que puedes contrastar:

| Comprimido | Ruta del CSV dentro del comprimido | Tamaño interno declarado |
| --- | --- | ---: |
| train.csv.7z | train.csv | 46.667.771 bytes |
| train_v2.csv.7z | data/churn_comp_refresh/train_v2.csv | 45.635.134 bytes |

La ruta interna es importante: el archivo comprimido y su CSV no siempre están al mismo nivel. Este listado consulta metadatos; no garantiza que todo el archivo se descomprima sin errores.

## Qué debes comprender

- El tamaño de un .7z es distinto del tamaño del CSV que contiene.
- Listar el contenido no crea una copia descomprimida en el disco.
- La ruta interna de train_v2 no es simplemente train_v2.csv.
- Un CSV local de 0 bytes no contiene datos y no sustituye al archivo interno.
- Todavía no sabemos por estos comandos qué periodo representa cada etiqueta ni cuántos usuarios abandonan.

## Qué compartir para revisar el paso

Comparte la versión y ruta de Python, y la salida de los dos listados de etiquetas. No hace falta copiar registros de usuarios. Si aparece un error, comparte el mensaje exacto.

Con esos resultados prepararemos el siguiente ejercicio: leer la cabecera y contar etiquetas desde el comprimido de forma progresiva, explicando cómo se conecta el descompresor con Python. El código lo incorporarás y ejecutarás tú.
