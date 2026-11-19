from decimal import Decimal

from django import forms

from core.forms import EstiloBootstrapMixin

from .models import Producto


class ProductoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Producto
        fields = (
            "codigo",
            "nombre",
            "categoria",
            "descripcion",
            "espesor",
            "precio_unitario",
            "stock",
            "proveedor",
            "activo",
        )
        error_messages = {
            "codigo": {"unique": "Ya existe un producto con este código."},
        }

    def clean_precio_unitario(self):
        precio = self.cleaned_data.get("precio_unitario")
        if precio is not None and precio <= Decimal("0"):
            raise forms.ValidationError("El precio unitario debe ser mayor a 0.")
        return precio
