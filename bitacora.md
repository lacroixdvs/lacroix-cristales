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
