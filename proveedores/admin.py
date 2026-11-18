from django.contrib import admin

from .models import Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("razon_social", "cuit", "rubro", "email", "activo")
    list_filter = ("activo", "rubro")
    search_fields = ("razon_social", "cuit", "email", "rubro")
