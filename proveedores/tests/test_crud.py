from django.urls import reverse
from django.test import TestCase

from proveedores.models import Proveedor
from usuarios.models import Rol

from . import DATOS_FORMULARIO, crear_proveedor, crear_usuario


class CrudProveedoresTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = crear_usuario("admin-crud-proveedores", Rol.ADM)
        cls.activo = crear_proveedor(razon_social="Activo SA", cuit="30-11111111-1")
        cls.inactivo = crear_proveedor(
            razon_social="Inactivo SA", cuit="30-22222222-2", activo=False
        )

    def setUp(self):
        self.client.login(username=self.admin.username, password="clave-de-prueba-123")

    def test_listado_muestra_activos_por_defecto(self):
        respuesta = self.client.get(reverse("proveedores:proveedor-list"))
        self.assertContains(respuesta, "Activo SA")
        self.assertNotContains(respuesta, "Inactivo SA")

    def test_filtro_de_inactivos_y_todos(self):
        url = reverse("proveedores:proveedor-list")
        self.assertContains(self.client.get(url, {"activo": "0"}), "Inactivo SA")
        respuesta = self.client.get(url, {"activo": "todos"})
        self.assertContains(respuesta, "Activo SA")
        self.assertContains(respuesta, "Inactivo SA")

    def test_live_search_por_rubro(self):
        crear_proveedor(razon_social="Otro", cuit="30-99999999-9", rubro="Accesorios")
        respuesta = self.client.get(
            reverse("proveedores:proveedor-list"),
            {"q": "accesorios"},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        self.assertContains(respuesta, "Otro")
        self.assertNotContains(respuesta, "Activo SA")

    def test_paginacion_de_20(self):
        for i in range(25):
            crear_proveedor(razon_social=f"Proveedor {i:02d}", cuit=f"30-55{i:06d}-5")
        respuesta = self.client.get(reverse("proveedores:proveedor-list"))
        self.assertEqual(len(respuesta.context["proveedores"]), 20)
        self.assertTrue(respuesta.context["is_paginated"])

    def test_alta_edicion_baja_y_reactivacion(self):
        respuesta = self.client.post(
            reverse("proveedores:proveedor-create"), DATOS_FORMULARIO, follow=True
        )
        self.assertRedirects(respuesta, reverse("proveedores:proveedor-list"))
        self.assertContains(respuesta, "Proveedor creado correctamente.")
        creado = Proveedor.objects.get(cuit="30-44444444-4")

        self.client.post(
            reverse("proveedores:proveedor-update", args=[creado.pk]),
            {**DATOS_FORMULARIO, "razon_social": "Editado SA"},
        )
        creado.refresh_from_db()
        self.assertEqual(creado.razon_social, "Editado SA")

        self.client.post(reverse("proveedores:proveedor-baja", args=[creado.pk]))
        creado.refresh_from_db()
        self.assertFalse(creado.activo)

        self.client.post(reverse("proveedores:proveedor-reactivar", args=[creado.pk]))
        creado.refresh_from_db()
        self.assertTrue(creado.activo)
        self.assertTrue(Proveedor.objects.filter(pk=creado.pk).exists())
