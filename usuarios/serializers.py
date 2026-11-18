"""Serializers del perfil USUARIO con el patrón Base / Get / Post."""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Rol

Usuario = get_user_model()


class UsuarioBaseSerializer(serializers.ModelSerializer):
    """Campos comunes y validaciones compartidas."""

    class Meta:
        model = Usuario
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "contacto",
            "rol",
            "activo",
        )


class UsuarioGetSerializer(UsuarioBaseSerializer):
    """Lectura: expone los grupos de Django Auth que determinan el rol efectivo."""

    grupos = serializers.SerializerMethodField()
    rol_etiqueta = serializers.CharField(source="get_rol_display", read_only=True)

    class Meta(UsuarioBaseSerializer.Meta):
        fields = UsuarioBaseSerializer.Meta.fields + ("grupos", "rol_etiqueta")

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_grupos(self, obj):
        return list(obj.groups.values_list("name", flat=True))


class UsuarioPostSerializer(UsuarioBaseSerializer):
    """Escritura: password hasheado y email único (case-insensitive)."""

    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta(UsuarioBaseSerializer.Meta):
        fields = UsuarioBaseSerializer.Meta.fields + ("password",)
        extra_kwargs = {"email": {"required": True}}

    def validate_email(self, valor):
        email = valor.strip().lower()
        existentes = Usuario.objects.filter(email__iexact=email)
        if self.instance:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return email

    def validate_rol(self, valor):
        if valor not in Rol.values:
            raise serializers.ValidationError("Rol no válido.")
        return valor

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        usuario = Usuario(**validated_data)
        if password:
            usuario.set_password(password)
        else:
            usuario.set_unusable_password()
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
