from django.urls import reverse
from django.test import TestCase

from usuarios.models import Rol

from . import crear_proveedor, crear_usuario


class PermisosProveedoresTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = crear_usuario("admin-proveedores", Rol.ADM)
        cls.vendedor = crear_usuario("vendedor-proveedores", Rol.VENDEDOR)
        cls.usuario = crear_usuario("usuario-proveedores", Rol.USUARIO)
        cls.proveedor = crear_proveedor()

    def setUp(self):
        self.client.login(username=self.admin.username, password="clave-de-prueba-123")

    def _url(self, nombre, *args):
        return reverse(f"proveedores:{nombre}", args=args)

    def test_admin_accede_a_todas_las_vistas(self):
        urls = [
            self._url("proveedor-list"),
            self._url("proveedor-detail", self.proveedor.pk),
            self._url("proveedor-create"),
            self._url("proveedor-update", self.proveedor.pk),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_vendedor_no_puede_listar(self):
        self.client.login(username=self.vendedor.username, password="clave-de-prueba-123")
        self.assertEqual(self.client.get(self._url("proveedor-list")).status_code, 403)

    def test_usuario_no_puede_listar(self):
        self.client.login(username=self.usuario.username, password="clave-de-prueba-123")
        self.assertEqual(self.client.get(self._url("proveedor-list")).status_code, 403)

    def test_vendedor_no_puede_crear_editar_ni_dar_de_baja(self):
        self.client.login(username=self.vendedor.username, password="clave-de-prueba-123")
        urls = [
            self._url("proveedor-create"),
            self._url("proveedor-update", self.proveedor.pk),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(
            self.client.post(self._url("proveedor-baja", self.proveedor.pk)).status_code,
            403,
        )
        self.proveedor.refresh_from_db()
        self.assertTrue(self.proveedor.activo)

    def test_anonimo_es_redirigido_al_login(self):
        self.client.logout()
        respuesta = self.client.get(self._url("proveedor-list"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/accounts/login/", respuesta.url)
