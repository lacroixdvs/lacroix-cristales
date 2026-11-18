"""Serializers de proveedores con el patrón Base / Get / Post."""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.validators import normalizar_cuit

from .models import Proveedor


class ProveedorBaseSerializer(serializers.ModelSerializer):
    """Campos comunes y validaciones compartidas."""

    class Meta:
        model = Proveedor
        fields = (
            "id",
            "razon_social",
            "cuit",
            "contacto",
            "email",
            "direccion",
            "rubro",
            "activo",
        )


class ProveedorGetSerializer(ProveedorBaseSerializer):
    """Lectura: incluye el resumen de productos vinculados."""

    productos_activos = serializers.SerializerMethodField()

    class Meta(ProveedorBaseSerializer.Meta):
        fields = ProveedorBaseSerializer.Meta.fields + ("productos_activos",)

    @extend_schema_field(serializers.IntegerField)
    def get_productos_activos(self, obj):
        return obj.productos.filter(activo=True).count()


class ProveedorPostSerializer(ProveedorBaseSerializer):
    """Escritura: normaliza y controla la unicidad del CUIT."""

    # Evita el RegexValidator del modelo para poder normalizar 11 dígitos.
    cuit = serializers.CharField(max_length=13)

    class Meta(ProveedorBaseSerializer.Meta):
        extra_kwargs = {"activo": {"required": False}}

    def validate_cuit(self, valor):
        cuit = normalizar_cuit(valor)
        existentes = Proveedor.objects.filter(cuit=cuit)
        if self.instance:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise serializers.ValidationError("Ya existe un proveedor con este CUIT.")
        return cuit
