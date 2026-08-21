# Aprendizaje de estado y criterio de cierre

## 2026-08-20 — Criterio operativo de avance

Durante el cierre de la etapa de métricas globales se estableció un criterio que debe conservarse como aprendizaje del proyecto:

- 🔴 **Pendiente**: existe una tarea importante cuyo camino de resolución todavía no está definido o requiere investigación adicional.
- 🟡 **Pendiente con camino definido**: sabemos exactamente qué falta, conocemos la estrategia para resolverlo y solo queda ejecutar/verificar la integración.
- 🟢 **Validado**: la funcionalidad fue implementada y comprobada mediante pruebas relevantes.

### Aplicación al estado actual

El **Merge a `main`** y el **cierre del PR #5** pasaron de 🔴 a 🟡 porque ya existe un camino de integración segura: sincronizar referencias, integrar `main` en la rama de trabajo sin reescribir historia, resolver conflictos si aparecen, ejecutar `check` y la batería de pruebas, verificar las funcionalidades ya validadas y solo entonces hacer el merge y cerrar el PR.

Este cambio de color no representa una conclusión prematura. Representa una mejora real del conocimiento del estado del proyecto: el problema dejó de ser "no sabemos cómo resolverlo" y pasó a ser "sabemos cómo resolverlo y falta ejecutar la integración y verificarla".

## Principio para futuras etapas

El estado del proyecto debe reflejar el **grado de conocimiento y control sobre la tarea**, no solamente si la tarea está terminada. Una tarea puede permanecer pendiente y, aun así, representar un avance importante cuando su solución ya está definida y verificable.

Este criterio debe utilizarse junto con las pruebas técnicas, la revisión de código y la validación funcional antes de declarar una etapa cerrada.
