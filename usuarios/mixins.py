"""Control de acceso en backend: los templates solo ocultan, no autorizan."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from core.roles import rol_de

from .models import Rol


class RolRequeridoMixin(LoginRequiredMixin):
    """Exige login y que el rol efectivo esté en `roles_permitidos`."""

    roles_permitidos = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if rol_de(request.user) not in self.roles_permitidos:
            raise PermissionDenied("No tenés permiso para acceder a este módulo.")
        return super().dispatch(request, *args, **kwargs)


class SoloAdminMixin(RolRequeridoMixin):
    """Acceso exclusivo para el perfil ADM."""

    roles_permitidos = (Rol.ADM,)
