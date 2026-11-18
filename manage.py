#!/usr/bin/env python
"""Punto de entrada de los comandos de Django para Vit Cristales."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def main():
    """Carga el módulo de settings indicado por entorno y ejecuta el comando."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está activo el entorno virtual e instaladas las dependencias?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
