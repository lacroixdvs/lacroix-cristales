from django.contrib.auth.models import AbstractUser
from django.db import models


class Rol(models.TextChoices):
    """Perfiles de acceso acordados para Vit Cristales."""

    ADM = "ADM", "Administrador"
    VENDEDOR = "VENDEDOR", "Vendedor"
    USUARIO = "USUARIO", "Usuario"


class Usuario(AbstractUser):
    """Usuario del sistema: login por username, email único y baja lógica.

    Los grupos de Django Auth y `rol` se mantienen sincronizados mediante
    signals. `activo` es el estado canónico de baja lógica y `is_active` lo
    refleja para Django.
    """

    email = models.EmailField("email", unique=True)
    contacto = models.CharField("contacto (teléfono/WhatsApp)", max_length=30, blank=True)
    rol = models.CharField("rol", max_length=20, choices=Rol.choices, default=Rol.USUARIO)
    activo = models.BooleanField("activo", default=True)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        """Muestra el nombre completo y, si falta, el username."""
        return self.get_full_name() or self.username
