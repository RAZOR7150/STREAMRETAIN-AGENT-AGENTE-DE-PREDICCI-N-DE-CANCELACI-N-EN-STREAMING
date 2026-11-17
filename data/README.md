# Datos del proyecto y obtención reproducible

El requisito del curso permite `data/: datos o script de descarga`. Esta carpeta incluye instrucciones, descripción y un script de descarga. Los comprimidos de KKBox y las tablas derivadas se conservan localmente; no se redistribuyen aquí.

## Fuente y acceso

[KKBox Churn Prediction Challenge](https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data). Se necesita una cuenta con acceso y aceptar las [reglas de la competencia](https://www.kaggle.com/c/kkbox-churn-prediction-challenge/rules). Cada evaluador obtiene los datos con sus propias credenciales. No guardar tokens ni kaggle.json en el repositorio.

Para reproducir el hito 2 solo se necesita **transactions.csv.7z**, aproximadamente 707,5 MB comprimidos. No es necesario descargar user_logs.csv.7z ni descomprimir el historial completo. manifest.json contiene la ruta, tamaño y SHA-256 comprobados del archivo realmente utilizado.

## Descarga

1. Instalar la [CLI oficial de Kaggle](https://github.com/Kaggle/kaggle-cli): `python -m pip install kaggle`.
2. Autenticarse siguiendo sus instrucciones y aceptar las reglas de la competencia en Kaggle. El script no configura credenciales ni acepta reglas en tu nombre.
3. Desde la raíz del proyecto, ejecutar en PowerShell:

```powershell
& .\data\descargar_datos.ps1
```

El script descarga exclusivamente transactions.csv.7z si no existe y comprueba tamaño y huella. No sobrescribe una descarga existente ni la elimina si hay discrepancias. Sintaxis y verificación sobre el archivo local comprobadas; la descarga autenticada no se repitió porque el archivo ya está disponible. Si Kaggle entrega un formato distinto o niega acceso, revisar sus instrucciones en lugar de alterar el hash de referencia para forzar aceptación.

Alternativa manual: descargar ese archivo desde Kaggle y guardarlo en `data/kkbox-churn-prediction-challenge/transactions.csv.7z`. Después ejecutar el script para verificar la huella.

## Cohortes derivadas

Seguir los comandos del README raíz para construir los pilotos, candidatos, etiquetas y cohortes de marzo/junio, y ejecutar la línea base. Esos CSV incluyen identificadores y no se publican. Las huellas de las cohortes de referencia están en `experiments/baseline_marzo_junio.json`.

Las imágenes descriptivas conservadas en esta carpeta documentan el esquema recibido. La carpeta del dataset y data/derived se excluyen de Git. GitHub limita a 100 MiB los archivos normales de Git: [documentación oficial](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github). Este repositorio ofrece el script para obtener el original desde su fuente, no intenta dividir el dataset para eludir el límite.
