from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

from . import views

app_name = "usuarios"

urlpatterns = [
    path(
        "accounts/login/",
        LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "accounts/logout/",
        LogoutView.as_view(next_page=reverse_lazy("core:home")),
        name="logout",
    ),
    path("accounts/registro/", views.RegistroView.as_view(), name="registro"),
    path("usuarios/", views.UsuarioListView.as_view(), name="usuario-list"),
    path("usuarios/nuevo/", views.UsuarioCreateView.as_view(), name="usuario-create"),
    path("usuarios/<int:pk>/editar/", views.UsuarioUpdateView.as_view(), name="usuario-update"),
    path("usuarios/<int:pk>/baja/", views.UsuarioBajaView.as_view(), name="usuario-baja"),
]
