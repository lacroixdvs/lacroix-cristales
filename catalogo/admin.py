from django.contrib import admin

from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "categoria", "precio_unitario", "stock", "activo")
    list_filter = ("categoria", "activo", "proveedor")
    search_fields = ("codigo", "nombre", "descripcion")
