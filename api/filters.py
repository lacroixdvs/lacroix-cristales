"""Filtros `django-filter` reutilizables por los ViewSets de la API."""

import django_filters

from catalogo.models import Producto
from clientes.models import Cliente
from proveedores.models import Proveedor
from usuarios.models import Usuario
from ventas.models import Venta


class UsuarioFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter(field_name="activo")

    class Meta:
        model = Usuario
        fields = ("rol", "activo")


class ProveedorFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter(field_name="activo")

    class Meta:
        model = Proveedor
        fields = ("activo", "rubro")


class ClienteFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter(field_name="activo")

    class Meta:
        model = Cliente
        fields = ("activo",)


class ProductoFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter(field_name="activo")

    class Meta:
        model = Producto
        fields = ("activo", "categoria", "proveedor")


class VentaFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter(field_name="activo")

    class Meta:
        model = Venta
        fields = ("activo", "estado", "cliente", "vendedor")
