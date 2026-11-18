"""Serializers de clientes con el patrón Base / Get / Post."""

from decimal import Decimal

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.validators import normalizar_cuit

from .models import Cliente


class ClienteBaseSerializer(serializers.ModelSerializer):
    """Campos comunes y validaciones compartidas."""

    class Meta:
        model = Cliente
        fields = (
            "id",
            "razon_social",
            "cuit",
            "contacto",
            "email",
            "direccion",
            "descuento_mayorista",
            "activo",
        )


class ClienteGetSerializer(ClienteBaseSerializer):
    """Lectura: incluye la cantidad de ventas registradas."""

    ventas_totales = serializers.SerializerMethodField()

    class Meta(ClienteBaseSerializer.Meta):
        fields = ClienteBaseSerializer.Meta.fields + ("ventas_totales",)

    @extend_schema_field(serializers.IntegerField)
    def get_ventas_totales(self, obj):
        return obj.ventas.count()


class ClientePostSerializer(ClienteBaseSerializer):
    """Escritura: CUIT normalizado/único y descuento entre 0 y 100."""

    # Campo explícito para no heredar el RegexValidator del modelo, que exige
    # guiones y rechazaría los 11 dígitos antes de poder normalizarlos.
    cuit = serializers.CharField(max_length=13)

    class Meta(ClienteBaseSerializer.Meta):
        extra_kwargs = {"activo": {"required": False}}

    def validate_cuit(self, valor):
        cuit = normalizar_cuit(valor)
        existentes = Cliente.objects.filter(cuit=cuit)
        if self.instance:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise serializers.ValidationError("Ya existe un cliente con este CUIT.")
        return cuit

    def validate_descuento_mayorista(self, valor):
        if valor is not None and not (Decimal("0") <= valor <= Decimal("100")):
            raise serializers.ValidationError("El descuento mayorista debe estar entre 0 y 100.")
        return valor
