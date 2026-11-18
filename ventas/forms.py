"""Formularios de ventas con opciones activas y precios snapshot."""

from django import forms

from clientes.models import Cliente
from core.forms import EstiloTailwindMixin
from usuarios.models import Rol, Usuario

from .models import Venta


class VentaForm(EstiloTailwindMixin, forms.ModelForm):
    class Meta:
        model = Venta
        fields = ("cliente", "vendedor", "observaciones")
        widgets = {"observaciones": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.filter(activo=True)
        self.fields["vendedor"].queryset = Usuario.objects.filter(
            groups__name=Rol.VENDEDOR, activo=True
        ).distinct()
