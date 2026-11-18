from django.urls import path

from . import views

app_name = "proveedores"

urlpatterns = [
    path("", views.ProveedorListView.as_view(), name="proveedor-list"),
    path("nuevo/", views.ProveedorCreateView.as_view(), name="proveedor-create"),
    path("<int:pk>/", views.ProveedorDetailView.as_view(), name="proveedor-detail"),
    path("<int:pk>/editar/", views.ProveedorUpdateView.as_view(), name="proveedor-update"),
    path("<int:pk>/baja/", views.ProveedorBajaView.as_view(), name="proveedor-baja"),
    path(
        "<int:pk>/reactivar/",
        views.ProveedorReactivarView.as_view(),
        name="proveedor-reactivar",
    ),
]
