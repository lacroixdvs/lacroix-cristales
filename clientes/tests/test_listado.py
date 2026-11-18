from django.test import TestCase
from django.urls import reverse

from usuarios.models import Rol

from . import crear_cliente, crear_usuario


class ListadoClientesTests(TestCase):
    def setUp(self):
        self.activo = crear_cliente(razon_social="Vidrios Acme", cuit="30-11111111-1")
        self.inactivo = crear_cliente(
            razon_social="Espejos Luna",
            cuit="30-22222222-2",
            email="luna@ejemplo.com",
            activo=False,
        )

    def test_oculta_bajas_por_defecto_tambien_para_adm(self):
        self.client.force_login(crear_usuario("admin", Rol.ADM))
        respuesta = self.client.get(reverse("clientes:cliente-list"))
        self.assertContains(respuesta, "Vidrios Acme")
        self.assertNotContains(respuesta, "Espejos Luna")

    def test_adm_puede_listar_inactivos(self):
        self.client.force_login(crear_usuario("admin", Rol.ADM))
        respuesta = self.client.get(reverse("clientes:cliente-list"), {"activo": "0"})
        self.assertContains(respuesta, "Espejos Luna")
        self.assertNotContains(respuesta, "Vidrios Acme")

    def test_adm_puede_listar_todos(self):
        self.client.force_login(crear_usuario("admin", Rol.ADM))
        respuesta = self.client.get(reverse("clientes:cliente-list"), {"activo": "todos"})
        self.assertContains(respuesta, "Vidrios Acme")
        self.assertContains(respuesta, "Espejos Luna")

    def test_vendedor_ignora_el_filtro_de_inactivos(self):
        self.client.force_login(crear_usuario("vendedor", Rol.VENDEDOR))
        respuesta = self.client.get(reverse("clientes:cliente-list"), {"activo": "0"})
        self.assertContains(respuesta, "Vidrios Acme")
        self.assertNotContains(respuesta, "Espejos Luna")

    def test_live_search_por_razon_cuit_y_email(self):
        self.client.force_login(crear_usuario("admin", Rol.ADM))
        for termino in ("Acme", "22222222", "luna@"):
            with self.subTest(termino=termino):
                respuesta = self.client.get(
                    reverse("clientes:cliente-list"),
                    {"q": termino, "activo": "todos"},
                    headers={"X-Requested-With": "XMLHttpRequest"},
                )
                self.assertEqual(respuesta.status_code, 200)
                self.assertTemplateUsed("clientes/partials/cliente_resultados.html")

    def test_paginacion(self):
        for numero in range(25):
            crear_cliente(
                razon_social=f"Cliente {numero:02d}",
                cuit=f"30-{numero:08d}-9",
                email=f"cliente{numero}@ejemplo.com",
            )
        self.client.force_login(crear_usuario("admin", Rol.ADM))
        respuesta = self.client.get(reverse("clientes:cliente-list"))
        self.assertTrue(respuesta.context["is_paginated"])
        self.assertEqual(len(respuesta.context["page_obj"]), 20)
