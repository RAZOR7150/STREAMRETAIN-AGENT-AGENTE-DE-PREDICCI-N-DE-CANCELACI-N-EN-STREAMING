# Hito 2 — Paso 3: usuarios únicos y etiquetas contradictorias

## Objetivo

Extender tú mismo `scripts/02_revisar_etiquetas.py` para distinguir:

- Cantidad de filas.
- Cantidad de usuarios diferentes con etiqueta válida.
- Filas adicionales de usuarios ya vistos.
- Usuarios que aparecen tanto con etiqueta 0 como con etiqueta 1.

No borraremos filas ni elegiremos una etiqueta automáticamente. Esta revisión corresponde a un único archivo; no mezclar aún las versiones.

## 1. Agrega dos estructuras junto a los contadores iniciales

```python
# Cada clave será un identificador de usuario.
# Cada valor será un conjunto de las etiquetas observadas para ese usuario.
etiquetas_por_usuario = {}

# Cuenta apariciones adicionales de usuarios ya registrados.
filas_repetidas_usuario = 0
```

El diccionario guardará algo como `{"usuario_A": {"0", "1"}}`. El conjunto interior conserva valores distintos: añadir "0" dos veces deja un solo "0".

## 2. Agrega este bloque dentro del bucle

Colócalo después del bloque que cuenta etiquetas válidas o inválidas, al mismo nivel de sangría que `if etiqueta in conteos:`. Debe permanecer dentro de `for fila in lector:`.

```python
        # Solo estudiamos identidad y contradicciones en registros utilizables.
        # Las incidencias de los demás registros ya se cuentan por separado.
        if usuario != "" and etiqueta in conteos:
            if usuario in etiquetas_por_usuario:
                # El usuario ya apareció: esta es una fila adicional de ese usuario.
                filas_repetidas_usuario += 1
            else:
                # Un usuario nuevo comienza con un conjunto vacío de etiquetas.
                etiquetas_por_usuario[usuario] = set()

            # Añadimos la etiqueta al conjunto del usuario.
            # add no crea otra copia si esa etiqueta ya estaba presente.
            etiquetas_por_usuario[usuario].add(etiqueta)
```

La pertenencia `usuario in etiquetas_por_usuario` comprueba las claves del diccionario. No pregunta si la etiqueta ya existía: cuenta repeticiones de usuario incluso cuando la etiqueta coincide.

## 3. Agrega el resumen al final del programa

```python
# len aplicado al diccionario cuenta sus claves: usuarios diferentes.
usuarios_unicos = len(etiquetas_por_usuario)

# Contaremos cada usuario contradictorio una vez, aunque tenga muchas filas.
usuarios_con_conflicto = 0
for etiquetas_observadas in etiquetas_por_usuario.values():
    # Un conjunto con dos etiquetas contiene tanto 0 como 1.
    if len(etiquetas_observadas) > 1:
        usuarios_con_conflicto += 1

print("Usuarios únicos con etiqueta válida:", usuarios_unicos)
print("Filas adicionales de usuarios repetidos:", filas_repetidas_usuario)
print("Usuarios con etiquetas contradictorias:", usuarios_con_conflicto)

# Estas dos cantidades reconstruyen las filas incluidas en este análisis.
print("Filas con usuario y etiqueta válidos:", usuarios_unicos + filas_repetidas_usuario)
```

## Ejemplo pequeño para entender los contadores

| Fila | Usuario ficticio | Etiqueta |
| --- | --- | --- |
| 1 | A | 0 |
| 2 | A | 0 |
| 3 | A | 1 |
| 4 | B | 1 |

Aquí hay 4 filas, 2 usuarios únicos, 2 filas adicionales de usuarios repetidos y 1 usuario con etiquetas contradictorias. No hay 2 usuarios repetidos: el contador de filas adicionales mide apariciones, no personas.

En un historial con fechas, varias filas del mismo usuario pueden ser correctas: una persona puede renovar en un periodo y abandonar en otro. En una tabla de etiquetas de una misma cohorte, necesitamos investigar las repeticiones antes de dar por válida una fila por usuario. Contar usuarios únicos no elimina registros ni corrige errores automáticamente.

## Memoria

La lectura del CSV sigue siendo progresiva, pero este ejercicio sí conserva un registro por usuario en memoria. Su memoria crece con el número de usuarios: no tiene consumo constante como los contadores anteriores. Se limita aquí al archivo de etiquetas; no aplicar esta estructura indiscriminadamente a todos los eventos de escucha. Si aparece un error de memoria, comparte el mensaje y adaptaremos el método, sin extraer el CSV gigante.

## Ejecución y revisión

Vuelve a ejecutar desde la raíz:

```powershell
& 'C:\Users\HP\anaconda3\python.exe' scripts/02_revisar_etiquetas.py
```

Comparte el resumen completo. Los conteos anteriores deben mantenerse si no cambiaste la fuente ni la lógica de clasificación. No anticipamos si habrá o no duplicados. Si los controles anteriores siguen en cero, usuarios únicos más filas adicionales debe sumar las 970.960 filas comunicadas.

Este paso no entrena un modelo, no deduplica los datos y no cambia sus etiquetas. Después revisaremos la relación entre archivos y el protocolo temporal.
