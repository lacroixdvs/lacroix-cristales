from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default = True
    default_auto_field = "django.db.models.BigAutoField"
    name = "usuarios"
    verbose_name = "Usuarios"

    def ready(self):
        """Registra las señales de roles y baja lógica."""
        from . import signals  # noqa: F401
