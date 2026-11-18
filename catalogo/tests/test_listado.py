from django.urls import reverse
from django.test import TestCase

from catalogo.models import Categoria
from usuarios.models import Rol

from . import crear_producto, crear_usuario


class ListadoCatalogoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = crear_usuario("admin-listado-catalogo", Rol.ADM)
        cls.vendedor = crear_usuario("vendedor-listado-catalogo", Rol.VENDEDOR)
        cls.usuario = crear_usuario("usuario-listado-catalogo", Rol.USUARIO)
        cls.activo = crear_producto(codigo="LIS-001", nombre="Vidrio activo")
        cls.inactivo = crear_producto(
            codigo="LIS-002", nombre="Vidrio inactivo", activo=False
        )
        cls.espejo = crear_producto(
            codigo="LIS-003", nombre="Espejo redondo", categoria=Categoria.ESPEJO
        )

    def test_activos_por_defecto(self):
        self.client.login(username=self.admin.username, password="clave-de-prueba-123")
        respuesta = self.client.get(reverse("catalogo:producto-list"))
        self.assertContains(respuesta, "Vidrio activo")
        self.assertNotContains(respuesta, "Vidrio inactivo")

    def test_filtro_de_estado_solo_para_admin(self):
        url = reverse("catalogo:producto-list")

        self.client.login(username=self.admin.username, password="clave-de-prueba-123")
        self.assertContains(self.client.get(url, {"activo": "0"}), "Vidrio inactivo")

        self.client.login(username=self.vendedor.username, password="clave-de-prueba-123")
        respuesta = self.client.get(url, {"activo": "0"})
        self.assertContains(respuesta, "Vidrio activo")
        self.assertNotContains(respuesta, "Vidrio inactivo")

    def test_live_search_por_codigo_nombre_y_categoria(self):
        url = reverse("catalogo:producto-list")
        headers = {"X-Requested-With": "XMLHttpRequest"}
        self.client.login(username=self.usuario.username, password="clave-de-prueba-123")

        for texto, esperado, no_esperado in [
            ("LIS-003", "Espejo redondo", "Vidrio activo"),
            ("Vidrio activo", "Vidrio activo", "Espejo redondo"),
            ("Espejo", "Espejo redondo", "Vidrio activo"),
        ]:
            with self.subTest(texto=texto):
                respuesta = self.client.get(url, {"q": texto}, headers=headers)
                self.assertContains(respuesta, esperado)
                self.assertNotContains(respuesta, no_esperado)

    def test_paginacion_de_20(self):
        for i in range(25):
            crear_producto(codigo=f"PAG-{i:03d}", nombre=f"Producto {i:02d}")
        self.client.login(username=self.usuario.username, password="clave-de-prueba-123")
        respuesta = self.client.get(reverse("catalogo:producto-list"))
        self.assertEqual(len(respuesta.context["productos"]), 20)
        self.assertTrue(respuesta.context["is_paginated"])
