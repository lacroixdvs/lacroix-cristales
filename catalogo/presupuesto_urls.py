"""Ruta pública del presupuesto en sesión, definida en `design.md`."""

from django.urls import path

from . import views

app_name = "catalogo"

urlpatterns = [
    path("presupuesto/", views.PresupuestoView.as_view(), name="presupuesto"),
]
