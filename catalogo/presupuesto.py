"""Presupuesto del perfil USUARIO, guardado únicamente en `request.session`."""

from decimal import Decimal

from .models import Producto

CLAVE_SESION = "presupuesto"


def obtener(request):
    """Devuelve `{str(producto_id): cantidad}` sin exponer el dict de la sesión."""
    return dict(request.session.get(CLAVE_SESION, {}))


def _guardar(request, items):
    request.session[CLAVE_SESION] = items
    request.session.modified = True


def agregar(request, producto, cantidad):
    """Suma un producto activo al presupuesto (no descuenta stock)."""
    items = obtener(request)
    clave = str(producto.pk)
    items[clave] = int(items.get(clave, 0)) + int(cantidad)
    _guardar(request, items)


def cambiar_cantidad(request, producto_id, cantidad):
    items = obtener(request)
    clave = str(producto_id)
    if clave not in items:
        return False
    items[clave] = int(cantidad)
    _guardar(request, items)
    return True


def quitar(request, producto_id):
    items = obtener(request)
    items.pop(str(producto_id), None)
    _guardar(request, items)


def vaciar(request):
    request.session.pop(CLAVE_SESION, None)
    request.session.modified = True


def resumen(request):
    """Items con su subtotal y totales calculados desde precios actuales del catálogo."""
    items = obtener(request)
    if not items:
        return {"items": [], "subtotal": Decimal("0.00"), "total": Decimal("0.00"), "cantidad_total": 0}

    ids = []
    for clave, cantidad in items.items():
        try:
            ids.append(int(clave))
        except (TypeError, ValueError):
            continue
    productos = {p.pk: p for p in Producto.objects.filter(pk__in=ids, activo=True)}

    filas = []
    subtotal = Decimal("0.00")
    cantidad_total = 0
    for producto_id in ids:
        producto = productos.get(producto_id)
        if producto is None:
            continue
        cantidad = int(items[str(producto_id)])
        if cantidad < 1:
            continue
        importe = producto.precio_unitario * cantidad
        filas.append(
            {
                "producto": producto,
                "cantidad": cantidad,
                "precio_unitario": producto.precio_unitario,
                "subtotal": importe,
            }
        )
        subtotal += importe
        cantidad_total += cantidad

    return {"items": filas, "subtotal": subtotal, "total": subtotal, "cantidad_total": cantidad_total}
