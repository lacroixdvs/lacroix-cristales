# Prototipo Maestro - Guía de Arquitectura, Metodología y Estándares

> **Nota:** Los nombres de las apps y modelos en los ejemplos (pacientes, turnos, facturacion) son de referencia. Reemplazalos por los de tu propio dominio, pero mantené la estructura de carpetas, la metodología de GitFlow y los estándares de código.

> **Propósito:** este archivo es la guía maestra para arrancar un proyecto Django full-stack desde cero siguiendo nuestras reglas de trabajo. Está pensado para que otro desarrollador (o su agente de IA) pueda leerlo, entender el contexto y empezar a generar la estructura base sin improvisar.

> **Cómo usarlo:** poné este archivo en la raíz de tu proyecto, abrilo en OpenCode y decile al agente:
> *"Leé el archivo inicio.md y empezá a generar la estructura base del proyecto. Decime qué archivos vamos a crear primero."*

---

## 1. Filosofía de Trabajo (Metodología)

### 1.1 Flujo de trabajo con GitFlow

Trabajamos con un GitFlow simplificado y prolijo. La idea es que `main` siempre sea desplegable y `develop` sea la rama de integración.

| Rama | Propósito | Sale de | Vuelve a |
|------|-----------|---------|----------|
| `main` | Código en producción, siempre estable | — | — |
| `develop` | Integración de features antes de producción | `main` | `main` (vía PR) |
| `feature/*` | Nueva funcionalidad | `develop` | `develop` (vía PR) |
| `bugfix/*` | Corrección de un error detectado | `develop` | `develop` (vía PR) |
| `hotfix/*` | Corrección urgente en producción | `main` | `main` y `develop` |

**Nomenclatura de ramas (en minúsculas, con guiones):**

```text
feature/crud-pacientes
feature/turnos-live-search
bugfix/login-redirect
hotfix/error-total-factura
chore/limpieza-static
docs/readme-y-swagger
```

**Reglas del flujo:**

- Nunca se commitea directo a `main` ni a `develop`.
- Cada feature o bugfix se desarrolla en su rama y se integra mediante **Pull Request**.
- Todo PR debe describir: qué cambia, por qué, cómo se probó y qué capturas aplican.
- Antes de abrir un PR: `manage.py check`, correr los tests y probar el flujo manualmente.
- Se prefiere PRs chicos y enfocados antes que PRs gigantes con muchas cosas mezcladas.

**Comandos sugeridos (los ejecuta el humano, nunca el agente):**

```bash
# Crear rama de trabajo
git checkout develop
git pull origin develop
git checkout -b feature/nombre-descriptivo

# Guardar avances
git add .
git commit -m "feat(pacientes): agrego listado con baja lógica"

# Publicar rama y abrir PR
git push -u origin feature/nombre-descriptivo
```

### 1.2 Commits semánticos

Usamos el estándar **Conventional Commits**. El mensaje debe decir qué se hizo y sobre qué módulo.

```text
<tipo>(<alcance opcional>): <descripción en imperativo y minúsculas>

[cuerpo opcional explicando el por qué]

[footer opcional: refs, breaking changes]
```

**Tipos permitidos:**

| Tipo | Cuándo usarlo |
|------|---------------|
| `feat` | Nueva funcionalidad visible para el usuario |
| `fix` | Corrección de un bug |
| `docs` | Cambios en documentación (`.md`, README, Swagger) |
| `style` | Formato, indentación, Tailwind, sin cambios de lógica |
| `refactor` | Reestructuración de código sin cambiar comportamiento |
| `test` | Agregado o ajuste de tests |
| `chore` | Configuración, dependencias, Docker, tareas de mantenimiento |
| `perf` | Mejora de rendimiento |

**Ejemplos reales:**

```text
feat(turnos): agrego validación de turnos solapados
fix(facturacion): corrijo recálculo del total al anular un pago
docs(bitacora): registro la jornada de deploy en Render
refactor(usuarios): extraigo validación de DNI a un mixin reutilizable
style(home): ajusto espaciado de las tarjetas estadísticas
test(tratamientos): cubro la regla de negocio de objetivos vencidos
```

- Descripción en **imperativo** ("agrego", "corrijo", "elimino"), no en pasado.
- Sin punto final.
- Un commit = un cambio lógico. Si tocaste 5 cosas distintas, son 5 commits.

### 1.3 Uso de la IA como arquitecto y ejecutor

La IA (OpenCode / Nemotron) actúa como **arquitecto y ejecutor**, pero **la revisión humana es obligatoria**. Nada se mergea sin que una persona lo haya leído, probado y entendido.

**Cómo trabajamos con la IA:**

1. **Contexto primero:** antes de pedir código, la IA lee `inicio.md`, `memoria.md`, `proyecto.md` y `design.md`.
2. **Plan antes de ejecutar:** para tareas no triviales, la IA propone un plan (archivos a tocar, decisiones, riesgos) y espera aprobación.
3. **Cambios chicos y revisables:** preferimos muchos cambios pequeños antes que un monolito de código.
4. **Explicar el por qué:** la IA justifica decisiones arquitectónicas, no solo "escribe código que anda".
5. **Nunca Git:** la IA **sugiere** comandos, pero no los ejecuta. El humano controla el repositorio.
6. **Verificación obligatoria:** la IA corre `manage.py check` y los tests antes de dar una tarea por terminada. Si no puede ejecutarlos, lo dice explícitamente.
7. **Honestidad:** si algo no se probó o quedó pendiente, se declara. No se "inventa" que funciona.

**Qué se le pide a la IA:**

- Respetar la estructura de carpetas y los estándares de este documento.
- No agregar dependencias nuevas sin justificarlo y consultarlo.
- No borrar ni reescribir archivos grandes sin mostrar el diff o explicar el alcance.
- No tocar configuración de seguridad (`.env`, `SECRET_KEY`, CORS, CSRF) sin advertirlo.

### 1.4 Archivos de contexto (memoria del proyecto)

La IA no tiene memoria entre sesiones: la memoria vive en archivos. Son parte del proyecto y se versionan.

| Archivo | Qué guarda | Cuándo se actualiza |
|---------|------------|---------------------|
| `memoria.md` | Estado actual, decisiones arquitectónicas, stack, pendientes, "por qué" de las cosas | Al cerrar hitos o tomar decisiones importantes |
| `bitacora.md` | Cronología de lo que se hizo, día por día, con archivos tocados y verificaciones | Después de cada tarea importante |
| `proyecto.md` | Arquitectura, apps, modelos, endpoints, estado de cada módulo | Cuando cambia la estructura o se suma un módulo |
| `design.md` | Guía de estilo UI/UX: paleta, tipografía, botones, tablas, modales | Cuando cambia el sistema visual |

**Regla de oro:** si una decisión no está escrita en un `.md`, no existe. El próximo desarrollador (o la próxima sesión de IA) tiene que poder reconstruir el contexto leyendo estos archivos.

---

## 2. Stack Tecnológico Base (Django Full-Stack)

### 2.1 Backend

- **Framework:** Django (última versión estable del proyecto).
- **Base de datos:**
  - **Desarrollo:** SQLite (`db.sqlite3`), simple y sin fricción.
  - **Producción:** PostgreSQL (recomendado Supabase o similar).
- **API (si se requiere):** Django REST Framework + `django-filter` + `drf-spectacular` (Swagger/OpenAPI).
- **Autenticación API:** JWT con `djangorestframework-simplejwt`.
- **Archivos media:** `FileSystemStorage` en dev, storage S3-compatible (Supabase Storage) en prod, de forma **condicional por variable de entorno**.
- **Archivos estáticos:** WhiteNoise.
- **Servidor de aplicación:** Gunicorn.

### 2.2 Frontend

- **Templates HTML con MVT** (Model-View-Template) de Django.
- **TailwindCSS vía CDN** para el estilado (rápido de arrancar, sin build step).
- **Alpine.js o JavaScript vanilla** para interactividad:
  - Modales, dropdowns, tabs.
  - Live Search en tablas.
  - Confirmaciones y feedback sin recargar.
- Sin frameworks SPA (React/Vue) para el MVP. Si el proyecto lo justifica, se evalúa aparte.

### 2.3 Autenticación

- **Web (MVT):** Django Auth con **sesiones** y `LoginRequiredMixin` / decoradores.
- **API:** JWT (access + refresh) con SimpleJWT.
- **Roles:** mínimo 2 perfiles, implementados con grupos/permisos de Django o un campo de rol en el usuario. Los permisos se validan en backend **siempre**; el ocultamiento en templates es solo cosmético.

### 2.4 Despliegue

- **Docker** para empaquetar la app (multi-stage build, usuario no root, healthcheck).
- **Render** (o similar) para el servicio web.
- **Supabase** (o similar) para PostgreSQL y Storage de media.
- **Variables de entorno** gestionadas en el panel del proveedor, nunca en el repo.

**Archivos esperados de despliegue:**

```text
Dockerfile
docker-compose.yml
.dockerignore
render.yaml          # o el equivalente del proveedor
.env.example         # plantilla, sin secretos reales
```

---

## 3. Requisitos Mínimos de la Facultad (MVP)

El MVP debe cumplir, como mínimo, con todo esto:

- [ ] **Autenticación y roles:** login/logout funcional y al menos **2 perfiles** con permisos distintos (por ejemplo Admin y Profesional/Operador).
- [ ] **3 CRUDs completos** con **baja lógica (soft delete)**:
  - Crear, listar, ver detalle, editar y "eliminar" (marcar inactivo).
  - El registro eliminado no aparece en los listados por defecto y no se borra físicamente de la base.
- [ ] **Mensajes de feedback:** éxito y error visibles para el usuario (Django Messages + estilos Tailwind).
- [ ] **Tests unitarios** sobre reglas de negocio (no solo smoke tests): validaciones, cálculos, permisos, baja lógica.
- [ ] **Deploy funcional en la nube** con base de datos y variables de entorno configuradas.
- [ ] **Documentación:**
  - `README.md` con instalación, variables de entorno, comandos y link al deploy.
  - **Swagger** funcional (drf-spectacular) en `/api/schema/swagger/` si hay API.

**Definición de "CRUD completo":**

| Operación | Requisito |
|-----------|-----------|
| Create | Formulario validado en backend, mensaje de éxito |
| Read (lista) | Tabla con búsqueda/filtros y paginación si aplica |
| Read (detalle) | Vista de detalle o modal con la información completa |
| Update | Formulario precargado, validaciones y mensaje de éxito |
| Delete | Baja lógica (`activo = False`), confirmación y mensaje de éxito |

---

## 4. Estructura de Carpetas y Archivos Esperada

### 4.1 Árbol de referencia

```text
mi_proyecto/
├── config/                     # Configuración del proyecto Django
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # Configuración compartida
│   │   ├── development.py      # DEBUG=True, SQLite, storage local
│   │   ├── production.py       # DEBUG=False, PostgreSQL, S3, seguridad
│   │   └── testing.py          # DB de test, settings aislados
│   ├── urls.py                 # URLs raíz (incluye routers y apps)
│   ├── asgi.py
│   └── wsgi.py
├── core/                       # App central: home, dashboard, vistas comunes
│   ├── views.py
│   ├── urls.py
│   └── templatetags/
├── pacientes/                  # App de dominio (ejemplo)
│   ├── models.py
│   ├── forms.py                # Formularios de la app
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py          # Solo si la app expone API
│   ├── admin.py
│   ├── signals.py
│   ├── tests/
│   │   ├── test_models.py
│   │   └── test_views.py
│   └── migrations/
├── turnos/                     # Otra app de dominio
│   └── ...
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── partials/               # navbar, sidebar, messages, footer
│   ├── registration/           # login, password reset
│   ├── pacientes/              # templates propios de la app
│   │   ├── list.html
│   │   ├── detail.html
│   │   ├── form.html
│   │   └── confirm_delete.html
│   └── turnos/
│       └── ...
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── media/                      # Archivos subidos (dev, no versionar)
├── docs/                       # Documentación extra, capturas, manuales
├── manage.py
├── pyproject.toml              # o requirements.txt
├── .env                        # Secretos locales (NO versionar)
├── .env.example                # Plantilla de variables (SÍ versionar)
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── README.md
├── memoria.md
├── bitacora.md
├── proyecto.md
├── design.md
└── inicio.md                   # Este archivo
```

### 4.2 Reglas de organización

- **Separación de settings:** siempre `base.py`, `development.py`, `production.py` (y opcionalmente `testing.py`). `base.py` define lo común; cada ambiente importa `*` de base y sobreescribe lo necesario.
- **App `core`:** centraliza home, dashboard, vistas transversales y templates compartidos (`base.html`, `partials/`). No mezclar lógica de dominio acá.
- **Una app por dominio:** `pacientes`, `turnos`, `facturacion`, etc. Cada app es dueña de sus modelos, forms, vistas, URLs y templates.
- **Templates por app:** `templates/<app>/`. Los compartidos van en `templates/partials/`.
- **`forms.py` por app:** los formularios se definen en la app dueña del modelo. Si hay un form realmente transversal, va en `core/forms.py`.
- **Serializers (si hay API):** `serializers.py` en cada app, con el **patrón de 3 niveles** (ver sección 6.2).
- **`signals.py` por app:** automatizaciones (stock, totales, asistencias) viven en la app que las origina, registradas en `apps.py`.
- **Archivos `.md` obligatorios en la raíz:** `memoria.md`, `bitacora.md`, `proyecto.md`, `design.md`.

### 4.3 Configuración de settings

```python
# config/settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

```python
# config/settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# PostgreSQL vía DATABASE_URL / variables de entorno
# STORAGES con S3/Supabase
# SECURE_* y CSRF_TRUSTED_ORIGINS obligatorios
```

```bash
# Selección del ambiente (nunca hardcodear en manage.py)
export DJANGO_SETTINGS_MODULE=config.settings.development
```

---

## 5. Estándares de Código y UI

### 5.1 Cero secretos en el código

- **Todo secreto va en `.env`:** `SECRET_KEY`, credenciales de base, claves S3, tokens, emails, etc.
- `.env` **nunca** se versiona. `.env.example` sí, con valores de ejemplo y comentarios.
- En `base.py`: `load_dotenv()` y lectura por `os.environ`.
- Nunca commitear claves, tokens ni contraseñas. Ante la duda, revisar el diff antes de commitear.

```text
# .env.example (sin valores reales)
SECRET_KEY=cambiar-en-produccion
DEBUG=True
DATABASE_URL=postgres://usuario:password@host:5432/db
USE_SUPABASE_STORAGE=False
SUPABASE_S3_ACCESS_KEY=
SUPABASE_S3_SECRET_KEY=
SUPABASE_S3_BUCKET=
SUPABASE_S3_ENDPOINT=
```

### 5.2 Validaciones dobles (backend y frontend)

- **Backend es la fuente de verdad:** validaciones en `forms.py`, modelos y/o serializers. Nunca confiar solo en el HTML.
- **Frontend es ayuda, no seguridad:** atributos `required`, `min`, `max`, `pattern`, `type="email"`, etc., para mejor UX.
- Mensajes de error claros, asociados al campo, y visibles en el formulario.
- Reglas de negocio cruzadas (fechas, solapamientos, stock, totales, DNI único) siempre en backend.

### 5.3 Modales nativos y Live Search

**Modales:**

- Usar el elemento nativo `<dialog>` (accesible y sin dependencias).
- Cerrar con botón X, click en backdrop y tecla `Escape`.
- Clases de referencia: `p-0 rounded-xl shadow-2xl backdrop:bg-black/50 w-full max-w-lg`.

```html
<dialog id="modal-detalle" class="p-0 rounded-xl shadow-2xl backdrop:bg-black/50 w-full max-w-lg">
  <div class="p-6">
    <div class="flex justify-between items-start">
      <h2 class="text-lg font-semibold text-gray-700">Detalle</h2>
      <button type="button" onclick="document.getElementById('modal-detalle').close()">✕</button>
    </div>
    <!-- contenido -->
  </div>
</dialog>
```

**Live Search:**

- Input con ícono de lupa, `id` único en el contenedor de resultados.
- Debounce de ~300ms, `fetch` al backend y reemplazo del contenedor sin recargar.
- Event delegation en el contenedor para que los clicks sobrevivan al re-render.
- El filtro del backend respeta permisos por rol y usa `Q` objects.
- Actualizar la URL con `history.replaceState` para que el estado sea compartible.

### 5.4 Diseño limpio con Tailwind

Base visual en `design.md`. Resumen:

| Elemento | Estilo |
|----------|--------|
| Fondo general | `bg-gray-50` |
| Tarjetas | `bg-white border border-gray-100 shadow-sm` |
| Color primario | Verde (`bg-primary-600`, `text-primary-600`) |
| Error | `bg-red-100 text-red-800` |
| Advertencia | `bg-yellow-100 text-yellow-800` |
| Éxito | `bg-green-100 text-green-800` |
| Información | `bg-sky-100 text-sky-800` |
| Títulos | `text-2xl font-bold text-gray-900` |
| Tablas (thead) | `text-gray-500 uppercase text-xs` |
| Filas | `hover:bg-gray-50 cursor-pointer` |
| Badges | `px-2.5 py-0.5 rounded-full text-xs font-medium` |

**Regla de oro de UI:** nunca modificar atributos lógicos (IDs, `name`, `onclick`, URLs, variables de Django) al hacer ajustes visuales. Solo clases de Tailwind y estructura visual.

**Feedback de usuario:** usar `django.contrib.messages` y renderizar en `templates/partials/messages.html` con estilos por nivel (`success`, `error`, `warning`, `info`). Toda acción que muta datos debe dejar un mensaje.

### 5.5 Estilo de código Python/Django

- Nombres de modelos en **singular** y `PascalCase` (`Paciente`, `PlanTratamiento`).
- Campos y métodos en `snake_case`.
- Vistas basadas en clases cuando aportan (ListView, DetailView, CreateView, UpdateView); funciones cuando es más simple.
- `select_related` / `prefetch_related` para evitar N+1 en listados y detalles.
- Sin lógica de negocio en templates ni en `views.py` cuando corresponde a un modelo/servicio.
- Docstrings y comentarios en español, cortos y útiles.
- Formateo consistente (línea máxima ~100 caracteres) y sin imports muertos.

### 5.6 Soft delete (baja lógica)

- Todo modelo de dominio tiene `activo = models.BooleanField(default=True)`.
- No se hace `DELETE` físico desde la UI.
- Los querysets de listado filtran `activo=True` por defecto.
- El "eliminar" de la UI es un POST que setea `activo=False` y redirige con mensaje de éxito.
- Si un registro se puede reactivar, se ofrece la acción explícita.

---

## 6. Instrucciones para el Agente de IA

Estas reglas son obligatorias para cualquier agente que trabaje en el proyecto.

### 6.1 Antes de escribir código

1. Leer `inicio.md` (este archivo).
2. Leer `memoria.md` si existe, para entender estado y decisiones.
3. Leer `proyecto.md` y `design.md` si la tarea toca arquitectura o UI.
4. Revisar la estructura real del repo antes de asumir nombres o rutas.
5. Para tareas no triviales: **proponer un plan** (archivos, decisiones, riesgos) y esperar aprobación.
6. Verificar si la dependencia o patrón que se quiere usar ya existe en el proyecto. No inventar librerías.

### 6.2 Patrones obligatorios de implementación

- **Si es API:** aplicar siempre el **patrón de 3 niveles en serializers**:

```python
class PacienteBaseSerializer(serializers.ModelSerializer):
    """Campos comunes y validaciones compartidas."""
    class Meta:
        model = Paciente
        fields = [...]  # campos base


class PacienteGetSerializer(PacienteBaseSerializer):
    """Lectura: incluye datos relacionados y anidados."""
    pass


class PacientePostSerializer(PacienteBaseSerializer):
    """Escritura: valida reglas de negocio y relaciones."""
    pass
```

- **Si es MVT:** la validación y los widgets van en **`forms.py`** de la app. Las vistas no repiten validaciones que ya hace el form.
- **Permisos:** validar en backend (mixins, decoradores, permisos DRF). El ocultamiento en templates es solo UX.
- **Reglas de negocio:** en modelos, forms/serializers o servicios, nunca en templates.
- **Migraciones:** una migración por cambio lógico, con nombre descriptivo. Revisar antes de aplicar.

### 6.3 Git

- **Nunca ejecutar Git directamente.** Ni `add`, ni `commit`, ni `push`, ni `merge`, ni `rebase`, ni `checkout`.
- **Solo sugerir los comandos** en un bloque de código, explicando qué hacen y por qué.
- El humano decide cuándo y cómo ejecutarlos.
- Tampoco modificar configuración de Git ni hooks.

### 6.4 Documentación y cierre de tarea

- **Actualizar `bitacora.md` después de cada tarea importante**, con fecha, qué se hizo, archivos tocados y verificaciones.
- Actualizar `memoria.md` cuando cambie el estado del proyecto o se tome una decisión arquitectónica.
- Actualizar `proyecto.md` cuando cambie la arquitectura, un modelo o un endpoint.
- Actualizar `README.md` si cambian instalación, variables o comandos.
- Verificar antes de cerrar:
  - `python manage.py check`
  - Tests relevantes (`pytest` o `python manage.py test`)
  - Flujo manual si aplica (crear/editar/eliminar, feedback, permisos).
- Si no se pudo verificar algo, decirlo explícitamente. No afirmar que funciona sin evidencia.

### 6.5 Límites y seguridad

- No commitear secretos ni mostrarlos en logs.
- No borrar archivos o datos sin confirmación.
- No cambiar `.env`, CORS, CSRF, `ALLOWED_HOSTS` ni settings de seguridad sin advertirlo.
- No instalar dependencias nuevas sin justificar y consultar.
- No reescribir archivos grandes sin mostrar el alcance o el diff.
- Ante ambigüedad, preguntar antes de asumir.

---

## 7. Checklist de Arranque de un Proyecto Nuevo

- [ ] Crear carpeta del proyecto y repositorio.
- [ ] Copiar `inicio.md` a la raíz y leerlo completo.
- [ ] Crear entorno virtual e instalar Django.
- [ ] Crear proyecto (`config`) y separar settings (`base`, `development`, `production`, `testing`).
- [ ] Configurar `.env` + `.env.example` + `.gitignore`.
- [ ] Crear app `core` y `templates/base.html` + `partials/`.
- [ ] Configurar Tailwind por CDN y la paleta de `design.md`.
- [ ] Implementar auth y roles mínimos.
- [ ] Crear `memoria.md`, `bitacora.md`, `proyecto.md`, `design.md`.
- [ ] Desarrollar los 3 CRUDs con soft delete y feedback.
- [ ] Escribir tests de reglas de negocio.
- [ ] Configurar Swagger si hay API.
- [ ] Dockerizar y desplegar.
- [ ] Completar README con instalación, variables y link al deploy.
- [ ] Registrar el cierre en `bitacora.md`.

---

## 8. Cómo arranca un compañero con este archivo

1. Crea su carpeta del proyecto.
2. Copia `inicio.md` en la raíz.
3. Abre OpenCode y le dice:
   *"Leé el archivo inicio.md y empezá a generar la estructura base del proyecto. Decime qué archivos vamos a crear primero."*
4. El agente lee este documento, entiende las reglas y propone el plan de arranque.
5. A partir de ahí, el agente sabe que debe:
   - Crear `memoria.md`, `bitacora.md`, `proyecto.md` y `design.md`.
   - Trabajar con GitFlow y commits semánticos.
   - Aplicar validaciones dobles.
   - Seguir el estilo de `design.md`.
   - Nunca ejecutar Git, solo sugerir comandos.
   - Actualizar la bitácora al cerrar cada tarea.

> **Recordatorio final:** este documento no reemplaza el criterio humano. Es una guía viva: si una regla deja de servir, se discute, se actualiza acá y se registra la decisión en `memoria.md`.
