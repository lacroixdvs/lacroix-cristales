"""Reglas de negocio de ventas: totales, stock y cambios de estado.

Todas las operaciones que tocan stock se ejecutan dentro de `transaction.atomic`
y bloquean los productos con `select_for_update()`.
"""

from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction

from catalogo.models import Producto

from .models import DetalleVenta, EstadoVenta, Venta

CENTAVOS = Decimal("0.01")
CERO = Decimal("0.00")


def redondear(valor):
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def calcular_subtotal(cantidad, precio_unitario):
    return redondear(Decimal(precio_unitario) * Decimal(cantidad))


def recalcular_totales(venta):
    """Suma detalles activos, aplica el descuento mayorista y persiste el resumen."""
    subtotal = sum(
        (detalle.subtotal for detalle in venta.detalles.filter(activo=True)), CERO
    )
    descuento = Decimal(venta.cliente.descuento_mayorista or CERO)
    descuento_importe = redondear(subtotal * descuento / Decimal("100"))
    venta.subtotal = redondear(subtotal)
    venta.descuento_mayorista = descuento
    venta.total = redondear(subtotal - descuento_importe)
    venta.save(update_fields=["subtotal", "descuento_mayorista", "total"])
    return venta


def resumen(venta):
    """Detalle legible del cálculo, con el descuento explicito."""
    descuento_importe = redondear(
        Decimal(venta.subtotal) * Decimal(venta.descuento_mayorista) / Decimal("100")
    )
    return {
        "subtotal": venta.subtotal,
        "descuento_porcentaje": venta.descuento_mayorista,
        "descuento_importe": descuento_importe,
        "total": venta.total,
    }


def agregar_detalle(venta, producto, cantidad):
    """Agrega un ítem a un borrador guardando el precio histórico del producto."""
    if venta.estado != EstadoVenta.BORRADOR:
        raise ValidationError("Solo se pueden agregar ítems a una venta en borrador.")
    if not venta.activo:
        raise ValidationError("La venta no está activa.")
    if not producto.activo:
        raise ValidationError("El producto no está activo.")
    if cantidad < 1:
        raise ValidationError("La cantidad debe ser al menos 1.")

    detalle = DetalleVenta.objects.create(
        venta=venta,
        producto=producto,
        cantidad=cantidad,
        precio_unitario=producto.precio_unitario,
        subtotal=calcular_subtotal(cantidad, producto.precio_unitario),
    )
    recalcular_totales(venta)
    return detalle


def quitar_detalle(detalle):
    """Baja lógica del ítem y recálculo de totales; solo en borradores."""
    venta = detalle.venta
    if venta.estado != EstadoVenta.BORRADOR:
        raise ValidationError("Solo se pueden quitar ítems de una venta en borrador.")
    detalle.activo = False
    detalle.save(update_fields=["activo", "subtotal"])
    recalcular_totales(venta)
    return detalle


@transaction.atomic
def confirmar_venta(venta):
    """Confirma un borrador validando todo antes de descontar un solo stock."""
    venta = Venta.objects.select_for_update().select_related("cliente").get(pk=venta.pk)
    if venta.estado != EstadoVenta.BORRADOR:
        raise ValidationError("La venta no está en borrador.")

    detalles = list(
        venta.detalles.filter(activo=True).select_related("producto")
    )
    if not detalles:
        raise ValidationError("La venta no tiene ítems activos.")

    ids = {detalle.producto_id for detalle in detalles}
    productos = {
        producto.pk: producto
        for producto in Producto.objects.select_for_update().filter(pk__in=ids)
    }

    # Fase de validación: no se escribe nada hasta que todo esté verificado.
    for detalle in detalles:
        producto = productos.get(detalle.producto_id)
        if producto is None or not producto.activo:
            raise ValidationError("Uno de los productos no está activo.")
        if producto.stock < detalle.cantidad:
            raise ValidationError(
                f"Stock insuficiente para {producto.nombre}: "
                f"hay {producto.stock} y se requieren {detalle.cantidad}."
            )

    for detalle in detalles:
        producto = productos[detalle.producto_id]
        producto.stock -= detalle.cantidad
        producto.save(update_fields=["stock"])

    venta.estado = EstadoVenta.CONFIRMADA
    venta.save(update_fields=["estado"])
    recalcular_totales(venta)
    return venta


@transaction.atomic
def cancelar_venta(venta):
    """Cancela la venta y reintegra el stock de sus detalles activos."""
    venta = Venta.objects.select_for_update().get(pk=venta.pk)
    if venta.estado == EstadoVenta.CANCELADA:
        return venta

    if venta.estado == EstadoVenta.CONFIRMADA:
        detalles = list(venta.detalles.filter(activo=True).select_related("producto"))
        ids = {detalle.producto_id for detalle in detalles}
        productos = {
            producto.pk: producto
            for producto in Producto.objects.select_for_update().filter(pk__in=ids)
        }
        for detalle in detalles:
            producto = productos.get(detalle.producto_id)
            if producto is None:
                continue
            producto.stock += detalle.cantidad
            producto.save(update_fields=["stock"])

    venta.estado = EstadoVenta.CANCELADA
    venta.save(update_fields=["estado"])
    return venta


@transaction.atomic
def dar_de_baja(venta):
    """Baja lógica de una venta confirmada: reintegra stock y la marca inactiva."""
    venta = cancelar_venta(venta)
    venta.activo = False
    venta.save(update_fields=["activo"])
    return venta
