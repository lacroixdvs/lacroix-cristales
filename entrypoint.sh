#!/bin/sh
set -eu

echo "==> Aplicando migraciones..."
python manage.py migrate --noinput

echo "==> Sincronizando roles y permisos..."
if [ -n "${ADMIN_PASSWORD:-}" ]; then
    python manage.py cargar_roles --crear-admin \
        --admin-username "${ADMIN_USERNAME:-admin}" \
        --admin-email "${ADMIN_EMAIL:-admin@vitcristales.local}"
else
    python manage.py cargar_roles
fi

echo "==> Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "==> Levantando Gunicorn en 0.0.0.0:${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-3}" \
    --timeout "${WEB_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
