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
