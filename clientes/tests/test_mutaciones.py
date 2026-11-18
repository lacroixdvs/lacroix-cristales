from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from usuarios.models import Rol

from . import DATOS_FORMULARIO, crear_cliente, crear_usuario


def mensajes(respuesta):
    return [str(mensaje) for mensaje in get_messages(respuesta.wsgi_request)]


class MutacionesClientesTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_usuario("admin", Rol.ADM))

    def test_adm_crea_cliente_con_mensaje(self):
        respuesta = self.client.post(reverse("clientes:cliente-create"), DATOS_FORMULARIO)
        self.assertEqual(respuesta.status_code, 302)
        cliente = Cliente.objects.get(cuit="30-87654321-0")
        self.assertEqual(cliente.razon_social, "Espejos del Sur SA")
        self.assertTrue(any("creado" in texto for texto in mensajes(respuesta)))

    def test_adm_edita_cliente_con_mensaje(self):
        cliente = crear_cliente()
        datos = dict(DATOS_FORMULARIO, razon_social="Razón Actualizada")
        respuesta = self.client.post(
            reverse("clientes:cliente-update", args=[cliente.pk]), datos
        )
        self.assertEqual(respuesta.status_code, 302)
        cliente.refresh_from_db()
        self.assertEqual(cliente.razon_social, "Razón Actualizada")
        self.assertTrue(any("actualizado" in texto for texto in mensajes(respuesta)))

    def test_adm_da_de_baja_y_reactiva_con_mensajes(self):
        cliente = crear_cliente()

        baja = self.client.post(reverse("clientes:cliente-baja", args=[cliente.pk]))
        cliente.refresh_from_db()
        self.assertFalse(cliente.activo)
        self.assertTrue(Cliente.objects.filter(pk=cliente.pk).exists())
        self.assertTrue(any("baja" in texto for texto in mensajes(baja)))

        alta = self.client.post(reverse("clientes:cliente-reactivar", args=[cliente.pk]))
        cliente.refresh_from_db()
        self.assertTrue(cliente.activo)
        self.assertTrue(any("reactivado" in texto for texto in mensajes(alta)))
