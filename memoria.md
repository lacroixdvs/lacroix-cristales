# Memoria — Vit Cristales

> Memoria viva del proyecto. Toda decisión relevante debe estar acá; si no está escrita, no existe.
> Guía maestra: [`inicio.md`](inicio.md).

## Estado actual

- **Fecha:** 2026-11-18
- **Fase:** 3 de 9 — Core y UI base (completada)
- **Ubicación:** `C:\Users\Nico\Desktop\lacroix-cristales`
- **Nombre comercial:** Vit Cristales (documentación e interfaz). La carpeta conserva el nombre `lacroix-cristales`.
- **Código generado:** `manage.py`, `config/` con settings separados, app `usuarios` con su migración inicial y app `core` con home, dashboard por rol, templates base/parciales y esqueletos JS. Aún no hay modelos de dominio ni CRUDs.
- **Verificación:** `python manage.py check` sin problemas y 4 tests de humo de `core` ejecutados con los settings de testing: **OK**.

## Stack definido

| Capa | Elección |
|---|---|
| Backend web | Django 5.x con MVT (Templates) |
| Frontend | TailwindCSS vía CDN, Alpine.js/JS vanilla, `<dialog>` nativo, live search |
| API | Django REST Framework + `django-filter` + `drf-spectacular` + `djangorestframework-simplejwt` |
| Autenticación | Sesiones para MVT; JWT (access/refresh) para API; grupos de Django Auth |
| Base de datos | SQLite en desarrollo; PostgreSQL en producción |
| Archivos | `FileSystemStorage` en dev; storage S3-compatible en prod (condicional por entorno) |
| Estáticos / servidor | WhiteNoise + Gunicorn |
| Deploy | Docker (multi-stage) + Render + Supabase (a configurar en Fase 8) |
| Tests | `python manage.py test` (sin pytest) |

## Decisiones confirmadas (2026-11-18)

1. **Login:** por `username`. El `email` es único y obligatorio.
2. **Roles:** los grupos `ADM`, `VENDEDOR` y `USUARIO` de Django Auth son la fuente de verdad. El campo `rol` del modelo `Usuario` se sincroniza desde esos grupos vía `signals`. El campo `activo` se vincula con `is_active`.
3. **Cotización del perfil USUARIO:** selección de artículos en `request.session` más una vista de armado de presupuesto. No se crea un modelo persistido en este alcance.
4. **Stock:** descuento dentro de `transaction.atomic` al pasar la venta al estado `CONFIRMADA`; reintegro al anular la venta o al darla de baja lógica.
5. **Catálogo:** requiere login. Se incluye registro público que asigna el rol `USUARIO` por defecto.
6. **Baja lógica de ventas:** solo `ADM` puede dar de baja ventas confirmadas. `VENDEDOR` crea, consulta y edita borradores.
7. **Unicidad y soft delete:** `unique=True` en `CUIT` de `Proveedor` y `Cliente`, y en `código` de `Producto`. Todos los modelos incluyen `activo = models.BooleanField(default=True)`.
8. **Marca:** carpeta `lacroix-cristales`, nombre comercial "Vit Cristales" en documentación e interfaz.

## Registro técnico de la Fase 2

- Dependencias instaladas en `.venv` con Python 3.12.5: **Django 5.2.19**, DRF 3.18.3, SimpleJWT 5.5.1, django-filter 25.2, drf-spectacular 0.30.0, dj-database-url 2.3.0, psycopg 3.3.9, whitenoise 6.12.0 y gunicorn 23.0.0.
- `AUTH_USER_MODEL = "usuarios.Usuario"` quedó definido en `config/settings/base.py` **antes** de generar cualquier migración.
- `manage.py`, `wsgi.py` y `asgi.py` cargan `.env` y toman el ambiente de `DJANGO_SETTINGS_MODULE` (default: `config.settings.development`). No se hardcodeó la selección de settings fuera de ese default.
- `.env` local creado desde `.env.example` con una `SECRET_KEY` aleatoria de desarrollo; el valor no se mostró en logs y no está versionado.
- Migración `usuarios/migrations/0001_initial.py` generada con `makemigrations usuarios`. **No se ejecutó `migrate`**: `db.sqlite3` existe pero está vacío (sin tablas), creado al consultar el historial de migraciones.
- En `production.py` se definieron cabeceras de seguridad (`SECURE_SSL_REDIRECT`, cookies seguras, HSTS y `SECURE_PROXY_SSL_HEADER`) y WhiteNoise. Esto es nuevo, no modifica un archivo previo, pero queda registrado por la regla de no tocar seguridad sin advertir.
- El storage S3/Supabase sigue pendiente para Fase 8; en `base.py` queda `FileSystemStorage` por defecto.

## Registro técnico de la Fase 3

- El rol efectivo se resuelve en `core/roles.py`: grupos de Django Auth como fuente de verdad con prioridad `ADM` > `VENDEDOR` > `USUARIO`, y fallback al campo `Usuario.rol` hasta que las señales de Fase 4 lo sincronicen.
- `DashboardView` usa `LoginRequiredMixin` y entrega a la plantilla `rol`, `rol_etiqueta`, `modulos` y flags `es_adm`/`es_vendedor`/`es_usuario`. La lógica de qué módulo se muestra vive en `MODULOS_POR_ROL` (backend), no en el template.
- Los tags `rol_actual` y `es_rol` solo presentan/condicionan la UI; no validan permisos.
- Tailwind se carga por CDN con un `tailwind.config` inline que define la paleta `primary` (verde) de `design.md`. No hay build step.
- `base.html` incluye los parciales `navbar`, `sidebar`, `messages` y `footer` de forma global. `messages.html` aplica clases por nivel del mensaje.
- `static/js/live-search.js` y `static/js/modales.js` son esqueletos genéricos configurados por atributos `data-*`; aún no apuntan a endpoints reales de dominio (eso llega con los CRUDs).
- `LOGIN_URL = "/accounts/login/"` y los enlaces de login/logout del navbar quedan como rutas previstas: se cablean recién en Fase 4.
- Se agregó `STATICFILES_DIRS = [BASE_DIR / "static"]` para que `{% static %}` resuelva los JS.

## Decisiones heredadas de `inicio.md`

- GitFlow simplificado, PRs chicos y enfocados, commits semánticos. **La IA nunca ejecuta Git: solo sugiere comandos.**
- Settings separados: `base.py`, `development.py`, `production.py`, `testing.py`.
- App `core` para vistas transversales; una app por dominio con sus propios forms, views, urls, serializers y tests.
- Serializers con patrón de 3 niveles (Base / Get / Post).
- Backend es la fuente de verdad en validaciones y permisos; el ocultamiento en templates es solo cosmético.
- Soft delete en todo modelo de dominio; nunca borrado físico desde la UI.
- Mensajes de feedback con `django.contrib.messages` en `partials/messages.html`.
- Migraciones: una por cambio lógico, con nombre descriptivo.
- Los archivos `.md` de contexto se actualizan al cerrar cada hito.

## Pendientes

- **Fase 4:** completar `usuarios` con registro público, login/logout, grupos `ADM`/`VENDEDOR`/`USUARIO` y señales de rol/`is_active` (el modelo y la migración inicial ya existen).
- **Fases 5-6:** CRUDs con baja lógica, cálculo de totales y control de stock.
- **Fase 7:** API, Swagger en `/api/schema/swagger/` y JWT.
- **Fases 8-9:** Docker/Render, README final y cierre de bitácora.

## Riesgos y recordatorios

- Ya existe la app `usuarios` y `AUTH_USER_MODEL` está configurado, pero **`migrate` todavía no se corrió**; se ejecutará cuando se completen las apps de dominio (Fase 5-6) o cuando se necesite probar auth.
- El cambio de estado de la venta y el movimiento de stock deben ocurrir en la misma transacción.
- No instalar dependencias nuevas sin justificar y consultar. Las de storage S3 se evalúan recién en Fase 8.
- No tocar `.env`, CORS, CSRF, `ALLOWED_HOSTS` ni settings de seguridad sin advertirlo antes.
- Los importes se manejan con `Decimal`, nunca con `float`.
