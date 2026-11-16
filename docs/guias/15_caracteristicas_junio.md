# Guía 15 — Características de junio (ruta prioritaria al hito 2)

Por solicitud del estudiante se omiten por ahora siete casos manuales restantes de junio. Se revisaron los casos 03 y 08 y pasó la coherencia interna reportada de 7.210 etiquetas. Esto es una auditoría parcial, no completa. Se mantiene el supuesto de cobertura y los controles automáticos. No altera el objetivo temporal ni autoriza a Codex a ejecutar procesamiento o entrenamiento.

## Adaptación

Copia en tu editor `scripts/08_caracteristicas_historicas.py` a `scripts/13_caracteristicas_junio.py`. El nombre del original ya está corregido en disco. Mantén su lógica y las seis características. Cambia estas asignaciones antes de calcular las ventanas:

```python
archivo_piloto = carpeta / "piloto_2016-06-06.csv"
archivo_candidatos = carpeta / "candidatos_2016-06-06.csv"
archivo_etiquetas = carpeta / "etiquetas_piloto_2016-06-06.csv"
salida = carpeta / "cohorte_2016-06-06.csv"
corte = date(2016, 6, 6)
```

Sustituye los controles en sus posiciones originales:

```python
if len(candidatos) != 7210:
    raise ValueError("No corresponde a los 7.210 candidatos de junio")
```

```python
if filas_piloto != 40612 or filas_futuras_excluidas != 17447:
    raise ValueError("Los tamaños no coinciden con el piloto de junio")
```

Dentro de la lectura de etiquetas, cambia también la comprobación de seguimiento:

```python
        if date.fromisoformat(fila["observado_hasta"]) != date(2016, 8, 4):
            raise ValueError("Etiqueta con otro seguimiento")
```

Mantén la indentación de ese bloque dentro del for. Conserva los demás controles y no incluyas nuevas características. Las ventanas se calculan con timedelta: 90 días desde el 8 de marzo y 30 desde el 7 de mayo; ambos excluyen el 6 de junio.

## Ejecutar

```powershell
& "C:\Users\HP\anaconda3\python.exe" "scripts\13_caracteristicas_junio.py"
```

Revisa que indique 7.210 filas, seis características, 6.799 renovaciones y 411 abandonos. Debe excluir 17.447 filas futuras y guardar cohorte_2016-06-06.csv. No sabemos aún el resumen numérico de las características. Un error requiere revisión, no eliminación del control. Si la salida existe, no sobrescribir sin revisar.

Para acelerar esta entrega puedes continuar directamente con la guía 16 si estos controles pasan y la ejecución termina correctamente. Comparte después ambas salidas. No hace falta completar más preguntas de comprensión antes de estas dos ejecuciones. Sigues siendo responsable de escribir y ejecutar los programas.
