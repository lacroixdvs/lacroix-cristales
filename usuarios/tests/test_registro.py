from django.test import TestCase
from django.urls import reverse

from usuarios.models import Rol, Usuario


class RegistroPublicoTests(TestCase):
    def datos_validos(self, email="ana@ejemplo.com"):
        return {
            "username": "nuevo",
            "first_name": "Ana",
            "last_name": "Pérez",
            "email": email,
            "contacto": "555-1234",
            "password1": "ClaveSegura123!",
            "password2": "ClaveSegura123!",
        }

    def test_registro_asigna_grupo_y_rol_usuario(self):
        respuesta = self.client.post(reverse("usuarios:registro"), self.datos_validos())
        self.assertEqual(respuesta.status_code, 302)

        usuario = Usuario.objects.get(username="nuevo")
        self.assertEqual(usuario.rol, Rol.USUARIO)
        self.assertTrue(usuario.groups.filter(name=Rol.USUARIO).exists())
        self.assertTrue(usuario.check_password("ClaveSegura123!"))

    def test_registro_rechaza_email_duplicado(self):
        Usuario.objects.create_user(
            username="viejo", email="igual@ejemplo.com", password="clave-de-prueba-123"
        )
        respuesta = self.client.post(
            reverse("usuarios:registro"), self.datos_validos(email="igual@ejemplo.com")
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Usuario.objects.filter(username="nuevo").exists())
