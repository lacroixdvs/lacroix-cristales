from django.urls import reverse
from django.test import TestCase

from catalogo.models import Producto
from usuarios.models import Rol

from . import DATOS_FORMULARIO, crear_producto, crear_usuario


class CrudCatalogoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = crear_usuario("admin-crud-catalogo", Rol.ADM)
        cls.proveedor = crear_producto(codigo="CRU-001").proveedor
        cls.producto = crear_producto(cls.proveedor, codigo="CRU-002", nombre="Original")

    def setUp(self):
        self.client.login(username=self.admin.username, password="clave-de-prueba-123")

    def test_alta_edicion_baja_y_reactivacion(self):
        datos = {**DATOS_FORMULARIO, "proveedor": self.proveedor.pk}
        respuesta = self.client.post(
            reverse("catalogo:producto-create"), datos, follow=True
        )
        self.assertRedirects(respuesta, reverse("catalogo:producto-list"))
        self.assertContains(respuesta, "Producto creado correctamente.")
        creado = Producto.objects.get(codigo="ESP-100")

        self.client.post(
            reverse("catalogo:producto-update", args=[creado.pk]),
            {**datos, "nombre": "Editado"},
        )
        creado.refresh_from_db()
        self.assertEqual(creado.nombre, "Editado")

        self.client.post(reverse("catalogo:producto-baja", args=[creado.pk]))
        creado.refresh_from_db()
        self.assertFalse(creado.activo)

        self.client.post(reverse("catalogo:producto-reactivar", args=[creado.pk]))
        creado.refresh_from_db()
        self.assertTrue(creado.activo)
        self.assertTrue(Producto.objects.filter(pk=creado.pk).exists())
