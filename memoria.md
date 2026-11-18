# Memoria — Vit Cristales

> Memoria viva del proyecto. Toda decisión relevante debe estar acá; si no está escrita, no existe.
> Guía maestra: [`inicio.md`](inicio.md).

## Estado actual

- **Fecha:** 2026-11-18
- **Fase:** 7 de 9 — API REST con DRF, JWT y Swagger/OpenAPI, completada
- **Ubicación:** `C:\Users\Nico\Desktop\lacroix-cristales`
- **Nombre comercial:** Vit Cristales (documentación e interfaz). La carpeta conserva el nombre `lacroix-cristales`.
- **Código generado:** `manage.py`, `config/`, `core`, `usuarios`, `clientes`, `proveedores`, `catalogo`, `ventas` y `api`, todos con modelo/serializers, vistas, templates, admin, migración y tests. Falta el despliegue (Fase 8).
- **Verificación:** `python manage.py check` sin problemas, `migrate` ejecutado en desarrollo, `cargar_roles` actualizado, esquema OpenAPI validado sin errores ni warnings y 156 tests (54 nuevos de API + 102 previos) **OK** con settings de testing.

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

## Pendientes

- **Fase 6:** completada (proveedores, catálogo, presupuesto en sesión, ventas con totales y control de stock). Verificado con `check`, `migrate`, `cargar_roles` y 102 tests OK.
- **Fase 7:** completada (ViewSets, routers, serializers 3 niveles, JWT, filtros, baja lógica, Swagger en `/api/schema/swagger/`). Verificado con `check`, `spectacular --validate` (0 errores/warnings) y 156 tests OK.
- **Fases 8-9:** Docker/Render, README final y cierre de bitácora.

## Riesgos y recordatorios

- `migrate` **ya se ejecutó en desarrollo** (Fases 4, 5 y 6, con `proveedores.0001_initial`, `catalogo.0001_initial` y `ventas.0001_initial`). Toda nueva app de dominio requerirá su propia migración antes de usarla.
- Después de crear cada app de dominio conviene volver a correr `cargar_roles`: el comando es idempotente y completa los permisos de los grupos con los modelos nuevos.
- Si se crea un administrador con `cargar_roles --crear-admin`, la contraseña debe pasarse por variable de entorno `ADMIN_PASSWORD` en entornos compartidos para no dejar secretos en el historial de comandos.
- El cambio de estado de la venta y el movimiento de stock deben ocurrir en la misma transacción.
- No instalar dependencias nuevas sin justificar y consultar. Las de storage S3 se evalúan recién en Fase 8.
- No tocar `.env`, CORS, CSRF, `ALLOWED_HOSTS` ni settings de seguridad sin advertirlo antes.
- Los importes se manejan con `Decimal`, nunca con `float`.
