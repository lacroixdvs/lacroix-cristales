from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from .validators import CUIT_FORMATO, MENSAJE_CUIT, normalizar_cuit


class Cliente(models.Model):
    """Cliente mayorista de Vit Cristales con baja lógica."""

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
    descuento_mayorista = models.DecimalField(
        "descuento mayorista (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0"), message="El descuento no puede ser negativo."),
            MaxValueValidator(Decimal("100"), message="El descuento no puede superar 100."),
        ],
        help_text="Porcentaje entre 0 y 100.",
    )
    activo = models.BooleanField("activo", default=True)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["razon_social"]

    def __str__(self):
        return f"{self.razon_social} ({self.cuit})"

    def clean(self):
        """Normaliza el CUIT también desde el admin, no solo desde nuestro form."""
        super().clean()
        if self.cuit:
            self.cuit = normalizar_cuit(self.cuit)
