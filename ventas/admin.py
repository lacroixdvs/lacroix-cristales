from django.contrib import admin

from .models import DetalleVenta, Venta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ("subtotal",)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "vendedor", "fecha", "estado", "total", "activo")
    list_filter = ("estado", "activo")
    search_fields = ("cliente__razon_social", "cliente__cuit", "vendedor__username")
    inlines = (DetalleVentaInline,)


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ("venta", "producto", "cantidad", "precio_unitario", "subtotal", "activo")
    list_filter = ("activo",)
