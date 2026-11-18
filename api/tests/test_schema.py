"""Tests de generación del esquema OpenAPI y del Swagger UI."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.tests import crear_usuario
from usuarios.models import Rol


class SchemaSwaggerTests(APITestCase):
    def test_schema_se_genera_sin_errores(self):
        respuesta = self.client.get(reverse("api:schema"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        contenido = respuesta.content.decode()
        self.assertIn("openapi", contenido)
        self.assertIn("Vit Cristales API", contenido)
        self.assertIn("/api/catalogo/", contenido)
        self.assertIn("/api/ventas/", contenido)
        self.assertIn("/api/token/", contenido)

    def test_schema_incluye_los_5_recursos_y_los_tags_jwt(self):
        respuesta = self.client.get(reverse("api:schema"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        contenido = respuesta.content.decode()
        for ruta in (
            "/api/usuarios/",
            "/api/proveedores/",
            "/api/clientes/",
            "/api/catalogo/",
            "/api/ventas/",
            "/api/token/",
            "/api/token/refresh/",
        ):
            with self.subTest(ruta=ruta):
                self.assertIn(ruta, contenido)

    def test_swagger_ui_esta_disponible(self):
        respuesta = self.client.get(reverse("api:swagger"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertContains(respuesta, "swagger-ui")

    def test_schema_es_publico_pero_swagger_tambien(self):
        # Spectacular sirve el esquema sin exigir autenticación para que el UI funcione.
        self.assertEqual(
            self.client.get(reverse("api:schema")).status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            self.client.get(reverse("api:swagger")).status_code, status.HTTP_200_OK
        )

    def test_link_de_swagger_visible_solo_para_adm_en_navbar(self):
        admin = crear_usuario("admin-nav", Rol.ADM)
        self.client.force_login(admin)
        respuesta = self.client.get(reverse("core:home"))
        self.assertContains(respuesta, reverse("api:swagger"))

        usuario = crear_usuario("usuario-nav", Rol.USUARIO)
        self.client.force_login(usuario)
        respuesta = self.client.get(reverse("core:home"))
        self.assertNotContains(respuesta, reverse("api:swagger"))
