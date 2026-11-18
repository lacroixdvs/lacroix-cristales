"""URLs de la API REST: routers, JWT y esquema OpenAPI."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .viewsets import (
    ClienteViewSet,
    ProductoViewSet,
    ProveedorViewSet,
    UsuarioViewSet,
    VentaViewSet,
)

app_name = "api"

router = DefaultRouter()
router.register("usuarios", UsuarioViewSet, basename="usuario")
router.register("proveedores", ProveedorViewSet, basename="proveedor")
router.register("clientes", ClienteViewSet, basename="cliente")
router.register("catalogo", ProductoViewSet, basename="producto")
router.register("ventas", VentaViewSet, basename="venta")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="api:schema"),
        name="swagger",
    ),
    path("", include(router.urls)),
]
