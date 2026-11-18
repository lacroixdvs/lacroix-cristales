"""URLs raíz de Vit Cristales.

Las URLs de las apps de dominio, autenticación y API se incluyen en fases posteriores.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("", include("usuarios.urls")),
    path("clientes/", include("clientes.urls")),
    path("proveedores/", include("proveedores.urls")),
    path("catalogo/", include("catalogo.urls")),
    path("presupuesto/", RedirectView.as_view(pattern_name="catalogo:presupuesto", permanent=False)),
    path("ventas/", include("ventas.urls")),
    path("api/", include("api.urls")),
]
