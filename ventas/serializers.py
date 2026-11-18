"""Serializers de ventas con el patrón Base / Get / Post.

Las reglas cruzadas (totales, snapshot de precio y stock) se delegan a
`ventas.services`; acá solo se valida la forma de los datos de entrada.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from catalogo.models import Producto
from catalogo.serializers import ProductoBaseSerializer
from clientes.models import Cliente
from clientes.serializers import ClienteBaseSerializer
from usuarios.models import Rol, Usuario
from usuarios.serializers import UsuarioBaseSerializer

from . import services
from .models import DetalleVenta, EstadoVenta, Venta


class DetalleVentaBaseSerializer(serializers.ModelSerializer):
    """Campos comunes del ítem: precio y subtotal son calculados por el servicio."""

    class Meta:
        model = DetalleVenta
        fields = (
            "id",
            "venta",
            "producto",
            "cantidad",
            "precio_unitario",
            "subtotal",
            "activo",
        )
        read_only_fields = ("precio_unitario", "subtotal")


class DetalleVentaGetSerializer(DetalleVentaBaseSerializer):
    """Lectura: producto anidado y venta como PK legible."""

    producto = ProductoBaseSerializer(read_only=True)

    class Meta(DetalleVentaBaseSerializer.Meta):
        fields = DetalleVentaBaseSerializer.Meta.fields


class DetalleVentaPostSerializer(DetalleVentaBaseSerializer):
    """Escritura: delega la creación a `services.agregar_detalle`."""

    class Meta(DetalleVentaBaseSerializer.Meta):
        extra_kwargs = {"activo": {"required": False}}

    def validate_cantidad(self, valor):
        if valor < 1:
            raise serializers.ValidationError("La cantidad debe ser al menos 1.")
        return valor

    def validate_producto(self, valor):
        if not valor.activo:
            raise serializers.ValidationError("El producto no está activo.")
        return valor

    def create(self, validated_data):
        try:
            return services.agregar_detalle(
                validated_data["venta"],
                validated_data["producto"],
                validated_data["cantidad"],
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error


class VentaBaseSerializer(serializers.ModelSerializer):
    """Campos comunes; estado e importes son calculados, no escritos por el cliente."""

    estado = serializers.CharField(read_only=True)

    class Meta:
        model = Venta
        fields = (
            "id",
            "cliente",
            "vendedor",
            "fecha",
            "estado",
            "observaciones",
            "subtotal",
            "descuento_mayorista",
            "total",
            "activo",
        )
        read_only_fields = ("fecha", "subtotal", "descuento_mayorista", "total")


class VentaGetSerializer(VentaBaseSerializer):
    """Lectura: relaciones anidadas y detalles activos con precio snapshot."""

    cliente = serializers.SerializerMethodField()
    vendedor = serializers.SerializerMethodField()
    detalles = serializers.SerializerMethodField()
    resumen = serializers.SerializerMethodField()

    class Meta(VentaBaseSerializer.Meta):
        fields = VentaBaseSerializer.Meta.fields + ("detalles", "resumen")

    @extend_schema_field(ClienteBaseSerializer)
    def get_cliente(self, obj):
        return ClienteBaseSerializer(obj.cliente).data

    @extend_schema_field(UsuarioBaseSerializer)
    def get_vendedor(self, obj):
        return UsuarioBaseSerializer(obj.vendedor).data

    @extend_schema_field(DetalleVentaGetSerializer(many=True))
    def get_detalles(self, obj):
        return DetalleVentaGetSerializer(obj.detalles.filter(activo=True), many=True).data

    @extend_schema_field(
        serializers.DictField(child=serializers.CharField())
    )
    def get_resumen(self, obj):
        return services.resumen(obj)


class VentaPostSerializer(VentaBaseSerializer):
    """Escritura: cliente/vendedor activos y edición limitada a borradores."""

    class Meta(VentaBaseSerializer.Meta):
        extra_kwargs = {"activo": {"required": False}}

    def validate_cliente(self, valor):
        if not Cliente.objects.filter(pk=valor.pk, activo=True).exists():
            raise serializers.ValidationError("El cliente no existe o no está activo.")
        return valor

    def validate_vendedor(self, valor):
        if not valor.activo or not valor.groups.filter(name=Rol.VENDEDOR).exists():
            raise serializers.ValidationError("El vendedor debe ser un usuario VENDEDOR activo.")
        return valor

    def validate(self, attrs):
        if self.instance and self.instance.estado != EstadoVenta.BORRADOR:
            raise serializers.ValidationError("Solo se pueden editar ventas en borrador.")
        return attrs
