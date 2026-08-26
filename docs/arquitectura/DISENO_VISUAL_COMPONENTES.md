# Resumen Arquitectónico: Unificación Visual y Herencia Multinivel

**Fecha:** Agosto 2026
**Objetivo:** Transición de un diseño monolítico a una Arquitectura Basada en Componentes (Estilo Laravel/Blade) usando Django Templates y TailwindCSS.

---

## 1. ¿Por qué se hizo este cambio?
El sistema anterior tenía un problema de escalabilidad visual: cada archivo HTML (`salud_form.html`, `animal_detalle.html`) tenía inyectado su propio código CSS y estructura de diseño. Si queríamos cambiar el color de un botón o el estilo de una tarjeta, debíamos editar 15 archivos distintos. 
Con la nueva arquitectura, preparamos el terreno para que Hato pueda recibir un **Template Comercial (Dashboard Admin)** en el futuro cambiando un solo archivo.

## 2. La Nueva Estructura (Paso a Paso)

El sistema ahora se divide en 4 capas lógicas:

### Capa 1: El Layout Raíz (Global)
*   **Archivo:** `apps/administrador/templates/administrador/base_root.html`
*   **¿Qué hace?:** Es el HTML más puro (`<head>`, `<body>`). Su única función es cargar la librería **TailwindCSS** y los estilos nativos. 
*   **¿Cuándo editarlo?:** Solo si vas a agregar una nueva librería global (Ej: Google Fonts, FontAwesome, o un framework de JavaScript).

### Capa 2: El Layout Secundario (El Cascarón Administrativo)
*   **Archivo:** `apps/administrador/templates/administrador/base.html`
*   **¿Qué hace?:** Hereda de `base_root.html`. Dibuja la Barra Superior (Topbar) con el usuario y la finca activa, y la Barra Lateral Oscura (Sidebar) con los menús.
*   **¿Cuándo editarlo?:** Aquí es donde integrarás el código del **Template Comercial** en el futuro. Si quieres agregar un nuevo enlace al menú o cambiar el color de la barra superior, este es el archivo.

### Capa 3: Los Componentes Reutilizables (Las piezas de Lego)
*   **Ubicación:** Carpeta `apps/administrador/templates/administrador/componentes/`
*   **Archivos Clave:** 
    *   `_form_card.html`: El molde para todos los formularios (Pesajes, Movilidad, Salud). Dibuja la tarjeta blanca, los botones de "Guardar/Cancelar" y muestra los errores de Django en rojo.
    *   `_header_pantalla.html`: Dibuja los títulos grandes y botones de "Registrar" de las tablas.
    *   `_paginador.html`: La barra de anterior/siguiente.
*   **¿Cuándo editarlo?:** Si quieres que todos los formularios del sistema ahora tengan bordes cuadrados en vez de redondeados, o si quieres que el botón "Guardar" pase de azul a verde. Editas aquí y el cambio impacta a todo el Hato.

### Capa 4: Las Vistas Hijas (La Operación Diaria)
*   **Ubicación:** `apps/ganado/templates/ganado/...`
*   **¿Qué hacen?:** Son archivos diminutos (de 5 a 10 líneas) que simplemente llaman a los componentes pasándoles los datos (`{% include "administrador/componentes/_form_card.html" ... %}`). Ya no contienen código de diseño.

---

## 3. ¿Cómo implementar esto en el Hato AI Lab Original?

Para que el equipo principal adopte esta estructura, solo deben fusionar (hacer merge) de los últimos 4 commits que creamos en esta prueba:
1. Reestructuración de listas y paginación.
2. Inyección de Componentes Base (`_form_card`).
3. Rediseño del Dashboard (Ficha) del Animal.
4. Implementación de Herencia Multinivel (`base_root.html` y `base.html`).
