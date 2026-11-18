"""Crea o actualiza los grupos de roles y sus permisos base."""

import os

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from usuarios.models import Rol, Usuario

# Los permisos de dominio se omiten sin warning hasta que existan esas apps (Fase 5-6).
PERMISOS_POR_ROL = {
    Rol.ADM: [
        ("add_usuario", "usuarios", "usuario"),
        ("change_usuario", "usuarios", "usuario"),
        ("delete_usuario", "usuarios", "usuario"),
        ("view_usuario", "usuarios", "usuario"),
        ("add_proveedor", "proveedores", "proveedor"),
        ("change_proveedor", "proveedores", "proveedor"),
        ("delete_proveedor", "proveedores", "proveedor"),
        ("view_proveedor", "proveedores", "proveedor"),
        ("add_cliente", "clientes", "cliente"),
        ("change_cliente", "clientes", "cliente"),
        ("delete_cliente", "clientes", "cliente"),
        ("view_cliente", "clientes", "cliente"),
        ("add_producto", "catalogo", "producto"),
        ("change_producto", "catalogo", "producto"),
        ("delete_producto", "catalogo", "producto"),
        ("view_producto", "catalogo", "producto"),
        ("add_venta", "ventas", "venta"),
        ("change_venta", "ventas", "venta"),
        ("delete_venta", "ventas", "venta"),
        ("view_venta", "ventas", "venta"),
        ("add_detalleventa", "ventas", "detalleventa"),
        ("change_detalleventa", "ventas", "detalleventa"),
        ("delete_detalleventa", "ventas", "detalleventa"),
        ("view_detalleventa", "ventas", "detalleventa"),
    ],
    Rol.VENDEDOR: [
        ("view_cliente", "clientes", "cliente"),
        ("view_producto", "catalogo", "producto"),
        ("add_venta", "ventas", "venta"),
        ("change_venta", "ventas", "venta"),
        ("view_venta", "ventas", "venta"),
        ("add_detalleventa", "ventas", "detalleventa"),
        ("change_detalleventa", "ventas", "detalleventa"),
        ("view_detalleventa", "ventas", "detalleventa"),
    ],
    Rol.USUARIO: [
        ("view_producto", "catalogo", "producto"),
    ],
}


class Command(BaseCommand):
    """Idempotente: se puede correr en cada deploy sin duplicar grupos ni permisos."""

    help = "Crea los grupos ADM/VENDEDOR/USUARIO con sus permisos base."

    def add_arguments(self, parser):
        parser.add_argument(
            "--crear-admin",
            action="store_true",
            help="Crea un usuario administrador inicial si no existe.",
        )
        parser.add_argument("--admin-username", default="admin")
        parser.add_argument("--admin-email", default="admin@vitcristales.local")
        parser.add_argument(
            "--admin-password",
            default=None,
            help="Si se omite, se lee ADMIN_PASSWORD del entorno. Nunca se muestra en logs.",
        )

    def handle(self, *args, **options):
        for rol, especificaciones in PERMISOS_POR_ROL.items():
            grupo, creado = Group.objects.get_or_create(name=rol)
            asignados = 0
            for codename, app_label, modelo in especificaciones:
                try:
                    permiso = Permission.objects.get_by_natural_key(codename, app_label, modelo)
                except (Permission.DoesNotExist, ContentType.DoesNotExist):
                    continue
                grupo.permissions.add(permiso)
                asignados += 1

            estado = "creado" if creado else "existente"
            self.stdout.write(
                self.style.SUCCESS(f"Grupo {rol} {estado}: {asignados} permisos disponibles.")
            )

        if options["crear_admin"]:
            self.crear_admin(options)

    def crear_admin(self, options):
        """Crea el administrador inicial solo si no existe; no imprime secretos."""
        username = options["admin_username"]
        password = options["admin_password"] or os.environ.get("ADMIN_PASSWORD")
        if not password:
            raise CommandError(
                "Definí --admin-password o la variable ADMIN_PASSWORD para crear el administrador."
            )

        if Usuario.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"El usuario '{username}' ya existe; no se modificó."))
            return

        admin = Usuario.objects.create_superuser(
            username=username,
            email=options["admin_email"],
            password=password,
            rol=Rol.ADM,
            activo=True,
        )
        self.stdout.write(self.style.SUCCESS(f"Administrador '{admin.username}' creado."))
