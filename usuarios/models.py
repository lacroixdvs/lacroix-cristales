from django.contrib.auth.models import AbstractUser
from django.db import models


class Rol(models.TextChoices):
    """Perfiles de acceso acordados para Vit Cristales."""

    ADM = "ADM", "Administrador"
    VENDEDOR = "VENDEDOR", "Vendedor"
    USUARIO = "USUARIO", "Usuario"


class Usuario(AbstractUser):
    """Usuario del sistema: login por username, email único y baja lógica.

    Los grupos de Django Auth son la fuente de verdad de permisos; `rol` se
    sincronizará desde esos grupos mediante signals en la Fase 4.
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

    def save(self, *args, **kwargs):
        """Mantiene `is_active` alineado con el campo `activo` del proyecto."""
        self.is_active = self.activo
        return super().save(*args, **kwargs)
