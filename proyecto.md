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
├── usuarios/             # Usuario custom (AbstractUser), grupos, signals
├── proveedores/          # Proveedor
├── clientes/             # Cliente mayorista
├── catalogo/             # Producto
├── ventas/               # Venta y DetalleVenta
├── api/                  # routers, serializers 3 niveles, JWT, Swagger
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── partials/         # navbar, sidebar, messages, footer
│   ├── registration/     # login, registro, reset
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
| `core` | Home, dashboard según rol, templates base y parciales | Planificada (Fase 3) |
| `usuarios` | `Usuario` custom, grupos `ADM`/`VENDEDOR`/`USUARIO`, registro y señales | Modelo y `0001_initial.py` creados en Fase 2; registro/señales en Fase 4 |
| `proveedores` | CRUD de proveedores con baja lógica | Planificada (Fase 6) |
| `clientes` | CRUD de clientes mayoristas con baja lógica | Planificada (Fase 5) |
| `catalogo` | CRUD de artículos con baja lógica | Planificada (Fase 6) |
| `ventas` | Ventas, detalles, totales y control de stock | Planificada (Fase 6) |
| `api` | Routers, serializers Base/Get/Post, JWT y Swagger | Planificada (Fase 7) |

## Modelos

Todos los modelos de dominio incluyen `activo = models.BooleanField(default=True)`.

### `usuarios.Usuario(AbstractUser)`

- Hereda `username` y `password`. Login por `username`.
- Propios: nombre (`first_name`), apellido (`last_name`), `email` (único y obligatorio), `contacto` (teléfono/WhatsApp), `rol` (`ADM`/`VENDEDOR`/`USUARIO`), `activo` (vinculado a `is_active`).
- `rol` se sincroniza desde los grupos de Django Auth mediante `signals`.
- `AUTH_USER_MODEL = "usuarios.Usuario"` se define antes de la primera migración.

### `proveedores.Proveedor`

- `razon_social`, `cuit` (`unique=True`), `contacto`, `email`, `direccion`, `activo`.

### `clientes.Cliente`

- Cliente mayorista: `razon_social`, `cuit` (`unique=True`), `contacto`, `email`, `direccion`, `descuento_mayorista` (Decimal opcional), `activo`.

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
