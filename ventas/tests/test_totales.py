from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from ventas import services
from ventas.models import EstadoVenta

from . import crear_cliente, crear_producto, crear_usuario, crear_venta


class TotalesVentaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vendedor = crear_usuario("vendedor-totales", "VENDEDOR")
        cls.cliente = crear_cliente(descuento_mayorista="10.00")
        cls.producto = crear_producto(precio_unitario="10000.00", stock=20)
        cls.venta = crear_venta(cliente=cls.cliente, vendedor=cls.vendedor)

    def test_subtotal_y_total_con_descuento_mayorista(self):
        detalle = services.agregar_detalle(self.venta, self.producto, 3)
        self.assertEqual(detalle.subtotal, Decimal("30000.00"))
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.subtotal, Decimal("30000.00"))
        self.assertEqual(self.venta.descuento_mayorista, Decimal("10.00"))
        self.assertEqual(self.venta.total, Decimal("27000.00"))
        resumen = services.resumen(self.venta)
        self.assertEqual(resumen["descuento_importe"], Decimal("3000.00"))
        self.assertEqual(resumen["total"], Decimal("27000.00"))

    def test_snapshot_de_precio_historico(self):
        detalle = services.agregar_detalle(self.venta, self.producto, 2)
        self.assertEqual(detalle.precio_unitario, Decimal("10000.00"))

        self.producto.precio_unitario = Decimal("15000.00")
        self.producto.save(update_fields=["precio_unitario"])
        detalle.refresh_from_db()
        self.assertEqual(detalle.precio_unitario, Decimal("10000.00"))
        self.assertEqual(detalle.subtotal, Decimal("20000.00"))
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.total, Decimal("18000.00"))

    def test_recálculo_al_agregar_y_quitar_detalles(self):
        primero = services.agregar_detalle(self.venta, self.producto, 1)
        segundo = services.agregar_detalle(self.venta, self.producto, 2)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.total, Decimal("27000.00"))

        services.quitar_detalle(primero)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.subtotal, Decimal("20000.00"))
        self.assertEqual(self.venta.total, Decimal("18000.00"))
        segundo.refresh_from_db()
        self.assertTrue(segundo.activo)

    def test_no_se_pueden_agregar_items_a_una_venta_confirmada(self):
        services.agregar_detalle(self.venta, self.producto, 1)
        self.venta.estado = EstadoVenta.CONFIRMADA
        self.venta.save(update_fields=["estado"])
        with self.assertRaises(ValidationError):
            services.agregar_detalle(self.venta, self.producto, 1)

    def test_cantidad_debe_ser_al_menos_uno(self):
        with self.assertRaises(ValidationError):
            services.agregar_detalle(self.venta, self.producto, 0)
