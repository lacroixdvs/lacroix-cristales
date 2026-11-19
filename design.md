# Design — Vit Cristales

> Guía de estilo UI/UX. Se actualiza cuando cambia el sistema visual. Base: sección 5 de [`inicio.md`](inicio.md).
> Sistema visual actual: **Bootstrap 5.3 + Bootstrap Icons 1.11** (migrado desde Tailwind; sin build step).

## Principios

- Interfaz limpia, densidad media y foco en tablas de consulta rápida (catálogo, clientes, ventas).
- La navegación es MVT pura: hay una URL real por vista; los modales y el live search son mejoras progresivas.
- El nombre comercial mostrado es **Vit Cristales**.
- Todo dato que muta deja un mensaje visible al usuario.
- La librería visual es un detalle de presentación: la lógica, los permisos y los atributos funcionales no se tocan.

## Integración de Bootstrap

- `templates/base.html` carga por CDN:
  - `bootstrap@5.3.3/dist/css/bootstrap.min.css`
  - `bootstrap-icons@1.11.3/font/bootstrap-icons.min.css`
  - `bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js` (necesario para el cierre de alerts)
- El tema institucional vive en `static/css/vit-cristales.css`, que sobreescribe variables Bootstrap (`--bs-primary`, `--bs-body-bg`, `--bs-body-color`, `--bs-border-color`, etc.). No hay compilación ni `package.json`.
- `static/js/live-search.js` y `static/js/modales.js` se cargan con `defer` y **no se modificaron** en el refactor.
- Layout base: `container-fluid` > `row g-0` > sidebar `col-md-3 col-lg-2` + `main col py-4`, navbar y footer globales.

## Paleta y superficies

| Elemento | Clase / variable de referencia |
|---|---|
| Fondo general | `bg-body-tertiary` (`--bs-body-bg: #f8fafc`) |
| Tarjetas | `card border-0 shadow-sm` |
| Color primario | Verde esmeralda (`--bs-primary: #15803d`) vía `.btn-vit`, `.text-vit`, `.bg-vit` |
| Gris pizarra | `--bs-body-color: #334155`, `--bs-secondary-color: #64748b`, `--bs-border-color: #e2e8f0` |
| Éxito | `badge text-bg-success` / `alert alert-success` |
| Error | `badge text-bg-danger` / `alert alert-danger` |
| Advertencia | `badge text-bg-warning` / `alert alert-warning` |
| Información | `badge text-bg-info` / `alert alert-info` |
| Títulos | `h2 fw-bold` (o `h1`/`h5` según jerarquía) |
| Encabezados de tabla | `table-light text-uppercase small` |
| Filas | `table table-hover align-middle` |
| Badges | `badge rounded-pill` o `badge text-bg-*` |

## Tipografía y componentes

- Tipografía del sistema Bootstrap (`--bs-font-sans-serif`), sin fuentes externas obligatorias.
- Botón primario: `btn btn-vit` ( verde institucional con hover/active más oscuro definidos en CSS propio).
- Botón secundario: `btn btn-outline-secondary`.
- Botón de baja: `btn btn-danger` y siempre con confirmación mediante `<dialog>`.
- Formularios: `form-label`, `form-control`, `form-select` y `form-check-input` (según widget, aplicados por `core.forms.EstiloBootstrapMixin`). Errores con `invalid-feedback d-block` y ayudas con `form-text`.
- Mensajes: `templates/partials/messages.html` usa `alert alert-success|danger|warning|info alert-dismissible fade show` con `btn-close` y `data-bs-dismiss="alert"`.
- Tablas: envolver siempre en `table-responsive` para pantallas chicas.

## Badges del dominio

**Categorías de producto** (`catalogo.Producto.categoria`, filtro `badge_categoria`):

| Categoría | Clase sugerida |
|---|---|
| Vidrio | `badge text-bg-info` |
| Mampara | `badge text-bg-primary` |
| Espejo | `badge text-bg-secondary` |
| Cerramiento de oficina | `badge text-bg-success` |

**Estados de venta** (`ventas.Venta.estado`, filtro `badge_estado`):

| Estado | Clase sugerida |
|---|---|
| BORRADOR | `badge text-bg-warning` |
| CONFIRMADA | `badge text-bg-success` |
| CANCELADA | `badge text-bg-danger` |

## Modales

- Se mantiene el elemento nativo `<dialog>` (accesible, sin dependencias de Bootstrap para su lógica).
- `#modal-base` y los modales de baja/cancelación conservan sus `id` y los atributos `data-modal-open` / `data-modal-close`.
- Apariencia: `dialog.rounded-3.shadow-lg.p-0` conteniendo `modal-content` con `modal-header`, `modal-body` y `modal-footer`.
- Cerrar con `btn-close` (`data-modal-close`), click en backdrop y tecla `Escape`; el backdrop se oscurece con `dialog::backdrop` en el CSS propio.
- No poner lógica de negocio dentro del modal: solo presentación y acciones que apunten a URLs reales.

## Live search

- Input con ícono de lupa (`input-group`), `form-control` e `id` único del contenedor de resultados (`data-live-search`).
- Debounce de ~300 ms, `fetch` al backend y reemplazo del contenedor sin recargar la página.
- Event delegation en el contenedor para que los clicks sobrevivan al re-render.
- El filtro del backend respeta permisos por rol y usa `Q` objects.
- Actualizar la URL con `history.replaceState` para que el estado sea compartible; los filtros vigentes se conservan.

## Dashboards por rol

- **ADM:** tarjetas con totales de ventas, stock bajo, proveedores y clientes activos; accesos a todos los módulos.
- **VENDEDOR:** ventas propias, borradores pendientes y catálogo de solo lectura.
- **USUARIO:** catálogo de solo lectura y acceso a su presupuesto armado en sesión.

## Presupuesto en sesión (perfil USUARIO)

- Vista `/presupuesto/` con artículos seleccionados, cantidades y total estimado.
- La selección vive en `request.session`; no se persiste en base de datos en este alcance.
- Los botones de agregar/quitar son acciones reales con feedback por mensajes.

## Regla de oro de UI

**Nunca modificar atributos lógicos** (`id`, `name`, `action`, `method`, `data-*`, URLs, variables y bloques `{% if %}` / `{% for %}` de Django) al hacer ajustes visuales. Solo cambian clases y estructura visual. La validación y los permisos viven en backend.
