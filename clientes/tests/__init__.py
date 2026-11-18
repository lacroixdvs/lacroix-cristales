"""Helpers compartidos por los tests de clientes."""

from clientes.models import Cliente
from usuarios.models import Rol, Usuario


def crear_cliente(**overrides):
    datos = {
        "razon_social": "Vidrios Acme SA",
        "cuit": "30-12345678-9",
        "contacto": "555-1234",
        "email": "acme@ejemplo.com",
        "direccion": "Av. Siempre Viva 123",
        "descuento_mayorista": "0.00",
        "activo": True,
    }
    datos.update(overrides)
    return Cliente.objects.create(**datos)


def crear_usuario(username, rol):
    return Usuario.objects.create_user(
        username=username,
        email=f"{username}@ejemplo.com",
        password="clave-de-prueba-123",
        rol=rol,
    )


DATOS_FORMULARIO = {
    "razon_social": "Espejos del Sur SA",
    "cuit": "30-87654321-0",
    "contacto": "555-9876",
    "email": "sur@ejemplo.com",
    "direccion": "Calle Sur 456",
    "descuento_mayorista": "12.50",
    "activo": "on",
}
