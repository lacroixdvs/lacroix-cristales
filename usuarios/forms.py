from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.forms import EstiloBootstrapMixin

from .models import Rol, Usuario


class RegistroForm(EstiloBootstrapMixin, UserCreationForm):
    """Registro público: siempre crea un usuario con el rol USUARIO."""

    email = forms.EmailField(label="Email", required=True)
    contacto = forms.CharField(label="Contacto (teléfono/WhatsApp)", required=False, max_length=30)

    class Meta:
        model = Usuario
        fields = ("username", "first_name", "last_name", "email", "contacto")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este email.")
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data["email"]
        usuario.rol = Rol.USUARIO
        usuario.activo = True
        if commit:
            usuario.save()
        return usuario


class UsuarioAdminBaseForm(EstiloBootstrapMixin, forms.ModelForm):
    """Campos comunes del alta y la edición desde el panel de ADM."""

    class Meta:
        model = Usuario
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "contacto",
            "rol",
            "activo",
            "is_staff",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        existentes = Usuario.objects.filter(email__iexact=email)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError("Ya existe un usuario con este email.")
        return email


class UsuarioCrearForm(UsuarioAdminBaseForm):
    """Alta de usuarios con contraseña obligatoria."""

    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario


class UsuarioEditarForm(UsuarioAdminBaseForm):
    """Edición de usuarios; la contraseña se cambia solo si se completa."""

    password = forms.CharField(
        label="Nueva contraseña (opcional)", widget=forms.PasswordInput, required=False
    )

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if self.cleaned_data.get("password"):
            usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario
