"""Presentación repetible de formularios: solo clases Tailwind, sin lógica."""


from django import forms


class EstiloTailwindMixin:
    """Aplica la paleta y el borde de `design.md` a todos los widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault(
                    "class", "h-4 w-4 rounded border-gray-300 text-primary-600"
                )
            else:
                field.widget.attrs.setdefault(
                    "class",
                    "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm "
                    "focus:border-primary-600 focus:ring-primary-600",
                )
