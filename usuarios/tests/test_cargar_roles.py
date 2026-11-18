from io import StringIO

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase

from usuarios.models import Rol, Usuario


class CargarRolesTests(TestCase):
    def test_es_idempotente(self):
        salida = StringIO()
        call_command("cargar_roles", stdout=salida)
        call_command("cargar_roles", stdout=salida)

        self.assertEqual(
            Group.objects.filter(name__in=[Rol.ADM, Rol.VENDEDOR, Rol.USUARIO]).count(), 3
        )

    def test_crea_admin_solo_si_no_existe_y_no_muestra_password(self):
        salida = StringIO()
        call_command(
            "cargar_roles",
            crear_admin=True,
            admin_username="root",
            admin_email="root@vitcristales.local",
            admin_password="SecretoDePrueba123!",
            stdout=salida,
        )
        self.assertTrue(Usuario.objects.filter(username="root", rol=Rol.ADM).exists())
        self.assertNotIn("SecretoDePrueba123!", salida.getvalue())

        call_command(
            "cargar_roles",
            crear_admin=True,
            admin_username="root",
            admin_email="root@vitcristales.local",
            admin_password="OtroSecreto123!",
            stdout=salida,
        )
        self.assertEqual(Usuario.objects.filter(username="root").count(), 1)
