"""Sincronización entre grupos de Django Auth, `rol` y baja lógica de Usuario."""

from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver

from .models import Rol, Usuario

_ROLES_EN_PRIORIDAD = (Rol.ADM, Rol.VENDEDOR, Rol.USUARIO)


@receiver(pre_save, sender=Usuario)
def sincronizar_activo_con_is_active(sender, instance, **kwargs):
    """`activo` es el campo canónico de baja lógica; `is_active` lo refleja."""
    instance.is_active = instance.activo
    if instance.pk:
        instance._rol_original = (
            sender.objects.filter(pk=instance.pk).values_list("rol", flat=True).first()
        )
    else:
        instance._rol_original = None


@receiver(post_save, sender=Usuario)
def sincronizar_grupos_desde_rol(sender, instance, created, **kwargs):
    """Si cambia `rol`, ajusta el grupo para que Auth siga siendo la fuente de verdad."""
    rol_original = getattr(instance, "_rol_original", None)
    if not created and rol_original == instance.rol:
        return

    grupo, _ = Group.objects.get_or_create(name=instance.rol)
    instance.groups.set([grupo])


@receiver(m2m_changed, sender=Usuario.groups.through)
def sincronizar_rol_desde_grupos(sender, instance, action, reverse, **kwargs):
    """Al cambiar los grupos, actualiza `rol` sin disparar nuevos saves."""
    if reverse or action not in {"post_add", "post_remove", "post_clear"}:
        return

    nombres = set(instance.groups.values_list("name", flat=True))
    rol = next((item for item in _ROLES_EN_PRIORIDAD if item in nombres), Rol.USUARIO)
    if instance.rol != rol:
        Usuario.objects.filter(pk=instance.pk).update(rol=rol)
        instance.rol = rol
