# Bitácora — Vit Cristales

> Cronología de trabajo. Cada entrada registra fecha, qué se hizo, archivos tocados y verificaciones.
> Formato de entrada: `## YYYY-MM-DD — Fase N: título`.

## 2026-11-18 — Fase 1: contexto y cimentación

**Qué se hizo**

- Lectura completa de `inicio.md` (530 líneas) y verificación de la estructura real de carpetas.
- Identificación de la carpeta de trabajo correcta: `C:\Users\Nico\Desktop\lacroix-cristales`, que contenía solo `inicio.md`. Se descartó `C:\Users\Nico\Documents\Default Project` por tratarse de otro proyecto ya existente.
- Armado del plan de arranque y posterior ajuste al caso real de Vit Cristales: vidrios, mamparas de vidrio, espejos y cerramientos de oficinas.
- Confirmación de las 8 decisiones de diseño (login, roles, cotización en sesión, stock, acceso al catálogo, baja de ventas, unicidad y marca), registradas en `memoria.md`.
- Creación de los 8 archivos iniciales acordados.

**Archivos tocados**

- Creados: `memoria.md`, `bitacora.md`, `proyecto.md`, `design.md`, `.gitignore`, `.env.example`, `requirements.txt`, `README.md`.
- Leído sin modificar: `inicio.md`.
- No se modificaron archivos de configuración ni de Git.

**Verificaciones**

- `python manage.py check`: **no ejecutado**. Todavía no existe el proyecto Django; corresponde a la Fase 2.
- Tests: **no ejecutados**. Todavía no hay código.
- Dependencias: **no se instalaron**.
- Git: **no se ejecutó ningún comando**. La carpeta contiene un directorio `.git`, que no fue tocado.
- Falta la revisión humana de los 8 archivos antes de avanzar.

**Siguiente**

- Fase 2: crear `manage.py` y `config/` con settings separados, definiendo `AUTH_USER_MODEL` desde el inicio.

## 2026-11-18 — Fase 2: configuración base de Django

**Qué se hizo**

- Instalación de `requirements.txt` con el pip de `.venv` (Python 3.12.5): Django 5.2.19, DRF 3.18.3, SimpleJWT 5.5.1, django-filter 25.2, drf-spectacular 0.30.0, dj-database-url 2.3.0, psycopg 3.3.9, whitenoise 6.12.0 y gunicorn 23.0.0.
- Creación de `manage.py` y del paquete `config/` con `settings/base.py`, `development.py`, `production.py`, `testing.py`, `urls.py`, `wsgi.py` y `asgi.py`.
- `manage.py`, `wsgi.py` y `asgi.py` cargan `.env` antes de elegir el módulo de settings; el ambiente se toma de `DJANGO_SETTINGS_MODULE` con default de desarrollo.
- Configuración de `AUTH_USER_MODEL = "usuarios.Usuario"` en `base.py` **antes** de cualquier migración.
- Creación de la app mínima `usuarios`: `Usuario(AbstractUser)` con `email` único y obligatorio, `contacto`, `rol` (ADM/VENDEDOR/USUARIO) y `activo` vinculado a `is_active` en `save()`. Admin registrado con esos campos.
- Generación de `usuarios/migrations/0001_initial.py` mediante `makemigrations usuarios`. **No se ejecutó `migrate`.**
- Creación del `.env` local desde `.env.example` con una `SECRET_KEY` aleatoria para desarrollo (valor no mostrado en logs) y `DJANGO_SETTINGS_MODULE=config.settings.development`.

**Archivos tocados**

- Creados: `manage.py`, `config/__init__.py`, `config/settings/{__init__,base,development,production,testing}.py`, `config/{urls,wsgi,asgi}.py`, `usuarios/{__init__,apps,models,admin}.py`, `usuarios/migrations/__init__.py`, `usuarios/migrations/0001_initial.py`, `.env` (no versionado).
- Modificados: `bitacora.md`, `memoria.md`.

**Verificaciones**

- `python manage.py check`: **ejecutado, sin problemas** (`System check identified no issues (0 silenced).`).
- `python manage.py makemigrations usuarios`: **ejecutado**, generó `0001_initial.py`.
- `migrate`: **no ejecutado**. Se creó el archivo vacío `db.sqlite3` al consultar el historial de migraciones; no contiene ninguna tabla.
- Tests: **no ejecutados** (sin tests aún; se agregan con los CRUDs).
- Git: **ningún comando ejecutado**.

**Siguiente**

- Fase 3: app `core`, templates base y parciales, Tailwind CDN y mensajes de feedback.

## 2026-11-18 — Fase 3: core y UI base

**Qué se hizo**

- Creación de la app `core`, registrada en `INSTALLED_APPS`, con `HomeView` (pública) y `DashboardView` (con `LoginRequiredMixin`) que condiciona módulos y etiqueta según el rol efectivo.
- Resolución del rol en backend mediante `core/roles.py`: los grupos de Django Auth son la fuente de verdad, con fallback al campo `rol` hasta que las señales de Fase 4 lo sincronicen. Etiqueta de prioridad ADM > VENDEDOR > USUARIO.
- Tags de template `rol_actual` y `es_rol` en `core/templatetags/roles.py` para mostrar/condicionar la UI sin mover reglas a los templates.
- Templates `base.html`, `home.html`, `core/dashboard.html` y parciales `navbar`, `sidebar`, `messages`, `footer`, `modal-base` y `live-search`, con Tailwind CDN y la paleta verde/grises definida en `design.md`.
- Esqueletos reutilizables en `static/js`: `live-search.js` (debounce 300 ms, `fetch`, reemplazo del contenedor, `history.replaceState` y event delegation) y `modales.js` (`<dialog>` nativo, cierre por X/backdrop y Escape del navegador).
- Se agregó `STATICFILES_DIRS = [BASE_DIR / "static"]` en `base.py` y `include("core.urls")` en `config/urls.py`.
- 4 tests de humo en `core/tests.py`: home 200, dashboard requiere login, módulos por rol y precedencia del grupo sobre el campo `rol`.

**Archivos tocados**

- Creados: `core/__init__.py`, `core/apps.py`, `core/roles.py`, `core/views.py`, `core/urls.py`, `core/tests.py`, `core/templatetags/{__init__,roles}.py`, `templates/base.html`, `templates/home.html`, `templates/core/dashboard.html`, `templates/partials/{navbar,sidebar,messages,footer,modal-base,live-search}.html`, `static/js/{live-search,modales}.js`.
- Modificados: `config/settings/base.py`, `config/urls.py`, `bitacora.md`, `memoria.md`, `proyecto.md`.

**Verificaciones**

- `python manage.py check`: **ejecutado, sin problemas**.
- `DJANGO_SETTINGS_MODULE=config.settings.testing python manage.py test`: **ejecutado**, 4 tests, **OK** (base de test creada y destruida correctamente).
- Migraciones: **no se corrieron nuevas** (`core` no tiene modelos). `migrate` sigue sin ejecutarse en desarrollo.
- Git: **ningún comando ejecutado**.

**Siguiente**

- Fase 4: completar `usuarios` con registro público, login/logout, grupos `ADM`/`VENDEDOR`/`USUARIO` y señales de rol/`is_active`.

## 2026-11-18 — Fase 4: autenticación, roles y gestión de usuarios

**Qué se hizo**

- Señales en `usuarios/signals.py` registradas desde `UsuariosConfig.ready()`: sincronización bidireccional grupo↔`rol` (prioridad ADM > VENDEDOR > USUARIO) y de `activo`→`is_active`. Se extrajo esa responsabilidad del `save()` del modelo.
- Management command `cargar_roles` idempotente: crea los 3 grupos con los permisos disponibles en este momento (los permisos de dominio de Fase 5-6 se omiten sin error) y opción `--crear-admin` con password por argumento o variable `ADMIN_PASSWORD` (nunca se imprime).
- Flujo de autenticación completo: login/logout de Django, registro público que fuerza el grupo/rol USUARIO, templates dedicados y enlaces cableados en el navbar/home/sidebar.
- Mixins `RolRequeridoMixin` y `SoloAdminMixin` con control en backend (`PermissionDenied`), más CRUD de usuarios solo para ADM: listado con live search y paginación, alta, edición de datos/rol y baja lógica (`activo=False`, sin borrado). El admin no puede darse de baja a sí mismo.
- Se corrigió el manejo de excepciones del command: Django lanza `ContentType.DoesNotExist` (no `Permission.DoesNotExist`) cuando la app de dominio todavía no existe.
- Se ajustó el test de humo de Fase 3 para reflejar la sincronización bidireccional definitiva: ahora crea el usuario como USUARIO y le asigna el grupo VENDEDOR.

**Archivos tocados**

- Creados: `usuarios/signals.py`, `usuarios/forms.py`, `usuarios/mixins.py`, `usuarios/views.py`, `usuarios/urls.py`, `usuarios/management/{__init__,commands/__init__,commands/cargar_roles}.py`, `usuarios/tests/{__init__,test_signals,test_registro,test_permisos,test_baja,test_cargar_roles}.py`, `templates/registration/{login,registro}.html`, `templates/usuarios/{usuario_list,usuario_form,partials/usuario_resultados}.html`.
- Modificados: `usuarios/apps.py`, `usuarios/models.py`, `config/urls.py`, `templates/partials/{navbar,sidebar}.html`, `templates/home.html`, `core/tests.py`, `bitacora.md`, `memoria.md`, `proyecto.md`.

**Verificaciones**

- `python manage.py check`: **ejecutado, sin problemas**.
- `python manage.py migrate`: **ejecutado en desarrollo** (aplicó `usuarios.0001_initial` y el resto de apps de Django). Era la primera vez.
- `python manage.py cargar_roles`: **ejecutado dos veces** para confirmar idempotencia (grupos existentes en la segunda corrida).
- `DJANGO_SETTINGS_MODULE=config.settings.testing python manage.py test`: **ejecutado**, 19 tests (15 nuevos de `usuarios` + 4 de `core`), **OK**.
- `python manage.py makemigrations --check --dry-run`: **sin cambios detectados**.
- Git: **ningún comando ejecutado**.

**Siguiente**

- Fase 5: app `clientes` con CRUD, baja lógica y permisos por rol.

## 2026-11-18 — Fase 5: app clientes (patrón vertical de referencia)

**Qué se hizo**

- Creación de la app `clientes`, registrada en `INSTALLED_APPS`, con el modelo `Cliente` mayorista: `razon_social`, `cuit` (único), `contacto`, `email`, `direccion`, `descuento_mayorista` (`DecimalField` 0–100, default 0) y `activo` (baja lógica).
- Validación de CUIT compartida en `clientes/validators.py`: acepta `XX-XXXXXXXX-X` u 11 dígitos y normaliza siempre al formato con guiones. Se aplica en el modelo (`RegexValidator` + `clean()`) y en el form (`clean_cuit` con control de unicidad), con mensajes claros por campo.
- Doble validación del descuento: validadores `MinValueValidator`/`MaxValueValidator` en el modelo y `clean_descuento_mayorista()` en el form.
- Listado con live search (razón social, CUIT o email) usando `Q`, paginación de 20 y filtro de estado. Activos por defecto; el filtro de inactivos/todos solo es operable para ADM y se ignora en backend para VENDEDOR.
- Detalle, alta, edición, baja lógica y reactivación exclusivos de ADM, con mensajes de feedback en cada mutación. Baja y reactivación son POST; la baja usa confirmación en `<dialog>`.
- Templates `clientes/` con Tailwind y la paleta de `design.md`; modelo registrado en el admin y enlace del sidebar cableado.
- Se mejoró `static/js/live-search.js` para conservar los parámetros ya aplicados (como `activo`) al buscar, descartando solo `page`.
- Se volvió a correr `cargar_roles` tras la migración: ahora ADM tiene 8 permisos disponibles y VENDEDOR 1 (`view_cliente`).

**Archivos tocados**

- Creados: `clientes/{__init__,apps,models,validators,forms,views,urls,admin}.py`, `clientes/migrations/0001_initial.py`, `clientes/tests/{__init__,test_validaciones,test_permisos,test_listado,test_mutaciones}.py`, `templates/clientes/{cliente_list,cliente_form,cliente_detail,partials/cliente_resultados}.html`.
- Modificados: `config/settings/base.py`, `config/urls.py`, `templates/partials/sidebar.html`, `static/js/live-search.js`, `bitacora.md`, `memoria.md`, `proyecto.md`.

**Verificaciones**

- `python manage.py check`: **ejecutado, sin problemas**.
- `python manage.py makemigrations clientes`: **ejecutado**, generó `0001_initial.py`.
- `python manage.py migrate`: **ejecutado en desarrollo** (aplicó `clientes.0001_initial`).
- `python manage.py cargar_roles`: **ejecutado** para reflejar los nuevos permisos de `clientes`.
- `DJANGO_SETTINGS_MODULE=config.settings.testing python manage.py test`: **ejecutado**, 44 tests (25 nuevos de `clientes` + 19 previos), **OK**.
- `python manage.py makemigrations --check --dry-run`: **sin cambios detectados**.
- Git: **ningún comando ejecutado**.

**Siguiente**

- Fase 6: apps `proveedores`, `catalogo` y `ventas`, con cálculo de totales y control de stock.

## 2026-11-18 — Fase 6: dominio de proveedores, catálogo y ventas

**Qué se hizo**

- Se extrajo el validador de CUIT a `core/validators.py`; `clientes/validators.py` quedó como re-export por compatibilidad. Se agregó `core/forms.py` con `EstiloTailwindMixin` para no triplicar clases Tailwind.
- App `proveedores`: modelo `Proveedor` con CUIT único normalizado, `rubro` opcional y baja lógica. CRUD completo solo para ADM, con live search (razón social/CUIT/email/rubro), filtro de estado, paginación de 20, detalle, alta, edición, baja y reactivación con `<dialog>` y mensajes.
- App `catalogo`: modelo `Producto` con `codigo` único, `categoria` (`VIDRIO`/`MAMPARA`/`ESPEJO`/`CERRAMIENTO`), `precio_unitario` > 0, `stock`, FK protegida a `Proveedor` y baja lógica. ADM hace CRUD; VENDEDOR y USUARIO solo leen, buscan (código/nombre/categoría) y pueden agregar al presupuesto. El filtro de estado se ignora en backend para roles no-ADM.
- Presupuesto en `request.session` (`catalogo/presupuesto.py`): agregar, cambiar cantidades, quitar y vaciar; calcula subtotal/total con precios vigentes del catálogo sin descuentar stock ni crear ventas. Ruta canónica `/catalogo/presupuesto/` más alias `/presupuesto/` por `design.md`.
- App `ventas`: `Venta` (cliente, vendedor, estado `BORRADOR`/`CONFIRMADA`/`CANCELADA`, `subtotal`, `descuento_mayorista`, `total`, baja lógica) y `DetalleVenta` (FK protegida a `Producto`, `cantidad >= 1`, `precio_unitario` snapshot, `subtotal`, baja lógica).
- Capa de servicio `ventas/services.py`: `agregar_detalle`/`quitar_detalle` guardan el precio histórico y recalculan totales; `confirmar_venta`, `cancelar_venta` y `dar_de_baja` usan `transaction.atomic()` con `select_for_update()` sobre venta y productos. La validación previa (ítems activos, productos activos, stock suficiente) ocurre antes de escribir, por lo que un rechazo no deja descuentos parciales. El descuento mayorista del cliente se persiste y se muestra explícitamente en el resumen.
- Permisos: ADM accede a todo y es el único que da de baja ventas confirmadas; VENDEDOR crea borradores, carga/quita ítems, confirma y consulta solo sus ventas; USUARIO no entra a `ventas`.
- Sidebar y dashboard: enlaces reales de Proveedores, Catálogo, Ventas y Presupuesto; `MODULOS_POR_ROL` ya los contemplaba.
- Templates con Tailwind y paleta de `design.md`: badges de categoría y estado, tablas con parciales para live search, modales nativos de baja/cancelación y formularios de carga de ítems.

**Archivos tocados**

- Creados: `core/{validators,forms}.py`; `proveedores/{__init__,apps,models,forms,views,urls,admin}.py`, `proveedores/migrations/0001_initial.py`, `proveedores/tests/{__init__,test_validaciones,test_permisos,test_crud}.py`; `catalogo/{__init__,apps,models,forms,presupuesto,views,urls,admin}.py`, `catalogo/migrations/0001_initial.py`, `catalogo/templatetags/{__init__,catalogo_tags}.py`, `catalogo/tests/{__init__,test_modelo,test_permisos,test_listado,test_crud,test_presupuesto}.py`; `ventas/{__init__,apps,models,forms,services,views,urls,admin}.py`, `ventas/migrations/0001_initial.py`, `ventas/templatetags/{__init__,ventas_tags}.py`, `ventas/tests/{__init__,test_totales,test_stock,test_permisos}.py`.
- Creados (templates): `templates/proveedores/`, `templates/catalogo/` y `templates/ventas/` con sus listados, formularios, detalles y parciales.
- Modificados: `clientes/validators.py`, `clientes/models.py`, `config/settings/base.py`, `config/urls.py`, `templates/partials/sidebar.html`, `bitacora.md`, `memoria.md`, `proyecto.md`.
- Eliminado: `catalogo/presupuesto_urls.py` (ruta unificada para evitar namespaces duplicados).

**Verificaciones**

- `python manage.py check`: **ejecutado, sin problemas**.
- `python manage.py makemigrations proveedores catalogo ventas`: **ejecutado**, generó los tres `0001_initial.py`.
- `python manage.py migrate`: **ejecutado en desarrollo** (aplicó `proveedores.0001_initial`, `catalogo.0001_initial` y `ventas.0001_initial`).
- `python manage.py cargar_roles`: **ejecutado**: ADM 24 permisos, VENDEDOR 8, USUARIO 1 (`view_producto`).
- `DJANGO_SETTINGS_MODULE=config.settings.testing python manage.py test`: **ejecutado**, 102 tests (44 previos + 58 nuevos), **OK**.
- `python manage.py makemigrations --check --dry-run`: **sin cambios detectados**.
- Git: **ningún comando ejecutado**.

**Siguiente**

- Fase 7: API REST con DRF, SimpleJWT y Swagger.

## 2026-11-18 — Fase 7: API REST, JWT y Swagger/OpenAPI

**Qué se hizo**

- Se configuró DRF en `config/settings/base.py`: autenticación JWT (Bearer) primero y `SessionAuthentication` después para navegar Swagger con la sesión del MVT; `IsAuthenticated` por defecto; `PageNumberPagination` de 20; `DjangoFilterBackend` + `SearchFilter` + `OrderingFilter`; `AutoSchema` de drf-spectacular. Se agregaron `SIMPLE_JWT` (access 60 min, refresh 1 día) y `SPECTACULAR_SETTINGS` con metadata de Vit Cristales. Se registró la app `api` en `INSTALLED_APPS`.
- Se implementó el **patrón de 3 niveles** (`*BaseSerializer`, `*GetSerializer` con relaciones anidadas/legibles, `*PostSerializer` con validaciones de negocio) en los cinco `serializers.py` de dominio: `usuarios`, `proveedores`, `clientes`, `catalogo` y `ventas` (incluye `DetalleVenta`). Los Get exponen grupos/rol, conteos, proveedor anidado, etiqueta de categoría, detalles con snapshot de precio y resumen de descuento; los Post normalizan CUIT, validan descuento/precio/categoría/vendedor y delegan las reglas cruzadas a `ventas.services`.
- Se crearon los ViewSets en `api/viewsets.py` y los routers en `api/urls.py` bajo `/api/`: `/api/usuarios/`, `/api/proveedores/`, `/api/clientes/`, `/api/catalogo/` y `/api/ventas/`, más acciones anidadas de ventas (`confirmar`, `cancelar`, `detalles/agregar`, `detalles/<id>`). La misma matriz de roles del MVT: ADM acceso total; VENDEDOR lectura de clientes/catálogo y gestión de sus propias ventas; USUARIO solo GET de productos activos. La baja lógica en `perform_destroy` setea `activo=False` (y `is_active=False` en usuarios) sin borrado físico; `VentaViewSet.perform_destroy` llama a `services.dar_de_baja()` para reintegrar stock.
- Se cablearon los endpoints JWT (`/api/token/`, `/api/token/refresh/`), el esquema (`/api/schema/`) y Swagger UI (`/api/schema/swagger/`) en `config/urls.py`. Se agregó un enlace "API / Swagger" visible solo para ADM en el navbar.
- `confirmar`, `cancelar`, agregar y quitar ítems invocan `ventas.services` sin duplicar la lógica de totales, descuento ni stock; las excepciones `ValidationError` de Django se traducen a respuestas 400 de DRF.
- Se corrigió la generación del esquema para que no emitiera warnings: `swagger_fake_view` en `VentaViewSet.get_queryset`, `source` redundante removido y anotaciones `@extend_schema_field` en los campos calculados.

**Archivos tocados**

- Creados: `api/{__init__,apps,permissions,filters,viewsets,urls}.py`, `api/tests/{__init__,test_jwt,test_serializers,test_filtros,test_permisos,test_baja_logica,test_schema,test_ventas_acciones}.py`.
- Creados (serializers): `usuarios/serializers.py`, `proveedores/serializers.py`, `clientes/serializers.py`, `catalogo/serializers.py`, `ventas/serializers.py`.
- Modificados: `config/settings/base.py` (DRF/SimpleJWT/Spectacular + app `api`), `config/settings/testing.py` (SECRET_KEY largo para evitar warnings de JWT), `config/urls.py`, `templates/partials/navbar.html`, `bitacora.md`, `memoria.md`, `proyecto.md`.
- Sin nuevas dependencias: DRF 3.18.3, SimpleJWT 5.5.1, django-filter 25.2 y drf-spectacular 0.30.0 ya estaban en `requirements.txt` e instalados.

**Verificaciones**

- `python manage.py check`: **ejecutado, sin problemas**.
- `python manage.py makemigrations --check --dry-run`: **sin cambios detectados**.
- `python manage.py spectacular --validate`: **ejecutado, 0 errores y 0 warnings**.
- `DJANGO_SETTINGS_MODULE=config.settings.testing python manage.py test`: **ejecutado**, 156 tests (102 previos + 54 nuevos de API), **OK**.
- Git: **ningún comando ejecutado**.

**Siguiente**

- Fase 8: despliegue (Docker/Render) y ajustes de producción.

## 2026-11-18 — Fase 8: empaquetado Docker, producción y Render

**Qué se hizo**

- Se reescribió `config/settings/production.py`: `DATABASE_URL` vía `dj-database-url` con `conn_max_age=600` y `conn_health_checks=True`, fallback a SQLite para pruebas locales; WhiteNoise en el middleware y `CompressedManifestStaticFilesStorage` con override por entorno; `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` desde entorno con soporte automático para `RENDER_EXTERNAL_HOSTNAME`, `.onrender.com` y `https://*.onrender.com`; cabeceras HTTPS (`SECURE_SSL_REDIRECT`, cookies seguras, HSTS, `SECURE_PROXY_SSL_HEADER`, referrer policy) activables/desactivables por variable para no romper HTTP dentro de Docker; storage S3/Supabase **condicional** (solo con `USE_SUPABASE_STORAGE=True` y las cuatro credenciales completas).
- Se creó `entrypoint.sh` con LF: ejecuta `migrate --noinput`, `cargar_roles` (con creación opcional de admin si hay `ADMIN_PASSWORD`), `collectstatic --noinput` y luego `exec gunicorn config.wsgi:application` respetando `PORT`, `WEB_CONCURRENCY` y `WEB_TIMEOUT`.
- Se creó un `Dockerfile` multi-stage sobre `python:3.12-slim` (builder con venv en `/opt/venv`, runtime sin compiladores, usuario no-root `app`, normalización de CRLF y `chmod +x` del entrypoint, healthcheck con curl). Se agregaron `.dockerignore`, `docker-compose.yml` (web + PostgreSQL 16 con healthcheck y `depends_on: service_healthy`) y `render.yaml` (Blueprint con DB gratuita, web Docker, `SECRET_KEY` generado, `DATABASE_URL` inyectada, secretos `sync: false`).
- Se amplió `.env.example` con todas las variables de producción/despliegue y se agregaron `django-storages>=1.14,<2.0` y `boto3>=1.34,<2.0` a `requirements.txt` (no instalados localmente porque el storage es condicional y no se necesita para verificar).

**Archivos tocados**

- Creados: `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `render.yaml`, `entrypoint.sh`.
- Modificados: `config/settings/production.py`, `requirements.txt`, `.env.example`, `bitacora.md`, `memoria.md`, `proyecto.md`.
- No se tocó `.env` ni ninguna settings de seguridad de base/development/testing.

**Verificaciones**

- `python manage.py check`: **ejecutado, sin problemas**.
- `python manage.py check --settings=config.settings.production` con `SECRET_KEY`, `DATABASE_URL` y `RENDER_EXTERNAL_HOSTNAME` de prueba: **ejecutado, sin problemas**. Se confirmó por `manage.py shell` que se agregan `.onrender.com` a `ALLOWED_HOSTS` y `https://*.onrender.com` a `CSRF_TRUSTED_ORIGINS`, que el fallback sin `DATABASE_URL` es SQLite y que el backend de estáticos es WhiteNoise Manifest.
- `entrypoint.sh`: **25 LF y 0 CRLF** verificado a nivel de bytes; el Dockerfile además normaliza CRLF y aplica `chmod +x` en build.
- `docker-compose.yml` y `render.yaml`: **parseados con `yaml.safe_load`, sintaxis válida**.
- `DJANGO_SETTINGS_MODULE=config.settings.testing python manage.py test`: **ejecutado**, 156 tests, **OK**.
- **Docker no está disponible en este entorno**: no se pudo ejecutar `docker build` ni `docker compose config`. La imagen y el compose quedan listos pero sin validación de runtime local; se declara expresamente.
- Git: **ningún comando ejecutado**.

**Siguiente**

- Fase 9: README final, cierre de bitácora y verificación integral del MVP.

## 2026-11-18 — Fase 9: cierre del proyecto y documentación final (EFI)

**Qué se hizo**

- Se creó `core/management/commands/cargar_datos_demo.py`: comando idempotente que siembra 3 usuarios (ADM/VENDEDOR/USUARIO con contraseña `Demo1234!`), 3 proveedores de vidrio/herrajes, 4 clientes con descuentos 15/10/5/0 %, 8 productos (2 por categoría: VIDRIO, MAMPARA, ESPEJO, CERRAMIENTO) y 2 ventas de ejemplo (una confirmada vía servicios con descuento y stock descontado, una en borrador). Llama a `cargar_roles` con salida capturada y usa claves naturales para no duplicar nada.
- Se agregaron 3 tests en `core/test_datos_demo.py` que cubren carga inicial, idempotencia, roles y totales de la venta confirmada y que el borrador no toca stock.
- Se redactó el `README.md` definitivo: dominio real de Vit Cristales, arquitectura híbrida MVT + Tailwind CDN + API DRF/JWT/Swagger, DER lógico con entidades/atributos/cardinalidades/reglas de integridad, matriz completa de roles, tabla de endpoints Web/API/JWT/Swagger, guía de instalación en Windows y Linux, ejecución de `cargar_roles`/`cargar_datos_demo`, verificación de 159 tests, guía Docker/Render y sección visible "Deploy productivo" para completar la URL.
- Se marcaron todas las apps y módulos como completados en `proyecto.md`, se actualizó `memoria.md` al estado final de 9/9 fases y se cerró esta bitácora con el checklist del MVP.

**Archivos tocados**

- Creados: `core/management/__init__.py`, `core/management/commands/__init__.py`, `core/management/commands/cargar_datos_demo.py`, `core/test_datos_demo.py`.
- Modificados: `README.md`, `proyecto.md`, `memoria.md`, `bitacora.md`.
- Git: **ningún comando ejecutado**.

**Verificaciones**

- `python manage.py check`: **ejecutado, sin problemas**.
- `python manage.py cargar_datos_demo`: **ejecutado dos veces sobre la DB de desarrollo**. Primera pasada: 20 creados, 0 existentes. Segunda: 0 creados, 20 existentes. Conteos invariantes (3 usuarios, 3 proveedores, 4 clientes, 8 productos, 2 ventas, 5 detalles), stock invariante (VID-001 = 116) y totales invariantes (confirmada 2.618.100,00; borrador 1.164.600,00). Idempotencia confirmada.
- `DJANGO_SETTINGS_MODULE=config.settings.testing python manage.py test`: **ejecutado**, **159 tests** (156 previos + 3 nuevos), **OK**.
- `python manage.py spectacular --validate` y `makemigrations --check --dry-run`: verificados en fases anteriores; la Fase 9 no agregó modelos ni migraciones.

**Checklist del MVP verificado**

| Requisito | Estado | Evidencia |
|---|:---:|---|
| Autenticación y roles (≥ 2 perfiles) con grupos de Django Auth | ✔ | 3 roles (ADM/VENDEDOR/USUARIO), tests de permisos MVT y API, `rol_de()` |
| 3 CRUDs completos con baja lógica | ✔ | Usuarios, proveedores, clientes, catálogo y ventas; `activo=False`, nunca borrado físico |
| Baja lógica excluye inactivos de listados y API | ✔ | Querysets filtrados y tests de `DELETE` sin borrar filas |
| Mensajes de feedback éxito/error | ✔ | `templates/partials/messages.html` en todas las vistas |
| Tests de reglas de negocio (no solo smoke) | ✔ | 159 tests: CUIT, descuentos, stock, totales, JWT, permisos, baja, demo |
| API REST con JWT y documentación | ✔ | `/api/token/`, `/api/schema/`, `/api/schema/swagger/`, esquema sin warnings |
| Base de datos en producción y variables de entorno | ✔ | `DATABASE_URL` + PostgreSQL en `render.yaml`/compose; secretos fuera del repo |
| Empaquetado y despliegue configurado | ✔ | Dockerfile multi-stage, compose con Postgres 16, Blueprint de Render. Deploy real funcionando en [https://lacroix-cristales.onrender.com](https://lacroix-cristales.onrender.com) con PostgreSQL. |
| Documentación (README, memoria, proyecto, bitácora, diseño) | ✔ | README definitivo con DER, matriz, endpoints y guías; archivos actualizados |

**Estado final:** 9 de 9 fases completadas y checklist del MVP **100 % completado**. Deploy productivo publicado en [https://lacroix-cristales.onrender.com](https://lacroix-cristales.onrender.com) con PostgreSQL sobre Docker en Render. Sin pasos externos pendientes.

**Cierre**

- Entrega cerrada: aplicación desplegada y funcionando, enlace público documentado en el README y secretos cargados en el panel del proveedor sin publicarlos en el repositorio.

## 2026-11-18 — Refactor UI: Tailwind → Bootstrap 5.3

> Las entradas de las Fases 3 a 9 describen Tailwind porque era el estado de ese momento. Esta entrada registra el cambio de sistema visual; la lógica de negocio no se tocó.

**Qué se hizo**

- Se reemplazó el CDN de Tailwind y su `tailwind.config` inline en `templates/base.html` por Bootstrap 5.3.3 (CSS + JS bundle) y Bootstrap Icons 1.11.3, siempre vía CDN y sin build step.
- Se creó `static/css/vit-cristales.css` con la paleta institucional: verde esmeralda (`--bs-primary: #15803d`) y gris pizarra (`--bs-body-color`, `--bs-body-bg`, `--bs-border-color`). Define también `.btn-vit`, `.text-vit`, `.bg-vit` y el backdrop oscurecido de los `<dialog>`.
- Se migraron todos los templates a componentes Bootstrap: `container-fluid`, `navbar`/`nav-pills`, sidebar por rol, `card`, `table table-hover align-middle` dentro de `table-responsive`, `badge`, `btn`, `form-label`, `form-control`, `form-select`, `form-check-input`, `input-group` y `alert alert-dismissible fade show`.
- `core.forms.EstiloTailwindMixin` pasó a llamarse `EstiloBootstrapMixin` y aplica la clase nativa según el widget. Los forms de `usuarios`, `clientes`, `proveedores`, `catalogo` y `ventas` dejaron de importar el mixin antiguo.
- Los filtros `badge_categoria` (`catalogo`) y `badge_estado` (`ventas`) ahora devuelven clases `text-bg-*`.
- Se conservaron intactos `static/js/live-search.js` y `static/js/modales.js`, junto con todos los `id`, `name`, `action`, `method`, atributos `data-*` y bloques `{% if %}` / `{% for %}` funcionales. En particular: `buscador-articulos`, `resultados-articulos`, `modal-base`, `data-modal-open`, `data-modal-close` y los parámetros de paginación `query_base`.
- Se actualizaron `design.md`, `memoria.md`, `proyecto.md`, `README.md` y esta bitácora para reflejar Bootstrap 5.3 como sistema visual vigente.

**Archivos tocados**

- Modificados: `templates/base.html`; los 6 parciales de `templates/partials/`; `templates/home.html`, `templates/core/dashboard.html`, `templates/registration/{login,registro}.html`; templates de listado/formulario/detalle y parciales de resultados de `usuarios`, `proveedores`, `clientes`, `catalogo` (incluido `presupuesto.html`) y `ventas`.
- Modificados: `core/forms.py`, `usuarios/forms.py`, `clientes/forms.py`, `proveedores/forms.py`, `catalogo/forms.py`, `ventas/forms.py`, `catalogo/templatetags/catalogo_tags.py`, `ventas/templatetags/ventas_tags.py`.
- Creado: `static/css/vit-cristales.css`.
- Modificados (documentación): `design.md`, `memoria.md`, `proyecto.md`, `README.md`, `bitacora.md`.
- No modificados: `static/js/live-search.js`, `static/js/modales.js`, vistas, URLs, modelos, permisos, serializers y servicios.

**Verificaciones**

- `python manage.py check` con `config.settings.development`: **sin problemas**.
- `DJANGO_SETTINGS_MODULE=config.settings.testing python manage.py test`: **159 tests, OK**.
- Búsqueda de clases Tailwind en `.html`, `.py` y `.css`: **sin coincidencias**.
- Git: **ningún comando ejecutado**. El trabajo quedó en la rama `refactor/ui-bootstrap` para que el usuario lo integre.

## 2026-11-18 — Pulido visual: tipografía, portada y KPIs

**Qué se hizo**

- `templates/base.html` incorpora Google Fonts (Plus Jakarta Sans para títulos y encabezados; Inter para texto y tablas) con `preconnect` y `display=swap`, sin reemplazar Bootstrap, Icons ni los scripts propios.
- `static/css/vit-cristales.css` se refinó manteniendo la paleta: tarjetas con borde gris hielo, radio `0.75rem` y sombra suave (`.card-hover` con elevación discreta), navbar `sticky` translúcido con `backdrop-filter: blur(8px)`, transiciones suaves en botones/tarjetas/enlaces, `thead` tenue con tipografía prolija y hover de fila casi imperceptible. Los `<dialog>` recibieron borde y radio coherentes.
- `templates/home.html` estrenó hero sobrio `.vit-hero` con CTA según sesión (dashboard + presupuesto si está logueado; ingresar + crear cuenta si no) y cuatro tarjetas de líneas de producto — Vidrios, Mamparas, Espejos y Cerramientos — con Bootstrap Icons y acceso al catálogo o al login.
- `core/views.py` sumó `STOCK_BAJO = 10` (solo informativo) y `DashboardView._kpis()`, indicadores reales y de solo lectura por rol: ADM (productos activos, stock bajo, clientes activos, ventas confirmadas), VENDEDOR (mis ventas, borradores, productos activos, stock bajo) y USUARIO (productos disponibles, ítems en presupuesto desde sesión, categorías). `templates/core/dashboard.html` los renderiza como tarjetas con ícono lateral y tono sobrio.
- Los listados de usuarios, proveedores, clientes, catálogo y ventas ganaron contador discreto junto al subtítulo (`page_obj.paginator.count`) y estados vacíos prolijos con ícono y sugerencia dentro de `{% empty %}`.

**Archivos tocados**

- Modificados: `templates/base.html`, `static/css/vit-cristales.css`, `templates/home.html`, `templates/core/dashboard.html`, `core/views.py`.
- Modificados: `templates/{usuarios,proveedores,clientes,catalogo,ventas}/*_list.html` y sus `partials/*_resultados.html`.
- Modificados (documentación): `design.md`, `memoria.md`, `bitacora.md`.
- No modificados: `static/js/live-search.js`, `static/js/modales.js`, modelos, URLs, permisos, serializers, servicios ni atributos funcionales (`id`, `name`, `action`, `method`, `data-*`, bloques Django).

**Verificaciones**

- `python manage.py check` con `config.settings.development`: **sin problemas**.
- `DJANGO_SETTINGS_MODULE=config.settings.testing python manage.py test`: **159 tests, OK**.
- Selectores críticos confirmados presentes: `buscador-articulos`, `resultados-articulos`, `modal-base`, `data-modal-open`, `data-modal-close` y `data-live-search`.
- Git: **ningún comando ejecutado**. El trabajo quedó en la rama `refactor/ui-pulido-visual` para que el usuario lo integre.

## 2026-11-19 — Publicación del deploy productivo y cierre del MVP

**Qué se hizo**

- Se confirmó que la aplicación está desplegada y funcionando en **[https://lacroix-cristales.onrender.com](https://lacroix-cristales.onrender.com)**, con PostgreSQL y Docker en Render.
- Se reemplazó el marcador pendiente de la sección "Deploy productivo" del `README.md` por la URL oficial, se agregó el estado productivo y se aclaró que las credenciales demo se entregan por canal privado.
- Se actualizó la nota de verificación del README: la ausencia de Docker local ya no impide dar por validado el runtime, porque el deploy en Render ejecutó la imagen real contra PostgreSQL.
- Se actualizó `memoria.md` (fecha, estado, URL oficial, checklist 100 % y recordatorios de despliegue) y esta bitácora (fila de empaquetado/despliegue, estado final y cierre sin pendientes).
- El checklist del MVP quedó **100 % completado**: 9 de 9 fases, documentación, despliegue y enlace público.

**Archivos tocados**

- Modificados (documentación): `README.md`, `memoria.md`, `bitacora.md`.
- No modificados: código, templates, estilos, scripts, modelos, vistas, URLs ni settings.

**Verificaciones**

- URL productiva verificada por el usuario: [https://lacroix-cristales.onrender.com](https://lacroix-cristales.onrender.com).
- Git: **ningún comando ejecutado**.
