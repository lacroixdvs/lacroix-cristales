from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Registro del usuario custom en el admin de Django."""

    fieldsets = UserAdmin.fieldsets + (
        ("Datos de Vit Cristales", {"fields": ("contacto", "rol", "activo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Datos de Vit Cristales", {"fields": ("email", "contacto", "rol")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "rol", "activo", "is_staff")
    list_filter = ("rol", "activo", "is_staff", "is_superuser")
