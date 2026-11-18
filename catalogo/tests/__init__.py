"""Helpers compartidos por los tests de catálogo."""

from itertools import count

from catalogo.models import Categoria, Producto
from proveedores.models import Proveedor
from usuarios.models import Rol, Usuario


_secuencia_cuit = count(1)


def crear_proveedor(**overrides):
    sufijo = next(_secuencia_cuit)
    datos = {
        "razon_social": "Proveedor Catálogo SA",
        "cuit": f"30-700000{sufijo:02d}-7",
        "rubro": "Vidrios",
    }
    datos.update(overrides)
    return Proveedor.objects.create(**datos)


def crear_producto(proveedor=None, **overrides):
    datos = {
        "codigo": "VID-001",
        "nombre": "Vidrio templado 8mm",
        "categoria": Categoria.VIDRIO,
        "descripcion": "Vidrio para mamparas",
        "espesor": "8mm",
        "precio_unitario": "15000.00",
        "stock": 20,
        "activo": True,
    }
    datos.update(overrides)
    if proveedor is None:
        proveedor = crear_proveedor()
    datos["proveedor"] = proveedor
    return Producto.objects.create(**datos)


def crear_usuario(username, rol):
    return Usuario.objects.create_user(
        username=username,
        email=f"{username}@ejemplo.com",
        password="clave-de-prueba-123",
        rol=rol,
    )


DATOS_FORMULARIO = {
    "codigo": "ESP-100",
    "nombre": "Espejo rectangular",
    "categoria": Categoria.ESPEJO,
    "descripcion": "Espejo con marco",
    "espesor": "5mm",
    "precio_unitario": "25000.00",
    "stock": 10,
    "activo": "on",
}
