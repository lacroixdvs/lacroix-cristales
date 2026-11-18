"""Settings de producción: PostgreSQL, WhiteNoise, seguridad y storage S3 opcional.

Todo lo sensible se lee de variables de entorno. Los valores por defecto de
seguridad son los estrictos; para probar HTTP dentro de Docker se pueden
desactivar explícitamente con SECURE_SSL_REDIRECT=False y cookies no seguras.
"""

import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403


def _lista_env(nombre):
    """Divide una variable CSV en una lista limpia, sin entradas vacías."""
    return [item.strip() for item in os.environ.get(nombre, "").split(",") if item.strip()]


def _bool_env(nombre, default=False):
    valor = os.environ.get(nombre)
    if valor is None or not valor.strip():
        return default
    return valor.strip().lower() in ("1", "true", "yes", "on")


# --- Seguridad base -------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
if not SECRET_KEY:
    raise ImproperlyConfigured("Definí SECRET_KEY en las variables de entorno")

DEBUG = False

# --- Hosts y orígenes CSRF ------------------------------------------------
ALLOWED_HOSTS = _lista_env("ALLOWED_HOSTS")
# Render inyecta RENDER_EXTERNAL_HOSTNAME automáticamente. El comodín con
# punto inicial es la forma de Django de aceptar cualquier subdominio.
if os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip():
    host_render = os.environ["RENDER_EXTERNAL_HOSTNAME"].strip()
    if host_render not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host_render)
    if ".onrender.com" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(".onrender.com")
# Fallback seguro para healthchecks locales dentro de Docker.
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CSRF_TRUSTED_ORIGINS = _lista_env("CSRF_TRUSTED_ORIGINS")
if ".onrender.com" in ALLOWED_HOSTS and "https://*.onrender.com" not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append("https://*.onrender.com")
for host in ALLOWED_HOSTS:
    if host.endswith(".onrender.com") and host != ".onrender.com":
        origen = f"https://{host}"
        if origen not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origen)

# --- Base de datos --------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
else:
    # Fallback seguro: el SQLite de base.py, útil solo para pruebas locales.
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

# --- Archivos estáticos con WhiteNoise ------------------------------------
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Manifest es lo recomendado; se puede bajar a CompressedStaticFilesStorage
# con la variable de entorno si algún archivo referenciado no existe.
STORAGES["staticfiles"] = {
    "BACKEND": os.environ.get(
        "STATICFILES_STORAGE_BACKEND",
        "whitenoise.storage.CompressedManifestStaticFilesStorage",
    )
}
WHITENOISE_AUTOREFRESH = _bool_env("WHITENOISE_AUTOREFRESH", False)

# --- Cabeceras de seguridad (activables/desactivables por entorno) --------
SECURE_SSL_REDIRECT = _bool_env("SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", True)
CSRF_COOKIE_SECURE = _bool_env("CSRF_COOKIE_SECURE", True)
SECURE_CONTENT_TYPE_NOSNIFF = _bool_env("SECURE_CONTENT_TYPE_NOSNIFF", True)
SECURE_REFERRER_POLICY = os.environ.get("SECURE_REFERRER_POLICY", "same-origin")
# Render termina TLS en su proxy; confiamos en el header que él setea.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if _bool_env("SECURE_HSTS_ENABLED", True):
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = _bool_env("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = _bool_env("SECURE_HSTS_PRELOAD", True)
else:
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

# --- Storage de media compatible con S3 / Supabase (condicional) ----------
# Se activa solo si el flag está en True Y existen las cuatro credenciales.
_S3 = {
    "access_key": os.environ.get("SUPABASE_S3_ACCESS_KEY", "").strip(),
    "secret_key": os.environ.get("SUPABASE_S3_SECRET_KEY", "").strip(),
    "bucket": os.environ.get("SUPABASE_S3_BUCKET", "").strip(),
    "endpoint": os.environ.get("SUPABASE_S3_ENDPOINT", "").strip(),
}

if _bool_env("USE_SUPABASE_STORAGE", False) and all(_S3.values()):
    try:
        import storages.backends.s3  # noqa: F401
    except ImportError as exc:  # pragma: no cover - depende del entorno de deploy
        raise ImproperlyConfigured(
            "USE_SUPABASE_STORAGE=True requiere django-storages y boto3 en requirements.txt"
        ) from exc

    ubicacion = os.environ.get("SUPABASE_S3_LOCATION", "media").strip("/")
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": _S3["access_key"],
            "secret_key": _S3["secret_key"],
            "bucket_name": _S3["bucket"],
            "endpoint_url": _S3["endpoint"],
            "region_name": os.environ.get("SUPABASE_S3_REGION", "auto").strip(),
            "location": ubicacion,
            "default_acl": None,
            "file_overwrite": False,
            "use_ssl": _S3["endpoint"].startswith("https://"),
        },
    }
    MEDIA_URL = (
        os.environ.get(
            "SUPABASE_S3_PUBLIC_URL",
            f"{_S3['endpoint'].rstrip('/')}/{_S3['bucket']}/{ubicacion}/",
        ).rstrip("/")
        + "/"
    )
