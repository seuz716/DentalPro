# Auditoría de Frontend, UX y Odontograma para DentalPro

## 1. Observaciones de UX y HTMX

A continuación, se detalla el análisis y las correcciones de UX y HTMX de acuerdo con los requerimientos iniciales:

### Prioridad Alta
- **Falta de Feedback Visual en Búsquedas:** El input de búsqueda utilizaba HTMX de forma correcta (`keyup changed delay:300ms`), pero faltaba un indicador de estado. Se sugirió añadir un `<div id="spinner">` con estilos de Tailwind (`animate-spin`) vinculándolo al input usando `hx-indicator="#spinner"`.
- **Prevención de Envíos Accidentales en Tabs:** Los botones del selector de pestañas en `patient_detail.html` no contaban con el atributo `type="button"`, lo cual es un riesgo en contextos cercanos a formularios. 

### Prioridad Media
- **Accesibilidad y Contraste en Paginación:** Los botones de paginación tenían clases básicas (`bg-white hover:bg-slate-50`). Se sugirió un contraste mejorado en su estado de interacción con estilos primarios: `hover:bg-teal-50 hover:text-teal-700 hover:border-teal-300`.
- **Navegación Fluida:** Sugerencia de agregar el atributo `hx-push-url="true"` a los enlaces de "Ver" en los resultados de la tabla para sincronizar la URL del navegador con la navegación HTMX en caso de habilitarse `hx-boost`.

### Prioridad Baja
- **Responsive de Sidebar Fija:** Si existe una barra lateral fija de 64px (`w-64`), se recomienda encarecidamente utilizar las clases de utilidad responsivas: `w-full md:w-64`.
- **Pestañas por Demanda vs. Cargadas Inicialmente:** Actualmente, las pestañas en `patient_detail.html` hacen peticiones HTMX para reemplazar `#tab-content`. Esto es una excelente práctica para optimizar la carga inicial. No obstante, si hay requerimientos de trabajo 100% offline, podría considerarse prerenderizar todos los tabs.

---

## 2. Recomendaciones Estratégicas para el Odontograma SVG Completo

Dado que se requería un odontograma completo (dientes FDI 11 a 48) con capacidad offline, la mejor estrategia dictaminada fue **generar el SVG dinámicamente usando Jinja/Django Templates** en lugar de hardcodear coordenadas o depender fuertemente de JS del lado del cliente.

### Estrategia de Implementación Propuesta:
1. **Definir el patrón SVG base (Símbolo o Def):**
   Crear la estructura del diente (una cruz para las 5 caras: oclusal, vestibular, lingual/palatina, mesial, distal) dentro de una etiqueta `<defs>` con un `<g id="tooth-template">`.
2. **Generación con Bucle (Template Loop):**
   Desde la vista de Django, calcular y enviar una lista estructurada con las coordenadas (x,y) de cada diente.
3. **Manejo de Eventos (HTMX):**
   Al agregar `hx-post` y `cursor-pointer`, cada diente actúa como un botón interactivo y reactivo.
4. **Accesibilidad:**
   Incluir `aria-label` descriptivos en cada grupo (`<g>`), `role="button"`, y permitir el enfoque a través del teclado con `tabindex="0"`.

---

## 3. Estado Actual y Resoluciones Implementadas

> [!NOTE]
> Las siguientes resoluciones ya han sido integradas en el proyecto `DentalPro` de manera exitosa y verifican que se ha concluido con las observaciones de la auditoría y sirven de base estable para futuros desarrollos.

### Mejoras Aplicadas a Templates
Se implementó un refactor completo de la estructura de las vistas y componentes siguiendo y expandiendo las observaciones iniciales:
- **`patient_list.html`**: Se refinó la accesibilidad del formulario de búsqueda (`role="search"`, `aria-label`), se mejoró visualmente el input y se estructuró un `<div id="spinner">` respetando estrictamente el comportamiento de la clase `.htmx-indicator`.
- **`patient_detail.html`**: Se modularizó el sistema de pestañas separando las secciones en archivos parciales (`_tab_personal.html`, `_tab_clinical.html`, `_tab_odontogram.html`). Se implementó lógica híbrida elegante (JS + HTMX) para que al hacer clic en los botones de las pestañas (`type="button"`) el estado visual de la UI responda instantáneamente y, en paralelo, se cargue el contenido HTML apropiado usando `hx-get`.

### Resolución Definitiva del Odontograma SVG
Se descartó el uso de generadores en JavaScript del lado del cliente creados temporalmente a favor de la estrategia "Offline-first nativa" orientada al servidor (SSR Puro):
- **Cálculo Backend (`pacientes/views.py`)**: Se añadió lógica en el `get_context_data` del tab `odontogram` para calcular matemáticamente las coordenadas `X` y `Y` de los 32 dientes del sistema FDI. Los dientes fueron agrupados en cuadrantes y posicionados simétricamente dentro de un viewBox más amplio (864x320) asegurando escalabilidad y precisión en dispositivos móviles.
- **Template Dinámico (`_odontogram_svg.html`)**: El SVG fue reconstruido aprovechando la etiqueta `<defs>` para la cruz de cada diente (5 caras iteractivas). El renderizado se ejecuta a través de un bucle `{% for tooth in odontogram_teeth %}` inyectando directamente atributos esenciales (`tabindex="0"`, `role="button"`, `aria-label`) para cumplir con estándares WCAG y asignando un endpoint estandarizado para HTMX (`hx-post="/pacientes/{{ patient.pk|default:'0' }}/diente/{{ tooth.id }}/estado/"`) para preparar futuras interacciones y mutaciones del estado de las piezas dentales, sin requerir código JavaScript manual.
