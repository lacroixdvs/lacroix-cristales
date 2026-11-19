"""Etiquetas de presentación del catálogo (badges de Bootstrap 5)."""

from django import template

register = template.Library()

BADGES = {
    "VIDRIO": "text-bg-info",
    "MAMPARA": "text-bg-primary",
    "ESPEJO": "text-bg-secondary",
    "CERRAMIENTO": "text-bg-success",
}


@register.filter
def badge_categoria(categoria):
    return BADGES.get(categoria, "text-bg-light border")
