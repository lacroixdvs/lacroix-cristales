"""Etiquetas de presentación de ventas (badges de Bootstrap 5)."""

from django import template

register = template.Library()

BADGES = {
    "BORRADOR": "text-bg-warning",
    "CONFIRMADA": "text-bg-success",
    "CANCELADA": "text-bg-danger",
}


@register.filter
def badge_estado(estado):
    return BADGES.get(estado, "text-bg-secondary")
