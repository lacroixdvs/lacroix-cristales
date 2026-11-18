from django.urls import path

from . import views

app_name = "ventas"

urlpatterns = [
    path("", views.VentaListView.as_view(), name="venta-list"),
    path("nueva/", views.VentaCreateView.as_view(), name="venta-create"),
    path("<int:pk>/", views.VentaDetailView.as_view(), name="venta-detail"),
    path("<int:pk>/editar/", views.VentaUpdateView.as_view(), name="venta-update"),
    path("<int:pk>/confirmar/", views.VentaConfirmarView.as_view(), name="venta-confirmar"),
    path("<int:pk>/cancelar/", views.VentaCancelarView.as_view(), name="venta-cancelar"),
    path("<int:pk>/baja/", views.VentaBajaView.as_view(), name="venta-baja"),
    path(
        "<int:pk>/detalles/agregar/",
        views.DetalleAgregarView.as_view(),
        name="detalle-agregar",
    ),
    path(
        "<int:pk>/detalles/<int:detalle_id>/quitar/",
        views.DetalleQuitarView.as_view(),
        name="detalle-quitar",
    ),
]
