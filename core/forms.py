"""Presentación repetible de formularios: solo clases Bootstrap 5, sin lógica."""


from django import forms


class EstiloBootstrapMixin:
    """Aplica clases nativas de Bootstrap 5 a todos los widgets.

    No altera validaciones, nombres ni valores: solo agrega `form-control`,
    `form-select` o `form-check-input` cuando el widget aún no las define.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                clase = "form-check-input"
            elif isinstance(widget, forms.Select):
                clase = "form-select"
            else:
                clase = "form-control"
            widget.attrs.setdefault("class", clase)
