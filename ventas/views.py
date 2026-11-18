from urllib.parse import urlencode

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from catalogo.models import Producto
from core.roles import rol_de
from usuarios.mixins import RolRequeridoMixin, SoloAdminMixin
from usuarios.models import Rol

from . import services
from .forms import VentaForm
from .models import DetalleVenta, EstadoVenta, Venta

ROLES_VENTAS = (Rol.ADM, Rol.VENDEDOR)


class VentaListView(RolRequeridoMixin, ListView):
    """Listado para ADM y VENDEDOR; activas por defecto y filtro de estado ADM."""

    roles_permitidos = ROLES_VENTAS
    model = Venta
    template_name = "ventas/venta_list.html"
    context_object_name = "ventas"
    paginate_by = 20
    partial_template = "ventas/partials/venta_resultados.html"

    def get_queryset(self):
        queryset = (
            Venta.objects.select_related("cliente", "vendedor")
            .all()
            .order_by("-fecha", "-id")
        )
        es_adm = rol_de(self.request.user) == Rol.ADM
        activo = self.request.GET.get("activo", "1")

        if not es_adm:
            queryset = queryset.filter(activo=True, vendedor=self.request.user)
        elif activo == "1":
            queryset = queryset.filter(activo=True)
        elif activo == "0":
            queryset = queryset.filter(activo=False)

        estado = self.request.GET.get("estado", "")
        if estado:
            queryset = queryset.filter(estado=estado)

        texto = self.request.GET.get("q", "").strip()
        if texto:
            queryset = queryset.filter(
                Q(cliente__razon_social__icontains=texto)
                | Q(cliente__cuit__icontains=texto)
                | Q(vendedor__username__icontains=texto)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        es_adm = rol_de(self.request.user) == Rol.ADM
        activo = self.request.GET.get("activo", "1") if es_adm else "1"
        estado = self.request.GET.get("estado", "")
        q = self.request.GET.get("q", "").strip()

        parametros = {}
        if q:
            parametros["q"] = q
        if es_adm:
            parametros["activo"] = activo
        if estado:
            parametros["estado"] = estado

        context.update(
            {
                "q": q,
                "activo": activo,
                "estado": estado,
                "es_adm": es_adm,
                "estados": EstadoVenta.choices,
                "query_base": urlencode(parametros),
            }
        )
        return context

    def get_template_names(self):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return [self.partial_template]
        return [self.template_name]


class VentaDetailView(RolRequeridoMixin, DetailView):
    roles_permitidos = ROLES_VENTAS
    template_name = "ventas/venta_detail.html"
    context_object_name = "venta"

    def get_queryset(self):
        queryset = Venta.objects.select_related("cliente", "vendedor").prefetch_related(
            "detalles__producto"
        )
        if rol_de(self.request.user) != Rol.ADM:
            queryset = queryset.filter(activo=True, vendedor=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        es_adm = rol_de(self.request.user) == Rol.ADM
        context["es_adm"] = es_adm
        context["resumen"] = services.resumen(self.object)
        context["productos_disponibles"] = (
            Producto.objects.filter(activo=True).order_by("nombre")
            if es_adm or self.object.estado == EstadoVenta.BORRADOR
            else Producto.objects.none()
        )
        return context


class VentaCreateView(RolRequeridoMixin, CreateView):
    """ADM y VENDEDOR crean borradores."""

    roles_permitidos = ROLES_VENTAS
    model = Venta
    form_class = VentaForm
    template_name = "ventas/venta_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if rol_de(self.request.user) == Rol.VENDEDOR:
            kwargs["initial"] = {**kwargs.get("initial", {}), "vendedor": self.request.user}
        return kwargs

    def form_valid(self, form):
        if rol_de(self.request.user) == Rol.VENDEDOR and form.instance.vendedor_id != self.request.user.pk:
            form.add_error("vendedor", "Un vendedor solo puede cargar ventas a su nombre.")
            return self.form_invalid(form)
        respuesta = super().form_valid(form)
        messages.success(self.request, "Venta creada en borrador. Agregá ítems para continuar.")
        return respuesta

    def get_success_url(self):
        return reverse_lazy("ventas:venta-detail", kwargs={"pk": self.object.pk})


class VentaUpdateView(RolRequeridoMixin, UpdateView):
    """Edición de cabecera: ADM o VENDEDOR sobre sus propios borradores."""

    roles_permitidos = ROLES_VENTAS
    model = Venta
    form_class = VentaForm
    template_name = "ventas/venta_form.html"

    def get_queryset(self):
        queryset = Venta.objects.all()
        if rol_de(self.request.user) != Rol.ADM:
            queryset = queryset.filter(
                activo=True,
                estado=EstadoVenta.BORRADOR,
                vendedor=self.request.user,
            )
        return queryset

    def form_valid(self, form):
        if rol_de(self.request.user) == Rol.VENDEDOR and form.instance.vendedor_id != self.request.user.pk:
            form.add_error("vendedor", "Un vendedor solo puede cargar ventas a su nombre.")
            return self.form_invalid(form)
        respuesta = super().form_valid(form)
        messages.success(self.request, "Venta actualizada correctamente.")
        return respuesta

    def get_success_url(self):
        return reverse_lazy("ventas:venta-detail", kwargs={"pk": self.object.pk})


class DetalleAgregarView(RolRequeridoMixin, View):
    roles_permitidos = ROLES_VENTAS
    http_method_names = ["post"]

    def post(self, request, pk):
        venta = get_object_or_404(Venta, pk=pk)
        if not self._puede_editar(request, venta):
            messages.error(request, "No podés modificar esta venta.")
            return redirect("ventas:venta-detail", pk=pk)

        producto = Producto.objects.filter(pk=request.POST.get("producto_id")).first()
        if producto is None:
            messages.error(request, "El producto no existe.")
            return redirect("ventas:venta-detail", pk=pk)
        try:
            cantidad = int(request.POST.get("cantidad", "1"))
            services.agregar_detalle(venta, producto, cantidad)
        except (TypeError, ValueError):
            messages.error(request, "La cantidad debe ser un número entero.")
        except ValidationError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, "Ítem agregado; totales actualizados.")
        return redirect("ventas:venta-detail", pk=pk)

    def _puede_editar(self, request, venta):
        if not venta.activo or venta.estado != EstadoVenta.BORRADOR:
            return False
        return rol_de(request.user) == Rol.ADM or venta.vendedor_id == request.user.pk


class DetalleQuitarView(RolRequeridoMixin, View):
    roles_permitidos = ROLES_VENTAS
    http_method_names = ["post"]

    def post(self, request, pk, detalle_id):
        detalle = get_object_or_404(DetalleVenta, pk=detalle_id, venta_id=pk)
        venta = detalle.venta
        if not self._puede_editar(request, venta):
            messages.error(request, "No podés modificar esta venta.")
            return redirect("ventas:venta-detail", pk=pk)
        try:
            services.quitar_detalle(detalle)
        except ValidationError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, "Ítem quitado; totales actualizados.")
        return redirect("ventas:venta-detail", pk=pk)

    def _puede_editar(self, request, venta):
        if not venta.activo or venta.estado != EstadoVenta.BORRADOR:
            return False
        return rol_de(request.user) == Rol.ADM or venta.vendedor_id == request.user.pk


class VentaConfirmarView(RolRequeridoMixin, View):
    roles_permitidos = ROLES_VENTAS
    http_method_names = ["post"]

    def post(self, request, pk):
        venta = get_object_or_404(Venta, pk=pk)
        if not (rol_de(request.user) == Rol.ADM or venta.vendedor_id == request.user.pk):
            messages.error(request, "No podés confirmar esta venta.")
            return redirect("ventas:venta-detail", pk=pk)
        try:
            services.confirmar_venta(venta)
        except ValidationError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, "Venta confirmada; stock descontado.")
        return redirect("ventas:venta-detail", pk=pk)


class VentaCancelarView(RolRequeridoMixin, View):
    """ADM cancela cualquier venta; VENDEDOR solo sus borradores."""

    roles_permitidos = ROLES_VENTAS
    http_method_names = ["post"]

    def post(self, request, pk):
        venta = get_object_or_404(Venta, pk=pk)
        es_adm = rol_de(request.user) == Rol.ADM
        if not (es_adm or (venta.vendedor_id == request.user.pk and venta.estado == EstadoVenta.BORRADOR)):
            messages.error(request, "No podés cancelar esta venta.")
            return redirect("ventas:venta-detail", pk=pk)
        try:
            services.cancelar_venta(venta)
        except ValidationError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, "Venta cancelada; stock reintegrado si correspondía.")
        return redirect("ventas:venta-detail", pk=pk)


class VentaBajaView(SoloAdminMixin, View):
    """Solo ADM da de baja ventas (incluso confirmadas) con reintegro de stock."""

    http_method_names = ["post"]

    def post(self, request, pk):
        venta = get_object_or_404(Venta, pk=pk)
        services.dar_de_baja(venta)
        messages.success(request, "Venta dada de baja; stock reintegrado.")
        return redirect("ventas:venta-list")
