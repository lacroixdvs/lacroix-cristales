"""Helpers compartidos por los tests de ventas."""

from clientes.models import Cliente
from catalogo.models import Categoria, Producto
from proveedores.models import Proveedor
from usuarios.models import Rol, Usuario
from ventas.models import EstadoVenta, Venta


def crear_cliente(**overrides):
    datos = {
        "razon_social": "Cliente Ventas SA",
        "cuit": "30-12345678-9",
        "email": "ventas@ejemplo.com",
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


def crear_proveedor():
    return Proveedor.objects.create(
        razon_social="Proveedor Ventas SA", cuit="30-99999999-9"
    )


def crear_producto(proveedor=None, **overrides):
    datos = {
        "codigo": "VT-001",
        "nombre": "Vidrio 8mm",
        "categoria": Categoria.VIDRIO,
        "precio_unitario": "10000.00",
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
        vendedor = crear_usuario("vendedor-helper", Rol.VENDEDOR)
    datos["cliente"] = cliente
    datos["vendedor"] = vendedor
    return Venta.objects.create(**datos)
