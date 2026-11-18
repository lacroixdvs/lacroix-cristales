"""Settings aislados para la suite de tests."""

from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = "clave-solo-para-tests-suffixed-longitud-suficiente-jwt"
ALLOWED_HOSTS = ["testserver"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
