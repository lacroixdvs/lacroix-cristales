# Vit Cristales

Sistema de gestión para Vit Cristales, empresa dedicada a **vidrios, mamparas de vidrio, espejos y cerramientos de oficinas**. Administra proveedores, clientes mayoristas, catálogo de artículos y ventas con control de stock, con tres perfiles de acceso, API REST y despliegue en la nube.

> **Estado:** proyecto en construcción — Fase 1 de 9 completada (contexto y cimentación). Todavía no hay código Django ejecutable. Ver [`bitacora.md`](bitacora.md).

## Documentación

| Archivo | Contenido |
|---|---|
| [`inicio.md`](inicio.md) | Guía maestra de arquitectura, metodología y estándares |
| [`memoria.md`](memoria.md) | Estado actual, decisiones y pendientes |
| [`proyecto.md`](proyecto.md) | Apps, modelos, roles y endpoints |
| [`design.md`](design.md) | Guía visual UI/UX |

## Stack

- Django 5.x (MVT con Templates) + TailwindCSS vía CDN + Alpine.js/JS vanilla.
- Django REST Framework, SimpleJWT (access/refresh), `django-filter` y `drf-spectacular` (Swagger).
- SQLite en desarrollo / PostgreSQL en producción; WhiteNoise + Gunicorn.
- Docker + Render + Supabase (storage S3 condicional por variable de entorno).
- Tests con `python manage.py test`.

## Roles

| Perfil | Alcance |
|---|---|
| `ADM` | Acceso total a usuarios, proveedores, clientes, catálogo y ventas; único perfil que puede dar de baja ventas confirmadas |
| `VENDEDOR` | Crea, consulta y edita borradores de ventas; consulta clientes mayoristas y artículos |
| `USUARIO` | Solo lectura del catálogo y armado de presupuesto en sesión |

El registro público crea usuarios con el rol `USUARIO` por defecto. Los permisos se validan siempre en backend; el ocultamiento en templates es solo cosmético.

## Estructura (objetivo)

```text
config/            settings por ambiente, urls, wsgi/asgi
core/              home, dashboard por rol, partials
usuarios/          Usuario custom (AbstractUser) y grupos
proveedores/       Proveedor
clientes/          Cliente mayorista
catalogo/          Producto
ventas/            Venta y DetalleVenta
api/               routers, serializers Base/Get/Post, JWT, Swagger
templates/         base.html, partials/, una carpeta por app
static/            css, js, img
media/             archivos subidos en desarrollo (no versionar)
```

El detalle completo está en [`proyecto.md`](proyecto.md).

## Variables de entorno

Copiar `.env.example` a `.env` y completar los valores reales. **`.env` nunca se versiona.**

| Variable | Uso |
|---|---|
| `DJANGO_SETTINGS_MODULE` | Módulo de settings activo |
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | Modo depuración |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma |
| `DATABASE_URL` | URL de PostgreSQL en producción |
| `USE_SUPABASE_STORAGE` / `SUPABASE_S3_*` | Storage de media compatible con S3 |

## Instalación (prevista)

> Estos comandos se validarán cuando se genere la estructura base en la Fase 2.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Completar SECRET_KEY en .env
python manage.py migrate
python manage.py runserver
```

## Verificación

```powershell
python manage.py check
python manage.py test
```

## API

- Autenticación: `POST /api/token/` y `POST /api/token/refresh/`.
- Recursos: `/api/usuarios/`, `/api/proveedores/`, `/api/clientes/`, `/api/catalogo/`, `/api/ventas/`.
- Documentación interactiva: `/api/schema/swagger/`.
- Serializers con patrón de 3 niveles (Base / Get / Post) en cada app.

## Despliegue

Pendiente (Fase 8): `Dockerfile` multi-stage, `docker-compose.yml`, `.dockerignore`, `render.yaml`, `build.sh`, Gunicorn + WhiteNoise y media en Supabase Storage.

## Metodología

GitFlow simplificado (`main`, `develop`, `feature/*`, `bugfix/*`, `hotfix/*`), Pull Requests chicos y commits semánticos. La IA **sugiere** comandos de Git pero nunca los ejecuta; la revisión humana es obligatoria antes de integrar cualquier cambio.
