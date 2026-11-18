from django.core.exceptions import ValidationError
from django.test import TestCase

from ventas import services
from ventas.models import EstadoVenta

from . import crear_cliente, crear_producto, crear_usuario, crear_venta


class StockVentaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vendedor = crear_usuario("vendedor-stock", "VENDEDOR")
        cls.cliente = crear_cliente()
        cls.producto = crear_producto(
            codigo="ST-001", nombre="Vidrio", precio_unitario="10000.00", stock=10
        )

    def setUp(self):
        self.venta = crear_venta(cliente=self.cliente, vendedor=self.vendedor)
        self.producto.refresh_from_db()

    def test_confirmar_descuenta_stock_y_cambia_estado(self):
        services.agregar_detalle(self.venta, self.producto, 4)
        services.confirmar_venta(self.venta)
        self.producto.refresh_from_db()
        self.venta.refresh_from_db()
        self.assertEqual(self.producto.stock, 6)
        self.assertEqual(self.venta.estado, EstadoVenta.CONFIRMADA)

    def test_confirmar_sin_items_se_rechaza(self):
        with self.assertRaisesMessage(ValidationError, "no tiene ítems activos"):
            services.confirmar_venta(self.venta)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)

    def test_stock_insuficiente_rechaza_toda_la_operacion(self):
        otro = crear_producto(
            self.producto.proveedor,
            codigo="ST-002",
            nombre="Espejo",
            precio_unitario="5000.00",
            stock=1,
        )
        services.agregar_detalle(self.venta, self.producto, 2)
        services.agregar_detalle(self.venta, otro, 5)

        with self.assertRaisesMessage(ValidationError, "Stock insuficiente"):
            services.confirmar_venta(self.venta)

        self.producto.refresh_from_db()
        otro.refresh_from_db()
        self.venta.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(otro.stock, 1)
        self.assertEqual(self.venta.estado, EstadoVenta.BORRADOR)

    def test_producto_inactivo_rechaza_la_confirmacion(self):
        services.agregar_detalle(self.venta, self.producto, 1)
        self.producto.activo = False
        self.producto.save(update_fields=["activo"])

        with self.assertRaisesMessage(ValidationError, "no está activo"):
            services.confirmar_venta(self.venta)

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado, EstadoVenta.BORRADOR)

    def test_cancelar_venta_confirmada_reintegra_stock(self):
        services.agregar_detalle(self.venta, self.producto, 4)
        services.confirmar_venta(self.venta)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 6)

        services.cancelar_venta(self.venta)
        self.producto.refresh_from_db()
        self.venta.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(self.venta.estado, EstadoVenta.CANCELADA)

    def test_baja_de_venta_confirmada_reintegra_stock(self):
        services.agregar_detalle(self.venta, self.producto, 3)
        services.confirmar_venta(self.venta)

        services.dar_de_baja(self.venta)
        self.producto.refresh_from_db()
        self.venta.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)
        self.assertFalse(self.venta.activo)
        self.assertEqual(self.venta.estado, EstadoVenta.CANCELADA)

    def test_cancelar_venta_ya_cancelada_no_duplica_stock(self):
        services.agregar_detalle(self.venta, self.producto, 3)
        services.confirmar_venta(self.venta)
        services.cancelar_venta(self.venta)
        services.cancelar_venta(self.venta)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)

    def test_confirmar_dos_veces_no_descuenta_stock_otra_vez(self):
        services.agregar_detalle(self.venta, self.producto, 2)
        services.confirmar_venta(self.venta)
        with self.assertRaises(ValidationError):
            services.confirmar_venta(self.venta)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 8)
