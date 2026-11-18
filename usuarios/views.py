from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from .forms import RegistroForm, UsuarioCrearForm, UsuarioEditarForm
from .mixins import SoloAdminMixin
from .models import Usuario


class RegistroView(CreateView):
    """Alta pública: el formulario fuerza el rol USUARIO."""

    form_class = RegistroForm
    template_name = "registration/registro.html"
    success_url = reverse_lazy("usuarios:login")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, "Registro exitoso. Ya podés ingresar con tu usuario.")
        return respuesta


class UsuarioListView(SoloAdminMixin, ListView):
    """Listado de usuarios con búsqueda en vivo y filtro por baja lógica."""

    model = Usuario
    template_name = "usuarios/usuario_list.html"
    context_object_name = "usuarios"
    paginate_by = 20
    partial_template = "usuarios/partials/usuario_resultados.html"

    def get_queryset(self):
        queryset = Usuario.objects.all().order_by("username")
        texto = self.request.GET.get("q", "").strip()
        if texto:
            queryset = queryset.filter(
                Q(username__icontains=texto)
                | Q(email__icontains=texto)
                | Q(first_name__icontains=texto)
                | Q(last_name__icontains=texto)
            )
        activo = self.request.GET.get("activo")
        if activo in ("1", "0"):
            queryset = queryset.filter(activo=(activo == "1"))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["activo"] = self.request.GET.get("activo", "")
        return context

    def get_template_names(self):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return [self.partial_template]
        return [self.template_name]


class UsuarioCreateView(SoloAdminMixin, CreateView):
    """Alta de usuarios desde el panel de ADM."""

    model = Usuario
    form_class = UsuarioCrearForm
    template_name = "usuarios/usuario_form.html"
    success_url = reverse_lazy("usuarios:usuario-list")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, "Usuario creado correctamente.")
        return respuesta


class UsuarioUpdateView(SoloAdminMixin, UpdateView):
    """Edición de datos, rol y estado de un usuario."""

    model = Usuario
    form_class = UsuarioEditarForm
    template_name = "usuarios/usuario_form.html"
    success_url = reverse_lazy("usuarios:usuario-list")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, "Usuario actualizado correctamente.")
        return respuesta


class UsuarioBajaView(SoloAdminMixin, View):
    """Baja lógica: activo=False, sin borrado físico."""

    http_method_names = ["post"]

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        if usuario.pk == request.user.pk:
            messages.error(request, "No podés dar de baja tu propio usuario.")
        else:
            usuario.activo = False
            usuario.save(update_fields=["activo", "is_active"])
            messages.success(request, "Usuario dado de baja correctamente.")
        return redirect("usuarios:usuario-list")
