from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from catalogo.forms import ProductoForm
from catalogo.models import Categoria, Producto
from proveedores.models import Proveedor

from . import crear_producto


class ModeloProductoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.proveedor = Proveedor.objects.create(
            razon_social="Proveedor Modelo SA", cuit="30-88888888-8"
        )

    def test_precio_debe_ser_mayor_a_cero(self):
        producto = Producto(
            codigo="PREC-0",
            nombre="Precio cero",
            categoria=Categoria.VIDRIO,
            precio_unitario=Decimal("0"),
            proveedor=self.proveedor,
        )
        with self.assertRaises(ValidationError):
            producto.full_clean()
        form = ProductoForm(
            data={
                "codigo": "PREC-0",
                "nombre": "Precio cero",
                "categoria": Categoria.VIDRIO,
                "precio_unitario": "0.00",
                "stock": 1,
                "proveedor": self.proveedor.pk,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("precio_unitario", form.errors)

    def test_codigo_unico_en_modelo_y_base(self):
        crear_producto(self.proveedor)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Producto.objects.create(
                    codigo="VID-001",
                    nombre="Duplicado",
                    categoria=Categoria.VIDRIO,
                    precio_unitario=Decimal("1.00"),
                    proveedor=self.proveedor,
                )

    def test_proveedor_esta_protegido_contra_borrado_fisico(self):
        crear_producto(self.proveedor)
        with self.assertRaises(ProtectedError):
            self.proveedor.delete()

    def test_valores_por_defecto_y_choices(self):
        producto = crear_producto(self.proveedor, codigo="DEF-001")
        self.assertTrue(producto.activo)
        self.assertEqual(producto.stock, 20)
        self.assertEqual(producto.categoria_etiqueta, "Vidrio")
        self.assertEqual(
            [choice[0] for choice in Categoria.choices],
            ["VIDRIO", "MAMPARA", "ESPEJO", "CERRAMIENTO"],
        )
