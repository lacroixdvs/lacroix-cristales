from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView, View

from core.roles import rol_de
from usuarios.mixins import RolRequeridoMixin, SoloAdminMixin
from usuarios.models import Rol

from . import presupuesto
from .forms import ProductoForm
from .models import Producto

ROLES_LECTURA = (Rol.ADM, Rol.VENDEDOR, Rol.USUARIO)


class ProductoListView(RolRequeridoMixin, ListView):
    roles_permitidos = ROLES_LECTURA
    model = Producto
    template_name = "catalogo/producto_list.html"
    context_object_name = "productos"
    paginate_by = 20
    partial_template = "catalogo/partials/producto_resultados.html"

    def get_queryset(self):
        queryset = Producto.objects.select_related("proveedor").all().order_by("nombre")
        es_adm = rol_de(self.request.user) == Rol.ADM
        activo = self.request.GET.get("activo", "1")

        if not es_adm:
            queryset = queryset.filter(activo=True)
        elif activo == "1":
            queryset = queryset.filter(activo=True)
        elif activo == "0":
            queryset = queryset.filter(activo=False)

        texto = self.request.GET.get("q", "").strip()
        if texto:
            queryset = queryset.filter(
                Q(codigo__icontains=texto)
                | Q(nombre__icontains=texto)
                | Q(categoria__icontains=texto)
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


class ProductoDetailView(RolRequeridoMixin, DetailView):
    roles_permitidos = ROLES_LECTURA
    template_name = "catalogo/producto_detail.html"
    context_object_name = "producto"

    def get_queryset(self):
        queryset = Producto.objects.select_related("proveedor").all()
        if rol_de(self.request.user) != Rol.ADM:
            queryset = queryset.filter(activo=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["es_adm"] = rol_de(self.request.user) == Rol.ADM
        return context


class ProductoCreateView(SoloAdminMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "catalogo/producto_form.html"
    success_url = reverse_lazy("catalogo:producto-list")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, "Producto creado correctamente.")
        return respuesta


class ProductoUpdateView(SoloAdminMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "catalogo/producto_form.html"
    success_url = reverse_lazy("catalogo:producto-list")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, "Producto actualizado correctamente.")
        return respuesta


class ProductoBajaView(SoloAdminMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        producto.activo = False
        producto.save(update_fields=["activo"])
        messages.success(request, "Producto dado de baja correctamente.")
        return redirect("catalogo:producto-list")


class ProductoReactivarView(SoloAdminMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        producto.activo = True
        producto.save(update_fields=["activo"])
        messages.success(request, "Producto reactivado correctamente.")
        return redirect("catalogo:producto-list")


class PresupuestoView(LoginRequiredMixin, TemplateView):
    """Presupuesto en sesión: no descuenta stock ni crea ventas."""

    template_name = "catalogo/presupuesto.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(presupuesto.resumen(self.request))
        return context

    def post(self, request, *args, **kwargs):
        accion = request.POST.get("accion")
        if accion == "vaciar":
            presupuesto.vaciar(request)
            messages.success(request, "Presupuesto vaciado.")
        elif accion in {"agregar", "cambiar"}:
            producto_id = request.POST.get("producto_id")
            try:
                cantidad = int(request.POST.get("cantidad", "1"))
            except (TypeError, ValueError):
                cantidad = 0

            if cantidad < 1:
                messages.error(request, "La cantidad debe ser al menos 1.")
            else:
                producto = Producto.objects.filter(pk=producto_id, activo=True).first()
                if producto is None:
                    messages.error(request, "El producto no existe o no está activo.")
                elif accion == "agregar":
                    presupuesto.agregar(request, producto, cantidad)
                    messages.success(request, "Producto agregado al presupuesto.")
                elif not presupuesto.cambiar_cantidad(request, producto_id, cantidad):
                    messages.error(request, "Ese producto no está en el presupuesto.")
                else:
                    messages.success(request, "Cantidad actualizada.")
        elif accion == "quitar":
            presupuesto.quitar(request, request.POST.get("producto_id"))
            messages.success(request, "Producto quitado del presupuesto.")
        else:
            messages.error(request, "Acción no reconocida.")
        return redirect("catalogo:presupuesto")
