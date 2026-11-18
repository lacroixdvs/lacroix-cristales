"""Tests de las acciones de ventas que delegan en `ventas.services`."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.tests import crear_cliente, crear_producto, crear_usuario, crear_venta
from usuarios.models import Rol
from ventas.models import EstadoVenta


class AccionesVentaAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = crear_usuario("admin-acciones", Rol.ADM)
        cls.vendedor = crear_usuario("vendedor-acciones", Rol.VENDEDOR)
        cls.otro_vendedor = crear_usuario("otro-vendedor-acciones", Rol.VENDEDOR)
        cls.cliente = crear_cliente(descuento_mayorista="10.00")
        cls.producto = crear_producto(proveedor=None, stock=5, precio_unitario="1000.00")
        cls.venta = crear_venta(cliente=cls.cliente, vendedor=cls.vendedor)

    def setUp(self):
        self.client.force_authenticate(user=self.vendedor)

    def test_agregar_item_usa_servicio_y_actualiza_totales(self):
        respuesta = self.client.post(
            reverse("api:venta-agregar-item", args=[self.venta.pk]),
            {"producto": self.producto.pk, "cantidad": 2},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED, respuesta.data)
        self.assertEqual(str(respuesta.data["precio_unitario"]), "1000.00")
        self.venta.refresh_from_db()
        self.assertEqual(str(self.venta.subtotal), "2000.00")
        self.assertEqual(str(self.venta.total), "1800.00")

    def test_agregar_item_rechaza_cantidad_invalida(self):
        respuesta = self.client.post(
            reverse("api:venta-agregar-item", args=[self.venta.pk]),
            {"producto": self.producto.pk, "cantidad": 0},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_quitar_item_usa_servicio_y_recalcula(self):
        self.client.post(
            reverse("api:venta-agregar-item", args=[self.venta.pk]),
            {"producto": self.producto.pk, "cantidad": 2},
            format="json",
        )
        detalle_id = self.venta.detalles.first().pk
        respuesta = self.client.delete(
            reverse(
                "api:venta-quitar-item",
                args=[self.venta.pk, detalle_id],
            )
        )
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.venta.refresh_from_db()
        self.assertEqual(str(self.venta.total), "0.00")
        self.assertFalse(self.venta.detalles.first().activo)

    def test_confirmar_descuenta_stock_via_servicio(self):
        self.client.post(
            reverse("api:venta-agregar-item", args=[self.venta.pk]),
            {"producto": self.producto.pk, "cantidad": 3},
            format="json",
        )
        respuesta = self.client.post(
            reverse("api:venta-confirmar", args=[self.venta.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK, respuesta.data)
        self.venta.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(self.venta.estado, EstadoVenta.CONFIRMADA)
        self.assertEqual(self.producto.stock, 2)

    def test_cancelar_reintegra_stock_via_servicio(self):
        self.client.post(
            reverse("api:venta-agregar-item", args=[self.venta.pk]),
            {"producto": self.producto.pk, "cantidad": 3},
            format="json",
        )
        self.client.post(reverse("api:venta-confirmar", args=[self.venta.pk]))
        # Igual que en MVT: cancelar una confirmada es potestad de ADM.
        self.client.force_authenticate(user=self.admin)
        respuesta = self.client.post(
            reverse("api:venta-cancelar", args=[self.venta.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK, respuesta.data)
        self.venta.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(self.venta.estado, EstadoVenta.CANCELADA)
        self.assertEqual(self.producto.stock, 5)

    def test_vendedor_no_puede_operar_sobre_venta_ajena(self):
        ajena = crear_venta(cliente=self.cliente, vendedor=self.otro_vendedor)
        respuesta = self.client.post(reverse("api:venta-confirmar", args=[ajena.pk]))
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    def test_vendedor_no_puede_confirmar_venta_ya_confirmada(self):
        self.client.post(
            reverse("api:venta-agregar-item", args=[self.venta.pk]),
            {"producto": self.producto.pk, "cantidad": 1},
            format="json",
        )
        self.client.post(reverse("api:venta-confirmar", args=[self.venta.pk]))
        respuesta = self.client.post(reverse("api:venta-confirmar", args=[self.venta.pk]))
        # El permiso pasa (es suya) pero el servicio rechaza el estado con 400.
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_adm_puede_confirmar_cualquier_venta(self):
        ajena = crear_venta(cliente=self.cliente, vendedor=self.otro_vendedor)
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            reverse("api:venta-agregar-item", args=[ajena.pk]),
            {"producto": self.producto.pk, "cantidad": 1},
            format="json",
        )
        respuesta = self.client.post(reverse("api:venta-confirmar", args=[ajena.pk]))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK, respuesta.data)
        ajena.refresh_from_db()
        self.assertEqual(ajena.estado, EstadoVenta.CONFIRMADA)
