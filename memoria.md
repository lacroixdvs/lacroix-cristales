# Memoria — Vit Cristales

> Memoria viva del proyecto. Toda decisión relevante debe estar acá; si no está escrita, no existe.
> Guía maestra: [`inicio.md`](inicio.md).

## Estado actual

- **Fecha:** 2026-11-18
- **Fase:** 4 de 9 — Autenticación, roles y gestión de usuarios (completada)
- **Ubicación:** `C:\Users\Nico\Desktop\lacroix-cristales`
- **Nombre comercial:** Vit Cristales (documentación e interfaz). La carpeta conserva el nombre `lacroix-cristales`.
- **Código generado:** `manage.py`, `config/` con settings separados, app `core` (home, dashboard, UI base) y app `usuarios` completa: señales de roles, `cargar_roles`, auth, registro público y CRUD de usuarios para ADM. Aún no hay modelos de dominio (clientes/proveedores/catálogo/ventas).
- **Verificación:** `python manage.py check` sin problemas, `migrate` ejecutado en desarrollo, `cargar_roles` idempotente y 19 tests (4 de `core` + 15 de `usuarios`) **OK** con settings de testing.

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

- El rol efectivo se resuelve en `core/roles.py`: grupos de Django Auth con prioridad `ADM` > `VENDEDOR` > `USUARIO`, y fallback al campo `Usuario.rol`. Desde Fase 4 ambos se mantienen sincronizados (ver registro de Fase 4).
- `DashboardView` usa `LoginRequiredMixin` y entrega a la plantilla `rol`, `rol_etiqueta`, `modulos` y flags `es_adm`/`es_vendedor`/`es_usuario`. La lógica de qué módulo se muestra vive en `MODULOS_POR_ROL` (backend), no en el template.
- Los tags `rol_actual` y `es_rol` solo presentan/condicionan la UI; no validan permisos.
- Tailwind se carga por CDN con un `tailwind.config` inline que define la paleta `primary` (verde) de `design.md`. No hay build step.
- `base.html` incluye los parciales `navbar`, `sidebar`, `messages` y `footer` de forma global. `messages.html` aplica clases por nivel del mensaje.
- `static/js/live-search.js` y `static/js/modales.js` son esqueletos genéricos configurados por atributos `data-*`; aún no apuntan a endpoints reales de dominio (eso llega con los CRUDs).
- `LOGIN_URL = "/accounts/login/"` y los enlaces de login/logout del navbar quedan como rutas previstas: se cablean recién en Fase 4. **(Ya cableados en Fase 4.)**
- Se agregó `STATICFILES_DIRS = [BASE_DIR / "static"]` para que `{% static %}` resuelva los JS.

## Registro técnico de la Fase 4

- Sincronización bidireccional en `usuarios/signals.py`: `post_save` ajusta grupos cuando cambia `rol`; `m2m_changed` ajusta `rol` cuando cambian los grupos (prioridad ADM > VENDEDOR > USUARIO). `pre_save` guarda el rol original para no repetir trabajo y hace `is_active = activo`.
- `activo` es el campo canónico de baja lógica; `is_active` queda subordinado a él. Se extrajo esa responsabilidad del `save()` del modelo.
- Las señales se registran en `UsuariosConfig.ready()`; `apps.py` marca `default = True`.
- `cargar_roles` es idempotente. Los permisos de dominio todavía no existen, por lo que se omiten silenciosamente capturando `ContentType.DoesNotExist` y `Permission.DoesNotExist`; se reforzará al crear esas apps. La contraseña del admin inicial se lee de `--admin-password` o `ADMIN_PASSWORD` y nunca se imprime.
- El registro público usa `UserCreationForm` y fuerza `rol=Rol.USUARIO`; el `clean_email` es case-insensitive.
- `RolRequeridoMixin` / `SoloAdminMixin` validan en backend con `PermissionDenied` (403), no solo ocultando enlaces. El CRUD de usuarios es exclusivo de ADM; la baja es lógica (`activo=False`) e impide auto-baja.
- El test de humo de Fase 3 se adaptó: `rol_de()` prioriza grupos, pero como ahora las señales sincronizan `rol`, el escenario de prueba consiste en crear el usuario como USUARIO y asignarle el grupo VENDEDOR.
- `migrate` se ejecutó por primera vez en desarrollo. `makemigrations --check --dry-run` reporta "No changes detected".

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

- **Fases 5-6:** CRUDs con baja lógica, cálculo de totales y control de stock.
- **Fase 7:** API, Swagger en `/api/schema/swagger/` y JWT.
- **Fases 8-9:** Docker/Render, README final y cierre de bitácora.

## Riesgos y recordatorios

- `migrate` **ya se ejecutó en desarrollo** (Fase 4). Toda nueva app de dominio requerirá su propia migración antes de usarla.
- Si se crea un administrador con `cargar_roles --crear-admin`, la contraseña debe pasarse por variable de entorno `ADMIN_PASSWORD` en entornos compartidos para no dejar secretos en el historial de comandos.
- El cambio de estado de la venta y el movimiento de stock deben ocurrir en la misma transacción.
- No instalar dependencias nuevas sin justificar y consultar. Las de storage S3 se evalúan recién en Fase 8.
- No tocar `.env`, CORS, CSRF, `ALLOWED_HOSTS` ni settings de seguridad sin advertirlo antes.
- Los importes se manejan con `Decimal`, nunca con `float`.
