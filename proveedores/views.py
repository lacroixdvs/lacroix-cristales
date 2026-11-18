from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from usuarios.mixins import SoloAdminMixin

from .forms import ProveedorForm
from .models import Proveedor


class ProveedorListView(SoloAdminMixin, ListView):
    model = Proveedor
    template_name = "proveedores/proveedor_list.html"
    context_object_name = "proveedores"
    paginate_by = 20
    partial_template = "proveedores/partials/proveedor_resultados.html"

    def get_queryset(self):
        queryset = Proveedor.objects.all().order_by("razon_social")
        activo = self.request.GET.get("activo", "1")
        if activo == "1":
            queryset = queryset.filter(activo=True)
        elif activo == "0":
            queryset = queryset.filter(activo=False)

        texto = self.request.GET.get("q", "").strip()
        if texto:
            queryset = queryset.filter(
                Q(razon_social__icontains=texto)
                | Q(cuit__icontains=texto)
                | Q(email__icontains=texto)
                | Q(rubro__icontains=texto)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        activo = self.request.GET.get("activo", "1")
        parametros = {}
        if q:
            parametros["q"] = q
        parametros["activo"] = activo
        context.update({"q": q, "activo": activo, "query_base": urlencode(parametros)})
        return context

    def get_template_names(self):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return [self.partial_template]
        return [self.template_name]


class ProveedorDetailView(SoloAdminMixin, DetailView):
    model = Proveedor
    template_name = "proveedores/proveedor_detail.html"
    context_object_name = "proveedor"


class ProveedorCreateView(SoloAdminMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "proveedores/proveedor_form.html"
    success_url = reverse_lazy("proveedores:proveedor-list")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, "Proveedor creado correctamente.")
        return respuesta


class ProveedorUpdateView(SoloAdminMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "proveedores/proveedor_form.html"
    success_url = reverse_lazy("proveedores:proveedor-list")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, "Proveedor actualizado correctamente.")
        return respuesta


class ProveedorBajaView(SoloAdminMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        proveedor = get_object_or_404(Proveedor, pk=pk)
        proveedor.activo = False
        proveedor.save(update_fields=["activo"])
        messages.success(request, "Proveedor dado de baja correctamente.")
        return redirect("proveedores:proveedor-list")


class ProveedorReactivarView(SoloAdminMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        proveedor = get_object_or_404(Proveedor, pk=pk)
        proveedor.activo = True
        proveedor.save(update_fields=["activo"])
        messages.success(request, "Proveedor reactivado correctamente.")
        return redirect("proveedores:proveedor-list")
