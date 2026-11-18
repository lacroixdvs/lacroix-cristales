# Memoria — Vit Cristales

> Memoria viva del proyecto. Toda decisión relevante debe estar acá; si no está escrita, no existe.
> Guía maestra: [`inicio.md`](inicio.md).

## Estado actual

- **Fecha:** 2026-11-18
- **Fase:** 1 de 9 — Contexto y cimentación (completada)
- **Ubicación:** `C:\Users\Nico\Desktop\lacroix-cristales`
- **Nombre comercial:** Vit Cristales (documentación e interfaz). La carpeta conserva el nombre `lacroix-cristales`.
- **Código generado:** todavía no. La Fase 1 crea solo archivos de contexto y configuración de repositorio.
- **Verificación:** pendiente. No hay proyecto Django ejecutable hasta la Fase 2.

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

- **Fase 2:** crear `manage.py` y el paquete `config/` con settings separados. Definir `AUTH_USER_MODEL = "usuarios.Usuario"` antes de la primera migración.
- **Fase 3:** app `core`, templates base, Tailwind CDN y parciales.
- **Fase 4:** app `usuarios`, grupos, formulario de registro y señales de rol/`is_active`.
- **Fases 5-6:** CRUDs con baja lógica, cálculo de totales y control de stock.
- **Fase 7:** API, Swagger en `/api/schema/swagger/` y JWT.
- **Fases 8-9:** Docker/Render, README final y cierre de bitácora.

## Riesgos y recordatorios

- No correr `migrate` hasta que exista la app `usuarios` y `AUTH_USER_MODEL` esté configurado.
- El cambio de estado de la venta y el movimiento de stock deben ocurrir en la misma transacción.
- No instalar dependencias nuevas sin justificar y consultar. Las de storage S3 se evalúan recién en Fase 8.
- No tocar `.env`, CORS, CSRF, `ALLOWED_HOSTS` ni settings de seguridad sin advertirlo antes.
- Los importes se manejan con `Decimal`, nunca con `float`.
