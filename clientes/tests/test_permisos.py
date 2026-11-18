from django.test import TestCase
from django.urls import reverse

from usuarios.models import Rol

from . import crear_cliente, crear_usuario


class PermisosClientesTests(TestCase):
    def setUp(self):
        self.cliente = crear_cliente()

    def test_vendedor_puede_listar(self):
        self.client.force_login(crear_usuario("vendedor", Rol.VENDEDOR))
        respuesta = self.client.get(reverse("clientes:cliente-list"))
        self.assertEqual(respuesta.status_code, 200)

    def test_vendedor_no_puede_detalle(self):
        self.client.force_login(crear_usuario("vendedor", Rol.VENDEDOR))
        respuesta = self.client.get(reverse("clientes:cliente-detail", args=[self.cliente.pk]))
        self.assertEqual(respuesta.status_code, 403)

    def test_vendedor_no_puede_crear(self):
        self.client.force_login(crear_usuario("vendedor", Rol.VENDEDOR))
        respuesta = self.client.get(reverse("clientes:cliente-create"))
        self.assertEqual(respuesta.status_code, 403)

    def test_vendedor_no_puede_editar(self):
        self.client.force_login(crear_usuario("vendedor", Rol.VENDEDOR))
        respuesta = self.client.post(
            reverse("clientes:cliente-update", args=[self.cliente.pk]),
            {"razon_social": "Modificado"},
        )
        self.assertEqual(respuesta.status_code, 403)

    def test_vendedor_no_puede_dar_de_baja(self):
        self.client.force_login(crear_usuario("vendedor", Rol.VENDEDOR))
        respuesta = self.client.post(reverse("clientes:cliente-baja", args=[self.cliente.pk]))
        self.assertEqual(respuesta.status_code, 403)
        self.cliente.refresh_from_db()
        self.assertTrue(self.cliente.activo)

    def test_vendedor_no_puede_reactivar(self):
        inactivo = crear_cliente(
            razon_social="Baja", cuit="30-33333333-3", email="baja@ejemplo.com", activo=False
        )
        self.client.force_login(crear_usuario("vendedor", Rol.VENDEDOR))
        respuesta = self.client.post(reverse("clientes:cliente-reactivar", args=[inactivo.pk]))
        self.assertEqual(respuesta.status_code, 403)
        inactivo.refresh_from_db()
        self.assertFalse(inactivo.activo)

    def test_usuario_no_puede_listar(self):
        self.client.force_login(crear_usuario("usuario", Rol.USUARIO))
        respuesta = self.client.get(reverse("clientes:cliente-list"))
        self.assertEqual(respuesta.status_code, 403)

    def test_usuario_no_puede_crear(self):
        self.client.force_login(crear_usuario("usuario", Rol.USUARIO))
        respuesta = self.client.get(reverse("clientes:cliente-create"))
        self.assertEqual(respuesta.status_code, 403)

    def test_anonimo_es_redirigido_al_login(self):
        respuesta = self.client.get(reverse("clientes:cliente-list"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/accounts/login/", respuesta["Location"])
