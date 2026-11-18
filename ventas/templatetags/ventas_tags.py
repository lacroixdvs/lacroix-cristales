"""Etiquetas de presentación de ventas (clases de `design.md`)."""

from django import template

register = template.Library()

BADGES = {
    "BORRADOR": "bg-yellow-100 text-yellow-800",
    "CONFIRMADA": "bg-green-100 text-green-800",
    "CANCELADA": "bg-red-100 text-red-800",
}


@register.filter
def badge_estado(estado):
    return BADGES.get(estado, "bg-gray-100 text-gray-800")
