from django.urls import reverse
from django.test import TestCase

from ventas import services
from ventas.models import EstadoVenta

from . import crear_cliente, crear_producto, crear_usuario, crear_venta


class PermisosVentasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = crear_usuario("admin-ventas", "ADM")
        cls.vendedor = crear_usuario("vendedor-ventas", "VENDEDOR")
        cls.otro_vendedor = crear_usuario("otro-vendedor-ventas", "VENDEDOR")
        cls.usuario = crear_usuario("usuario-ventas", "USUARIO")
        cls.cliente = crear_cliente()
        cls.producto = crear_producto(stock=10)
        cls.venta = crear_venta(cliente=cls.cliente, vendedor=cls.vendedor)
        services.agregar_detalle(cls.venta, cls.producto, 1)

    def _url(self, nombre, *args):
        return reverse(f"ventas:{nombre}", args=args)

    def test_admin_accede_a_todo(self):
        self.client.login(username=self.admin.username, password="clave-de-prueba-123")
        for url in [
            self._url("venta-list"),
            self._url("venta-detail", self.venta.pk),
            self._url("venta-create"),
            self._url("venta-update", self.venta.pk),
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_vendedor_puede_crear_borrador_y_cargar_items(self):
        self.client.login(username=self.vendedor.username, password="clave-de-prueba-123")
        respuesta = self.client.post(
            self._url("venta-create"),
            {
                "cliente": self.cliente.pk,
                "vendedor": self.vendedor.pk,
                "observaciones": "Pedido de prueba",
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        venta = self.venta.__class__.objects.get(observaciones="Pedido de prueba")
        self.assertEqual(venta.estado, EstadoVenta.BORRADOR)
        self.assertEqual(venta.vendedor_id, self.vendedor.pk)

        respuesta = self.client.post(
            self._url("detalle-agregar", venta.pk),
            {"producto_id": self.producto.pk, "cantidad": "2"},
            follow=True,
        )
        self.assertContains(respuesta, "Ítem agregado")
        self.assertEqual(venta.detalles.filter(activo=True).count(), 1)

    def test_vendedor_puede_confirmar_y_consultar(self):
        self.client.login(username=self.vendedor.username, password="clave-de-prueba-123")
        respuesta = self.client.post(self._url("venta-confirmar", self.venta.pk), follow=True)
        self.assertContains(respuesta, "Venta confirmada")
        self.venta.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(self.venta.estado, EstadoVenta.CONFIRMADA)
        self.assertEqual(self.producto.stock, 9)
        self.assertEqual(self.client.get(self._url("venta-detail", self.venta.pk)).status_code, 200)

    def test_vendedor_no_puede_dar_de_baja_venta_confirmada(self):
        services.confirmar_venta(self.venta)
        self.client.login(username=self.vendedor.username, password="clave-de-prueba-123")
        respuesta = self.client.post(self._url("venta-baja", self.venta.pk))
        self.assertEqual(respuesta.status_code, 403)
        self.venta.refresh_from_db()
        self.assertTrue(self.venta.activo)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 9)

    def test_vendedor_no_puede_tocar_la_venta_de_otro_vendedor(self):
        self.client.login(
            username=self.otro_vendedor.username, password="clave-de-prueba-123"
        )
        self.assertEqual(self.client.get(self._url("venta-detail", self.venta.pk)).status_code, 404)
        self.assertEqual(self.client.get(self._url("venta-update", self.venta.pk)).status_code, 404)
        self.assertEqual(
            self.client.post(
                self._url("detalle-agregar", self.venta.pk),
                {"producto_id": self.producto.pk, "cantidad": "1"},
            ).status_code,
            302,
        )
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.detalles.filter(activo=True).count(), 1)

    def test_vendedor_no_puede_editar_una_venta_confirmada(self):
        services.confirmar_venta(self.venta)
        self.client.login(username=self.vendedor.username, password="clave-de-prueba-123")
        self.assertEqual(self.client.get(self._url("venta-update", self.venta.pk)).status_code, 404)

    def test_usuario_no_puede_ingresar_a_ventas(self):
        self.client.login(username=self.usuario.username, password="clave-de-prueba-123")
        for url in [self._url("venta-list"), self._url("venta-detail", self.venta.pk)]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_anonimo_es_redirigido_al_login(self):
        respuesta = self.client.get(self._url("venta-list"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/accounts/login/", respuesta.url)

    def test_admin_puede_dar_de_baja_una_venta_confirmada(self):
        services.confirmar_venta(self.venta)
        self.client.login(username=self.admin.username, password="clave-de-prueba-123")
        respuesta = self.client.post(self._url("venta-baja", self.venta.pk), follow=True)
        self.assertRedirects(respuesta, self._url("venta-list"))
        self.venta.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertFalse(self.venta.activo)
        self.assertEqual(self.producto.stock, 10)
