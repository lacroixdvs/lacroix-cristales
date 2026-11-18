# Proyecto — Vit Cristales

> Arquitectura, apps, modelos, endpoints y estado de cada módulo.
> Se actualiza cuando cambia la estructura o se suma un módulo. Ver también [`memoria.md`](memoria.md).

## Alcance

Sistema de gestión para Vit Cristales (vidrios, mamparas de vidrio, espejos y cerramientos de oficinas). Cubre proveedores, clientes mayoristas, catálogo de artículos, ventas con control de stock, tres perfiles de acceso, API REST y despliegue en la nube.

## Árbol objetivo

```text
lacroix-cristales/
├── config/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── core/                 # home, dashboard por rol, partials, templatetags
├── usuarios/             # Usuario custom (AbstractUser), señales, forms, mixins,
                          # management commands (cargar_roles), views, urls, tests
├── clientes/             # Cliente mayorista: validators, forms, views, urls,
                          # admin, migrations, tests (patrón vertical)
├── proveedores/          # Proveedor
├── clientes/             # Cliente mayorista
├── catalogo/             # Producto
├── ventas/               # Venta y DetalleVenta
├── api/                  # permisos, filters, viewsets, routers, JWT, esquema,
                          # tests; los serializers 3 niveles viven en cada app de dominio
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── partials/         # navbar, sidebar, messages, footer, modal, live search
│   ├── registration/     # login, registro (reset pendiente)
│   ├── usuarios/
│   ├── proveedores/
│   ├── clientes/
│   ├── catalogo/
│   └── ventas/
├── static/{css,js,img}/
├── media/                # desarrollo, no versionar
├── docs/                 # documentación extra y capturas
├── manage.py
├── requirements.txt
├── .env / .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── render.yaml
├── build.sh
├── README.md
├── memoria.md
├── bitacora.md
├── proyecto.md
├── design.md
└── inicio.md
```

## Apps

| App | Responsabilidad | Estado |
|---|---|---|
| `config` | Configuración por ambiente, URLs raíz, WSGI/ASGI | Creada en Fase 2 (check OK) |
| `core` | Home, dashboard según rol, tags de rol y tests de humo | Creada en Fase 3 (check OK, 4 tests) |
| `usuarios` | `Usuario` custom, señales de roles, `cargar_roles`, auth y CRUD de usuarios | Completa en Fase 4 (check OK, 15 tests) |
| `proveedores` | CRUD de proveedores con baja lógica | Completa en Fase 6 (check OK, 16 tests) |
| `clientes` | CRUD de clientes mayoristas con baja lógica, validación de CUIT y descuento | Completa en Fase 5 (check OK, 25 tests) — patrón de referencia |
| `catalogo` | Productos, baja lógica y presupuesto en sesión | Completa en Fase 6 (check OK, 20 tests) |
| `ventas` | Ventas, detalles, totales y control de stock | Completa en Fase 6 (check OK, 22 tests) |
| `api` | Routers, permisos, filtros, JWT, esquema y Swagger; serializers 3 niveles en cada app de dominio | Completa en Fase 7 (check OK, 54 tests) |

## Capa de presentación (Fase 3)

- `templates/base.html`: Tailwind CDN con paleta `primary` verde, bloques `title`/`content` e inclusión global de los parciales.
- `templates/partials/`: `navbar.html`, `sidebar.html`, `messages.html` (estilos por nivel), `footer.html`, `modal-base.html` (`<dialog>`) y `live-search.html` (input + contenedor de resultados).
- `static/js/live-search.js`: debounce de 300 ms, `fetch`, reemplazo del contenedor, `history.replaceState`, event delegation y conservación de filtros vigentes (descarta solo `page`).
- `static/js/modales.js`: apertura por `data-modal-open`, cierre por `data-modal-close` y click en backdrop; Escape nativo.
- `core/roles.py` resuelve el rol efectivo en backend; `core/templatetags/roles.py` solo lo muestra/condiciona en la UI.
- Las rutas de autenticación (`/accounts/login/`, `/accounts/logout/`, `/accounts/registro/`) quedan cableadas desde Fase 4. Desde Fase 6 el sidebar tiene enlaces reales a todos los módulos de dominio y al presupuesto.

## Autenticación y roles (Fase 4)

- Login por `username` con sesiones de Django; logout por POST desde el navbar.
- Registro público en `/accounts/registro/` con `RegistroForm`: fuerza `rol=USUARIO` y grupo `USUARIO`.
- Grupos de Django Auth `ADM`, `VENDEDOR`, `USUARIO` creados/actualizados por `python manage.py cargar_roles` (idempotente). `--crear-admin` crea el administrador inicial solo si no existe; contraseña vía `--admin-password` o `ADMIN_PASSWORD`.
- `usuarios/signals.py` mantiene sincronizados grupo↔`rol` (prioridad ADM > VENDEDOR > USUARIO) y `activo`→`is_active`.
- `RolRequeridoMixin` y `SoloAdminMixin` validan en backend con 403. El CRUD de `/usuarios/` (listado con live search, alta, edición y baja lógica) es exclusivo de ADM.
- Baja lógica: `activo=False`, sin borrado físico; un admin no puede darse de baja a sí mismo.

## Módulo `clientes` (Fase 5 — patrón vertical)

- Modelo `Cliente` con `activo` para baja lógica y `descuento_mayorista` en `Decimal`.
- `validators.py` normaliza el CUIT (11 dígitos → `XX-XXXXXXXX-X`) y lo valida tanto en el modelo como en el form; unicidad en DB, modelo y formulario.
- Listado `/clientes/`: ADM y VENDEDOR; activos por defecto; filtro `activo=1|0|todos` solo para ADM (en backend se ignora para VENDEDOR); live search por razón social/CUIT/email y paginación de 20.
- Detalle, alta, edición, baja y reactivación: solo ADM. Baja y reactivación por POST con mensaje; baja con confirmación en `<dialog>`.
- Templates: `clientes/cliente_list.html`, `cliente_form.html`, `cliente_detail.html` y `partials/cliente_resultados.html`.
- `cargar_roles` refleja los permisos del modelo: ADM 8, VENDEDOR 1 (`view_cliente`), USUARIO 0.

## Módulos de la Fase 6

- **Común:** el validador de CUIT pasó a `core/validators.py` (`clientes/validators.py` solo re-exporta) y `core/forms.py` centraliza el estilo Tailwind.
- **`proveedores`:** `Proveedor` con CUIT normalizado/único, `rubro` opcional y baja lógica. CRUD exclusivo de ADM con live search, filtro de estado, paginación de 20, detalle, alta, edición, baja y reactivación con `<dialog>`.
- **`catalogo`:** `Producto` con categorías `VIDRIO`/`MAMPARA`/`ESPEJO`/`CERRAMIENTO`, precio > 0, stock y FK protegida a `Proveedor`. ADM hace CRUD; VENDEDOR y USUARIO leen y buscan por código/nombre/categoría; el filtro de inactivos se ignora para no-ADM.
- **Presupuesto:** `catalogo/presupuesto.py` guarda la selección en `request.session`; permite agregar, cambiar cantidades, quitar y vaciar, mostrando subtotal/total con precios vigentes. No descuenta stock ni crea ventas. Ruta `/catalogo/presupuesto/` (`/presupuesto/` redirige).
- **`ventas`:** `Venta` + `DetalleVenta` con snapshot de precio, descuento mayorista explícito y recálculo de totales en `ventas/services.py`.
- **Stock:** `confirmar_venta()` valida ítems activos, productos activos y stock suficiente antes de descontar; todo en `transaction.atomic()` con `select_for_update()`. `cancelar_venta()` y `dar_de_baja()` reintegran stock; solo ADM puede dar de baja ventas confirmadas.
- **Permisos:** ADM accede a todo; VENDEDOR crea borradores, carga/quita ítems, confirma y consulta solo sus ventas; USUARIO no entra a `ventas`.
- `cargar_roles` tras Fase 6: ADM 24 permisos, VENDEDOR 8, USUARIO 1 (`view_producto`).

## Modelos

Todos los modelos de dominio incluyen `activo = models.BooleanField(default=True)`.

### `usuarios.Usuario(AbstractUser)`

- Hereda `username` y `password`. Login por `username`.
- Propios: nombre (`first_name`), apellido (`last_name`), `email` (único y obligatorio), `contacto` (teléfono/WhatsApp), `rol` (`ADM`/`VENDEDOR`/`USUARIO`), `activo` (vinculado a `is_active`).
- `rol` y los grupos de Django Auth se sincronizan en ambos sentidos mediante `signals`.
- `AUTH_USER_MODEL = "usuarios.Usuario"` se define antes de la primera migración.

### `proveedores.Proveedor`

- `razon_social`, `cuit` (`unique=True`, normalizado), `contacto`, `email`, `direccion`, `rubro` (opcional), `activo`. Los productos referenciados usan `on_delete=PROTECT`.

### `clientes.Cliente`

- Cliente mayorista: `razon_social`, `cuit` (`unique=True`, formato `XX-XXXXXXXX-X` normalizado), `contacto`, `email` (opcional), `direccion`, `descuento_mayorista` (`DecimalField` 0–100, default 0), `activo`.

### `catalogo.Producto`

- `codigo` (`unique=True`), `nombre`, `categoria` (`VIDRIO` / `MAMPARA` / `ESPEJO` / `CERRAMIENTO`), `descripcion`, `espesor`, `precio_unitario` (`DecimalField` > 0), `stock` (`PositiveIntegerField`), `proveedor` (FK a `Proveedor`, `PROTECT`), `activo`.

### `ventas.Venta`

- `cliente` (FK a `Cliente`, `PROTECT`), `vendedor` (FK a `Usuario`, `PROTECT`; el form solo ofrece usuarios del grupo `VENDEDOR`), `fecha` (`auto_now_add`), `estado` (`BORRADOR` / `CONFIRMADA` / `CANCELADA`), `observaciones` (opcional), `subtotal`, `descuento_mayorista` (snapshot del cliente), `total` (calculado), `activo`.

### `ventas.DetalleVenta`

- `venta` (FK con `related_name="detalles"`), `producto` (FK a `Producto`, `PROTECT`), `cantidad` (`>= 1`), `precio_unitario` (snapshot del catálogo al crear el detalle), `subtotal` (calculado), `activo`.

### Relaciones

```text
Proveedor 1 ──── * Producto
Cliente 1 ──── * Venta * ──── * DetalleVenta * ──── 1 Producto
Usuario (vendedor) 1 ──── * Venta
```

## Reglas de negocio

- `subtotal = cantidad × precio_unitario`; `total = (suma de subtotales activos) − descuento_mayorista%` del cliente, redondeado a 2 decimales (`ROUND_HALF_UP`). El descuento se persiste y se muestra por porcentaje e importe.
- El `precio_unitario` del detalle queda como snapshot histórico; no se recalcula si cambia el catálogo.
- Con `transaction.atomic` y `select_for_update()`: al pasar a `CONFIRMADA` se validan todos los ítems y se descuenta el stock solo si todo pasa; al cancelar o dar de baja se reintegra.
- Baja lógica en todos los modelos; ninguna acción de UI borra filas físicamente.
- Importes con `Decimal`, nunca `float`.
- Validaciones en modelos/forms/serializers; las reglas cruzadas siempre en backend.

## Roles y permisos

| Módulo | ADM | VENDEDOR | USUARIO |
|---|:---:|:---:|:---:|
| Home / dashboard por rol | ✔ global | ✔ propio | ✔ básico |
| Usuarios | CRUD total | ✘ | ✘ |
| Proveedores | CRUD total | ✘ | ✘ |
| Clientes mayoristas | CRUD total | Solo lectura | ✘ |
| Catálogo de artículos | CRUD total | Solo lectura | Solo lectura + seleccionar |
| Ventas | CRUD total | Crear / consultar / editar borradores, cargar ítems y confirmar (solo propias) | ✘ |
| Baja lógica de ventas | ✔ (incluso confirmadas) | ✘ | ✘ |
| Presupuesto en sesión | ✔ | ✔ | ✔ (propio) |
| API | CRUD total en los 5 recursos, baja de ventas y acciones de stock | Lectura de clientes/catálogo; crear y gestionar solo sus ventas (confirmar/cancelar borradores); sin baja de ventas | Solo GET de productos activos en `/api/catalogo/` |

Los grupos de Django Auth son la fuente de verdad de permisos; el campo `rol` y el ocultamiento en templates son derivados/cosméticos. La API usa los mismos grupos vía `core.roles.rol_de()`, no permisos de modelo de DRF.

## Endpoints

**Web (MVT) implementados:** `/`, `/dashboard/`, `/accounts/login/`, `/accounts/registro/`, `/usuarios/`, `/proveedores/`, `/clientes/`, `/catalogo/`, `/catalogo/presupuesto/` (alias: `/presupuesto/`), `/ventas/`.

**API REST implementada:** `/api/token/`, `/api/token/refresh/`, `/api/usuarios/`, `/api/proveedores/`, `/api/clientes/`, `/api/catalogo/`, `/api/ventas/`, `/api/schema/`, `/api/schema/swagger/`.

Acciones de ventas: `POST /api/ventas/<id>/confirmar/`, `POST /api/ventas/<id>/cancelar/`, `POST /api/ventas/<id>/detalles/agregar/`, `DELETE /api/ventas/<id>/detalles/<detalle_id>/`. Todas delegan en `ventas.services`.

**Configuración API:** autenticación JWT (Bearer) + sesión para Swagger, `IsAuthenticated` global, paginación de 20, filtros `django-filter` / `search` / `ordering`, metadata OpenAPI "Vit Cristales API" v1.0.0.

## Convenciones

- Un serializer por app de dominio con patrón de 3 niveles: `<Modelo>BaseSerializer`, `<Modelo>GetSerializer`, `<Modelo>PostSerializer`. `api/` solo agrupa permisos, filtros, viewsets, routers y tests (no tiene modelos ni migraciones).
- Los `ViewSet` usan el `GetSerializer` para `list`/`retrieve` y el `PostSerializer` para escrituras; `DELETE` hace baja lógica (`activo=False`), jamás borrado físico.
- Forms en la app dueña del modelo; `select_related`/`prefetch_related` en listados y detalles.
- Mensajes de éxito/error en `templates/partials/messages.html`.
- Una migración por cambio lógico, con nombre descriptivo.
