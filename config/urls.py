"""URL configuration for the LeviChords project."""

from django.contrib import admin
from django.urls import include, path

from apps.core.views import RememberMeLoginView
from apps.setlists.views import HomeRedirectView

urlpatterns = [
    path("", HomeRedirectView.as_view(), name="home"),
    path("musicas/", include("apps.songs.urls")),
    path("repertorios/", include("apps.setlists.urls")),
    path("usuarios/", include("apps.users.urls")),
    path("conta/", include("apps.users.account_urls")),
    path("contas/login/", RememberMeLoginView.as_view(), name="login"),
    path("contas/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
]
