from decimal import Decimal

from django.urls import reverse
from django.test import TestCase

from catalogo.presupuesto import CLAVE_SESION


def items_de(session):
    return dict(session.get(CLAVE_SESION, {}))

from . import crear_producto, crear_usuario
from usuarios.models import Rol


class PresupuestoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = crear_usuario("usuario-presupuesto", Rol.USUARIO)
        cls.proveedor = crear_producto().proveedor
        cls.producto = crear_producto(
            cls.proveedor, codigo="PRE-001", nombre="Vidrio", precio_unitario="15000.00", stock=3
        )
        cls.otro = crear_producto(
            cls.proveedor, codigo="PRE-002", nombre="Espejo", precio_unitario="25000.00", stock=5
        )

    def setUp(self):
        self.client.login(username=self.usuario.username, password="clave-de-prueba-123")
        self.url = reverse("catalogo:presupuesto")

    def test_agregar_y_calcular_totales_sin_tocar_stock(self):
        self.client.post(
            self.url,
            {"accion": "agregar", "producto_id": self.producto.pk, "cantidad": "2"},
        )
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.context["subtotal"], Decimal("30000.00"))
        self.assertEqual(respuesta.context["total"], Decimal("30000.00"))
        self.assertEqual(respuesta.context["cantidad_total"], 2)
        self.assertEqual(items_de(self.client.session), {str(self.producto.pk): 2})
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)

    def test_agregar_repite_suma_cantidades(self):
        for _ in range(2):
            self.client.post(
                self.url,
                {"accion": "agregar", "producto_id": self.producto.pk, "cantidad": "1"},
            )
        self.assertEqual(items_de(self.client.session), {str(self.producto.pk): 2})

    def test_modificar_quitar_y_vaciar(self):
        self.client.post(
            self.url,
            {"accion": "agregar", "producto_id": self.producto.pk, "cantidad": "1"},
        )
        self.client.post(
            self.url,
            {"accion": "cambiar", "producto_id": self.producto.pk, "cantidad": "4"},
        )
        self.assertEqual(items_de(self.client.session), {str(self.producto.pk): 4})

        self.client.post(self.url, {"accion": "quitar", "producto_id": self.producto.pk})
        self.assertEqual(items_de(self.client.session), {})

        self.client.post(
            self.url,
            {"accion": "agregar", "producto_id": self.otro.pk, "cantidad": "1"},
        )
        self.client.post(self.url, {"accion": "vaciar"})
        self.assertNotIn(CLAVE_SESION, self.client.session)

    def test_no_se_pueden_agregar_productos_inactivos(self):
        self.producto.activo = False
        self.producto.save(update_fields=["activo"])
        respuesta = self.client.post(
            self.url,
            {"accion": "agregar", "producto_id": self.producto.pk, "cantidad": "1"},
            follow=True,
        )
        self.assertContains(respuesta, "no está activo")
        self.assertEqual(items_de(self.client.session), {})

    def test_cantidad_invalida_se_rechaza(self):
        respuesta = self.client.post(
            self.url,
            {"accion": "agregar", "producto_id": self.producto.pk, "cantidad": "0"},
            follow=True,
        )
        self.assertContains(respuesta, "al menos 1")
        self.assertEqual(items_de(self.client.session), {})

    def test_varios_productos_suman_al_total(self):
        self.client.post(
            self.url,
            {"accion": "agregar", "producto_id": self.producto.pk, "cantidad": "1"},
        )
        self.client.post(
            self.url,
            {"accion": "agregar", "producto_id": self.otro.pk, "cantidad": "2"},
        )
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.context["total"], Decimal("65000.00"))
        self.assertEqual(respuesta.context["cantidad_total"], 3)
