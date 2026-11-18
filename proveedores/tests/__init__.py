"""Helpers compartidos por los tests de proveedores."""

from proveedores.models import Proveedor
from usuarios.models import Rol, Usuario


def crear_proveedor(**overrides):
    datos = {
        "razon_social": "Cristales del Norte SA",
        "cuit": "30-11111111-1",
        "contacto": "555-1111",
        "email": "norte@ejemplo.com",
        "direccion": "Av. Norte 100",
        "rubro": "Vidrios",
        "activo": True,
    }
    datos.update(overrides)
    return Proveedor.objects.create(**datos)


def crear_usuario(username, rol):
    return Usuario.objects.create_user(
        username=username,
        email=f"{username}@ejemplo.com",
        password="clave-de-prueba-123",
        rol=rol,
    )


DATOS_FORMULARIO = {
    "razon_social": "Espejos del Oeste SA",
    "cuit": "30-44444444-4",
    "contacto": "555-2222",
    "email": "oeste@ejemplo.com",
    "direccion": "Calle Oeste 200",
    "rubro": "Espejos",
    "activo": "on",
}
