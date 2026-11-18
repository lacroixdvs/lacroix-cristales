"""Tests de obtención y refresh de JWT."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.tests import CLAVE, crear_usuario
from usuarios.models import Rol


class JWTTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = crear_usuario("jwt-user", Rol.ADM)

    def test_obtener_token_con_credenciales_validas(self):
        respuesta = self.client.post(
            reverse("api:token_obtain_pair"),
            {"username": self.usuario.username, "password": CLAVE},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("access", respuesta.data)
        self.assertIn("refresh", respuesta.data)

    def test_token_no_se_entrega_con_password_invalido(self):
        respuesta = self.client.post(
            reverse("api:token_obtain_pair"),
            {"username": self.usuario.username, "password": "incorrecta"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", respuesta.data)

    def test_refresh_devuelve_nuevo_access(self):
        token = self.client.post(
            reverse("api:token_obtain_pair"),
            {"username": self.usuario.username, "password": CLAVE},
            format="json",
        ).data["refresh"]
        respuesta = self.client.post(
            reverse("api:token_refresh"), {"refresh": token}, format="json"
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("access", respuesta.data)

    def test_acceso_con_bearer_token(self):
        token = self.client.post(
            reverse("api:token_obtain_pair"),
            {"username": self.usuario.username, "password": CLAVE},
            format="json",
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        respuesta = self.client.get(reverse("api:usuario-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_sin_token_esta_prohibido(self):
        respuesta = self.client.get(reverse("api:proveedor-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)
