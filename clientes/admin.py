from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("razon_social", "cuit", "email", "descuento_mayorista", "activo")
    list_filter = ("activo",)
    search_fields = ("razon_social", "cuit", "email")
