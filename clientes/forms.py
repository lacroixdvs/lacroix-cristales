from decimal import Decimal

from django import forms

from .models import Cliente
from .validators import normalizar_cuit


class EstiloTailwindMixin:
    """Solo presentación: clases Tailwind en los widgets."""

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


class ClienteForm(EstiloTailwindMixin, forms.ModelForm):
    """Doble validación: normalización de CUIT y rango de descuento, además del modelo."""

    class Meta:
        model = Cliente
        fields = (
            "razon_social",
            "cuit",
            "contacto",
            "email",
            "direccion",
            "descuento_mayorista",
            "activo",
        )
        error_messages = {
            "cuit": {"unique": "Ya existe un cliente con este CUIT."},
        }

    def clean_cuit(self):
        cuit = normalizar_cuit(self.cleaned_data.get("cuit"))
        existentes = Cliente.objects.filter(cuit=cuit)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError("Ya existe un cliente con este CUIT.")
        return cuit

    def clean_descuento_mayorista(self):
        descuento = self.cleaned_data.get("descuento_mayorista")
        if descuento is None:
            return descuento
        if descuento < Decimal("0") or descuento > Decimal("100"):
            raise forms.ValidationError("El descuento mayorista debe estar entre 0 y 100.")
        return descuento
