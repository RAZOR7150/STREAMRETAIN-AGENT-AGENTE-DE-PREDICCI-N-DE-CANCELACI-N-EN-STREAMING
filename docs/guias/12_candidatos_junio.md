# Guía 12 — Candidatos de junio

## Objetivo

Usar el piloto de junio ya extraído (40.612 transacciones) para reconstruir el vencimiento conocido al lunes 2016-06-06 y seleccionar candidatos cuyo vencimiento esté entre ese día y el 2016-07-05. No usar las renovaciones posteriores para decidir quién entra. No cambiar la regla respecto de marzo ni exigir los mismos usuarios o cantidades.

## 1. Copia tu programa de candidatos

En el editor, copia el contenido de `scripts/05_candidatos_temporales.py` a un nuevo archivo:

`scripts/10_candidatos_junio.py`

Conserva intacto el original de marzo. En la copia sustituye las tres asignaciones de entrada, salida y corte, cerca del inicio:

```python
# Entrada: piloto de junio, no el de marzo.
entrada = raiz / "data" / "derived" / "piloto_2016-06-06.csv"
# Salida separada para no sobrescribir candidatos anteriores.
salida = raiz / "data" / "derived" / "candidatos_2016-06-06.csv"
# Definir el corte ANTES de calcular inicio y finales con timedelta.
corte = date(2016, 6, 6)
```

Mantén el resto del código, incluidas las funciones de validación/ordenación, las ventanas calculadas y las comprobaciones. No pegues estas asignaciones al final: deben reemplazar las originales antes de cualquier lectura o cálculo dependiente.

## 2. Qué hará

- Agrupará la historia del 8 de marzo al 5 de junio por usuario.
- Reconstruirá el vencimiento al corte con la convención de ordenación Scala.
- Clasificará los usuarios con historia en vencimiento anterior, candidato o vencimiento posterior a la ventana.
- Contará usuarios de seguimiento solo para describirlos; no exigirá eventos futuros para admitir un candidato.
- Guardará una fila por candidato, todavía sin etiqueta de abandono.

Las mismas firmas y reglas resuelven empates. No se consulta la etiqueta de marzo ni se filtra por haber pertenecido a su cohorte.

## 3. Ejecuta y compara los controles

Desde la raíz del proyecto:

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\10_candidatos_junio.py"
```

Debes recuperar estas cantidades del piloto de junio:

- Filas históricas: 23.165.
- Filas de seguimiento: 17.447.
- Total: 40.612.

El número de usuarios y candidatos todavía no se conoce. No copies 7.443 ni 10.447 como expectativas de junio. La suma de usuarios con vencimiento anterior, posterior y candidato debe coincidir con usuarios con historia, como comprueba el programa.

Si aparece FileExistsError, la salida ya existe: conserva el archivo y comparte el mensaje antes de sobrescribir. Si hay otro error, comparte el mensaje completo. No ejecutar todavía el etiquetador de marzo contra junio: requiere adaptar rutas y controles a los nuevos conteos.

## 4. Comparte la salida completa

Revisaremos los resultados antes de etiquetar junio y preparar sus características. El archivo guardado será `data/derived/candidatos_2016-06-06.csv`.

Preguntas breves:

1. Si alguien fue candidato en marzo, ¿tiene que ser candidato en junio? ¿Qué dato decide su elegibilidad ahora?
2. ¿Por qué no eliminamos de junio a todos los usuarios que ya aparecieron en marzo?

Este paso no entrena modelos. La primera línea base aprenderá la clase mayoritaria en marzo y será medida en junio. Diciembre sigue reservado como prueba final.
