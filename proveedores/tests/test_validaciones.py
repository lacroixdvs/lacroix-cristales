from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from proveedores.forms import ProveedorForm
from proveedores.models import Proveedor

from . import crear_proveedor


class ValidacionesProveedorTests(TestCase):
    def test_cuit_de_11_digitos_se_normaliza_al_guardar(self):
        form = ProveedorForm(
            data={
                "razon_social": "Cristales del Norte SA",
                "cuit": "30111111111",
                "rubro": "Vidrios",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        proveedor = form.save()
        self.assertEqual(proveedor.cuit, "30-11111111-1")

    def test_cuit_con_formato_invalido_se_rechaza_en_el_modelo(self):
        proveedor = Proveedor(razon_social="Invalida", cuit="30-1234-1")
        with self.assertRaises(ValidationError):
            proveedor.full_clean()

    def test_cuit_duplicado_se_rechaza_en_el_formulario(self):
        crear_proveedor()
        form = ProveedorForm(
            data={
                "razon_social": "Otro proveedor",
                "cuit": "30-11111111-1",
                "rubro": "Vidrios",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("cuit", form.errors)

    def test_cuit_duplicado_se_rechaza_en_la_base(self):
        crear_proveedor()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Proveedor.objects.create(razon_social="Otro", cuit="30-11111111-1")

    def test_rubro_y_activo_son_opcionales_con_valores_por_defecto(self):
        proveedor = Proveedor.objects.create(
            razon_social="Sin rubro", cuit="30-33333333-3"
        )
        self.assertEqual(proveedor.rubro, "")
        self.assertTrue(proveedor.activo)

    def test_form_normaliza_cuit(self):
        form = ProveedorForm(
            data={"razon_social": "Normaliza", "cuit": "30444444444"}
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["cuit"], "30-44444444-4")

