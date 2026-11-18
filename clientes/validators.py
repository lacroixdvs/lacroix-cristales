"""Compatibilidad: el validador de CUIT vive ahora en `core.validators`."""

from core.validators import CUIT_FORMATO, MENSAJE_CUIT, normalizar_cuit  # noqa: F401
