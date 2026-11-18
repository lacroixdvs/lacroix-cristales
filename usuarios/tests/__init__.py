"""Utilidades compartidas por los tests de usuarios."""

from usuarios.models import Usuario


def crear_usuario(username, rol, email=None, password="clave-de-prueba-123"):
    """Crea un usuario de prueba con el rol indicado."""
    return Usuario.objects.create_user(
        username=username,
        email=email or f"{username}@ejemplo.com",
        password=password,
        rol=rol,
    )
