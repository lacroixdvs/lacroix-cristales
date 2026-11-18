from django import template

from core.roles import rol_de

register = template.Library()


@register.filter
def rol_actual(user):
    """Devuelve el rol efectivo para mostrarlo en la interfaz."""
    return rol_de(user) or ""


@register.simple_tag
def es_rol(user, rol_esperado):
    """Verdadero cuando el rol efectivo coincide con el indicado."""
    return rol_de(user) == rol_esperado
