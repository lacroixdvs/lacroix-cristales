"""Carga datos de demostración realistas de Vit Cristales, de forma idempotente.

Se puede ejecutar las veces que haga falta en desarrollo: los registros se
buscan por una clave natural (username, CUIT, código de producto, observaciones
de la venta) y solo se crean si no existen. No modifica datos cargados por el
usuario ni duplica stock por ventas ya generadas.
"""

from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalogo.models import Categoria, Producto
from clientes.models import Cliente
from core.validators import normalizar_cuit
from proveedores.models import Proveedor
from usuarios.models import Rol, Usuario
from ventas import services
from ventas.models import Venta

DEMO_PASSWORD = "Demo1234!"
MARCA_DEMO = "[DEMO cargar_datos_demo]"

OBS_CONFIRMADA = f"{MARCA_DEMO} Venta confirmada de ejemplo."
OBS_BORRADOR = f"{MARCA_DEMO} Borrador de ejemplo pendiente de confirmar."

# (username, email, rol, nombre, apellido, contacto)
USUARIOS_DEMO = [
    ("demo_admin", "demo.admin@vitcristales.local", Rol.ADM, "Ana", "Ferreyra", "381 555-0101"),
    ("demo_vendedor", "demo.vendedor@vitcristales.local", Rol.VENDEDOR, "Marcos", "Ríos", "381 555-0102"),
    ("demo_usuario", "demo.usuario@vitcristales.local", Rol.USUARIO, "Lucía", "Pereyra", "381 555-0103"),
]

# (razón social, CUIT 11 dígitos, contacto, email, dirección, rubro)
PROVEEDORES_DEMO = [
    (
        "Vidrios del Litoral S.A.",
        "30123456781",
        "381 444-2201",
        "ventas@vidriosdellitoral.com.ar",
        "Av. Belgrano 1250, San Miguel de Tucumán",
        "Vidrio templado y laminado",
    ),
    (
        "Herrajes y Accesorios Sur S.R.L.",
        "30234567892",
        "381 444-2202",
        "pedidos@herrajesur.com.ar",
        "Calle Laprida 830, San Miguel de Tucumán",
        "Herrajes, marcos y accesorios",
    ),
    (
        "Cristales Premium Norte S.A.",
        "30345678903",
        "381 444-2203",
        "comercial@cristalespremium.com.ar",
        "Ruta 9 km 15, Tafí Viejo",
        "Espejos, mamparas y cerramientos",
    ),
]

# (razón social, CUIT 11 dígitos, contacto, email, dirección, descuento %)
CLIENTES_DEMO = [
    (
        "Constructora Andina S.A.",
        "30456789014",
        "381 333-1101",
        "compras@constructoraandina.com.ar",
        "Av. Aconquija 2450, Yerba Buena",
        Decimal("15.00"),
    ),
    (
        "Estudio de Arquitectura Moderna",
        "30567890125",
        "381 333-1102",
        "administracion@estudiomoderna.com.ar",
        "Calle San Martín 615, San Miguel de Tucumán",
        Decimal("10.00"),
    ),
    (
        "Comercial del Oeste S.R.L.",
        "30678901236",
        "381 333-1103",
        "gerencia@comercialoeste.com.ar",
        "Av. Mitre 1780, San Miguel de Tucumán",
        Decimal("5.00"),
    ),
    (
        "Inmobiliaria Central del Norte",
        "30789012347",
        "381 333-1104",
        "info@inmobiliariacentral.com.ar",
        "Calle 24 de Septiembre 320, San Miguel de Tucumán",
        Decimal("0.00"),
    ),
]

# (código, nombre, categoría, descripción, espesor, precio, stock, índice proveedor)
PRODUCTOS_DEMO = [
    ("VID-001", "Vidrio templado 8 mm", Categoria.VIDRIO, "Vidrio templado para cerramientos y frentes.", "8mm", Decimal("145000.00"), 120, 0),
    ("VID-002", "Vidrio laminado 4+4", Categoria.VIDRIO, "Laminado de seguridad para barandas y puertas.", "4+4 laminado", Decimal("198500.00"), 90, 2),
    ("MAM-001", "Mampara corredera 2 hojas", Categoria.MAMPARA, "Mampara de vidrio templado con riel superior.", "10mm", Decimal("620000.00"), 25, 2),
    ("MAM-002", "Mampara fija con marco de aluminio", Categoria.MAMPARA, "Panel fijo con marco de aluminio anodizado.", "8mm", Decimal("540000.00"), 30, 1),
    ("ESP-001", "Espejo rectangular 100 x 60", Categoria.ESPEJO, "Espejo con marco de aluminio para baño.", "5mm", Decimal("89000.00"), 60, 2),
    ("ESP-002", "Espejo circular 80 cm", Categoria.ESPEJO, "Espejo redondo con bisel perimetral.", "5mm", Decimal("76000.00"), 45, 2),
    ("CER-001", "Cerramiento de oficina vidrio/aluminio", Categoria.CERRAMIENTO, "Cerramiento completo con puerta y panel fijo.", "10mm", Decimal("950000.00"), 15, 2),
    ("CER-002", "Puerta de vidrio con marco", Categoria.CERRAMIENTO, "Puerta vaivén con marco de aluminio y vidrio templado.", "8mm", Decimal("380000.00"), 20, 1),
]

# (índice en PRODUCTOS_DEMO, cantidad) — el cliente y vendedor se definen por venta.
ITEMS_CONFIRMADA = [(0, 4), (3, 2), (6, 1)]
ITEMS_BORRADOR = [(4, 6), (7, 2)]


class Command(BaseCommand):
    """Crea el dataset de demostración sin duplicarlo en ejecuciones posteriores."""

    help = "Carga usuarios, proveedores, clientes, productos y ventas de ejemplo de Vit Cristales."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default=DEMO_PASSWORD,
            help=f"Contraseña para los 3 usuarios demo (por defecto: {DEMO_PASSWORD}).",
        )

    def handle(self, *args, **options):
        password = (options["password"] or "").strip()
        if not password:
            raise CommandError("La contraseña demo no puede estar vacía.")

        # Garantiza que existan los grupos y permisos antes de crear usuarios.
        salida_roles = StringIO()
        call_command("cargar_roles", stdout=salida_roles, verbosity=0)
        if options["verbosity"] > 1:
            self.stdout.write(salida_roles.getvalue())

        estadisticas = {"creados": 0, "existentes": 0}
        with transaction.atomic():
            usuarios = self._cargar_usuarios(password, estadisticas)
            proveedores = self._cargar_proveedores(estadisticas)
            clientes = self._cargar_clientes(estadisticas)
            productos = self._cargar_productos(proveedores, estadisticas)
            self._cargar_ventas(usuarios, clientes, productos, estadisticas)

        self.stdout.write(
            self.style.SUCCESS(
                "Datos demo listos: "
                f"{estadisticas['creados']} creados, "
                f"{estadisticas['existentes']} ya existían (sin duplicados)."
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f"Usuarios de prueba: {', '.join(u[0] for u in USUARIOS_DEMO)} "
                f"— contraseña: {password}"
            )
        )

    def _registro(self, modelo, busqueda, valores, etiqueta, estadisticas):
        """get_or_create con logging uniforme para todas las entidades."""
        objeto, creado = modelo.objects.get_or_create(defaults=valores, **busqueda)
        accion = "creado" if creado else "existente"
        estadisticas["creados" if creado else "existentes"] += 1
        self.stdout.write(f"  {etiqueta}: {accion}")
        return objeto

    def _cargar_usuarios(self, password, estadisticas):
        usuarios = {}
        for username, email, rol, nombre, apellido, contacto in USUARIOS_DEMO:
            usuario = Usuario.objects.filter(username=username).first()
            if usuario is None:
                usuario = Usuario.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    rol=rol,
                    first_name=nombre,
                    last_name=apellido,
                    contacto=contacto,
                    activo=True,
                )
                accion = "creado"
                estadisticas["creados"] += 1
            else:
                accion = "existente"
                estadisticas["existentes"] += 1
            self.stdout.write(f"  Usuario {username} ({rol}): {accion}")
            usuarios[rol] = usuario
        return usuarios

    def _cargar_proveedores(self, estadisticas):
        proveedores = []
        for razon, cuit, contacto, email, direccion, rubro in PROVEEDORES_DEMO:
            cuit = normalizar_cuit(cuit)
            proveedor = self._registro(
                Proveedor,
                {"cuit": cuit},
                {
                    "razon_social": razon,
                    "contacto": contacto,
                    "email": email,
                    "direccion": direccion,
                    "rubro": rubro,
                    "activo": True,
                },
                f"Proveedor {razon}",
                estadisticas,
            )
            proveedores.append(proveedor)
        return proveedores

    def _cargar_clientes(self, estadisticas):
        clientes = []
        for razon, cuit, contacto, email, direccion, descuento in CLIENTES_DEMO:
            cuit = normalizar_cuit(cuit)
            cliente = self._registro(
                Cliente,
                {"cuit": cuit},
                {
                    "razon_social": razon,
                    "contacto": contacto,
                    "email": email,
                    "direccion": direccion,
                    "descuento_mayorista": descuento,
                    "activo": True,
                },
                f"Cliente {razon} ({descuento}%)",
                estadisticas,
            )
            clientes.append(cliente)
        return clientes

    def _cargar_productos(self, proveedores, estadisticas):
        productos = {}
        for codigo, nombre, categoria, descripcion, espesor, precio, stock, proveedor_idx in PRODUCTOS_DEMO:
            producto = self._registro(
                Producto,
                {"codigo": codigo},
                {
                    "nombre": nombre,
                    "categoria": categoria,
                    "descripcion": descripcion,
                    "espesor": espesor,
                    "precio_unitario": precio,
                    "stock": stock,
                    "proveedor": proveedores[proveedor_idx],
                    "activo": True,
                },
                f"Producto {codigo} ({categoria})",
                estadisticas,
            )
            productos[codigo] = producto
        return productos

    def _cargar_ventas(self, usuarios, clientes, productos, estadisticas):
        """Crea una venta confirmada (descuenta stock) y un borrador."""
        confirmada, creada = Venta.objects.get_or_create(
            observaciones=OBS_CONFIRMADA,
            defaults={
                "cliente": clientes[0],
                "vendedor": usuarios[Rol.VENDEDOR],
            },
        )
        accion = "creada y confirmada" if creada else "existente (sin cambios)"
        estadisticas["creados" if creada else "existentes"] += 1
        self.stdout.write(f"  Venta confirmada de ejemplo: {accion}")
        if creada:
            for producto_idx, cantidad in ITEMS_CONFIRMADA:
                codigo = PRODUCTOS_DEMO[producto_idx][0]
                services.agregar_detalle(confirmada, productos[codigo], cantidad)
            services.confirmar_venta(confirmada)

        borrador, creado = Venta.objects.get_or_create(
            observaciones=OBS_BORRADOR,
            defaults={
                "cliente": clientes[1],
                "vendedor": usuarios[Rol.VENDEDOR],
            },
        )
        accion = "creada (borrador)" if creado else "existente (sin cambios)"
        estadisticas["creados" if creado else "existentes"] += 1
        self.stdout.write(f"  Venta borrador de ejemplo: {accion}")
        if creado:
            for producto_idx, cantidad in ITEMS_BORRADOR:
                codigo = PRODUCTOS_DEMO[producto_idx][0]
                services.agregar_detalle(borrador, productos[codigo], cantidad)
