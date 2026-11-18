from django.core.validators import RegexValidator
from django.db import models

from core.validators import CUIT_FORMATO, MENSAJE_CUIT, normalizar_cuit


class Proveedor(models.Model):
    """Proveedor de artículos de Vit Cristales con baja lógica."""

    razon_social = models.CharField("razón social", max_length=150)
    cuit = models.CharField(
        "CUIT",
        max_length=13,
        unique=True,
        validators=[RegexValidator(regex=CUIT_FORMATO, message=MENSAJE_CUIT)],
        help_text="Formato XX-XXXXXXXX-X (también se aceptan 11 dígitos).",
    )
    contacto = models.CharField("contacto (teléfono/WhatsApp)", max_length=30, blank=True)
    email = models.EmailField("email", blank=True)
    direccion = models.CharField("dirección", max_length=255, blank=True)
    rubro = models.CharField("rubro", max_length=100, blank=True)
    activo = models.BooleanField("activo", default=True)

    class Meta:
        verbose_name = "proveedor"
        verbose_name_plural = "proveedores"
        ordering = ["razon_social"]

    def __str__(self):
        return f"{self.razon_social} ({self.cuit})"

    def clean(self):
        super().clean()
        if self.cuit:
            self.cuit = normalizar_cuit(self.cuit)
