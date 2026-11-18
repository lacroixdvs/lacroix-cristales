from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from core.roles import rol_de
from usuarios.mixins import RolRequeridoMixin, SoloAdminMixin
from usuarios.models import Rol

from .forms import ClienteForm
from .models import Cliente


class ClienteListView(RolRequeridoMixin, ListView):
    """Listado para ADM y VENDEDOR: activos por defecto, live search y paginación."""

    roles_permitidos = (Rol.ADM, Rol.VENDEDOR)
    model = Cliente
    template_name = "clientes/cliente_list.html"
    context_object_name = "clientes"
    paginate_by = 20
    partial_template = "clientes/partials/cliente_resultados.html"

    def get_queryset(self):
        queryset = Cliente.objects.all().order_by("razon_social")
        es_adm = rol_de(self.request.user) == Rol.ADM
        activo = self.request.GET.get("activo", "1")

        # VENDEDOR nunca puede pedir bajas: el parámetro se ignora en backend.
        if not es_adm:
            queryset = queryset.filter(activo=True)
        elif activo == "1":
            queryset = queryset.filter(activo=True)
        elif activo == "0":
            queryset = queryset.filter(activo=False)

        texto = self.request.GET.get("q", "").strip()
        if texto:
            queryset = queryset.filter(
                Q(razon_social__icontains=texto)
                | Q(cuit__icontains=texto)
                | Q(email__icontains=texto)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        es_adm = rol_de(self.request.user) == Rol.ADM
        activo = self.request.GET.get("activo", "1") if es_adm else "1"
        q = self.request.GET.get("q", "").strip()

        parametros = {}
        if q:
            parametros["q"] = q
        if es_adm:
            parametros["activo"] = activo

        context.update(
            {
                "q": q,
                "activo": activo,
                "es_adm": es_adm,
                "query_base": urlencode(parametros),
            }
        )
        return context

    def get_template_names(self):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return [self.partial_template]
        return [self.template_name]


class ClienteDetailView(SoloAdminMixin, DetailView):
    model = Cliente
    template_name = "clientes/cliente_detail.html"
    context_object_name = "cliente"


class ClienteCreateView(SoloAdminMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"
    success_url = reverse_lazy("clientes:cliente-list")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, "Cliente creado correctamente.")
        return respuesta


class ClienteUpdateView(SoloAdminMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"
    success_url = reverse_lazy("clientes:cliente-list")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, "Cliente actualizado correctamente.")
        return respuesta


class ClienteBajaView(SoloAdminMixin, View):
    """Baja lógica: activo=False, sin borrado físico."""

    http_method_names = ["post"]

    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.activo = False
        cliente.save(update_fields=["activo"])
        messages.success(request, "Cliente dado de baja correctamente.")
        return redirect("clientes:cliente-list")


class ClienteReactivarView(SoloAdminMixin, View):
    """Reactivación de un cliente dado de baja."""

    http_method_names = ["post"]

    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.activo = True
        cliente.save(update_fields=["activo"])
        messages.success(request, "Cliente reactivado correctamente.")
        return redirect("clientes:cliente-list")
