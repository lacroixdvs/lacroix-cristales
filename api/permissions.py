"""Permisos de API: espejo exacto de la matriz del frontend MVT.

Los grupos de Django Auth son la fuente de verdad; `core.roles.rol_de()` resuelve
el rol efectivo con prioridad ADM > VENDEDOR > USUARIO.
"""

from rest_framework.permissions import BasePermission

from core.roles import rol_de
from usuarios.models import Rol


class RolRequerido(BasePermission):
    """Base: exige login y que el rol efectivo esté en `roles_permitidos`."""

    roles_permitidos = ()

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return rol_de(user) in self.roles_permitidos


class SoloAdmin(RolRequerido):
    roles_permitidos = (Rol.ADM,)


class AdminOVendedor(RolRequerido):
    roles_permitidos = (Rol.ADM, Rol.VENDEDOR)


class TodosLosRoles(RolRequerido):
    roles_permitidos = (Rol.ADM, Rol.VENDEDOR, Rol.USUARIO)


class AdminEscribeOtrosLeen(RolRequerido):
    """ADM escribe; VENDEDOR y USUARIO solo leen."""

    roles_permitidos = TodosLosRoles.roles_permitidos

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return rol_de(request.user) == Rol.ADM


class AdminEscribeVendedorLee(RolRequerido):
    """Clientes: ADM escribe; VENDEDOR solo lee; USUARIO no accede."""

    roles_permitidos = AdminOVendedor.roles_permitidos

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return rol_de(request.user) == Rol.ADM


_ACCIONES_SOLO_BORRADOR = {
    "update",
    "partial_update",
    "cancelar",  # Igual que en MVT: VENDEDOR solo cancela sus borradores.
    "agregar_item",
    "quitar_item",
}
# `confirmar` no va acá: el propio servicio rechaza ventas no-borrador con 400.


class VentaPermission(AdminOVendedor):
    """ADM gestiona todo; VENDEDOR solo sus ventas y solo en borrador para mutar."""

    def has_object_permission(self, request, view, obj):
        if rol_de(request.user) == Rol.ADM:
            return True
        if obj.vendedor_id != request.user.pk:
            return False
        # La baja lógica (DELETE) de la VENTA es exclusiva de ADM; quitar un
        # índice (también DELETE, pero acción `quitar_item`) sí se permite.
        if request.method == "DELETE" and getattr(view, "action", None) == "destroy":
            return False
        # Consultar una confirmada propia está permitido; mutar, no.
        if getattr(view, "action", None) in _ACCIONES_SOLO_BORRADOR:
            return obj.activo and obj.estado == "BORRADOR"
        return True


class DetallePermission(AdminOVendedor):
    """Solo se pueden alterar ítems de borradores propios (ADM puede todos)."""

    def has_object_permission(self, request, view, obj):
        if rol_de(request.user) == Rol.ADM:
            return True
        venta = obj.venta if hasattr(obj, "venta") else obj
        return (
            venta.vendedor_id == request.user.pk
            and venta.activo
            and venta.estado == "BORRADOR"
        )
