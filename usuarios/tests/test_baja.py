from django.test import TestCase
from django.urls import reverse

from usuarios.models import Rol, Usuario

from . import crear_usuario


class BajaLogicaUsuarioTests(TestCase):
    def test_baja_no_borra_y_desactiva(self):
        self.client.force_login(crear_usuario("admin", Rol.ADM))
        objetivo = crear_usuario("objetivo", Rol.VENDEDOR)

        respuesta = self.client.post(reverse("usuarios:usuario-baja", args=[objetivo.pk]))
        self.assertEqual(respuesta.status_code, 302)

        objetivo.refresh_from_db()
        self.assertFalse(objetivo.activo)
        self.assertFalse(objetivo.is_active)
        self.assertTrue(Usuario.objects.filter(pk=objetivo.pk).exists())

    def test_admin_no_puede_darse_de_baja_a_si_mismo(self):
        admin = crear_usuario("admin", Rol.ADM)
        self.client.force_login(admin)

        self.client.post(reverse("usuarios:usuario-baja", args=[admin.pk]))
        admin.refresh_from_db()
        self.assertTrue(admin.activo)
