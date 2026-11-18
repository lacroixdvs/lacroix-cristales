"""Resolución del rol efectivo a partir de los grupos de Django Auth."""

from usuarios.models import Rol

_PRIORIDAD = (Rol.ADM, Rol.VENDEDOR, Rol.USUARIO)


def rol_de(user):
    """Devuelve el rol efectivo del usuario.

    Los grupos son la fuente de verdad; el campo `rol` se usa como fallback
    hasta que las señales de la Fase 4 lo mantengan sincronizado.
    """
    if not user or not user.is_authenticated:
        return None

    grupos = set(user.groups.values_list("name", flat=True))
    for rol in _PRIORIDAD:
        if rol in grupos:
            return rol
    return user.rol or Rol.USUARIO
