from django import forms

from core.forms import EstiloBootstrapMixin
from core.validators import normalizar_cuit

from .models import Proveedor


class ProveedorForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = (
            "razon_social",
            "cuit",
            "contacto",
            "email",
            "direccion",
            "rubro",
            "activo",
        )
        error_messages = {
            "cuit": {"unique": "Ya existe un proveedor con este CUIT."},
        }

    def clean_cuit(self):
        cuit = normalizar_cuit(self.cleaned_data.get("cuit"))
        existentes = Proveedor.objects.filter(cuit=cuit)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError("Ya existe un proveedor con este CUIT.")
        return cuit
