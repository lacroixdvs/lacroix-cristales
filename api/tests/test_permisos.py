"""Tests de la matriz de roles en la API (200/201 vs 403)."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.tests import (
    crear_cliente,
    crear_producto,
    crear_proveedor,
    crear_usuario,
    crear_venta,
)
from usuarios.models import Rol


class PermisosAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = crear_usuario("admin-permisos", Rol.ADM)
        cls.vendedor = crear_usuario("vendedor-permisos", Rol.VENDEDOR)
        cls.usuario = crear_usuario("usuario-permisos", Rol.USUARIO)
        cls.proveedor = crear_proveedor()
        cls.cliente = crear_cliente()
        cls.producto = crear_producto(proveedor=cls.proveedor)
        cls.producto_inactivo = crear_producto(
            proveedor=cls.proveedor, codigo="API-INACT", nombre="Inactivo", activo=False
        )
        cls.venta_propia = crear_venta(cliente=cls.cliente, vendedor=cls.vendedor)
        cls.otro_vendedor = crear_usuario("otro-vendedor-permisos", Rol.VENDEDOR)
        cls.venta_ajena = crear_venta(cliente=cls.cliente, vendedor=cls.otro_vendedor)

    def autenticar(self, usuario):
        self.client.force_authenticate(user=usuario)

    # --- ADM: acceso total ---

    def test_adm_accede_a_todos_los_listados(self):
        self.autenticar(self.admin)
        for nombre in (
            "usuario-list",
            "proveedor-list",
            "cliente-list",
            "producto-list",
            "venta-list",
        ):
            with self.subTest(ruta=nombre):
                respuesta = self.client.get(reverse(f"api:{nombre}"))
                self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_adm_puede_crear_en_todos_los_recursos(self):
        self.autenticar(self.admin)
        respuestas = [
            self.client.post(
                reverse("api:usuario-list"),
                {"username": "nuevo-admin-api", "email": "nuevo@ejemplo.com", "rol": Rol.USUARIO},
                format="json",
            ),
            self.client.post(
                reverse("api:proveedor-list"),
                {"razon_social": "Proveedor Nuevo", "cuit": "30-77777777-7"},
                format="json",
            ),
            self.client.post(
                reverse("api:cliente-list"),
                {"razon_social": "Cliente Nuevo", "cuit": "30-66666666-6"},
                format="json",
            ),
            self.client.post(
                reverse("api:producto-list"),
                {
                    "codigo": "API-NUEVO",
                    "nombre": "Producto Nuevo",
                    "categoria": "ESPEJO",
                    "precio_unitario": "100.00",
                    "stock": 5,
                    "proveedor": self.proveedor.pk,
                },
                format="json",
            ),
            self.client.post(
                reverse("api:venta-list"),
                {"cliente": self.cliente.pk, "vendedor": self.vendedor.pk},
                format="json",
            ),
        ]
        for respuesta in respuestas:
            self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED, respuesta.data)

    # --- VENDEDOR ---

    def test_vendedor_puede_leer_clientes_y_catalogo(self):
        self.autenticar(self.vendedor)
        self.assertEqual(
            self.client.get(reverse("api:cliente-list")).status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            self.client.get(reverse("api:producto-list")).status_code, status.HTTP_200_OK
        )

    def test_vendedor_no_puede_leer_proveedores_ni_usuarios(self):
        self.autenticar(self.vendedor)
        self.assertEqual(
            self.client.get(reverse("api:proveedor-list")).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.get(reverse("api:usuario-list")).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_vendedor_no_puede_escribir_clientes_ni_catalogo(self):
        self.autenticar(self.vendedor)
        self.assertEqual(
            self.client.post(
                reverse("api:cliente-list"),
                {"razon_social": "No debería", "cuit": "30-55555555-5"},
                format="json",
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.post(
                reverse("api:producto-list"),
                {
                    "codigo": "NO-01",
                    "nombre": "No debería",
                    "categoria": "VIDRIO",
                    "precio_unitario": "10.00",
                    "stock": 1,
                    "proveedor": self.proveedor.pk,
                },
                format="json",
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_vendedor_solo_ve_sus_propias_ventas(self):
        self.autenticar(self.vendedor)
        respuesta = self.client.get(reverse("api:venta-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(respuesta.data["results"][0]["id"], self.venta_propia.pk)

    def test_vendedor_no_puede_ver_venta_ajena(self):
        self.autenticar(self.vendedor)
        respuesta = self.client.get(
            reverse("api:venta-detail", args=[self.venta_ajena.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    def test_vendedor_crea_venta_y_se_le_asigna_como_vendedor(self):
        self.autenticar(self.vendedor)
        respuesta = self.client.post(
            reverse("api:venta-list"),
            {"cliente": self.cliente.pk, "vendedor": self.otro_vendedor.pk},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED, respuesta.data)
        from ventas.models import Venta

        venta = Venta.objects.get(pk=respuesta.data["id"])
        self.assertEqual(venta.vendedor_id, self.vendedor.pk)

    def test_vendedor_no_puede_dar_de_baja_ventas(self):
        self.autenticar(self.vendedor)
        respuesta = self.client.delete(
            reverse("api:venta-detail", args=[self.venta_propia.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    # --- USUARIO ---

    def test_usuario_solo_puede_leer_catalogo(self):
        self.autenticar(self.usuario)
        self.assertEqual(
            self.client.get(reverse("api:producto-list")).status_code, status.HTTP_200_OK
        )
        for nombre in ("cliente-list", "proveedor-list", "usuario-list", "venta-list"):
            with self.subTest(ruta=nombre):
                self.assertEqual(
                    self.client.get(reverse(f"api:{nombre}")).status_code,
                    status.HTTP_403_FORBIDDEN,
                )

    def test_usuario_solo_ve_productos_activos(self):
        self.autenticar(self.usuario)
        respuesta = self.client.get(reverse("api:producto-list"))
        codigos = [item["codigo"] for item in respuesta.data["results"]]
        self.assertIn("API-001", codigos)
        self.assertNotIn("API-INACT", codigos)

    def test_usuario_no_puede_escribir_en_catalogo(self):
        self.autenticar(self.usuario)
        respuesta = self.client.post(
            reverse("api:producto-list"),
            {
                "codigo": "NO-USUARIO",
                "nombre": "No",
                "categoria": "VIDRIO",
                "precio_unitario": "10.00",
                "stock": 1,
                "proveedor": self.proveedor.pk,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    # --- Anónimo ---

    def test_anonimo_no_accede_a_nada(self):
        self.client.force_authenticate(user=None)
        for nombre in (
            "usuario-list",
            "proveedor-list",
            "cliente-list",
            "producto-list",
            "venta-list",
        ):
            with self.subTest(ruta=nombre):
                self.assertEqual(
                    self.client.get(reverse(f"api:{nombre}")).status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )
