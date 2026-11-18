"""ViewSets de la API con la misma matriz de roles que el frontend MVT."""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from catalogo.models import Producto
from catalogo.serializers import (
    ProductoBaseSerializer,
    ProductoGetSerializer,
    ProductoPostSerializer,
)
from clientes.models import Cliente
from clientes.serializers import ClienteBaseSerializer, ClienteGetSerializer, ClientePostSerializer
from core.roles import rol_de
from proveedores.models import Proveedor
from proveedores.serializers import (
    ProveedorBaseSerializer,
    ProveedorGetSerializer,
    ProveedorPostSerializer,
)
from usuarios.models import Rol, Usuario
from usuarios.serializers import UsuarioGetSerializer, UsuarioPostSerializer
from ventas import services
from ventas.models import DetalleVenta, Venta
from ventas.serializers import (
    DetalleVentaGetSerializer,
    DetalleVentaPostSerializer,
    VentaGetSerializer,
    VentaPostSerializer,
)

from .filters import (
    ClienteFilter,
    ProductoFilter,
    ProveedorFilter,
    UsuarioFilter,
    VentaFilter,
)
from .permissions import (
    AdminEscribeOtrosLeen,
    AdminEscribeVendedorLee,
    SoloAdmin,
    VentaPermission,
)


def _ejecutar_servicio(funcion, *args):
    """Traduce los `ValidationError` de Django a respuestas 400 de DRF."""
    try:
        return funcion(*args)
    except DjangoValidationError as error:
        raise ValidationError(error.messages) from error


class SerializerPorAccionMixin:
    """Get para lectura (relaciones anidadas); Post para escrituras validadas."""

    serializer_get = None
    serializer_post = None

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return self.serializer_get
        return self.serializer_post


class UsuarioViewSet(SerializerPorAccionMixin, viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by("username")
    serializer_get = UsuarioGetSerializer
    serializer_post = UsuarioPostSerializer
    permission_classes = (SoloAdmin,)
    filterset_class = UsuarioFilter
    search_fields = ("username", "email", "first_name", "last_name")
    ordering_fields = "__all__"

    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise ValidationError("Un administrador no puede darse de baja a sí mismo.")
        instance.activo = False
        instance.is_active = False
        instance.save(update_fields=["activo", "is_active"])


class ProveedorViewSet(SerializerPorAccionMixin, viewsets.ModelViewSet):
    queryset = Proveedor.objects.all().order_by("razon_social")
    serializer_get = ProveedorGetSerializer
    serializer_post = ProveedorPostSerializer
    permission_classes = (SoloAdmin,)
    filterset_class = ProveedorFilter
    search_fields = ("razon_social", "cuit", "email", "rubro")
    ordering_fields = "__all__"

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo"])


class ClienteViewSet(SerializerPorAccionMixin, viewsets.ModelViewSet):
    serializer_get = ClienteGetSerializer
    serializer_post = ClientePostSerializer
    permission_classes = (AdminEscribeVendedorLee,)
    filterset_class = ClienteFilter
    search_fields = ("razon_social", "cuit", "email")
    ordering_fields = "__all__"

    def get_queryset(self):
        queryset = Cliente.objects.all().order_by("razon_social")
        if rol_de(self.request.user) != Rol.ADM:
            queryset = queryset.filter(activo=True)
        return queryset

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo"])


class ProductoViewSet(SerializerPorAccionMixin, viewsets.ModelViewSet):
    serializer_get = ProductoGetSerializer
    serializer_post = ProductoPostSerializer
    permission_classes = (AdminEscribeOtrosLeen,)
    filterset_class = ProductoFilter
    search_fields = ("codigo", "nombre", "categoria")
    ordering_fields = "__all__"

    def get_queryset(self):
        queryset = Producto.objects.select_related("proveedor").all().order_by("nombre")
        if rol_de(self.request.user) != Rol.ADM:
            queryset = queryset.filter(activo=True)
        return queryset

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo"])


class VentaViewSet(SerializerPorAccionMixin, viewsets.ModelViewSet):
    serializer_get = VentaGetSerializer
    serializer_post = VentaPostSerializer
    permission_classes = (VentaPermission,)
    filterset_class = VentaFilter
    search_fields = ("cliente__razon_social", "cliente__cuit", "vendedor__username")
    ordering_fields = "__all__"

    def get_queryset(self):
        queryset = (
            Venta.objects.select_related("cliente", "vendedor")
            .prefetch_related("detalles__producto")
            .all()
            .order_by("-fecha", "-id")
        )
        # drf-spectacular introspecciona la vista sin request real.
        if getattr(self, "swagger_fake_view", False):
            return queryset
        if rol_de(self.request.user) != Rol.ADM:
            queryset = queryset.filter(vendedor=self.request.user, activo=True)
        return queryset

    def perform_create(self, serializer):
        if rol_de(self.request.user) == Rol.VENDEDOR:
            serializer.save(vendedor=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        if rol_de(self.request.user) == Rol.VENDEDOR:
            serializer.save(vendedor=self.request.user)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        # Solo ADM llega acá (VentaPermission). El servicio reintegra el stock.
        services.dar_de_baja(instance)

    def _detalle(self, venta, serializer_class=None):
        contexto = self.get_serializer_context()
        if serializer_class is None:
            serializer_class = VentaGetSerializer
        return serializer_class(venta, context=contexto).data

    @action(detail=True, methods=["post"], url_path="confirmar")
    def confirmar(self, request, pk=None):
        venta = self.get_object()
        _ejecutar_servicio(services.confirmar_venta, venta)
        venta.refresh_from_db()
        return Response(self._detalle(venta))

    @action(detail=True, methods=["post"], url_path="cancelar")
    def cancelar(self, request, pk=None):
        venta = self.get_object()
        _ejecutar_servicio(services.cancelar_venta, venta)
        venta.refresh_from_db()
        return Response(self._detalle(venta))

    @action(detail=True, methods=["post"], url_path="detalles/agregar")
    def agregar_item(self, request, pk=None):
        venta = self.get_object()
        datos = request.data.dict() if hasattr(request.data, "dict") else dict(request.data)
        datos["venta"] = venta.pk
        serializer = DetalleVentaPostSerializer(data=datos, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        detalle = serializer.save()
        return Response(
            DetalleVentaGetSerializer(detalle, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["delete"], url_path=r"detalles/(?P<detalle_id>\d+)")
    def quitar_item(self, request, pk=None, detalle_id=None):
        venta = self.get_object()
        detalle = get_object_or_404(
            DetalleVenta, pk=detalle_id, venta=venta, activo=True
        )
        _ejecutar_servicio(services.quitar_detalle, detalle)
        return Response(status=status.HTTP_204_NO_CONTENT)
