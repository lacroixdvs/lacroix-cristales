from django.db import IntegrityError, transaction
from django.test import TestCase

from clientes.forms import ClienteForm
from clientes.models import Cliente

from . import DATOS_FORMULARIO, crear_cliente


class ValidacionesClienteTests(TestCase):
    def test_normaliza_cuit_de_11_digitos(self):
        datos = dict(DATOS_FORMULARIO, cuit="30876543210")
        form = ClienteForm(data=datos)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["cuit"], "30-87654321-0")

    def test_rechaza_cuit_con_formato_invalido(self):
        datos = dict(DATOS_FORMULARIO, cuit="30-123-9")
        form = ClienteForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn("cuit", form.errors)
        self.assertIn("XX-XXXXXXXX-X", str(form.errors["cuit"]))

    def test_rechaza_cuit_duplicado_en_formulario(self):
        crear_cliente(cuit="30-87654321-0")
        datos = dict(DATOS_FORMULARIO, cuit="30876543210")
        form = ClienteForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn("cuit", form.errors)
        self.assertIn("Ya existe un cliente", str(form.errors["cuit"]))

    def test_cuit_es_unico_en_base(self):
        crear_cliente(cuit="30-11111111-1")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                crear_cliente(cuit="30-11111111-1")

    def test_rechaza_descuento_fuera_de_rango(self):
        for valor in ("-1", "100.01"):
            with self.subTest(valor=valor):
                form = ClienteForm(data=dict(DATOS_FORMULARIO, descuento_mayorista=valor))
                self.assertFalse(form.is_valid())
                self.assertIn("descuento_mayorista", form.errors)

    def test_acepta_descuento_en_limites(self):
        for valor in ("0", "100"):
            with self.subTest(valor=valor):
                form = ClienteForm(data=dict(DATOS_FORMULARIO, descuento_mayorista=valor))
                self.assertTrue(form.is_valid(), form.errors)

    def test_descuento_por_defecto_es_cero(self):
        cliente = Cliente.objects.create(razon_social="Sin descuento", cuit="30-22222222-2")
        self.assertEqual(cliente.descuento_mayorista, 0)
        self.assertTrue(cliente.activo)
