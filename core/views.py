from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from usuarios.models import Rol

from .roles import rol_de

MODULOS_POR_ROL = {
    Rol.ADM: ["Usuarios", "Proveedores", "Clientes", "Catálogo", "Ventas"],
    Rol.VENDEDOR: ["Clientes", "Catálogo", "Ventas"],
    Rol.USUARIO: ["Catálogo", "Presupuesto"],
}


class HomeView(TemplateView):
    """Página inicial pública de Vit Cristales."""

    template_name = "home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    """Panel inicial: expone solo los módulos permitidos para el rol."""

    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rol = rol_de(self.request.user)
        context["rol"] = rol
        context["rol_etiqueta"] = dict(Rol.choices).get(rol, "Sin rol")
        context["modulos"] = MODULOS_POR_ROL.get(rol, [])
        context["es_adm"] = rol == Rol.ADM
        context["es_vendedor"] = rol == Rol.VENDEDOR
        context["es_usuario"] = rol == Rol.USUARIO
        return context
