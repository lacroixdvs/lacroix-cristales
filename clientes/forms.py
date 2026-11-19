from decimal import Decimal

from django import forms

from core.forms import EstiloBootstrapMixin

from .models import Cliente
from .validators import normalizar_cuit


class ClienteForm(EstiloBootstrapMixin, forms.ModelForm):
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
