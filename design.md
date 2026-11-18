# Design — Vit Cristales

> Guía de estilo UI/UX. Se actualiza cuando cambia el sistema visual. Base: sección 5 de [`inicio.md`](inicio.md).

## Principios

- Interfaz limpia, densidad media y foco en tablas de consulta rápida (catálogo, clientes, ventas).
- La navegación es MVT pura: hay una URL real por vista; los modales y el live search son mejoras progresivas.
- El nombre comercial mostrado es **Vit Cristales**.
- Todo dato que muta deja un mensaje visible al usuario.

## Paleta y superficies

| Elemento | Clase de referencia |
|---|---|
| Fondo general | `bg-gray-50` |
| Tarjetas | `bg-white border border-gray-100 shadow-sm` |
| Color primario | Verde (`bg-primary-600`, `text-primary-600`, `hover:bg-primary-700`) |
| Éxito | `bg-green-100 text-green-800` |
| Error | `bg-red-100 text-red-800` |
| Advertencia | `bg-yellow-100 text-yellow-800` |
| Información | `bg-sky-100 text-sky-800` |
| Títulos | `text-2xl font-bold text-gray-900` |
| Encabezados de tabla | `text-gray-500 uppercase text-xs` |
| Filas | `hover:bg-gray-50 cursor-pointer` |
| Badges | `px-2.5 py-0.5 rounded-full text-xs font-medium` |

## Tipografía y componentes

- Tipografía del sistema Tailwind (`font-sans`), sin fuentes externas obligatorias.
- Botón primario: `bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700`.
- Botón secundario: `bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50`.
- Botón de baja: `bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700` y siempre con confirmación.
- Formularios: label arriba del campo, `border-gray-300 rounded-lg`, error en rojo debajo del campo.
- Mensajes: renderizar en `templates/partials/messages.html` con estilo por nivel (`success`, `error`, `warning`, `info`).

## Badges del dominio

**Categorías de producto** (`catalogo.Producto.categoria`):

| Categoría | Clase sugerida |
|---|---|
| Vidrio | `bg-sky-100 text-sky-800` |
| Mampara | `bg-indigo-100 text-indigo-800` |
| Espejo | `bg-purple-100 text-purple-800` |
| Cerramiento de oficina | `bg-teal-100 text-teal-800` |

**Estados de venta** (`ventas.Venta.estado`):

| Estado | Clase sugerida |
|---|---|
| BORRADOR | `bg-yellow-100 text-yellow-800` |
| CONFIRMADA | `bg-green-100 text-green-800` |
| ANULADA | `bg-red-100 text-red-800` |

## Modales

- Usar el elemento nativo `<dialog>` (accesible, sin dependencias).
- Cerrar con botón X, click en backdrop y tecla `Escape`.
- Clases de referencia: `p-0 rounded-xl shadow-2xl backdrop:bg-black/50 w-full max-w-lg`.
- No poner lógica de negocio dentro del modal: solo presentación y acciones que apunten a URLs reales.

## Live search

- Input con ícono de lupa e `id` único del contenedor de resultados.
- Debounce de ~300 ms, `fetch` al backend y reemplazo del contenedor sin recargar la página.
- Event delegation en el contenedor para que los clicks sobrevivan al re-render.
- El filtro del backend respeta permisos por rol y usa `Q` objects.
- Actualizar la URL con `history.replaceState` para que el estado sea compartible.

## Dashboards por rol

- **ADM:** tarjetas con totales de ventas, stock bajo, proveedores y clientes activos; accesos a todos los módulos.
- **VENDEDOR:** ventas propias, borradores pendientes y catálogo de solo lectura.
- **USUARIO:** catálogo de solo lectura y acceso a su presupuesto armado en sesión.

## Presupuesto en sesión (perfil USUARIO)

- Vista `/presupuesto/` con artículos seleccionados, cantidades y total estimado.
- La selección vive en `request.session`; no se persiste en base de datos en este alcance.
- Los botones de agregar/quitar son acciones reales con feedback por mensajes.

## Regla de oro de UI

**Nunca modificar atributos lógicos** (`id`, `name`, `onclick`, URLs, variables de Django) al hacer ajustes visuales. Solo clases de Tailwind y estructura visual. La validación y los permisos viven en backend.
