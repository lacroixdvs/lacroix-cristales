from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Rol, Usuario

from .roles import rol_de


class CoreSmokeTests(TestCase):
    """Pruebas de humo de la home y del dashboard por rol."""

    def crear_usuario(self, username, email, rol):
        """Crea un usuario de prueba con el rol indicado."""
        return Usuario.objects.create_user(
            username=username,
            email=email,
            password="clave-de-prueba-123",
            rol=rol,
        )

    def test_home_disponible(self):
        respuesta = self.client.get(reverse("core:home"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Vit Cristales")

    def test_dashboard_requiere_login(self):
        respuesta = self.client.get(reverse("core:dashboard"))
        self.assertEqual(respuesta.status_code, 302)

    def test_dashboard_muestra_modulos_segun_rol(self):
        casos = [
            (Rol.ADM, "Usuarios"),
            (Rol.VENDEDOR, "Ventas"),
            (Rol.USUARIO, "Presupuesto"),
        ]
        for rol, modulo in casos:
            with self.subTest(rol=rol):
                usuario = self.crear_usuario(
                    f"user-{rol.lower()}", f"{rol.lower()}@ejemplo.com", rol
                )
                self.client.force_login(usuario)
                respuesta = self.client.get(reverse("core:dashboard"))
                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, modulo)

    def test_grupo_define_el_rol_efectivo(self):
        usuario = self.crear_usuario("vendedor", "vendedor@ejemplo.com", Rol.USUARIO)
        usuario.groups.add(Group.objects.create(name=Rol.VENDEDOR))
        self.assertEqual(rol_de(usuario), Rol.VENDEDOR)
