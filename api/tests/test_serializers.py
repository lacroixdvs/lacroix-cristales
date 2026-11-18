"""Tests del patrón obligatorio de serializers Base / Get / Post."""

from catalogo.serializers import (
    ProductoBaseSerializer,
    ProductoGetSerializer,
    ProductoPostSerializer,
)
from clientes.serializers import (
    ClienteBaseSerializer,
    ClienteGetSerializer,
    ClientePostSerializer,
)
from proveedores.serializers import (
    ProveedorBaseSerializer,
    ProveedorGetSerializer,
    ProveedorPostSerializer,
)
from usuarios.serializers import (
    UsuarioBaseSerializer,
    UsuarioGetSerializer,
    UsuarioPostSerializer,
)
from ventas.serializers import (
    DetalleVentaBaseSerializer,
    DetalleVentaGetSerializer,
    DetalleVentaPostSerializer,
    VentaBaseSerializer,
    VentaGetSerializer,
    VentaPostSerializer,
)

from django.test import TestCase

from api.tests import crear_cliente, crear_producto, crear_proveedor, crear_usuario, crear_venta
from usuarios.models import Rol
from ventas import services


class PatronSerializersTests(TestCase):
    def test_las_tres_capas_son_subclases_en_cada_app(self):
        pares = [
            (UsuarioBaseSerializer, UsuarioGetSerializer, UsuarioPostSerializer),
            (ProveedorBaseSerializer, ProveedorGetSerializer, ProveedorPostSerializer),
            (ClienteBaseSerializer, ClienteGetSerializer, ClientePostSerializer),
            (ProductoBaseSerializer, ProductoGetSerializer, ProductoPostSerializer),
            (VentaBaseSerializer, VentaGetSerializer, VentaPostSerializer),
            (DetalleVentaBaseSerializer, DetalleVentaGetSerializer, DetalleVentaPostSerializer),
        ]
        for base, get, post in pares:
            with self.subTest(base=base.__name__):
                self.assertTrue(issubclass(get, base))
                self.assertTrue(issubclass(post, base))

    def test_get_expone_relaciones_legibles(self):
        self.assertIn("grupos", UsuarioGetSerializer().fields)
        self.assertIn("rol_etiqueta", UsuarioGetSerializer().fields)
        self.assertIn("productos_activos", ProveedorGetSerializer().fields)
        self.assertIn("ventas_totales", ClienteGetSerializer().fields)
        self.assertIn("categoria_etiqueta", ProductoGetSerializer().fields)
        from proveedores.serializers import ProveedorBaseSerializer

        self.assertIsInstance(
            ProductoGetSerializer().fields["proveedor"], ProveedorBaseSerializer
        )
        self.assertIn("detalles", VentaGetSerializer().fields)
        self.assertIn("resumen", VentaGetSerializer().fields)
        self.assertIn("producto", DetalleVentaGetSerializer().fields)

    def test_post_valida_reglas_de_negocio(self):
        self.assertFalse(ClientePostSerializer(data={"razon_social": "X"}).is_valid())
        self.assertFalse(ProductoPostSerializer(data={"codigo": "X"}).is_valid())
        self.assertFalse(ProveedorPostSerializer(data={"razon_social": "X"}).is_valid())
        self.assertFalse(VentaPostSerializer(data={}).is_valid())
        self.assertFalse(DetalleVentaPostSerializer(data={"cantidad": 0}).is_valid())


class SerializacionDatosRealesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.proveedor = crear_proveedor()
        cls.cliente = crear_cliente(descuento_mayorista="10.00")
        cls.producto = crear_producto(proveedor=cls.proveedor, precio_unitario="1000.00")
        cls.vendedor = crear_usuario("vendedor-serial", Rol.VENDEDOR)
        cls.venta = crear_venta(cliente=cls.cliente, vendedor=cls.vendedor)

    def test_get_cliente_incluye_conteo_de_ventas(self):
        datos = ClienteGetSerializer(self.cliente).data
        self.assertEqual(datos["ventas_totales"], 1)
        self.assertEqual(datos["cuit"], "30-12345678-9")

    def test_get_producto_incluye_proveedor_anidado_y_etiqueta(self):
        datos = ProductoGetSerializer(self.producto).data
        self.assertEqual(datos["categoria_etiqueta"], "Vidrio")
        self.assertEqual(datos["proveedor"]["razon_social"], self.proveedor.razon_social)

    def test_post_cliente_normaliza_cuit_y_valida_descuento(self):
        serializer = ClientePostSerializer(
            data={
                "razon_social": "Nuevo Cliente",
                "cuit": "34123456789",
                "descuento_mayorista": "15.00",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["cuit"], "34-12345678-9")

        invalido = ClientePostSerializer(
            data={"razon_social": "Mal", "cuit": "30-12345678-9", "descuento_mayorista": "150"}
        )
        self.assertFalse(invalido.is_valid())

    def test_post_producto_valida_precio_y_proveedor(self):
        serializer = ProductoPostSerializer(
            data={
                "codigo": "NUEVO-01",
                "nombre": "Espejo",
                "categoria": "ESPEJO",
                "precio_unitario": "500.00",
                "stock": 2,
                "proveedor": self.proveedor.pk,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        sin_precio = ProductoPostSerializer(
            data={
                "codigo": "MAL-01",
                "nombre": "Espejo",
                "categoria": "ESPEJO",
                "precio_unitario": "0",
                "stock": 2,
                "proveedor": self.proveedor.pk,
            }
        )
        self.assertFalse(sin_precio.is_valid())

    def test_post_detalle_delega_en_servicio_y_guarda_snapshot(self):
        serializer = DetalleVentaPostSerializer(
            data={"venta": self.venta.pk, "producto": self.producto.pk, "cantidad": 2}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        detalle = serializer.save()
        self.assertEqual(str(detalle.precio_unitario), "1000.00")
        self.assertEqual(str(detalle.subtotal), "2000.00")
        self.venta.refresh_from_db()
        self.assertEqual(str(self.venta.subtotal), "2000.00")
        self.assertEqual(str(self.venta.total), "1800.00")  # 10% de descuento

    def test_get_venta_incluye_detalles_y_resumen(self):
        services.agregar_detalle(self.venta, self.producto, 1)
        datos = VentaGetSerializer(self.venta).data
        self.assertEqual(len(datos["detalles"]), 1)
        self.assertEqual(datos["resumen"]["total"], self.venta.total)
