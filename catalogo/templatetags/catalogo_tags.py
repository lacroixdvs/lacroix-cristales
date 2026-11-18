"""Etiquetas de presentación del catálogo (clases de `design.md`)."""

from django import template

register = template.Library()

BADGES = {
    "VIDRIO": "bg-sky-100 text-sky-800",
    "MAMPARA": "bg-indigo-100 text-indigo-800",
    "ESPEJO": "bg-purple-100 text-purple-800",
    "CERRAMIENTO": "bg-teal-100 text-teal-800",
}


@register.filter
def badge_categoria(categoria):
    return BADGES.get(categoria, "bg-gray-100 text-gray-800")
