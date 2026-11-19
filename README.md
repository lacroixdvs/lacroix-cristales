# Vit Cristales — Sistema integral de gestión

**Vit Cristales** es una empresa dedicada a la venta e instalación de **vidrios, mamparas, espejos y cerramientos de oficinas**. Este proyecto digitaliza su operación comercial: administración de proveedores, clientes mayoristas, catálogo de artículos con stock, ventas con descuentos y control de inventario, con acceso por roles, API REST y despliegue en la nube.

> **Estado:** proyecto finalizado — **Fase 9 de 9 completada** (cierre y documentación para la EFI). Implementación, tests y despliegue detallados en [`bitacora.md`](bitacora.md).

---

## Índice

- [Arquitectura y stack](#arquitectura-y-stack)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Modelo de datos (DER lógico)](#modelo-de-datos-der-lógico)
- [Roles y permisos](#roles-y-permisos)
- [Endpoints principales](#endpoints-principales)
- [Instalación local paso a paso](#instalación-local-paso-a-paso)
- [Verificación y tests](#verificación-y-tests)
- [Despliegue con Docker y Render](#despliegue-con-docker-y-render)
- [Deploy productivo](#deploy-productivo)
- [Documentación adicional](#documentación-adicional)

---

## Arquitectura y stack

La solución es **híbrida**: una misma base de datos y un mismo modelo de permisos alimentan dos interfaces.

| Capa | Tecnología | Uso |
|---|---|---|
| Backend MVT | Django 5.x + Templates | Interfaz web para ADM, VENDEDOR y USUARIO |
| Frontend | TailwindCSS vía CDN, Alpine.js / JS vanilla, `<dialog>` nativo | Estilos, modales, dropdowns y live search sin build step |
| API REST | Django REST Framework + `django-filter` | Recursos bajo `/api/` con paginación, búsqueda y orden |
| Autenticación API | `djangorestframework-simplejwt` | Access (60 min) / refresh (1 día) + sesión para Swagger |
| Documentación API | `drf-spectacular` | Esquema OpenAPI y Swagger UI |
| Base de datos | SQLite (desarrollo) / PostgreSQL (producción) | `dj-database-url` + `psycopg[binary]` |
| Estáticos y servidor | WhiteNoise + Gunicorn | `CompressedManifestStaticFilesStorage` |
| Media | `FileSystemStorage` / S3-compatible (Supabase) | Condicional por variables de entorno |
| Empaquetado | Docker multi-stage, `docker-compose.yml`, Render Blueprint | Usuario no-root, healthchecks, `entrypoint.sh` |
| Tests | `python manage.py test` | 159 pruebas unitarias e integrales |

Los grupos de **Django Auth son la fuente de verdad** de los roles. El campo `Usuario.rol` y el ocultamiento de menú son derivados; la API usa `core.roles.rol_de()` con los mismos grupos para que MVT y REST coincidan exactamente.

---

## Estructura del proyecto

```text
lacroix-cristales/
├── config/
│   ├── settings/{base,development,testing,production}.py
│   ├── urls.py                 # admin, MVT, API y redirección /presupuesto/
│   └── wsgi.py / asgi.py
├── core/                       # home, dashboard por rol, roles, validators
│   └── management/commands/cargar_datos_demo.py
├── usuarios/                   # Usuario custom, señales, grupos, auth, CRUD, comando cargar_roles
├── proveedores/                # Proveedor (CRUD + baja lógica)
├── clientes/                   # Cliente mayorista (CUIT, descuento, baja lógica)
├── catalogo/                   # Producto, categorías, stock, presupuesto en sesión
├── ventas/                     # Venta, DetalleVenta, services.py (totales y stock)
├── api/                        # permissions, filters, viewsets, routers, URLs y tests
├── templates/                  # base.html, partials/, plantillas por app
├── static/  media/
├── Dockerfile  .dockerignore  docker-compose.yml  render.yaml  entrypoint.sh
├── requirements.txt  .env.example  manage.py
├── README.md  inicio.md  memoria.md  proyecto.md  bitacora.md  design.md
```

Cada app de dominio sigue el patrón vertical: **modelo → forms → vistas → URLs → serializers → admin → tests**. Los serializers (`<Modelo>BaseSerializer`, `<Modelo>GetSerializer`, `<Modelo>PostSerializer`) viven en su app; `api/` solo concentra permisos, filtros, viewsets, routers y tests.

---

## Modelo de datos (DER lógico)

```text
  auth.Group ──<N:M>── Usuario ──1──<N── Venta ──N──>1── Cliente
       │                                  │
       └──<N:M>── auth.Permission          ├──1──<N── DetalleVenta ──N──>1── Producto ──N──>1── Proveedor
                                          └──N──>1── Usuario (vendedor)
```

### Entidades y atributos clave

| Entidad | Atributos principales | Observaciones |
|---|---|---|
| **Usuario** (`usuarios.Usuario`) | `username` (único), `email` (único), `password`, `first_name`, `last_name`, `contacto`, `rol` (`ADM`/`VENDEDOR`/`USUARIO`), `activo`, `is_active`, `groups` | Extiende `AbstractUser`. `activo` es el estado canónico; una señal lo refleja en `is_active` y sincroniza `groups` ↔ `rol`. |
| **Group / Permission** (Django Auth) | `name`, `permissions` | Fuente de verdad de permisos. `cargar_roles` crea ADM (24), VENDEDOR (8) y USUARIO (1). |
| **Proveedor** | `razon_social`, `cuit` (único), `contacto`, `email`, `direccion`, `rubro`, `activo` | CUIT con formato `XX-XXXXXXXX-X`. |
| **Cliente** | `razon_social`, `cuit` (único), `contacto`, `email`, `direccion`, `descuento_mayorista` (0–100 %), `activo` | El descuento se aplica al total de cada venta. |
| **Producto** | `codigo` (único), `nombre`, `categoria` (`VIDRIO`/`MAMPARA`/`ESPEJO`/`CERRAMIENTO`), `descripcion`, `espesor`, `precio_unitario` (> 0), `stock` (≥ 0), `proveedor` (FK), `activo` | `PROTECT`: no se puede borrar un proveedor con productos. |
| **Venta** | `cliente` (FK), `vendedor` (FK a Usuario), `fecha` (auto), `estado` (`BORRADOR`/`CONFIRMADA`/`CANCELADA`), `observaciones`, `subtotal`, `descuento_mayorista`, `total`, `activo` | Ambas FK son `PROTECT`. El resumen de totales se persiste en la fila. |
| **DetalleVenta** | `venta` (FK `CASCADE`), `producto` (FK `PROTECT`), `cantidad` (≥ 1), `precio_unitario` (**snapshot**), `subtotal`, `activo` | `save()` calcula `subtotal = precio_unitario × cantidad`. |

### Cardinalidades

- `Usuario 1 ──< N Venta` como **vendedor** (`PROTECT`).
- `Cliente 1 ──< N Venta` (`PROTECT`).
- `Venta 1 ──< N DetalleVenta` (`CASCADE`).
- `Producto 1 ──< N DetalleVenta` (`PROTECT`).
- `Proveedor 1 ──< N Producto` (`PROTECT`).
- `Usuario N ──< N Group ──< N Permission` (relaciones de Django Auth).

### Reglas de integridad

1. **Baja lógica:** ningún CRUD de la UI ni de la API borra filas; se marca `activo=False`. En `Usuario` además `is_active=False`. Solo ADM puede dar de baja ventas.
2. **CUIT:** formato `XX-XXXXXXXX-X`, único; se normaliza desde forms, serializers y `clean()` del modelo.
3. **Montos:** `precio_unitario > 0`, `descuento_mayorista ∈ [0, 100]`, `cantidad ≥ 1`, `stock ≥ 0`.
4. **Snapshot de precio:** `DetalleVenta.precio_unitario` se copia del producto al agregar el ítem; cambios posteriores de precio no alteran ventas anteriores.
5. **Totales:** `Venta.recalcular_totales()` suma detalles activos, aplica el porcentaje del cliente y redondea a 2 decimales con `ROUND_HALF_UP`; `resumen()` expone descuento en importe y porcentaje.
6. **Confirmación:** `confirmar_venta()` valida borrador, ítems activos, productos activos y stock suficiente **antes** de escribir. Todo en `transaction.atomic()` con `select_for_update()`, sin descuentos parciales.
7. **Cancelación:** `cancelar_venta()` reintegra stock solo si la venta estaba `CONFIRMADA` y es idempotente. `dar_de_baja()` la cancela y marca `activo=False`.
8. **Mismo negocio en MVT y API:** los ViewSets de ventas delegan en `ventas.services`; no hay lógica duplicada de totales ni stock.

---

## Roles y permisos

| Módulo | ADM | VENDEDOR | USUARIO |
|---|:---:|:---:|:---:|
| Home / dashboard por rol | ✔ global | ✔ propio | ✔ básico |
| Usuarios | CRUD total | ✘ | ✘ |
| Proveedores | CRUD total | ✘ | ✘ |
| Clientes mayoristas | CRUD total | Solo lectura | ✘ |
| Catálogo de artículos | CRUD total | Solo lectura | Solo lectura + presupuesto |
| Ventas | CRUD total, baja de confirmadas | Crear/consultar/editar **solo sus borradores**, cargar ítems y confirmar | ✘ |
| Cancelar venta | ✔ | ✔ (propias, no borradas) | ✘ |
| Baja lógica de ventas | ✔ | ✘ | ✘ |
| Presupuesto en sesión | ✔ | ✔ | ✔ (propio) |
| API REST | CRUD total en los 5 recursos | Lectura de clientes/catálogo; gestionar solo sus ventas | Solo `GET` de productos activos |
| Enlace "API / Swagger" en navbar | ✔ | ✘ | ✘ |

- El registro público crea usuarios con rol `USUARIO`.
- La validación siempre ocurre en backend (mixins MVT y `core.roles.rol_de()` en la API); ocultar elementos en templates es solo cosmético.
- Solicitudes API sin credenciales devuelven **401**; con sesión válida pero rol insuficiente, **403**; objetos de otros vendedores se ocultan como **404**.

---

## Endpoints principales

### Web (MVT)

| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| GET | `/` | Home | Todos |
| GET | `/dashboard/` | Panel por rol | Autenticados |
| GET/POST | `/accounts/login/`, `/accounts/logout/` | Autenticación | Público / autenticados |
| GET/POST | `/accounts/registro/` | Registro público (rol USUARIO) | Público |
| GET/POST | `/usuarios/`, `/usuarios/nuevo/`, `/usuarios/<id>/editar/`, `/usuarios/<id>/baja/` | CRUD usuarios | ADM |
| GET/POST | `/proveedores/…` (`nuevo/`, `<id>/`, `editar/`, `baja/`, `reactivar/`) | CRUD proveedores | ADM |
| GET/POST | `/clientes/…` (`nuevo/`, `<id>/`, `editar/`, `baja/`, `reactivar/`) | CRUD clientes | ADM; VENDEDOR solo lectura |
| GET/POST | `/catalogo/…` (`nuevo/`, `<id>/`, `editar/`, `baja/`, `reactivar/`) | CRUD productos | ADM; VENDEDOR/USUARIO solo lectura |
| GET | `/catalogo/presupuesto/` (alias `/presupuesto/`) | Presupuesto en sesión | Todos los autenticados |
| GET/POST | `/ventas/…` (`nueva/`, `<id>/`, `editar/`, `confirmar/`, `cancelar/`, `baja/`, `detalles/agregar/`, `detalles/<id>/quitar/`) | Gestión de ventas | ADM / VENDEDOR (propias) |
| GET | `/admin/` | Django Admin | Superusuarios |

### API REST y documentación

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/token/` | Obtener access + refresh (JWT) |
| POST | `/api/token/refresh/` | Renovar access |
| GET | `/api/usuarios/`, `/api/proveedores/`, `/api/clientes/`, `/api/catalogo/`, `/api/ventas/` | Listado paginado (20) |
| GET | `/api/<recurso>/<id>/` | Detalle (serializer `Get`) |
| POST | `/api/<recurso>/` | Alta (serializer `Post`) |
| PUT / PATCH | `/api/<recurso>/<id>/` | Edición (serializer `Post`) |
| DELETE | `/api/<recurso>/<id>/` | **Baja lógica** (`activo=False`) |
| POST | `/api/ventas/<id>/confirmar/` | Confirmar borrador (valida y descuenta stock) |
| POST | `/api/ventas/<id>/cancelar/` | Cancelar y reintegrar stock |
| POST | `/api/ventas/<id>/detalles/agregar/` | Agregar ítem con snapshot de precio |
| DELETE | `/api/ventas/<id>/detalles/<detalle_id>/` | Quitar ítem y recalcular totales |
| GET | `/api/schema/` | Esquema OpenAPI YAML |
| GET | `/api/schema/swagger/` | Swagger UI |

Filtros disponibles: `django-filter` (`activo`, `estado`, `categoria`, `proveedor`, `rubro`, `cliente`, `vendedor`, `rol`) más `search` y `ordering` de DRF. Ejemplo: `/api/catalogo/?categoria=VIDRIO&activo=true&ordering=precio_unitario`.

---

## Instalación local paso a paso

Requisitos: **Python 3.12** y (opcional) Docker Desktop para production local.

### Windows (PowerShell)

```powershell
cd C:\Users\Nico\Desktop\lacroix-cristales

# 1. Entorno virtual e dependencias
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# 2. Variables de entorno (el .env ya incluye DJANGO_SETTINGS_MODULE=...development)
Copy-Item .env.example .env
# Editar .env: generar un SECRET_KEY propio

# 3. Base de datos, roles y datos de demostración
python manage.py migrate
python manage.py cargar_roles
python manage.py cargar_datos_demo

# 4. Servidor de desarrollo
python manage.py runserver
```

> `cargar_datos_demo` es **idempotente**: se puede ejecutar las veces que quiera sin duplicar registros ni descontar stock dos veces. Crea 3 usuarios, 3 proveedores, 4 clientes, 8 productos y 2 ventas de ejemplo.

### Linux / macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py cargar_roles
python manage.py cargar_datos_demo
python manage.py runserver
```

### Usuarios de demostración

| Usuario | Rol | Contraseña |
|---|---|---|
| `demo_admin` | ADM | `Demo1234!` |
| `demo_vendedor` | VENDEDOR | `Demo1234!` |
| `demo_usuario` | USUARIO | `Demo1234!` |

Si ya existe un superusuario creado con `cargar_roles --crear-admin`, use sus credenciales. Para cambiar la contraseña demo: `python manage.py cargar_datos_demo --password "OtraClave123!"`.

Ingrese a <http://127.0.0.1:8000/>, al dashboard por rol y a la API en <http://127.0.0.1:8000/api/schema/swagger/>. Para probar JWT:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_vendedor","password":"Demo1234!"}'
# Luego: Authorization: Bearer <access>
```

---

## Verificación y tests

```powershell
python manage.py check
python manage.py check --settings=config.settings.production   # requiere SECRET_KEY y entorno de prueba
python manage.py makemigrations --check --dry-run              # sin cambios pendientes
python manage.py spectacular --validate --file schema.yaml     # 0 errores, 0 warnings

$env:DJANGO_SETTINGS_MODULE = "config.settings.testing"
python manage.py test                                          # 159 tests → OK
```

La suite cubre: autenticación JWT, serializers de 3 niveles, filtros, permisos por rol (MVT y API), baja lógica sin borrado físico, stock y totales, acciones de ventas, generación del esquema y carga demo idempotente.

---

## Despliegue con Docker y Render

### Producción local con Docker Compose

```powershell
# 1. Completar en .env: SECRET_KEY, POSTGRES_PASSWORD, ADMIN_PASSWORD
$env:POSTGRES_PASSWORD = "cambiar-para-docker-compose"
docker compose up --build

# 2. La app queda en http://localhost:8000
# 3. Verificar logs/estado
docker compose ps
docker compose logs -f web
```

El servicio `web` espera a que PostgreSQL 16 esté sano (`pg_isready`) y ejecuta `entrypoint.sh`:

```text
migrate --noinput → cargar_roles → collectstatic --noinput → exec gunicorn config.wsgi:application
```

En compose las cabeceras HTTPS se desactivan (`SECURE_SSL_REDIRECT=False`, cookies no seguras) para permitir HTTP local; en producción permanecen activas.

### Render (Blueprint)

1. Crear cuenta en [Render](https://render.com/) y conectar el repositorio.
2. **New → Blueprint**, seleccionar el repo y la rama `develop`: `render.yaml` crea la base PostgreSQL y el servicio web Docker.
3. En el panel completar los valores marcados como `sync: false`: `ADMIN_PASSWORD` y, si se usa media remota, `SUPABASE_S3_*`.
4. `SECRET_KEY` se genera automáticamente (`generateValue: true`) y `DATABASE_URL` se inyecta desde la base (`fromDatabase`).
5. El healthcheck apunta a `/`; Render termina TLS en el proxy y la app confía en `X-Forwarded-Proto: https`.
6. Cada push a `develop` dispara un deploy automático (`autoDeploy: true`).

`production.py` lee todo desde entorno: hosts y CSRF (con soporte automático para `RENDER_EXTERNAL_HOSTNAME` y `.onrender.com`), PostgreSQL vía `dj-database-url` con `conn_max_age=600` y health checks, WhiteNoise y storage S3 condicional (`USE_SUPABASE_STORAGE=True` + credenciales completas).

> **Nota de verificación:** el entorno de desarrollo no tenía Docker instalado, por lo que la imagen y el compose se validaron por sintaxis YAML y `check` de producción, pero no se ejecutó `docker build` localmente.

---

## Deploy productivo

**Enlace al deploy:** _[completar aquí la URL pública de Render, por ejemplo `https://vit-cristales.onrender.com`]_

**Credenciales de demostración en producción:** _[completar solo si el tribunal debe usarlas; no publicar secretos reales]_

---

## Documentación adicional

| Archivo | Contenido |
|---|---|
| [`inicio.md`](inicio.md) | Guía maestra de arquitectura, metodología y estándares |
| [`memoria.md`](memoria.md) | Estado final, decisiones técnicas y recordatorios |
| [`proyecto.md`](proyecto.md) | Apps, modelos, endpoints y configuración de despliegue |
| [`bitacora.md`](bitacora.md) | Registro cronológico de las 9 fases y checklist del MVP |
| [`design.md`](design.md) | Guía visual UI/UX (paleta, componentes, layout) |

**Metodología:** GitFlow simplificado (`main`, `develop`, `feature/*`, `chore/*`, `docs/*`, `bugfix/*`, `hotfix/*`), Pull Requests chicos y commits semánticos. La IA sugiere comandos de Git pero **nunca los ejecuta**; la revisión humana es obligatoria antes de integrar cambios.
