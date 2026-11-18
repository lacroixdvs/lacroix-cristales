from django.test import TestCase
from django.urls import reverse

from usuarios.models import Rol

from . import crear_usuario


class AccesoCrudUsuariosTests(TestCase):
    def test_admin_puede_listar(self):
        self.client.force_login(crear_usuario("admin", Rol.ADM))
        respuesta = self.client.get(reverse("usuarios:usuario-list"))
        self.assertEqual(respuesta.status_code, 200)

    def test_vendedor_no_puede_listar(self):
        self.client.force_login(crear_usuario("vendedor", Rol.VENDEDOR))
        respuesta = self.client.get(reverse("usuarios:usuario-list"))
        self.assertEqual(respuesta.status_code, 403)

    def test_usuario_no_puede_crear(self):
        self.client.force_login(crear_usuario("usuario", Rol.USUARIO))
        respuesta = self.client.get(reverse("usuarios:usuario-create"))
        self.assertEqual(respuesta.status_code, 403)

    def test_anonimo_es_redirigido_al_login(self):
        respuesta = self.client.get(reverse("usuarios:usuario-list"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/accounts/login/", respuesta["Location"])
