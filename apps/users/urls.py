"""URL routes for the users app."""

from django.urls import path

from apps.users import views

app_name = "users"

urlpatterns = [
    path("", views.UserListView.as_view(), name="list"),
    path("novo/", views.UserCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.UserUpdateView.as_view(), name="update"),
]
