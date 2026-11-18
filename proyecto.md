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
├── api/                  # routers, serializers 3 niveles, JWT, Swagger
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
| `proveedores` | CRUD de proveedores con baja lógica | Planificada (Fase 6) |
| `clientes` | CRUD de clientes mayoristas con baja lógica, validación de CUIT y descuento | Completa en Fase 5 (check OK, 25 tests) — patrón de referencia |
| `catalogo` | CRUD de artículos con baja lógica | Planificada (Fase 6) |
| `ventas` | Ventas, detalles, totales y control de stock | Planificada (Fase 6) |
| `api` | Routers, serializers Base/Get/Post, JWT y Swagger | Planificada (Fase 7) |

## Capa de presentación (Fase 3)

- `templates/base.html`: Tailwind CDN con paleta `primary` verde, bloques `title`/`content` e inclusión global de los parciales.
- `templates/partials/`: `navbar.html`, `sidebar.html`, `messages.html` (estilos por nivel), `footer.html`, `modal-base.html` (`<dialog>`) y `live-search.html` (input + contenedor de resultados).
- `static/js/live-search.js`: debounce de 300 ms, `fetch`, reemplazo del contenedor, `history.replaceState`, event delegation y conservación de filtros vigentes (descarta solo `page`).
- `static/js/modales.js`: apertura por `data-modal-open`, cierre por `data-modal-close` y click en backdrop; Escape nativo.
- `core/roles.py` resuelve el rol efectivo en backend; `core/templatetags/roles.py` solo lo muestra/condiciona en la UI.
- Las rutas de autenticación (`/accounts/login/`, `/accounts/logout/`, `/accounts/registro/`) quedan cableadas desde Fase 4. `clientes` ya tiene su enlace en el sidebar (Fase 5); los demás módulos de dominio siguen previstos.

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

## Modelos

Todos los modelos de dominio incluyen `activo = models.BooleanField(default=True)`.

### `usuarios.Usuario(AbstractUser)`

- Hereda `username` y `password`. Login por `username`.
- Propios: nombre (`first_name`), apellido (`last_name`), `email` (único y obligatorio), `contacto` (teléfono/WhatsApp), `rol` (`ADM`/`VENDEDOR`/`USUARIO`), `activo` (vinculado a `is_active`).
- `rol` y los grupos de Django Auth se sincronizan en ambos sentidos mediante `signals`.
- `AUTH_USER_MODEL = "usuarios.Usuario"` se define antes de la primera migración.

### `proveedores.Proveedor`

- `razon_social`, `cuit` (`unique=True`), `contacto`, `email`, `direccion`, `activo`.

### `clientes.Cliente`

- Cliente mayorista: `razon_social`, `cuit` (`unique=True`, formato `XX-XXXXXXXX-X` normalizado), `contacto`, `email` (opcional), `direccion`, `descuento_mayorista` (`DecimalField` 0–100, default 0), `activo`.

### `catalogo.Producto`

- `codigo` (`unique=True`), `nombre`, `categoria` (`Vidrio` / `Mampara` / `Espejo` / `Cerramiento de oficina`), `descripcion`, `espesor`, `precio_unitario` (Decimal), `stock`, `proveedor` (FK a `Proveedor`), `activo`.

### `ventas.Venta`

- `cliente` (FK a `Cliente`), `vendedor` (FK a `Usuario`, restringido al grupo `VENDEDOR`), `fecha`, `estado` (`BORRADOR` / `CONFIRMADA` / `ANULADA`), `total` (calculado), `activo`.

### `ventas.DetalleVenta`

- `venta` (FK), `producto` (FK), `cantidad`, `precio_unitario` (copia del catálogo al crear el detalle), `subtotal` (calculado), `activo`.

### Relaciones

```text
Proveedor 1 ──── * Producto
Cliente 1 ──── * Venta * ──── * DetalleVenta * ──── 1 Producto
Usuario (vendedor) 1 ──── * Venta
```

## Reglas de negocio

- `subtotal = cantidad × precio_unitario`; `total = suma de subtotales activos`.
- El `precio_unitario` del detalle queda como snapshot histórico; no se recalcula si cambia el catálogo.
- Con `transaction.atomic`: al pasar a `CONFIRMADA` se valida y descuenta el stock; al anular o dar de baja se reintegra.
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
| Ventas | CRUD total | Crear / consultar / editar borradores | ✘ |
| Baja lógica de ventas | ✔ (incluso confirmadas) | ✘ | ✘ |
| Presupuesto en sesión | ✔ | ✔ | ✔ (propio) |
| API | Según permisos | Según permisos | Solo GET de catálogo |

Los grupos de Django Auth son la fuente de verdad de permisos; el campo `rol` y el ocultamiento en templates son derivados/cosméticos.

## Endpoints previstos

**Web (MVT):** `/`, `/dashboard/`, `/accounts/login/`, `/accounts/registro/`, `/usuarios/`, `/proveedores/`, `/clientes/`, `/catalogo/`, `/ventas/`, `/presupuesto/`.

**API REST:** `/api/token/`, `/api/token/refresh/`, `/api/usuarios/`, `/api/proveedores/`, `/api/clientes/`, `/api/catalogo/`, `/api/ventas/`, `/api/schema/swagger/`.

## Convenciones

- Un serializer por app con patrón de 3 niveles: `<Modelo>BaseSerializer`, `<Modelo>GetSerializer`, `<Modelo>PostSerializer`.
- Forms en la app dueña del modelo; `select_related`/`prefetch_related` en listados y detalles.
- Mensajes de éxito/error en `templates/partials/messages.html`.
- Una migración por cambio lógico, con nombre descriptivo.
