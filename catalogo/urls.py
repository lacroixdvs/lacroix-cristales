from django.urls import path

from . import views

app_name = "catalogo"

urlpatterns = [
    path("presupuesto/", views.PresupuestoView.as_view(), name="presupuesto"),
    path("", views.ProductoListView.as_view(), name="producto-list"),
    path("nuevo/", views.ProductoCreateView.as_view(), name="producto-create"),
    path("<int:pk>/", views.ProductoDetailView.as_view(), name="producto-detail"),
    path("<int:pk>/editar/", views.ProductoUpdateView.as_view(), name="producto-update"),
    path("<int:pk>/baja/", views.ProductoBajaView.as_view(), name="producto-baja"),
    path(
        "<int:pk>/reactivar/",
        views.ProductoReactivarView.as_view(),
        name="producto-reactivar",
    ),
]
