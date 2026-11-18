"""Tests de filtros con django-filter sobre los ViewSets."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.tests import crear_cliente, crear_producto, crear_proveedor, crear_usuario, crear_venta
from catalogo.models import Categoria
from usuarios.models import Rol
from ventas.models import EstadoVenta


class FiltrosAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = crear_usuario("admin-filtros", Rol.ADM)
        cls.proveedor_a = crear_proveedor(razon_social="Proveedor Alpha", rubro="Vidrios")
        cls.proveedor_b = crear_proveedor(
            razon_social="Proveedor Beta", cuit="30-88888888-8", rubro="Espejos"
        )
        cls.producto_vidrio = crear_producto(
            proveedor=cls.proveedor_a,
            codigo="FIL-001",
            nombre="Vidrio filtrable",
            categoria=Categoria.VIDRIO,
        )
        cls.producto_espejo = crear_producto(
            proveedor=cls.proveedor_b,
            codigo="FIL-002",
            nombre="Espejo filtrable",
            categoria=Categoria.ESPEJO,
        )
        cls.producto_inactivo = crear_producto(
            proveedor=cls.proveedor_a,
            codigo="FIL-003",
            nombre="Producto baja",
            categoria=Categoria.VIDRIO,
            activo=False,
        )
        cls.cliente_activo = crear_cliente(razon_social="Cliente Activo", cuit="30-11111111-1")
        cls.cliente_inactivo = crear_cliente(
            razon_social="Cliente Inactivo", cuit="30-22222222-2", activo=False
        )
        cls.vendedor = crear_usuario("vendedor-filtros", Rol.VENDEDOR)
        cls.venta_borrador = crear_venta(
            cliente=cls.cliente_activo, vendedor=cls.vendedor, estado=EstadoVenta.BORRADOR
        )
        cls.venta_confirmada = crear_venta(
            cliente=cls.cliente_activo,
            vendedor=cls.vendedor,
            estado=EstadoVenta.CONFIRMADA,
        )

    def setUp(self):
        self.client.force_authenticate(user=self.admin)

    def test_filtro_por_categoria_en_catalogo(self):
        respuesta = self.client.get(reverse("api:producto-list"), {"categoria": "VIDRIO"})
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        codigos = [item["codigo"] for item in respuesta.data["results"]]
        self.assertIn("FIL-001", codigos)
        self.assertIn("FIL-003", codigos)
        self.assertNotIn("FIL-002", codigos)

    def test_filtro_por_proveedor_en_catalogo(self):
        respuesta = self.client.get(
            reverse("api:producto-list"), {"proveedor": self.proveedor_b.pk}
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(respuesta.data["results"][0]["codigo"], "FIL-002")

    def test_filtro_booleano_activo_en_catalogo(self):
        respuesta = self.client.get(reverse("api:producto-list"), {"activo": "false"})
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(respuesta.data["results"][0]["codigo"], "FIL-003")

    def test_filtro_por_rubro_en_proveedores(self):
        respuesta = self.client.get(reverse("api:proveedor-list"), {"rubro": "Espejos"})
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(respuesta.data["results"][0]["razon_social"], "Proveedor Beta")

    def test_filtro_por_estado_en_ventas(self):
        respuesta = self.client.get(
            reverse("api:venta-list"), {"estado": EstadoVenta.CONFIRMADA}
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(respuesta.data["results"][0]["id"], self.venta_confirmada.pk)

    def test_filtro_por_activo_en_clientes(self):
        respuesta = self.client.get(reverse("api:cliente-list"), {"activo": "false"})
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(respuesta.data["results"][0]["razon_social"], "Cliente Inactivo")

    def test_busqueda_por_texto_en_catalogo(self):
        respuesta = self.client.get(reverse("api:producto-list"), {"search": "espejo"})
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        codigos = [item["codigo"] for item in respuesta.data["results"]]
        self.assertIn("FIL-002", codigos)

    def test_orden_por_nombre_en_catalogo(self):
        respuesta = self.client.get(
            reverse("api:producto-list"), {"ordering": "nombre"}
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        nombres = [item["nombre"] for item in respuesta.data["results"]]
        self.assertEqual(nombres, sorted(nombres))
