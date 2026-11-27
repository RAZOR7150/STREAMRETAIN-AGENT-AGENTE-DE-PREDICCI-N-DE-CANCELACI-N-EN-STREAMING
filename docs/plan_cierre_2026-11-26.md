# Plan de cierre — 26 de noviembre de 2026

## Cambio confirmado por el estudiante

La sustentación será grabada, no expuesta en clase. El estudiante quiere cerrar hoy. Se preguntó si hay duración/requisitos nuevos: respuesta pendiente. Propuesta provisional de guion:8 minutos de presentación y4 de demostración, tomados del formato anterior; no afirmar que el profesor confirmó12 minutos de video ni eliminar por cuenta propia requisitos nuevos de preguntas o modificación de código.

## Estado comprobado

- Entregables contiene PDFs de hitos1 y2. No hay informe final IEEE ni presentación final en esa carpeta.
- V1 y V4 entrenadas y evaluadas, con evidencia JSON conservada.
- V4:10variables,depth10,leaf100,class_weight=None,umbral0,30. F1medio validación0,53975; junio0,47912/septiembre0,60039.
- DiciembreV4 exploratorio: accuracy0,92725,precisión0,45684,recall0,38959,F1 0,42054,ROC-AUC0,64929,AP0,34597; matriz[[7405,258],[340,217]]. MetaF1>=0,50 no alcanzada en diciembre.
- V1: F1diciembre0,34615. V4 detectó28 abandonos más y produjo88 falsas alertas menos a sus umbrales respectivos. ROC-AUC empeoró y AP no mejoró: no decir que V4 domina todas las métricas.
- streamlit_app.py existe pero carga experiments/prueba_final, es decir V1 y seis características. No está alineada con V4 ni verificada como demoV4.
- El análisis de diez errores y grupos existente corresponde a V1. No atribuirlo a V4; hay predicciones localesV4 para analizar.
- Paquete streamretain tiene funciones compartidas de carga/métricas y preparación. El usuario pide reutilización mediante imports.
- El enlace público solicitado anteriormente sigue pendiente. La grabación local puede avanzar sin esperar la publicación; grabar no vuelve público localhost.

## Orden de cierre propuesto

| Paso | Resultado verificable | Responsabilidades |
| --- | --- | --- |
| 1. Cerrar experimentación | Conservar candidatoV4 y evidenciasV1; no nueva búsqueda para obtener0,50 | Decisión propuesta por Codex para cerrar; alumno revisa |
| 2. Alinear demo conV4 |10campos,modelo/hash correcto,umbral0,30,puntaje y recorrido, recomendación e historial; ejecución local reproducible | Codex guía modular y soporte; alumno implementa/ejecuta salvo autorización puntual |
| 3. Actualizar análisisV4 |Diez errores reales, tipos/hipótesis y grupos con tamaños; no reutilizar los deV1 comoV4 | Codex guía reutilizable; alumno ejecuta; revisión conjunta |
| 4. Informe final |IEEE doble columna6–8páginas sin referencias/anexos,>=5refs incluyendo>=3artículos y libro, tablas/figuras/limitaciones/IA/reflexión | Codex prepara documentos y verifica fuentes; alumno revisa y comprende |
| 5. Presentación y grabación |Diapositivas,guion,casos de demo y lista de comprobación del video | Codex prepara; alumno ensaya y graba |
| 6. Reproducibilidad y entrega |README conciso,deps,evidencia,bitácora,PDFs finales enEntregables,repo compartido; URL app si se mantiene | Codex soporte/documentación; Git y publicación de repo a cargo del alumno |

## Qué mostrar en la demo

Una entrada válida con alerta, otra sin alerta y una entrada incoherente rechazada. Las dos válidas deben comprobarse con V4 antes de asignarles esos nombres: no prometer los puntajes de los ejemplosV1. Mostrar que diez características se calculan con historia anterior al corte, que el puntaje no está calibrado y que se recomienda revisión humana sin ejecutar campañas reales. Si se muestran casos de error conocidos, identificarlos como tales. No simular que el sistema tiene acceso actual a KKBox.

## Mensaje central del informe/video

Se construyó un prototipo reproducible de apoyo a detección de abandono, con separación temporal y comparación contra baseline, logística, árbol y bosque. Añadir información histórica de suscripción mejoró el F1 de validación y el F1 exploratorio en diciembre. La meta final no se alcanzó y la evaluaciónV4 no es una prueba independiente nueva porque diciembre ya se había observado. El resultado aporta evidencia y límites; no es una garantía comercial ni una campaña de retención validada.

## Entregables propuestos (todavía pendientes)

- Entregables/streamretain_informe_final.pdf y su fuente editable.
- Entregables/streamretain_presentacion.pdf y fuente editable.
- Entregables/streamretain_guion_grabacion.md.
- Video final grabado por el estudiante y enlace de entrega según instrucciones del profesor.

N8n no está confirmado como requisito en el contexto revisado. No incorporarlo como obligación sin evidencia. La prioridad es una demoV4 coherente y los entregables exigidos.

## Respuesta posterior del estudiante

Duración indicada: aproximadamente20 minutos, pendiente precisión del docente. Solicita presentación,guion y despliegue público para que el profesor lo pruebe. Se descarta el supuesto provisional12min. Guion de apoyo en Entregables/streamretain_guion_grabacion.md. La accesibilidad pública se mantiene como objetivo; localhost no basta. Interfaz debe actualizarse aV4 antes de grabar/publicar.
