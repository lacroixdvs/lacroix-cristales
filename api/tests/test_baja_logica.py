"""Tests de baja lógica: DELETE setea activo=False, nunca borra la fila."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.tests import crear_cliente, crear_producto, crear_proveedor, crear_usuario
from catalogo.models import Producto
from clientes.models import Cliente
from proveedores.models import Proveedor
from usuarios.models import Rol
from ventas.models import Venta


class BajaLogicaAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = crear_usuario("admin-baja", Rol.ADM)
        cls.proveedor = crear_proveedor()
        cls.cliente = crear_cliente(cuit="30-12345678-9")
        cls.producto = crear_producto(proveedor=cls.proveedor)

    def setUp(self):
        self.client.force_authenticate(user=self.admin)

    def test_delete_proveedor_no_borra_fila_y_lo_desactiva(self):
        respuesta = self.client.delete(
            reverse("api:proveedor-detail", args=[self.proveedor.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.proveedor.refresh_from_db()
        self.assertFalse(self.proveedor.activo)
        self.assertTrue(Proveedor.objects.filter(pk=self.proveedor.pk).exists())

    def test_delete_cliente_no_borra_fila_y_lo_desactiva(self):
        respuesta = self.client.delete(
            reverse("api:cliente-detail", args=[self.cliente.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.cliente.refresh_from_db()
        self.assertFalse(self.cliente.activo)
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())

    def test_delete_producto_no_borra_fila_y_lo_desactiva(self):
        respuesta = self.client.delete(
            reverse("api:producto-detail", args=[self.producto.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.activo)
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_delete_usuario_no_borra_fila_y_lo_desactiva(self):
        otro = crear_usuario("otro-admin-baja", Rol.ADM)
        respuesta = self.client.delete(reverse("api:usuario-detail", args=[otro.pk]))
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        otro.refresh_from_db()
        self.assertFalse(otro.activo)
        self.assertFalse(otro.is_active)

    def test_admin_no_puede_darse_de_baja_a_si_mismo(self):
        respuesta = self.client.delete(
            reverse("api:usuario-detail", args=[self.admin.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.activo)

    def test_delete_venta_pasa_por_el_servicio_y_reintegra_stock(self):
        from api.tests import crear_venta
        from ventas import services

        venta = crear_venta(cliente=self.cliente, vendedor=crear_usuario("v-baja", Rol.VENDEDOR))
        services.agregar_detalle(venta, self.producto, 3)
        # Agregar ítems no toca el stock; solo la confirmación lo descuenta.
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)
        services.confirmar_venta(venta)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 7)

        respuesta = self.client.delete(reverse("api:venta-detail", args=[venta.pk]))
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        venta.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertFalse(venta.activo)
        self.assertEqual(venta.estado, "CANCELADA")
        self.assertEqual(self.producto.stock, 10)
        self.assertTrue(Venta.objects.filter(pk=venta.pk).exists())
