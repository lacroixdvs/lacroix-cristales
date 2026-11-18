from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class EstadoVenta(models.TextChoices):
    BORRADOR = "BORRADOR", "Borrador"
    CONFIRMADA = "CONFIRMADA", "Confirmada"
    CANCELADA = "CANCELADA", "Cancelada"


class Venta(models.Model):
    cliente = models.ForeignKey(
        "clientes.Cliente", on_delete=models.PROTECT, related_name="ventas"
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ventas"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=EstadoVenta.choices, default=EstadoVenta.BORRADOR)
    observaciones = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    descuento_mayorista = models.DecimalField(
        "descuento mayorista (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ],
    )
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "venta"
        verbose_name_plural = "ventas"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"Venta #{self.pk} — {self.cliente.razon_social} — {self.estado}"

    @property
    def detalles_activos(self):
        return self.detalles.filter(activo=True)


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(
        "catalogo.Producto", on_delete=models.PROTECT, related_name="detalles_venta"
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="La cantidad debe ser al menos 1.")]
    )
    precio_unitario = models.DecimalField(
        "precio unitario (snapshot)", max_digits=12, decimal_places=2
    )
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "detalle de venta"
        verbose_name_plural = "detalles de venta"
        ordering = ["id"]

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} @ ${self.precio_unitario}"

    def save(self, *args, **kwargs):
        precio = Decimal(self.precio_unitario)
        self.precio_unitario = precio
        self.subtotal = (precio * self.cantidad).quantize(Decimal("0.01"))
        return super().save(*args, **kwargs)
