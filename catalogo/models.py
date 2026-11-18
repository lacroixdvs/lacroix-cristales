from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.TextChoices):
    VIDRIO = "VIDRIO", "Vidrio"
    MAMPARA = "MAMPARA", "Mampara"
    ESPEJO = "ESPEJO", "Espejo"
    CERRAMIENTO = "CERRAMIENTO", "Cerramiento de oficina"


class Producto(models.Model):
    """Artículo del catálogo de Vit Cristales con control de stock."""

    codigo = models.CharField("código", max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    descripcion = models.TextField(blank=True)
    espesor = models.CharField(max_length=50, blank=True, help_text='Ej.: "8mm", "4+4 laminado".')
    precio_unitario = models.DecimalField(
        "precio unitario",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), message="El precio debe ser mayor a 0.")],
    )
    stock = models.PositiveIntegerField(default=0)
    proveedor = models.ForeignKey(
        "proveedores.Proveedor",
        on_delete=models.PROTECT,
        related_name="productos",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"

    @property
    def categoria_etiqueta(self):
        return self.get_categoria_display()
