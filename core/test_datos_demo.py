"""Tests del comando de datos de demostración (Fase 9)."""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from catalogo.models import Producto
from clientes.models import Cliente
from core.roles import rol_de
from proveedores.models import Proveedor
from usuarios.models import Rol, Usuario
from ventas.models import DetalleVenta, EstadoVenta, Venta


class CargarDatosDemoTests(TestCase):
    def cargar(self):
        call_command("cargar_datos_demo", stdout=StringIO())

    def test_carga_inicial_y_idempotencia(self):
        self.cargar()
        cantidades = (
            Usuario.objects.count(),
            Proveedor.objects.count(),
            Cliente.objects.count(),
            Producto.objects.count(),
            Venta.objects.count(),
            DetalleVenta.objects.count(),
        )
        self.assertEqual(cantidades, (3, 3, 4, 8, 2, 5))
        stock = dict(Producto.objects.values_list("codigo", "stock"))
        totales = list(Venta.objects.values_list("estado", "total"))

        self.cargar()
        self.assertEqual(
            (
                Usuario.objects.count(),
                Proveedor.objects.count(),
                Cliente.objects.count(),
                Producto.objects.count(),
                Venta.objects.count(),
                DetalleVenta.objects.count(),
            ),
            cantidades,
        )
        self.assertEqual(dict(Producto.objects.values_list("codigo", "stock")), stock)
        self.assertEqual(list(Venta.objects.values_list("estado", "total")), totales)

    def test_usuarios_tienen_un_rol_y_venta_confirmada_descuenta_stock(self):
        self.cargar()
        for username, rol in (
            ("demo_admin", Rol.ADM),
            ("demo_vendedor", Rol.VENDEDOR),
            ("demo_usuario", Rol.USUARIO),
        ):
            with self.subTest(username=username):
                usuario = Usuario.objects.get(username=username)
                self.assertEqual(rol_de(usuario), rol)

        confirmada = Venta.objects.get(observaciones__contains="confirmada")
        self.assertEqual(confirmada.estado, EstadoVenta.CONFIRMADA)
        self.assertEqual(confirmada.detalles.count(), 3)
        self.assertGreater(confirmada.total, 0)
        self.assertLess(confirmada.total, confirmada.subtotal)

        producto = Producto.objects.get(codigo="VID-001")
        self.assertEqual(producto.stock, 116)  # 120 iniciales - 4 vendidos

    def test_borrador_no_toca_stock(self):
        self.cargar()
        borrador = Venta.objects.get(observaciones__contains="Borrador")
        self.assertEqual(borrador.estado, EstadoVenta.BORRADOR)
        self.assertLess(borrador.total, borrador.subtotal)  # cliente con 10% de descuento
        self.assertEqual(Producto.objects.get(codigo="ESP-001").stock, 60)
