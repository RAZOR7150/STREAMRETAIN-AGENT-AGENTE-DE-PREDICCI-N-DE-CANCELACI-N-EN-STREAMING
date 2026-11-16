# Guía 06 — Preparar una muestra para el primer corte temporal

## Qué construirás

Un CSV local reducido con transacciones de aproximadamente el 1 % de los usuarios, entre 2015-12-08 y 2016-05-05. El primer corte propuesto es el lunes 2016-03-07. La muestra permitirá estudiar historia y resultado por separado. Aún no construimos etiquetas ni entrenamos.

Lee primero `docs/protocolo_evaluacion_temporal.md`: contiene el calendario propuesto y sus limitaciones. Usaremos solamente transactions original. Ahora sí guardaremos un CSV pequeño derivado, no la descompresión completa. Contiene identificadores y registros originales: mantenlo local, no lo publiques ni lo añadas a Git.

Crea tú `scripts/04_preparar_piloto_temporal.py` y escribe estos bloques en orden. No modifiques el script de auditoría. Codex no ha creado ni ejecutado este nuevo programa.

## 1. Rutas, fechas y muestra reproducible

```python
import csv
import hashlib  # Produce un resumen determinista de cada identificador.
import subprocess
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
comprimido = raiz / "data" / "kkbox-churn-prediction-challenge" / "transactions.csv.7z"
ruta_interna = "transactions.csv"
tar = Path(r"C:\Windows\System32\tar.exe")

corte = date(2016, 3, 7)
inicio = corte - timedelta(days=90)
# Incluimos vencimientos desde el corte hasta 29 días después.
fin_vencimientos = corte + timedelta(days=29)
# Después del último vencimiento dejamos 30 días de observación.
fin_seguimiento = fin_vencimientos + timedelta(days=30)

salida = raiz / "data" / "derived" / "piloto_2016-03-07.csv"
salida.parent.mkdir(parents=True, exist_ok=True)
for archivo in (tar, comprimido):
    if not archivo.is_file():
        raise FileNotFoundError(archivo)


def incluir_usuario(usuario):
    # El prefijo fija una versión de la regla de muestreo: no cambiar entre cortes.
    texto = "streamretain-v1:" + usuario
    resumen = hashlib.sha256(texto.encode("utf-8")).digest()
    # Convertimos los primeros 8 bytes en un entero estable.
    numero = int.from_bytes(resumen[:8], byteorder="big")
    # Aproximadamente uno de cada cien identificadores cae en este grupo.
    return numero % 100 == 0
```

`timedelta` suma o resta días reales de calendario. La ventana histórica termina el día anterior al corte. SHA-256 aquí solo sirve para seleccionar una muestra estable; no vuelve anónimos los datos guardados. A diferencia de elegir cada centésima fila, esta regla conserva todas las transacciones del usuario seleccionado dentro de la ventana. No usa la etiqueta ni exige que el usuario tenga eventos futuros. La fracción real no tiene por qué ser exactamente 1 %.

## 2. Lectura progresiva y escritura local

```python
leidas = 0
fechas_invalidas = 0
mal_formadas = 0
usuarios_vacios = 0
conteos = Counter()
por_mes = Counter()

# El modo x evita sobrescribir un archivo existente por accidente.
# Si ya existe, revisa si corresponde a una ejecución anterior antes de renombrarlo.
with salida.open("x", encoding="utf-8", newline="") as destino:
    proceso = subprocess.Popen(
        [str(tar), "-xOf", str(comprimido), ruta_interna],
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8-sig",
    )
    try:
        lector = csv.DictReader(proceso.stdout)
        campos = lector.fieldnames
        requeridos = {
            "msno", "transaction_date", "membership_expire_date",
            "payment_method_id", "payment_plan_days", "plan_list_price",
            "is_cancel",
        }
        if not campos or not requeridos.issubset(campos):
            raise ValueError(f"Cabecera inesperada: {campos}")
        if len(campos) != len(set(campos)):
            raise ValueError("Hay columnas repetidas")

        # Conservamos las columnas originales; no añadimos predicciones ni etiquetas.
        escritor = csv.DictWriter(destino, fieldnames=campos)
        escritor.writeheader()

        for fila in lector:
            leidas += 1
            if None in fila or any(v is None for v in fila.values()):
                mal_formadas += 1
                continue
            texto_fecha = fila["transaction_date"].strip()
            try:
                if (len(texto_fecha) != 8 or not texto_fecha.isascii()
                        or not texto_fecha.isdigit()):
                    raise ValueError("Formato de fecha incorrecto")
                fecha = date(int(texto_fecha[:4]), int(texto_fecha[4:6]),
                             int(texto_fecha[6:8]))
            except ValueError:
                fechas_invalidas += 1
                continue

            if not inicio <= fecha <= fin_seguimiento:
                continue  # No escribimos eventos fuera de esta ventana.
            usuario = fila["msno"].strip()
            if not usuario:
                usuarios_vacios += 1
                continue
            if not incluir_usuario(usuario):
                continue

            fila["msno"] = usuario
            escritor.writerow(fila)
            # Solo para informar: NO mezclamos estas fases al construir características.
            fase = "historia" if fecha < corte else "seguimiento"
            conteos[fase] += 1
            por_mes[f"{fecha.year:04d}-{fecha.month:02d}"] += 1

        codigo = proceso.wait()
        if codigo != 0:
            raise RuntimeError(f"tar falló con código {codigo}; salida incompleta")
    finally:
        proceso.stdout.close()
        if proceso.poll() is None:
            proceso.terminate()
        proceso.wait()
```

Solo una fila circula cada vez; los contadores crecen por mes, no por usuario. No guardamos millones de transacciones en una lista. Como el archivo original no se ha demostrado ordenado por fecha, hay que recorrerlo completo: no usar `break` cuando aparece una fecha posterior al límite.

Este primer fichero contiene historia y seguimiento juntos para inspección. En el paso siguiente se separarán explícitamente según la fecha. Jamás pasaremos todo este archivo directamente al modelo. `usuarios_vacios` cuenta únicamente filas dentro de la ventana; los controles de estructura y transaction_date recorren todo el archivo.

## 3. Resumen y controles

```python
# Estas comprobaciones se ejecutan después de cerrar el archivo de salida.
if mal_formadas or fechas_invalidas or usuarios_vacios:
    raise RuntimeError(
        f"Piloto no aprobado: estructura={mal_formadas}, "
        f"fecha={fechas_invalidas}, usuarios vacíos en ventana={usuarios_vacios}. "
        "El CSV quedó en disco para revisión; no usarlo para entrenar."
    )

if sum(por_mes.values()) != sum(conteos.values()):
    raise RuntimeError("No cuadran los conteos de salida")

print("Archivo de origen:", comprimido.name)
print("Filas recorridas:", leidas)
print("Inicio histórico:", inicio)
print("Corte:", corte)
print("Fin de seguimiento:", fin_seguimiento)
print("Transacciones históricas guardadas:", conteos["historia"])
print("Transacciones de seguimiento guardadas:", conteos["seguimiento"])
print("Total guardado:", sum(conteos.values()))
print("Por mes:")
for mes, cantidad in sorted(por_mes.items()):
    print(f"  {mes}: {cantidad}")
print("CSV local:", salida)
print("Tamaño en MiB:", round(salida.stat().st_size / (1024 ** 2), 2))
if conteos["historia"] == 0 or conteos["seguimiento"] == 0:
    print("Revisar: falta una de las fases en la muestra")
```

Si se interrumpe la ejecución o falla, puede quedar un CSV parcial: no usarlo como muestra válida. El modo x impedirá reemplazarlo en el siguiente intento; comparte el error para revisar el archivo antes de volver a ejecutar. No estamos contando usuarios únicos ni candidatos todavía. El número de filas guardadas no permite deducir cuántos usuarios resultarán elegibles.

## 4. Ejecuta y comparte el resumen

Desde PowerShell en la raíz del proyecto:

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\04_preparar_piloto_temporal.py"
```

No necesita instalar paquetes nuevos. Es un recorrido completo del original, por lo que puede tardar. El total recorrido debería coincidir con 21.547.746 si se usa el mismo archivo que auditaste y termina correctamente; el número de filas seleccionadas aún no se conoce. Comparte el resumen, no el CSV con identificadores.

## 5. Comprensión antes del siguiente paso

1. ¿Por qué seleccionamos usuarios con una función estable en lugar de seleccionar filas al azar?
2. ¿Qué uso tendrán los eventos anteriores al 7 de marzo y los posteriores?
3. ¿Por qué guardar una renovación futura para construir la etiqueta no autoriza usarla como característica?
4. ¿Por qué esta muestra todavía no es una cohorte de usuarios etiquetados?

Después de revisar el resumen, trabajaremos sobre este archivo pequeño: ordenación de eventos, estado al corte, elegibilidad y reglas de etiqueta con ejemplos verificables. No implementes todavía entrenamiento ni etiquetado simplificado por ausencia de filas.
