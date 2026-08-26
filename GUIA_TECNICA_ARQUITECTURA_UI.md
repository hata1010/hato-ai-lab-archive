# GUÍA TÉCNICA: Arquitectura Visual y Uso de Componentes UI

**Proyecto:** Hato AI Lab
**Propósito:** Manual para desarrolladores sobre cómo entender, utilizar y extender la nueva arquitectura de plantillas (Layouts y Componentes) del sistema.

---

## 1. Stack Tecnológico Implementado

Para lograr un diseño unificado y moderno sin depender de pesados archivos CSS personalizados, el sistema utiliza el siguiente stack en la capa de presentación:

*   **Tailwind CSS (vía CDN):** Framework de CSS basado en clases de utilidad (utility-first). Nos permite maquetar tarjetas, sombras, márgenes y colores directamente en el HTML (ej. `class="bg-white rounded-xl shadow-sm"`). Está inyectado de manera global en el archivo raíz.
*   **Django Templates (DTL):** El motor de plantillas nativo de Django, llevado a su máximo potencial usando herencia multinivel (`{% extends %}`) y reutilización de componentes inyectables (`{% include %}`).
*   **HTMX (En fase de experimentación):** Librería ligera de JavaScript utilizada para realizar peticiones asíncronas al servidor e inyectar HTML sin recargar la página (comprobado en los prototipos SPA).

---

## 2. La Estructura de Herencia Multinivel

El sistema ya no depende de un solo archivo `base.html` saturado. Ahora sigue una jerarquía estricta de 4 niveles (como Laravel/Blade):

1.  **NIVEL 1: Raíz Absoluta (`base_root.html`)**
    *   *Ubicación:* `apps/administrador/templates/administrador/base_root.html`
    *   *Función:* Es el cascarón técnico. Contiene el `<head>`, las etiquetas `meta`, la carga del script de **TailwindCSS** y los CSS nativos. NUNCA se debe modificar a menos que se añada una librería global nueva.
2.  **NIVEL 2: Layout Operativo (`base.html`)**
    *   *Ubicación:* `apps/administrador/templates/administrador/base.html`
    *   *Función:* Hereda de `base_root.html`. Renderiza la **Barra Superior (Topbar)** (con el usuario y finca activa) y el **Menú Lateral (Sidebar)**. Define el bloque central `{% block content %}`.
3.  **NIVEL 3: Componentes Reutilizables (Moldes)**
    *   *Ubicación:* `apps/administrador/templates/administrador/componentes/`
    *   *Ejemplos:* `_form_card.html` (molde para formularios), `_header_pantalla.html` (molde para títulos), `_paginador.html` (molde para paginación).
    *   *Función:* Centralizan el código visual de TailwindCSS.
4.  **NIVEL 4: Vistas Hijas (Páginas Finales)**
    *   *Ubicación:* Las plantillas de cada app (ej. `ganado/templates/ganado/`).
    *   *Función:* Páginas finales que no tienen código de diseño, solo lógica de inyección de componentes.

---

## 3. ¿Cómo llamar a la base y a los componentes?

Para que cualquier página del sistema adopte el diseño general, el archivo HTML **siempre** debe iniciar así:

```html
{% extends "administrador/base.html" %}

{% block content %}
    <!-- Aquí va el contenido de tu vista -->
{% endblock %}
```

Para inyectar un **Componente Reutilizable**, utilizamos la etiqueta `{% include %}` pasando las variables necesarias usando `with`:

```html
{% include "administrador/componentes/_header_pantalla.html" with titulo="Mi Nueva Pantalla" icono="🐄" %}
```

---

## 4. GUÍA PRÁCTICA: Cómo migrar/modificar un HTML viejo a la nueva estructura

Si te encuentras con un archivo HTML antiguo que tiene estilos feos o tablas rotas, así es como debes modernizarlo paso a paso:

### CASO A: Migrar un Formulario de Creación/Edición

**Código Viejo (A eliminar):**
```html
{% extends "administrador/base.html" %}
{% block content %}
    <h1>Registrar Medicamento</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Guardar</button>
    </form>
{% endblock %}
```

**Nuevo Código (La forma correcta):**
Borras todo el código espagueti y llamas al componente `_form_card.html`, pasándole los datos por parámetro.

```html
{% extends "administrador/base.html" %}
{% block title %}Registrar Medicamento{% endblock %}

{% block content %}
    {% url 'ganado:lista_salud' as url_volver %}
    
    {% include "administrador/componentes/_form_card.html" with titulo="Registrar Medicamento" icono="💊" boton_texto="Guardar Medicamento" url_cancelar=url_volver %}
{% endblock %}
```
*¡Y listo! Automáticamente el formulario se renderizará como una tarjeta blanca con sombras, diseño a dos columnas, inputs estilizados y manejo de errores de Django incorporado.*

### CASO B: Migrar una Lista o Tabla

Para las listas (como el Inventario), debes estructurarlo llamando al Header y usando clases de Tailwind para la tabla:

```html
{% extends "administrador/base.html" %}

{% block content %}
<div class="p-4 md:p-8 max-w-7xl mx-auto font-sans">
    
    <!-- 1. Llamar al Componente del Título -->
    {% url 'app:crear_registro' as url_boton %}
    {% include "administrador/componentes/_header_pantalla.html" with titulo="Mi Listado" boton_texto="Crear Nuevo" url_boton=url_boton %}

    <!-- 2. Crear la tabla con Tailwind -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table class="min-w-full divide-y divide-slate-200">
            <!-- (Tu código de tabla aquí) -->
        </table>
        
        <!-- 3. Inyectar el Componente Paginador -->
        {% include "administrador/componentes/_paginador.html" %}
    </div>

</div>
{% endblock %}
```

## Resumen de Reglas de Oro para el Equipo
1. **Jamás usar CSS en línea** (`style="..."`) en las vistas hijas. Todo debe resolverse con clases de Tailwind.
2. Si un formulario es estándar, **usa obligatoriamente `_form_card.html`**. Si el formulario es muy complejo (como el "Editar Animal"), entonces sí puedes maquetarlo usando la cuadrícula de Tailwind, pero respetando la paleta de colores de la aplicación.
