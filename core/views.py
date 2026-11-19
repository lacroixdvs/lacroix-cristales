from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from usuarios.models import Rol

from .roles import rol_de

MODULOS_POR_ROL = {
    Rol.ADM: ["Usuarios", "Proveedores", "Clientes", "Catálogo", "Ventas"],
    Rol.VENDEDOR: ["Clientes", "Catálogo", "Ventas"],
    Rol.USUARIO: ["Catálogo", "Presupuesto"],
}

# Umbral solo informativo para el indicador de "stock bajo" del dashboard.
STOCK_BAJO = 10


class HomeView(TemplateView):
    """Página inicial pública de Vit Cristales."""

    template_name = "home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    """Panel inicial: módulos e indicadores reales según el rol."""

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
        context["kpis"] = self._kpis(rol)
        return context

    def _kpis(self, rol):
        """Indicadores de solo lectura, con los mismos filtros que cada listado."""
        # Importaciones locales para mantener `core` desacoplado del resto de apps.
        from catalogo.models import Producto
        from catalogo.presupuesto import obtener
        from clientes.models import Cliente
        from ventas.models import EstadoVenta, Venta

        catalogo_url = reverse("catalogo:producto-list")
        presupuesto_url = reverse("catalogo:presupuesto")
        ventas_url = reverse("ventas:venta-list")
        clientes_url = reverse("clientes:cliente-list")

        def kpi(etiqueta, valor, icono, url, tono="primary"):
            return {
                "etiqueta": etiqueta,
                "valor": valor,
                "icono": icono,
                "url": url,
                "tono": tono,
            }

        activos = Producto.objects.filter(activo=True)
        stock_bajo = activos.filter(stock__lt=STOCK_BAJO).count()

        if rol == Rol.ADM:
            return [
                kpi("Productos activos", activos.count(), "bi-box-seam", catalogo_url),
                kpi("Stock bajo", stock_bajo, "bi-exclamation-triangle", catalogo_url, "warning"),
                kpi(
                    "Clientes activos",
                    Cliente.objects.filter(activo=True).count(),
                    "bi-people",
                    clientes_url,
                ),
                kpi(
                    "Ventas confirmadas",
                    Venta.objects.filter(activo=True, estado=EstadoVenta.CONFIRMADA).count(),
                    "bi-receipt",
                    ventas_url,
                    "info",
                ),
            ]

        if rol == Rol.VENDEDOR:
            mis_ventas = Venta.objects.filter(activo=True, vendedor=self.request.user)
            return [
                kpi("Mis ventas", mis_ventas.count(), "bi-receipt", ventas_url),
                kpi(
                    "Borradores",
                    mis_ventas.filter(estado=EstadoVenta.BORRADOR).count(),
                    "bi-file-earmark",
                    ventas_url,
                    "warning",
                ),
                kpi("Productos activos", activos.count(), "bi-box-seam", catalogo_url, "info"),
                kpi("Stock bajo", stock_bajo, "bi-exclamation-triangle", catalogo_url, "warning"),
            ]

        return [
            kpi("Productos disponibles", activos.count(), "bi-box-seam", catalogo_url),
            kpi(
                "Ítems en presupuesto",
                len(obtener(self.request)),
                "bi-file-earmark-ruled",
                presupuesto_url,
                "info",
            ),
            kpi(
                "Categorías",
                activos.values("categoria").distinct().count(),
                "bi-grid",
                catalogo_url,
                "warning",
            ),
        ]
