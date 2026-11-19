# Design — Vit Cristales

> Guía de estilo UI/UX. Se actualiza cuando cambia el sistema visual. Base: sección 5 de [`inicio.md`](inicio.md).
> Sistema visual actual: **Bootstrap 5.3 + Bootstrap Icons 1.11** (migrado desde Tailwind; sin build step), con un pulido visual elegante y sobrio aplicado en `refactor/ui-pulido-visual`.

## Principios

- Interfaz limpia, densidad media y foco en tablas de consulta rápida (catálogo, clientes, ventas).
- Estética arquitectónica: superficies claras, bordes finos, poco color y movimiento solo para acompañar la interacción.
- La navegación es MVT pura: hay una URL real por vista; los modales y el live search son mejoras progresivas.
- El nombre comercial mostrado es **Vit Cristales**.
- Todo dato que muta deja un mensaje visible al usuario.
- La librería visual es un detalle de presentación: la lógica, los permisos y los atributos funcionales no se tocan.

## Integración de Bootstrap

- `templates/base.html` carga por CDN:
  - Google Fonts: `Plus Jakarta Sans` (500–800) y `Inter` (400–700), con `preconnect` a `fonts.googleapis.com` y `fonts.gstatic.com`.
  - `bootstrap@5.3.3/dist/css/bootstrap.min.css`
  - `bootstrap-icons@1.11.3/font/bootstrap-icons.min.css`
  - `bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js` (necesario para el cierre de alerts)
- El tema institucional vive en `static/css/vit-cristales.css`, que sobreescribe variables Bootstrap (`--bs-primary`, `--bs-body-bg`, `--bs-body-color`, `--bs-border-color`, `--bs-font-sans-serif`, etc.). No hay compilación ni `package.json`.
- `static/js/live-search.js` y `static/js/modales.js` se cargan con `defer` y **no se modificaron** en el refactor ni en el pulido.
- Layout base: `container-fluid` > `row g-0` > sidebar `col-md-3 col-lg-2` + `main col py-4`, navbar y footer globales.

## Tipografía

| Uso | Fuente |
|---|---|
| Títulos, encabezados, `navbar-brand`, encabezados de tabla | **Plus Jakarta Sans** (`--vit-font-heading`) |
| Texto, tablas, formularios y botones | **Inter** (`--bs-font-sans-serif`) |
| Fallback | `system-ui`, `-apple-system`, `Segoe UI` |

Los títulos usan `letter-spacing: -0.02em`; los eyebrows y encabezados de tabla usan `letter-spacing` positivo y mayúsculas para dar ritmo sin aumentar el tamaño.

## Paleta y superficies

| Elemento | Clase / variable de referencia |
|---|---|
| Fondo general | `bg-body-tertiary` (`--bs-body-bg: #f8fafc`) |
| Tarjetas | `.card`: borde `1px` gris hielo (`--bs-border-color`), `border-radius: 0.75rem`, sombra suave (`--vit-shadow-card`) |
| Tarjetas interactivas | `.card-hover`: elevación de 2px y sombra apenas más presente al hover |
| Navbar | `.navbar.bg-white`: `rgba(255,255,255,.86)` + `backdrop-filter: blur(8px)`, `position: sticky` |
| Color primario | Verde esmeralda (`--bs-primary: #15803d`) vía `.btn-vit`, `.text-vit`, `.bg-vit` |
| Gris pizarra | `--bs-body-color: #334155`, `--bs-secondary-color: #64748b`, `--bs-border-color: #e2e8f0` |
| Éxito | `badge text-bg-success` / `alert alert-success` |
| Error | `badge text-bg-danger` / `alert alert-danger` |
| Advertencia | `badge text-bg-warning` / `alert alert-warning` |
| Información | `badge text-bg-info` / `alert alert-info` |
| Títulos | `h1`–`h6`, `.display-6`, con Plus Jakarta Sans |
| Encabezados de tabla | Fondo `#f1f5f9`, tipografía 0.72rem en mayúsculas, borde inferior fino |
| Filas | `table table-hover align-middle`, hover verde al 4.5% |
| Badges | `badge rounded-pill` o `badge text-bg-*` |
| Contadores de listado | `badge rounded-pill text-bg-light border text-secondary`, junto al subtítulo |
| Estados vacíos | `.vit-empty` con ícono tenue, título y sugerencia de ajustar filtros |

## Componentes

- Botón primario: `btn btn-vit` (verde institucional con hover/active más oscuro y sombra suave).
- Botón secundario: `btn btn-outline-secondary`.
- Botón de baja: `btn btn-danger` y siempre con confirmación mediante `<dialog>`.
- Transiciones: `0.2s ease` en `background-color`, `border-color`, `color`, `box-shadow` y `transform` de `.btn`, `.card` y `.nav-link`; foco visible con outline verde.
- Formularios: `form-label`, `form-control`, `form-select` y `form-check-input` (según widget, aplicados por `core.forms.EstiloBootstrapMixin`). Errores con `invalid-feedback d-block` y ayudas con `form-text`.
- Mensajes: `templates/partials/messages.html` usa `alert alert-success|danger|warning|info alert-dismissible fade show` con `btn-close` y `data-bs-dismiss="alert"`.
- Tablas: envolver siempre en `table-responsive` para pantallas chicas.

## Portada

- Hero sobrio `.vit-hero`: degradado blanco → verde muy claro, eyebrow, titular `display-6`, copy con `max-width` y CTA.
- CTA según sesión: autenticado → **Ir al dashboard** + **Ver presupuesto**; invitado → **Ingresar** + **Crear cuenta**.
- Cuatro tarjetas de línea (Vidrios `bi-layers`, Mamparas `bi-columns-gap`, Espejos `bi-brightness-high`, Cerramientos `bi-building`) con ícono lateral superior, descripción breve y enlace al catálogo (o al login si no hay sesión).

## Listados

Los cinco listados (usuarios, proveedores, clientes, catálogo y ventas) comparten:

- Encabezado con `h1` + subtítulo descriptivo + contador discreto (`{{ page_obj.paginator.count }}`).
- Filtros en `form method="get"` y resultados dentro del contenedor `data-live-search`.
- Estado vacío dentro de `{% empty %}` con ícono, mensaje y pista para ajustar búsqueda/filtros.
- `thead` limpio y filas con hover tenue; paginación conservando `query_base`.

## Dashboards por rol

`core.DashboardView` calcula KPIs **de solo lectura** en `_kpis()` y los pasa como `kpis` (`etiqueta`, `valor`, `icono`, `url`, `tono`). Cada KPI es una tarjeta con ícono a la izquierda y número destacado; el `tono` (`primary`, `warning`, `info`) solo elige el color del ícono.

- **ADM:** productos activos, stock bajo (`stock < 10`, umbral informativo `STOCK_BAJO` en `core/views.py`), clientes activos y ventas confirmadas; accesos a todos los módulos.
- **VENDEDOR:** mis ventas, borradores propios, productos activos y stock bajo; catálogo de solo lectura.
- **USUARIO:** productos disponibles, ítems en presupuesto (desde `request.session`) y categorías distintas; acceso a su presupuesto.

Los KPIs usan los mismos filtros que los listados (`activo=True`, `vendedor=request.user` cuando corresponde) y no escriben en base de datos.

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
- Apariencia: `dialog.rounded-3.shadow-lg.p-0` conteniendo `modal-content` con `modal-header`, `modal-body` y `modal-footer`; el CSS propio agrega borde gris hielo y radio `0.75rem`.
- Cerrar con `btn-close` (`data-modal-close`), click en backdrop y tecla `Escape`; el backdrop se oscurece con `dialog::backdrop` en el CSS propio.
- No poner lógica de negocio dentro del modal: solo presentación y acciones que apunten a URLs reales.

## Live search

- Input con ícono de lupa (`input-group`), `form-control` e `id` único del contenedor de resultados (`data-live-search`).
- Debounce de ~300 ms, `fetch` al backend y reemplazo del contenedor sin recargar la página.
- Event delegation en el contenedor para que los clicks sobrevivan al re-render.
- El filtro del backend respeta permisos por rol y usa `Q` objects.
- Actualizar la URL con `history.replaceState` para que el estado sea compartible; los filtros vigentes se conservan.

## Presupuesto en sesión (perfil USUARIO)

- Vista `/presupuesto/` con artículos seleccionados, cantidades y total estimado.
- La selección vive en `request.session`; no se persiste en base de datos en este alcance.
- Los botones de agregar/quitar son acciones reales con feedback por mensajes.

## Regla de oro de UI

**Nunca modificar atributos lógicos** (`id`, `name`, `action`, `method`, `data-*`, URLs, variables y bloques `{% if %}` / `{% for %}` de Django) al hacer ajustes visuales. Solo cambian clases y estructura visual. La validación y los permisos viven en backend. El pulido visual agregó consultas de solo lectura al dashboard; no introdujo nuevas escrituras ni cambió permisos.
