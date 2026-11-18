"""Serializers del catálogo con el patrón Base / Get / Post."""

from decimal import Decimal

from rest_framework import serializers

from proveedores.models import Proveedor
from proveedores.serializers import ProveedorBaseSerializer

from .models import Categoria, Producto


class ProductoBaseSerializer(serializers.ModelSerializer):
    """Campos comunes y validaciones compartidas."""

    class Meta:
        model = Producto
        fields = (
            "id",
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


class ProductoGetSerializer(ProductoBaseSerializer):
    """Lectura: proveedor anidado y etiqueta legible de la categoría."""

    proveedor = ProveedorBaseSerializer(read_only=True)
    categoria_etiqueta = serializers.CharField(read_only=True)

    class Meta(ProductoBaseSerializer.Meta):
        fields = ProductoBaseSerializer.Meta.fields + ("categoria_etiqueta",)


class ProductoPostSerializer(ProductoBaseSerializer):
    """Escritura: precio positivo, categoría válida y proveedor activo."""

    class Meta(ProductoBaseSerializer.Meta):
        extra_kwargs = {"activo": {"required": False}}

    def validate_categoria(self, valor):
        if valor not in Categoria.values:
            raise serializers.ValidationError("Categoría no válida.")
        return valor

    def validate_precio_unitario(self, valor):
        if valor is None or valor <= Decimal("0"):
            raise serializers.ValidationError("El precio unitario debe ser mayor a 0.")
        return valor

    def validate_proveedor(self, valor):
        if not Proveedor.objects.filter(pk=valor.pk, activo=True).exists():
            raise serializers.ValidationError("El proveedor no existe o no está activo.")
        return valor
