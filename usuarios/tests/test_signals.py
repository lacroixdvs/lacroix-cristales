from django.contrib.auth.models import Group
from django.test import TestCase

from usuarios.models import Rol

from . import crear_usuario


class SincronizacionRolesTests(TestCase):
    def test_agregar_grupo_actualiza_rol(self):
        usuario = crear_usuario("vendedor", Rol.USUARIO)
        grupo, _ = Group.objects.get_or_create(name=Rol.VENDEDOR)
        usuario.groups.add(grupo)
        usuario.refresh_from_db()
        self.assertEqual(usuario.rol, Rol.VENDEDOR)

    def test_quitar_grupo_vuelve_a_usuario(self):
        usuario = crear_usuario("administrador", Rol.ADM)
        grupo, _ = Group.objects.get_or_create(name=Rol.ADM)
        usuario.groups.add(grupo)
        usuario.groups.remove(grupo)
        usuario.refresh_from_db()
        self.assertEqual(usuario.rol, Rol.USUARIO)

    def test_cambiar_rol_actualiza_grupos(self):
        usuario = crear_usuario("cambia", Rol.USUARIO)
        usuario.rol = Rol.VENDEDOR
        usuario.save()
        self.assertEqual(list(usuario.groups.values_list("name", flat=True)), [Rol.VENDEDOR])

    def test_adm_tiene_prioridad_sobre_vendedor(self):
        usuario = crear_usuario("multi", Rol.USUARIO)
        usuario.groups.add(Group.objects.get_or_create(name=Rol.VENDEDOR)[0])
        usuario.groups.add(Group.objects.get_or_create(name=Rol.ADM)[0])
        usuario.refresh_from_db()
        self.assertEqual(usuario.rol, Rol.ADM)

    def test_activo_define_is_active(self):
        usuario = crear_usuario("baja", Rol.USUARIO)
        usuario.activo = False
        usuario.save()
        usuario.refresh_from_db()
        self.assertFalse(usuario.is_active)
