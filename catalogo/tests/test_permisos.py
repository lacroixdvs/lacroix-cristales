from django.urls import reverse
from django.test import TestCase

from usuarios.models import Rol

from . import crear_producto, crear_usuario


class PermisosCatalogoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = crear_usuario("admin-catalogo", Rol.ADM)
        cls.vendedor = crear_usuario("vendedor-catalogo", Rol.VENDEDOR)
        cls.usuario = crear_usuario("usuario-catalogo", Rol.USUARIO)
        cls.producto = crear_producto(codigo="PERM-001")

    def _url(self, nombre, *args):
        return reverse(f"catalogo:{nombre}", args=args)

    def test_admin_tiene_crud_completo(self):
        self.client.login(username=self.admin.username, password="clave-de-prueba-123")
        for url in [
            self._url("producto-list"),
            self._url("producto-detail", self.producto.pk),
            self._url("producto-create"),
            self._url("producto-update", self.producto.pk),
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_vendedor_y_usuario_solo_leen(self):
        for usuario in (self.vendedor, self.usuario):
            with self.subTest(usuario=usuario.username):
                self.client.login(username=usuario.username, password="clave-de-prueba-123")
                self.assertEqual(self.client.get(self._url("producto-list")).status_code, 200)
                self.assertEqual(self.client.get(self._url("producto-detail", self.producto.pk)).status_code, 200)
                self.assertEqual(self.client.get(self._url("producto-create")).status_code, 403)
                self.assertEqual(self.client.get(self._url("producto-update", self.producto.pk)).status_code, 403)
                self.assertEqual(
                    self.client.post(self._url("producto-baja", self.producto.pk)).status_code,
                    403,
                )
        self.producto.refresh_from_db()
        self.assertTrue(self.producto.activo)

    def test_anonimo_no_puede_ver_catalogo(self):
        respuesta = self.client.get(self._url("producto-list"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/accounts/login/", respuesta.url)

    def test_presupuesto_requiere_login(self):
        respuesta = self.client.get(self._url("presupuesto"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/accounts/login/", respuesta.url)

    def test_todos_los_roles_autenticados_pueden_armar_presupuesto(self):
        for usuario in (self.admin, self.vendedor, self.usuario):
            with self.subTest(usuario=usuario.username):
                self.client.login(username=usuario.username, password="clave-de-prueba-123")
                self.assertEqual(self.client.get(self._url("presupuesto")).status_code, 200)
