"""Helpers compartidos por los tests de la API."""

from catalogo.models import Categoria, Producto
from clientes.models import Cliente
from proveedores.models import Proveedor
from usuarios.models import Rol, Usuario
from ventas.models import EstadoVenta, Venta

CLAVE = "clave-de-prueba-123"


def crear_usuario(username, rol, **overrides):
    datos = {
        "email": f"{username}@ejemplo.com",
        "password": CLAVE,
        "rol": rol,
    }
    datos.update(overrides)
    return Usuario.objects.create_user(username=username, **datos)


def crear_proveedor(**overrides):
    datos = {
        "razon_social": "Proveedor API SA",
        "cuit": "30-99999999-9",
        "rubro": "Vidrios",
        "activo": True,
    }
    datos.update(overrides)
    return Proveedor.objects.create(**datos)


def crear_cliente(**overrides):
    datos = {
        "razon_social": "Cliente API SA",
        "cuit": "30-12345678-9",
        "descuento_mayorista": "10.00",
        "activo": True,
    }
    datos.update(overrides)
    return Cliente.objects.create(**datos)


def crear_producto(proveedor=None, **overrides):
    datos = {
        "codigo": "API-001",
        "nombre": "Vidrio API 8mm",
        "categoria": Categoria.VIDRIO,
        "precio_unitario": "1000.00",
        "stock": 10,
        "activo": True,
    }
    datos.update(overrides)
    if proveedor is None:
        proveedor = crear_proveedor()
    datos["proveedor"] = proveedor
    return Producto.objects.create(**datos)


def crear_venta(cliente=None, vendedor=None, **overrides):
    datos = {"estado": EstadoVenta.BORRADOR, "activo": True}
    datos.update(overrides)
    if cliente is None:
        cliente = crear_cliente()
    if vendedor is None:
        vendedor = crear_usuario("vendedor-api", Rol.VENDEDOR)
    datos["cliente"] = cliente
    datos["vendedor"] = vendedor
    return Venta.objects.create(**datos)
