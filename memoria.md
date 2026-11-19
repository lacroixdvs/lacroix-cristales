# Memoria — Vit Cristales

> Memoria viva del proyecto. Toda decisión relevante debe estar acá; si no está escrita, no existe.
> Guía maestra: [`inicio.md`](inicio.md).

## Estado actual

- **Fecha:** 2026-11-18
- **Fase:** 9 de 9 — Cierre del proyecto y documentación final para la EFI, **completada**
- **Ubicación:** `C:\Users\Nico\Desktop\lacroix-cristales`
- **Nombre comercial:** Vit Cristales (documentación e interfaz). La carpeta conserva el nombre `lacroix-cristales`.
- **Código generado:** `manage.py`, `config/`, `core`, `usuarios`, `clientes`, `proveedores`, `catalogo`, `ventas`, `api`, artefactos de deploy (`Dockerfile`, `docker-compose.yml`, `render.yaml`, `entrypoint.sh`, `.dockerignore`), comando `cargar_datos_demo` y documentación final (`README.md`, `proyecto.md`, `bitacora.md`). **Proyecto completo.**
- **Verificación:** `python manage.py check` (dev y production) sin problemas, `migrate` ejecutado en desarrollo, `cargar_roles` y `cargar_datos_demo` ejecutados (el segundo dos veces, sin duplicados), esquema OpenAPI validado sin errores ni warnings y **159 tests OK** con settings de testing. Docker no está disponible localmente: imagen y compose sin validación de runtime.

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
| Deploy | Docker (multi-stage) + Render Blueprint + Supabase S3 opcional (configurado en Fase 8) |
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

## Registro técnico de la Fase 5

- `clientes` es el **patrón vertical de referencia** para Fase 6: modelo con validadores, form con `clean_*`, vistas con mixins de rol, templates con parcial de resultados, admin, migración y carpeta `tests/`.
- CUIT: `clientes/validators.py` expone `normalizar_cuit()` y `CUIT_FORMATO`. Acepta 11 dígitos o `XX-XXXXXXXX-X` y normaliza a este último formato. Se usa en `Modelo.clean()` (para el admin) y en `ClienteForm.clean_cuit()` (con control de unicidad excluyendo la instancia actual). `unique=True` en la DB como última barrera.
- Descuento mayorista: `DecimalField(max_digits=5, decimal_places=2)` con `MinValueValidator(0)` y `MaxValueValidator(100)` en el modelo, más `clean_descuento_mayorista()` en el form. Nunca `float`.
- `ClienteListView` (`ADM` + `VENDEDOR`) filtra activos por defecto. El parámetro `activo` (`1`/`0`/`todos`) solo tiene efecto para ADM: para VENDEDOR se fuerza `activo=True` en el queryset, aunque envíe `?activo=0`. El control está en backend, no en la ocultación del `<select>`.
- Live search con `Q` sobre razón social, CUIT y email; respuesta parcial cuando llega `X-Requested-With: XMLHttpRequest`. `static/js/live-search.js` ahora preserva los query params vigentes y solo descarta `page`, para no perder el filtro de estado al escribir.
- Detalle, alta, edición, baja y reactivación son **solo ADM** (`SoloAdminMixin`). Baja y reactivación son POST con mensaje de feedback; la baja usa `<dialog>` de confirmación. No hay borrado físico.
- `cargar_roles` se volvió a ejecutar y asignó los permisos ya existentes de `clientes`: ADM 8, VENDEDOR 1 (`view_cliente`), USUARIO 0 (sigue esperando `catalogo.Producto`).
- `email` de `Cliente` es opcional (`blank=True`); no se declaró único porque no fue parte de los requisitos.

## Registro técnico de la Fase 6

- El validador de CUIT se movió a `core/validators.py`. `clientes/validators.py` quedó como re-export para no romper importaciones existentes, y `Cliente` importa directamente desde `core`. El mixin de estilos Tailwind también se centralizó en `core/forms.py` (`EstiloTailwindMixin`).
- `Proveedor` reutiliza el mismo CUIT normalizado que `Cliente` y agrega `rubro` opcional. Su CRUD es **solo ADM**; el filtro `activo` y el live search funcionan como en `clientes` (razón social/CUIT/email/rubro).
- `Producto.categoria` usa `TextChoices` (`VIDRIO`, `MAMPARA`, `ESPEJO`, `CERRAMIENTO`). `precio_unitario` tiene `MinValueValidator(0.01)` en el modelo y `clean_precio_unitario()` en el form. `proveedor` es FK con `PROTECT`, por lo que dar de baja un proveedor nunca borra sus productos (la baja es lógica).
- En `catalogo`, ADM hace CRUD; VENDEDOR y USUARIO leen y buscan. El filtro de estado se ignora en backend para no-ADM (igual que en `clientes`). El detalle de productos inactivos tampoco es accesible para ellos.
- `catalogo/presupuesto.py` guarda `{producto_id: cantidad}` en `request.session` bajo la clave `presupuesto`. `resumen()` recalcula importes con los precios **vigentes** del catálogo y solo considera productos activos; no toca stock ni crea `Venta`. Se expone en `/catalogo/presupuesto/` y `/presupuesto/` redirige a esa ruta (para no duplicar el namespace `catalogo`).
- `DetalleVenta.precio_unitario` es un **snapshot**: se copia de `Producto` al agregar el ítem y `DetalleVenta.save()` calcula `subtotal`. Los servicios usan `Decimal(...)` de forma explícita porque los valores pueden llegar como strings desde helpers/forms.
- `Venta` persiste `subtotal`, `descuento_mayorista` y `total`. `recalcular_totales()` suma detalles activos, aplica el porcentaje del cliente y redondea a 2 decimales con `ROUND_HALF_UP`. `resumen()` devuelve el descuento en importe y porcentaje para mostrarlo explícitamente.
- `confirmar_venta()` valida todo antes de escribir: borrador, ítems activos, productos activos y `stock >= cantidad`. Recién después descuenta y cambia el estado. Todo dentro de `transaction.atomic()` con `select_for_update()` sobre la venta y los productos, por lo que un `ValidationError` revierte la transacción completa y no quedan descuentos parciales.
- `cancelar_venta()` reintegra stock solo si la venta estaba `CONFIRMADA`; es idempotente para ventas ya canceladas. `dar_de_baja()` reutiliza esa cancelación y además marca `activo=False`; solo ADM puede invocarla.
- VENDEDOR opera únicamente sobre **sus propios borradores**: no ve detalles de otras ventas, no edita confirmadas y no da de bajas. ADM ve y opera todo. USUARIO no accede a `ventas`.
- `PERMISOS_POR_ROL` de `cargar_roles` ya contenía los permisos de Fase 6; alcanzó con volver a ejecutarlo tras migrar: ADM 24, VENDEDOR 8, USUARIO 1 (`view_producto`).

## Registro técnico de la Fase 7

- DRF usa JWT primero y sesión después. Eso hace que un request sin credenciales devuelva **401** (JWT entrega `WWW-Authenticate: Bearer`), mientras que los roles insuficientes con sesión válida devuelvan **403**. `IsAuthenticated` es el permiso global; cada ViewSet lo refine con permisos de rol propios basados en `core.roles.rol_de()`, no en permisos de modelo, para que API y MVT coincidan exactamente.
- Los serializers viven en cada app de dominio (`usuarios`, `proveedores`, `clientes`, `catalogo`, `ventas`), nunca centralizados en `api`. `api/` solo tiene permisos, filtros, viewsets, routers y tests. Cada app respeta `<Modelo>BaseSerializer` → `<Modelo>GetSerializer` → `<Modelo>PostSerializer`.
- Los `GetSerializer` enriquecen la lectura: grupos y etiqueta de rol (usuario), conteo de productos/proveedor y ventas/cliente, proveedor anidado y etiqueta de categoría (producto), y cliente/vendedor anidados + detalles con snapshot + resumen de descuento (venta).
- Los `PostSerializer` de proveedor y cliente declaran `cuit` de forma explícita para **no heredar el `RegexValidator` del modelo** (que exige guiones). Así `normalizar_cuit()` puede aceptar 11 dígitos, validar formato y controlar unicidad en un solo lugar. `validate_cuit` excluye la propia instancia en updates.
- `VentaViewSet.perform_create()` fuerza `vendedor=request.user` cuando el rol es VENDEDOR, ignorando un `vendedor` ajeno enviado en el payload. `VentaPermission` complementa el queryset: VENDEDOR solo ve sus ventas activas; la baja (DELETE) es ADM-only; las acciones que mutan requieren borrador propio, salvo `confirmar`, donde el servicio devuelve 400 si el estado no es `BORRADOR` (igual que el MVT).
- Las acciones `confirmar`, `cancelar`, `agregar_item` y `quitar_item` delegan en `ventas.services`. `_ejecutar_servicio()` traduce `django.core.exceptions.ValidationError` a `rest_framework.exceptions.ValidationError` (400), de modo que no se duplica ninguna regla de stock/totales.
- `perform_destroy()` jamás borra filas: setea `activo=False`. En `UsuarioViewSet` se persiste explícitamente `is_active=False` junto con `activo=False` porque `save(update_fields=[...])` no incluye el campo que calcula la señal `pre_save`. En ventas se llama a `services.dar_de_baja()` para reintegrar stock. Un admin no puede darse de baja a sí mismo (400).
- Filtros `django-filter` por `activo` (booleano), `estado`, `categoria`, `proveedor`, `rubro`, `cliente`, `vendedor` y `rol`, más `search` y `ordering` de DRF. Para no-ADM los querysets de clientes, catálogo y ventas filtran por `activo=True` (y ventas además por vendedor), incluso si el query param pide inactivos.
- El esquema se genera con `manage.py spectacular --validate`: **0 errores, 0 warnings**. Para lograrlo, `VentaViewSet.get_queryset()` contempla `swagger_fake_view`, se removió un `source` redundante en `categoria_etiqueta` y se anotaron todos los `SerializerMethodField` con `@extend_schema_field`. `SPECTACULAR_SETTINGS.SERVE_INCLUDE_SCHEMA=False` hace que Swagger UI fetchie `/api/schema/`.
- No se agregaron dependencias: DRF, SimpleJWT, django-filter y drf-spectacular ya figuraban en `requirements.txt` y estaban instalados desde Fase 2.
- Se subió el `SECRET_KEY` de testing a 56 caracteres para eliminar el `InsecureKeyLengthWarning` de PyJWT en la suite (no afecta producción ni desarrollo).

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

## Registro técnico de la Fase 8

- `production.py` ya no exige `DATABASE_URL`: si falta, cae al SQLite de `base.py` para poder levantar el contenedor local y correr healthchecks. Con `DATABASE_URL`, `dj_database_url.parse()` recibe `conn_max_age=600` y `conn_health_checks=True` (recomendado en Render porque la BD puede reiniciarse).
- Render inyecta `RENDER_EXTERNAL_HOSTNAME`. El settings lo agrega a `ALLOWED_HOSTS` junto con `.onrender.com` (comodín de subdominio de Django) y deriva `https://*.onrender.com` en `CSRF_TRUSTED_ORIGINS`, que Django soporta desde 4.0. Si no hay hosts configurados, quedan `localhost` y `127.0.0.1` como fallback.
- Las cabeceras de seguridad son estrictas por defecto (`SECURE_SSL_REDIRECT=True`, cookies seguras, HSTS 1 año) pero se pueden desactivar una por una por entorno. En `docker-compose.yml` se desactivan explícitamente para probar por HTTP; en `render.yaml` quedan activas y se confía en `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` porque Render termina TLS en el proxy.
- WhiteNoise se inserta en posición 1 del middleware (después de `SecurityMiddleware`) y se usa `CompressedManifestStaticFilesStorage`. Si `collectstatic` falla por un estático referenciado inexistente, `STATICFILES_STORAGE_BACKEND` permite bajar a `CompressedStaticFilesStorage` sin tocar código.
- El storage S3 solo se activa con `USE_SUPABASE_STORAGE=True` **y** `SUPABASE_S3_ACCESS_KEY`, `SECRET_KEY`, `BUCKET` y `ENDPOINT` completos. El import de `storages.backends.s3` es diferido y lanza `ImproperlyConfigured` con un mensaje claro si faltan las librerías. `default_acl=None` evita problemas de ACL con Supabase; `SUPABASE_S3_PUBLIC_URL` permite fijar la URL pública del bucket para `MEDIA_URL`.
- `entrypoint.sh` usa `set -eu`, corre migrate → cargar_roles → collectstatic y cierra con `exec gunicorn ...` para que el PID 1 sea Gunicorn y Render reciba las señales correctamente. Crea el admin inicial solo si `ADMIN_PASSWORD` está definido. Está escrito con LF y el Dockerfile además normaliza CRLF y aplica `chmod +x` por si el repo se clonó en Windows.
- El Dockerfile separa builder/runtime: el venv se compila con compiladores y se copia a una runtime limpia, sin root (usuario `app`), con `curl` para el healthcheck. `docker-compose.yml` espera a que `pg_isready` pase antes de levantar el web y monta volúmenes persistentes para Postgres, estáticos y media.
- `render.yaml` usa `generateValue: true` para `SECRET_KEY`, `fromDatabase` para `DATABASE_URL` y `sync: false` para contraseñas/credenciales S3: ningún secreto queda en el repo. No se instalaron `django-storages`/`boto3` en el `.venv` local porque el storage es condicional y no hace falta para los tests; sí están declarados en `requirements.txt` para el build de Docker/Render.
- Docker no está instalado en el entorno de trabajo: no se pudo correr `docker build` ni `docker compose config`. Se validó sintaxis YAML con `yaml.safe_load`, finales LF del script y `check` de producción con entorno simulado.

## Registro técnico de la Fase 9

- `cargar_datos_demo.py` vive en `core/management/commands/` y usa claves naturales para ser idempotente: `username`, `cuit`, `codigo` de producto y `observaciones` de venta (marcadas con `[DEMO cargar_datos_demo]`). Los usuarios se crean con `create_user` para hashear la contraseña; el resto con `get_or_create`. Todo dentro de `transaction.atomic()`.
- El comando llama a `cargar_roles` con `stdout` capturado en `StringIO` (solo se muestra con `-v 2`) para garantizar que los grupos existan antes de crear usuarios y no ensuciar la salida. La contraseña demo es `Demo1234!` y se puede cambiar con `--password`.
- La venta confirmada se arma con `services.agregar_detalle()` y `services.confirmar_venta()`, por lo que descuenta stock y aplica el 15 % del cliente; el borrador solo agrega ítems. En la segunda ejecución no se recrean ni se vuelve a descontar stock: se verificó que conteos, stock y totales quedan idénticos (3/3/4/8/2/5; VID-001 en 116; confirmada 2.618.100,00; borrador 1.164.600,00).
- Se agregaron 3 tests en `core/test_datos_demo.py` (carga inicial + idempotencia, roles/venta confirmada, borrador sin stock) llevando la suite de 156 a **159 tests**.
- El `README.md` definitivo incluye dominio, arquitectura híbrida, DER lógico con cardinalidades y reglas de integridad, matriz completa de roles, tabla de endpoints MVT/API/JWT/Swagger, guía de instalación, comandos demo, verificación, Docker/Render y un espacio visible para completar el enlace al deploy productivo.
- No se ejecutó ningún comando de Git en ninguna fase; la integración la realizó el usuario en cada rama.

## Pendientes

- **Fase 6:** completada (proveedores, catálogo, presupuesto en sesión, ventas con totales y control de stock). Verificado con `check`, `migrate`, `cargar_roles` y 102 tests OK.
- **Fase 7:** completada (ViewSets, routers, serializers 3 niveles, JWT, filtros, baja lógica, Swagger en `/api/schema/swagger/`). Verificado con `check`, `spectacular --validate` (0 errores/warnings) y 156 tests OK.
- **Fase 8:** completada (Docker multi-stage, entrypoint, compose con Postgres 16, production.py hardened, render.yaml y .env.example). Verificado con `check` dev/production y 156 tests OK. Sin validación de runtime Docker por falta de Docker local.
- **Fase 9:** completada (datos demo idempotentes, README definitivo, matriz/endpoints/DER, checklist del MVP y cierre de bitácora). Verificado con `check`, `cargar_datos_demo ×2` y 159 tests OK.
- **Estado:** las 9 fases están completadas. Único pendiente **externo**: completar la URL del deploy productivo en el README y cargar secretos en Render.

## Riesgos y recordatorios

- `migrate` **ya se ejecutó en desarrollo** (Fases 4, 5 y 6, con `proveedores.0001_initial`, `catalogo.0001_initial` y `ventas.0001_initial`). Toda nueva app de dominio requerirá su propia migración antes de usarla.
- Después de crear cada app de dominio conviene volver a correr `cargar_roles`: el comando es idempotente y completa los permisos de los grupos con los modelos nuevos.
- Si se crea un administrador con `cargar_roles --crear-admin`, la contraseña debe pasarse por variable de entorno `ADMIN_PASSWORD` en entornos compartidos para no dejar secretos en el historial de comandos.
- El cambio de estado de la venta y el movimiento de stock deben ocurrir en la misma transacción.
- No instalar dependencias nuevas sin justificar y consultar. En Fase 8 se agregaron `django-storages` y `boto3` a `requirements.txt` (aprobado para storage S3 condicional), pero no se instalaron en el `.venv` local.
- No tocar `.env`, CORS, CSRF, `ALLOWED_HOSTS` ni settings de seguridad sin advertirlo antes. En Fase 8 se amplió `.env.example` y se hicieron configurables por entorno las cabeceras HTTPS de `production.py`, sin modificar base/development/testing.
- Antes de desplegar: generar `SECRET_KEY`, cargar `ADMIN_PASSWORD` y las credenciales S3 en el panel de Render, y recordar que `render.yaml` apunta a la rama `develop`.
- Cierre EF: completar el enlace "Deploy productivo" del README con la URL real de Render después del primer deploy; la imagen Docker sigue sin validación de runtime porque no hay Docker en el entorno de desarrollo.
- Los importes se manejan con `Decimal`, nunca con `float`.
