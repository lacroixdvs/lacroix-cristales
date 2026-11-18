from django.urls import path

from . import views

app_name = "clientes"

urlpatterns = [
    path("", views.ClienteListView.as_view(), name="cliente-list"),
    path("nuevo/", views.ClienteCreateView.as_view(), name="cliente-create"),
    path("<int:pk>/", views.ClienteDetailView.as_view(), name="cliente-detail"),
    path("<int:pk>/editar/", views.ClienteUpdateView.as_view(), name="cliente-update"),
    path("<int:pk>/baja/", views.ClienteBajaView.as_view(), name="cliente-baja"),
    path("<int:pk>/reactivar/", views.ClienteReactivarView.as_view(), name="cliente-reactivar"),
]
