"""URLs raíz de Vit Cristales.

Las URLs de las apps de dominio, autenticación y API se incluyen en fases posteriores.
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
